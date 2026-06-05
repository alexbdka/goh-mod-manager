from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

type GemNodeValue = (
    str | bool | list[str] | list["GemNodeValue"] | dict[str, "GemNodeValue"]
)

TokenKind = Literal["open", "close", "atom"]


class GemParseError(ValueError):
    """Raised when GEM content is structurally invalid."""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} at line {line}, column {column}")


@dataclass(frozen=True)
class GemValidationResult:
    is_valid: bool
    errors: list[GemParseError]


@dataclass(frozen=True)
class GemRepairResult:
    content: str
    changed: bool
    added_closing_braces: int = 0
    removed_extra_closing_braces: int = 0


@dataclass(frozen=True)
class _Token:
    kind: TokenKind
    value: str
    line: int
    column: int


class GemNode:
    def __init__(self, name: str | None):
        self.name = name
        self.values: list[str] = []
        self.children: list[GemNode] = []
        self._line: int | None = None
        self._column: int | None = None

    def to_dict(self) -> GemNodeValue:
        result: dict[str, GemNodeValue] = {}
        if self.values:
            result["__values__"] = self.values
        for child in self.children:
            if child.name is None:
                continue

            child_value: GemNodeValue = (
                child.to_dict() if child.children or child.values else True
            )
            if child.name not in result:
                result[child.name] = child_value
            else:
                if not isinstance(result[child.name], list):
                    result[child.name] = cast(list[GemNodeValue], [result[child.name]])
                existing = result[child.name]
                if isinstance(existing, list):
                    cast(list[GemNodeValue], existing).append(child_value)

        # Simplify if it's just values
        if "__values__" in result and len(result) == 1:
            if len(self.values) == 1:
                return self.values[0]
            return self.values

        return result

    def __repr__(self):
        return (
            f"GemNode({self.name}, values={self.values}, children={len(self.children)})"
        )


def parse_gem(content: str) -> list[GemNode]:
    """
    Parse a GEM engine format string into a list of GemNodes.

    Comments starting with ``;`` are ignored only outside quoted strings.
    Quoted strings preserve spaces and support escaped quotes/backslashes.
    Structurally invalid input raises ``GemParseError``.
    """
    tokens = _tokenize(content)

    root = GemNode("root")
    stack = [root]

    for token in tokens:
        if token.kind == "open":
            new_node = GemNode(None)
            new_node._line = token.line
            new_node._column = token.column
            stack[-1].children.append(new_node)
            stack.append(new_node)
            continue

        if token.kind == "close":
            if len(stack) == 1:
                raise GemParseError(
                    "Unexpected closing brace", token.line, token.column
                )

            current = stack[-1]
            if current.name is None:
                raise GemParseError(
                    "Block is missing a name",
                    current._line or token.line,
                    current._column or token.column,
                )

            stack.pop()
            continue

        current = stack[-1]
        if current is root:
            raise GemParseError(
                "Unexpected value outside a block", token.line, token.column
            )

        if current.name is None:
            current.name = token.value
        else:
            current.values.append(token.value)

    if len(stack) > 1:
        current = stack[-1]
        raise GemParseError(
            "Unclosed block",
            current._line or 1,
            current._column or 1,
        )

    return root.children


def parse_gem_file(file_path: str) -> list[GemNode]:
    """
    Read and parse a GEM engine format file.
    """
    with open(file_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    try:
        return parse_gem(content)
    except GemParseError as exc:
        raise GemParseError(
            f"{file_path}: {exc.message}", exc.line, exc.column
        ) from exc


def validate_gem(content: str) -> GemValidationResult:
    """Return validation details without raising to the caller."""
    try:
        parse_gem(content)
    except GemParseError as exc:
        return GemValidationResult(is_valid=False, errors=[exc])
    return GemValidationResult(is_valid=True, errors=[])


def repair_gem_braces(content: str) -> GemRepairResult:
    """
    Repair only brace balance while respecting quoted strings and comments.

    Extra closing braces outside strings are removed. Missing closing braces are
    appended at the end. The function deliberately does not alter quoted text,
    comments, or node values.
    """
    output: list[str] = []
    depth = 0
    removed_extra = 0
    in_string = False
    in_comment = False
    escaped = False

    for char in content:
        if in_comment:
            output.append(char)
            if char == "\n":
                in_comment = False
            continue

        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == ";":
            in_comment = True
            output.append(char)
        elif char == '"':
            in_string = True
            output.append(char)
        elif char == "{":
            depth += 1
            output.append(char)
        elif char == "}":
            if depth == 0:
                removed_extra += 1
                continue
            depth -= 1
            output.append(char)
        else:
            output.append(char)

    added = depth
    if added:
        if output and not output[-1].endswith("\n"):
            output.append("\n")
        output.extend("}" for _ in range(added))

    repaired = "".join(output)
    return GemRepairResult(
        content=repaired,
        changed=removed_extra > 0 or added > 0,
        added_closing_braces=added,
        removed_extra_closing_braces=removed_extra,
    )


def _tokenize(content: str) -> list[_Token]:
    tokens: list[_Token] = []
    index = 0
    line = 1
    column = 1

    def advance(char: str) -> None:
        nonlocal line, column
        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1

    while index < len(content):
        char = content[index]

        if char.isspace():
            advance(char)
            index += 1
            continue

        if char == ";":
            while index < len(content) and content[index] != "\n":
                advance(content[index])
                index += 1
            continue

        if char == "{":
            tokens.append(_Token("open", char, line, column))
            advance(char)
            index += 1
            continue

        if char == "}":
            tokens.append(_Token("close", char, line, column))
            advance(char)
            index += 1
            continue

        if char == '"':
            token, index, line, column = _read_quoted(content, index, line, column)
            tokens.append(token)
            continue

        token, index, line, column = _read_unquoted(content, index, line, column)
        tokens.append(token)

    return tokens


def _read_quoted(
    content: str, index: int, line: int, column: int
) -> tuple[_Token, int, int, int]:
    start_line = line
    start_column = column
    index += 1
    column += 1
    value: list[str] = []
    escaped = False

    while index < len(content):
        char = content[index]

        if escaped:
            if char in {'"', "\\"}:
                value.append(char)
            else:
                value.append("\\")
                value.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            index += 1
            column += 1
            return (
                _Token("atom", "".join(value), start_line, start_column),
                index,
                line,
                column,
            )
        else:
            value.append(char)

        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1
        index += 1

    raise GemParseError("Unterminated quoted string", start_line, start_column)


def _read_unquoted(
    content: str, index: int, line: int, column: int
) -> tuple[_Token, int, int, int]:
    start_line = line
    start_column = column
    value: list[str] = []

    while index < len(content):
        char = content[index]
        if char.isspace() or char in "{};":
            break

        value.append(char)
        column += 1
        index += 1

    if not value:
        raise GemParseError("Unexpected character", start_line, start_column)

    return _Token("atom", "".join(value), start_line, start_column), index, line, column
