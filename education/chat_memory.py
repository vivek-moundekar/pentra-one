"""Account-owned Education chat memory using the existing chatbot tables."""
import re

from django.db import transaction
from django.contrib.auth import get_user_model
from chatbot.models import Conversation, Message

TITLE = "Udaan Education — saved doubts"


def conversation_for(user):
    # Lock the account while finding/creating its Education conversation.
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=user.pk)
        chat = Conversation.objects.filter(user=user, title=TITLE).order_by("id").first()
        return chat or Conversation.objects.create(user=user, title=TITLE)


def load_messages(user, limit=100):
    rows = list(Message.objects.filter(
        conversation__user=user, conversation__title=TITLE,
    ).order_by("-id")[:limit + 1])
    return ([{"role": row.role, "text": row.content} for row in reversed(rows[:limit])],
            len(rows) > limit)


def clear_messages(user):
    # Deleting the conversation also invalidates in-flight saves to this chat.
    Conversation.objects.filter(user=user, title=TITLE).delete()


def save_exchange(user, chat_id, question, answer):
    with transaction.atomic():
        chat = Conversation.objects.select_for_update().filter(
            pk=chat_id, user=user, title=TITLE,
        ).first()
        if chat is None:
            raise RuntimeError("This chat was cleared in another tab. Refresh before sending again.")
        Message.objects.bulk_create([
            Message(conversation=chat, role="user", content=question),
            Message(conversation=chat, role="assistant", content=answer),
        ])
        chat.save(update_fields=["updated_at"])


def prompt_memory(user, question):
    """Budget recent turns plus one older keyword match; avoid resending all text."""
    rows = list(Message.objects.filter(
        conversation__user=user, conversation__title=TITLE,
    ).order_by("-id")[:200])
    recent = list(reversed(rows[:6]))
    words = set(re.findall(r"\w{3,}", question.lower())) - {
        "the", "and", "this", "that", "what", "explain", "please", "question",
        "answer", "photo", "read", "step", "for", "with", "you", "how",
    }
    older = rows[6:]
    if older and words:
        def score(row):
            return len(words & set(re.findall(r"\w{3,}", row.content.lower())))
        match = max(older, key=score)
        if score(match):
            recent.insert(0, match)
    # Prioritize recent context when the small model's prompt budget is full.
    remaining = 2000
    selected = []
    for row in reversed(recent):
        text = row.content[:min(600, remaining)]
        if not text:
            break
        selected.append(f"{row.role}: {text}")
        remaining -= len(text)
    return "\n".join(reversed(selected))


# Only explicit student statements count as identity evidence. Never learn a
# name from an assistant's greeting or from a question about someone's name.
def stated_name(text):
    import unicodedata
    value = str(text).strip().strip('.!।').strip()
    patterns = (
        r"(?:mera|meraa)\s+(?:naam|nam|name)\s+(.+?)\s+(?:hai|he|hain)",
        r"my\s+name\s+is\s+(.+)",
        r"मेरा\s+नाम\s+(.+?)\s+है",
        r"माझ[ंे]\s+नाव\s+(.+?)\s+आहे",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, value, flags=re.IGNORECASE)
        if not match:
            continue
        name = ' '.join(match.group(1).split())
        if not name or len(name) > 80 or len(name.split()) > 5:
            return None
        if any(not (unicodedata.category(c)[0] in {'L', 'M'} or c in " '-’") for c in name):
            return None
        banned = {'kya', 'what', 'unknown', 'naam', 'name', 'nahi', 'nahin',
                  'not', 'ka', 'hai', 'he', 'is', 'है', 'क्या', 'नहीं', 'नाव', 'काय', 'नाही'}
        if set(name.casefold().split()) & banned:
            return None
        return name
    return None


def student_name(user):
    # Indexed by conversation/user first. Newest explicit statement wins.
    texts = Message.objects.filter(
        conversation__user=user, conversation__title=TITLE, role='user',
    ).order_by('-id').values_list('content', flat=True)
    for text in texts.iterator(chunk_size=200):
        name = stated_name(text)
        if name:
            return name
    return None


def identity_answer(question, language, name):
    """Resolve narrow identity questions without relying on model recall."""
    normalized = ' '.join(question.casefold().strip().rstrip('?.!।').split())
    student_queries = {
        'mera naam kya hai', 'mera nam kya hai', 'mera name kya hai',
        'mera naam batao', 'mera naam yaad hai', 'what is my name',
        "what's my name", 'do you remember my name', 'tell me my name',
        'मेरा नाम क्या है', 'मेरा नाम बताओ', 'माझे नाव काय आहे', 'माझं नाव काय आहे',
    }
    assistant_queries = {
        'tumhara naam kya hai', 'aapka naam kya hai', 'what is your name',
        "what's your name", 'आपका नाम क्या है', 'तुम्हारा नाम क्या है',
        'तुझे नाव काय आहे',
    }
    if normalized not in student_queries | assistant_queries:
        return None
    lang = language.lower().split('-')[0]
    if lang == 'auto':
        if normalized.startswith(('what', 'do you', 'tell me')):
            lang = 'en'
        elif normalized.startswith(('माझ', 'तुझे')):
            lang = 'mr'
        elif any('\u0900' <= c <= '\u097f' for c in normalized):
            lang = 'hi'
        else:
            lang = 'hinglish'
    if normalized in assistant_queries:
        return {'en':'My name is Udaan AI.', 'hi':'मेरा नाम Udaan AI है।',
                'mr':'माझे नाव Udaan AI आहे.'}.get(lang, 'Mera naam Udaan AI hai.')
    if name:
        return {'en':f'Your name is {name}.', 'hi':f'आपका नाम {name} है।',
                'mr':f'तुमचे नाव {name} आहे.'}.get(lang, f'Aapka naam {name} hai.')
    return {
        'en':'I cannot find your name in this saved chat. Please tell me: My name is …',
        'hi':'इस सेव की गई चैट में आपका नाम नहीं मिला। कृपया बताइए: मेरा नाम … है।',
        'mr':'या जतन केलेल्या चॅटमध्ये तुमचे नाव सापडले नाही. कृपया सांगा: माझे नाव … आहे.',
    }.get(lang, 'Is saved chat mein aapka naam nahi mila. Ek baar batao: Mera naam … hai.')
