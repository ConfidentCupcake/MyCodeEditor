# Small built-in catalog; later merge a validated user JSON file into it.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Snippet:
    """Named insertion available to the pallete and editor menu."""
    
    identifier: str
    title: str
    languages: tuple[str, ...]
    body: str
    
class SnippetCatalog:
    """Query immutable snippets by editor language."""

    def __init__(self) -> None:
        """Create immutable built-in Markdown and Python snippets with numbered fields."""
        self._items = (
            Snippet("markdown.link", "Markdown: Link", ("markdown",), "[${1:label}](${2:url})"),
            Snippet("markdown.image", "Markdown: Image", ("markdown",),
                    "![${1:alt text}](${2:image path})"),
            Snippet("markdown.table", "Markdown: Table", ("markdown",),
                    "| ${1:Column A} | ${2:Column B} |\n| --- | --- |\n| ${3:value} | ${4:value} |"),
            Snippet("markdown.frontmatter", "Markdown: Front Matter", ("markdown",),
                    "---\ntitle: ${1:title}\ndate: ${2:date}\n---\n\n${0:body}"),
            Snippet("markdown.fence", "Markdown: Fenced Code", ("markdown",),
                    "\u0060\u0060\u0060 ${1:language}\n${0:code}\n\u0060\u0060\u0060"),
            Snippet("markdown.admonition", "Markdown: Admonition", ("markdown",),
                    "> [!${1:NOTE}]\n> ${0:text}"),
            Snippet("python.function", "Python: Function", ("python",),
                    "def ${1:name}(${2:arguments}):\n    \"\"\"${3:summary}\"\"\"\n    ${0:pass}"),
            Snippet("python.class", "Python: Class", ("python",),
                    "class ${1:Name}:\n    \"\"\"${2:Summary}.\"\"\"\n\n    ${0:pass}"),
            Snippet("python.docstring", "Python: Docstring", ("python",),
                    "\"\"\"${1:Summary}.\n\n${2:Details}\n\"\"\""),
            Snippet("python.main", "Python: Main Guard", ("python",),
                    "if __name__ == \"__main__\":\n    ${0:main()}"),
        )

    def for_language(self, language: str) -> tuple[Snippet, ...]:
        """Return snippets whose declared language matches exactly."""
        return tuple(item for item in self._items if language in item.languages)

    def all(self) -> Any:
        """Expose the immutable built-in catalog to menus without private-field access."""
        return self._items