from __future__ import annotations

import re
from html.parser import HTMLParser


# Tags that are unsafe in generated artifacts.
BLOCKED_TAGS = {
    "script",
    "iframe",
    "object",
    "embed",
    "applet",
    "form",
    "base",
    "meta",
    "link",
}

# Event-handler attributes such as onclick, onload, onerror, etc.
EVENT_HANDLER_RE = re.compile(r"^on[a-zA-Z]+$")

# Dangerous URL schemes.
DANGEROUS_SCHEME_RE = re.compile(
    r"^\s*(javascript|vbscript|data):",
    re.IGNORECASE,
)


class HTMLSanitizer(HTMLParser):
    """
    Lightweight sanitizer for LLM-generated HTML.

    The generated artifact is considered untrusted.
    We remove executable or externally embeddable content
    before storing/rendering it.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)

        self.output: list[str] = []
        self.blocked_depth = 0

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()

        if tag in BLOCKED_TAGS:
            self.blocked_depth += 1
            return

        if self.blocked_depth > 0:
            return

        safe_attrs = []

        for name, value in attrs:
            name = name.lower()

            # Remove onclick, onload, onerror, etc.
            if EVENT_HANDLER_RE.match(name):
                continue

            # Remove dangerous URL attributes.
            if name in {"href", "src", "action", "formaction"}:
                if value and DANGEROUS_SCHEME_RE.match(value):
                    continue

            # Do not allow srcdoc.
            if name == "srcdoc":
                continue

            safe_attrs.append(
                (
                    name,
                    value,
                )
            )

        attr_text = ""

        for name, value in safe_attrs:
            if value is None:
                attr_text += f" {name}"
            else:
                escaped = (
                    value.replace("&", "&amp;")
                    .replace('"', "&quot;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                attr_text += f' {name}="{escaped}"'

        self.output.append(f"<{tag}{attr_text}>")

    def handle_startendtag(self, tag: str, attrs):
        tag = tag.lower()

        if tag in BLOCKED_TAGS:
            return

        if self.blocked_depth > 0:
            return

        safe_attrs = []

        for name, value in attrs:
            name = name.lower()

            if EVENT_HANDLER_RE.match(name):
                continue

            if name in {"href", "src", "action", "formaction"}:
                if value and DANGEROUS_SCHEME_RE.match(value):
                    continue

            if name == "srcdoc":
                continue

            safe_attrs.append((name, value))

        attr_text = ""

        for name, value in safe_attrs:
            if value is None:
                attr_text += f" {name}"
            else:
                escaped = (
                    value.replace("&", "&amp;")
                    .replace('"', "&quot;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                attr_text += f' {name}="{escaped}"'

        self.output.append(f"<{tag}{attr_text}/>")

    def handle_endtag(self, tag: str):
        tag = tag.lower()

        if tag in BLOCKED_TAGS:
            if self.blocked_depth > 0:
                self.blocked_depth -= 1
            return

        if self.blocked_depth > 0:
            return

        self.output.append(f"</{tag}>")

    def handle_data(self, data: str):
        if self.blocked_depth == 0:
            self.output.append(data)

    def handle_comment(self, data: str):
        # Comments are unnecessary in generated artifacts.
        return

    def get_html(self) -> str:
        return "".join(self.output)


def sanitize_html(html: str) -> str:
    """
    Sanitize untrusted LLM-generated HTML.

    Returns safe HTML suitable for rendering inside a
    sandboxed iframe.
    """

    if not html or not html.strip():
        return ""

    parser = HTMLSanitizer()

    try:
        parser.feed(html)
        parser.close()
    except Exception:
        # Fail closed if malformed HTML causes parser problems.
        return ""

    return parser.get_html()