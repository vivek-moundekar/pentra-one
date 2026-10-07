"""Local Ollama transport: role-based tutor chat, plus legacy generate callers."""
import json
from urllib.parse import urlsplit, urlunsplit
import requests
from decouple import config

OLLAMA_URL = config('OLLAMA_URL', default='http://127.0.0.1:11434/api/generate')
OLLAMA_MODEL = config('OLLAMA_MODEL', default='gemma3:4b')
OLLAMA_VISION_MODEL = config('OLLAMA_VISION_MODEL', default='gemma3:4b')
_session = requests.Session()


def is_placeholder(text):
    value = str(text or '').strip().casefold().strip(' .!\"\'`*')
    return value in {'', 'no answer', 'no response', 'none', 'n/a', 'null'}


def clean_history(history):
    # Retain complete turns; an old placeholder must not become an example
    # answer for the next request. This does not delete database records.
    pairs, pending = [], None
    for item in history or []:
        if not isinstance(item, dict):
            continue
        role = item.get('role')
        text = str(item.get('text', item.get('content', ''))).strip()
        if role == 'user':
            pending = text
        elif role == 'assistant':
            if pending and not is_placeholder(text):
                pairs.append((pending, text))
            pending = None
    messages = []
    for question, answer in pairs[-3:]:
        messages.extend([
            {'role':'user', 'content':question[:300]},
            {'role':'assistant', 'content':answer[:500]},
        ])
    return messages


def _payload(prompt, stream=False, images=None, mode='quick', system=None, history=None):
    payload = {
        'model': OLLAMA_VISION_MODEL if images else OLLAMA_MODEL,
        'stream': stream,
        'keep_alive': config('OLLAMA_KEEP_ALIVE', default='10m'),
        'options': {
            'temperature': 0.4,
            'num_predict': 550 if mode == 'detail' else 220,
            'num_ctx': config('OLLAMA_NUM_CTX', default=2048, cast=int),
        },
    }
    if system is None:
        payload['prompt'] = prompt
        if images:
            payload['images'] = images
    else:
        current = {'role':'user', 'content':prompt}
        if images:
            current['images'] = images
        payload['messages'] = [{'role':'system', 'content':system}] + clean_history(history) + [current]
    return payload


def _endpoint(chat):
    parts = urlsplit(OLLAMA_URL)
    path = parts.path.rstrip('/')
    if path.endswith(('/api/generate', '/api/chat')):
        path = path.rsplit('/', 1)[0] + ('/chat' if chat else '/generate')
    elif chat:
        raise RuntimeError('OLLAMA_URL must end in /api/generate or /api/chat for tutor chat.')
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def _check_response(response, images):
    if response.status_code == 404:
        raise RuntimeError('The selected AI model or endpoint is unavailable. Check Ollama model setup.')
    if images and not response.ok:
        raise RuntimeError('The photo model could not run. Check available memory and the model setup.')
    response.raise_for_status()


def _text(data, chat):
    if data.get('error'):
        raise RuntimeError('The AI model could not complete the request. Please retry.')
    result = data.get('message', {}).get('content', '') if chat else data.get('response', '')
    if not isinstance(result, str):
        raise RuntimeError('Ollama returned an unexpected response format.')
    return result


def ask_ollama(prompt, images=None, mode='quick', system=None, history=None):
    chat = system is not None
    with _session.post(
        _endpoint(chat), json=_payload(prompt, images=images, mode=mode, system=system, history=history),
        timeout=(10, 300 if images else 120),
    ) as response:
        _check_response(response, images)
        answer = _text(response.json(), chat)
    if is_placeholder(answer):
        raise RuntimeError('The model returned no useful answer. Please retry or rephrase your question.')
    return answer


def stream_ollama(prompt, images=None, mode='quick', system=None, history=None):
    chat = system is not None
    completed = False
    buffered = ''
    emitted = False
    with _session.post(
        _endpoint(chat), json=_payload(prompt, stream=True, images=images, mode=mode, system=system, history=history),
        timeout=(10, 300 if images else 120), stream=True,
    ) as response:
        _check_response(response, images)
        response.encoding = 'utf-8'
        for line in response.iter_lines(chunk_size=1, decode_unicode=True):
            if not line:
                continue
            data = json.loads(line)
            chunk = _text(data, chat)
            if chunk:
                if emitted:
                    yield chunk
                else:
                    buffered += chunk
                    # Only hold a very short prefix to detect placeholder answers.
                    if len(buffered) >= 32:
                        yield buffered
                        buffered = ''
                        emitted = True
            if data.get('done'):
                completed = True
                break
        if not completed:
            raise RuntimeError('The answer was interrupted. Please retry.')
        if not emitted:
            if is_placeholder(buffered):
                raise RuntimeError('The model returned no useful answer. Please retry or rephrase your question.')
            yield buffered
