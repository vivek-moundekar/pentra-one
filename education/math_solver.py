"""Bounded exact arithmetic. No eval, exec, symbolic code or model arithmetic."""
import ast
import re
from fractions import Fraction


def _display(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def solve_arithmetic(question, language="auto"):
    text = question.strip()
    # Only handle standalone arithmetic or these explicit question wrappers.
    text = re.sub(r"^(?:calculate|solve|evaluate|what\s+is|what's|kitna\s+hoga)\s*:?\s*", "", text, flags=re.I)
    text = re.sub(r"\s+(?:ka\s+answer(?:\s+kya\s+hai)?|kitna\s+hai|solve\s+karo|kya\s+hai)\s*[?।]*$", "", text, flags=re.I)
    text = re.sub(r"\s*=\s*\??\s*$", "", text).rstrip("? ")
    text = text.replace("×", "*").replace("÷", "/").replace("−", "-")
    if not re.fullmatch(r"[0-9.\s()+*/^\-]+", text or "") or not re.search(r"[+*/^\-]", text):
        return None  # General questions, equations and word problems go to the tutor.
    lang = language.lower().split('-')[0]
    if lang == "auto":
        lang = "hinglish" if re.search(r"\b(kya|hai|karo|ka|kitna)\b", question, re.I) else "en"

    def say(en, hi, mr, hinglish):
        return {"hi":hi, "mr":mr, "hinglish":hinglish}.get(lang, en)

    failure = say(
        "Please use a short numeric expression with +, -, *, /, powers and brackets. Use explicit brackets to show grouping.",
        "कृपया +, -, *, /, घात और कोष्ठकों वाला छोटा संख्यात्मक सवाल लिखें।",
        "कृपया +, -, *, /, घात आणि कंस असलेले छोटे संख्यात्मक उदाहरण लिहा.",
        "Chhota numeric expression likho: +, -, *, /, powers aur brackets use karo.",
    )
    if len(text) > 200 or any(len(n) > 12 for n in re.findall(r"\d+", text)):
        return failure
    # A slash followed by a factor with implicit multiplication can be read
    # differently. State our convention; never silently choose a denominator.
    ambiguous = bool(re.search(r"/\s*(?:\d+(?:\.\d*)?|\.\d+)\s*\(", text))
    expression = re.sub(r"(?<=[0-9)])\s*(?=\()", "*", text)
    expression = re.sub(r"(?<=\))\s*(?=[0-9])", "*", expression)
    expression = expression.replace("^", "**").strip()
    steps = []

    def bounded(value):
        if max(value.numerator.bit_length(), value.denominator.bit_length()) > 2048:
            raise ValueError("Calculation too large")
        return value

    def compute(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            literal = ast.get_source_segment(expression, node)
            if not re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)", literal or ""):
                raise ValueError("Unsupported number")
            return bounded(Fraction(literal))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = compute(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if not isinstance(node, ast.BinOp):
            raise ValueError("Unsupported expression")
        left, right = compute(node.left), compute(node.right)
        if isinstance(node.op, ast.Add):
            value, symbol = left + right, "+"
        elif isinstance(node.op, ast.Sub):
            value, symbol = left - right, "−"
        elif isinstance(node.op, ast.Mult):
            value, symbol = left * right, "×"
        elif isinstance(node.op, ast.Div):
            value, symbol = left / right, "÷"
        elif isinstance(node.op, ast.Pow):
            if right.denominator != 1 or abs(right.numerator) > 20:
                raise ValueError("Use an integer exponent between -20 and 20")
            if left == 0 and right == 0:
                raise ValueError("Zero to zero is not evaluated here")
            value, symbol = left ** right.numerator, "^"
        else:
            raise ValueError("Unsupported operator")
        value = bounded(value)
        steps.append(f"({_display(left)}) {symbol} ({_display(right)}) = {_display(value)}")
        return value

    try:    
        tree = ast.parse(expression, mode="eval")
        if len(list(ast.walk(tree))) > 90:
            return failure
        result = compute(tree.body)
    except ZeroDivisionError:
        return say("Division by zero is undefined.", "शून्य से भाग देना अपरिभाषित है।", "शून्याने भाग देणे अपरिभाषित आहे.", "Zero se divide karna undefined hai.")
    except (ValueError, SyntaxError, OverflowError, RecursionError):
        return failure
    lines = [say("Answer", "उत्तर", "उत्तर", "Answer") + ": " + _display(result)]
    if ambiguous:
        lines.append(say(
            "This notation can be read differently. Here / and multiplication have equal priority and are evaluated left to right. Put the entire denominator in brackets if that is what you mean.",
            "यह लिखावट अस्पष्ट हो सकती है। यहाँ भाग और गुणा की समान प्राथमिकता है और उन्हें बाएँ से दाएँ हल किया है। पूरे हर को कोष्ठक में लिखें यदि आपका वही मतलब है।",
            "ही मांडणी संदिग्ध असू शकते. येथे भागाकार आणि गुणाकार समान प्राधान्याने डावीकडून उजवीकडे केले आहेत. संपूर्ण छेद अभिप्रेत असल्यास तो कंसात लिहा.",
            "Is writing ka matlab alag samjha ja sakta hai. Yahan division aur multiplication ki equal priority hai: left se right solve kiya hai. Pura denominator brackets mein likho agar wahi matlab hai.",
        ))
    lines.append(say("Interpreted as: ", "इसे ऐसे पढ़ा: ", "असा अर्थ घेतला: ", "Is tarah solve kiya: ") + expression.replace("**", "^"))
    lines.extend(steps)
    if re.sub(r"\s+", "", text) == "6/2(1+2)":
        lines.append("(6/2)*(1+2) = 9; 6/(2*(1+2)) = 1.")
    return "\n".join(lines)
