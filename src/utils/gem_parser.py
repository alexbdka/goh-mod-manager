import re


class GemNode:
    def __init__(self, name: str):
        self.name = name
        self.values = []
        self.children = []

    def to_dict(self):
        result = {}
        if self.values:
            result["__values__"] = self.values
        for child in self.children:
            if child.name not in result:
                result[child.name] = (
                    child.to_dict() if child.children or child.values else True
                )
            else:
                if not isinstance(result[child.name], list):
                    result[child.name] = [result[child.name]]
                result[child.name].append(
                    child.to_dict() if child.children or child.values else True
                )

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
    Parses GEM engine format string into a list of GemNodes.
    """
    # Regex to match tokens: { } "..." or unquoted words
    # We also handle optional whitespace
    # Remove comments starting with ';'
    content = re.sub(r";.*", "", content)
    pattern = r'\{|\}|"[^"]*"|[^\s\{\}]+'
    tokens = [m.group(0) for m in re.finditer(pattern, content)]

    root = GemNode("root")
    stack = [root]

    for token in tokens:
        if token == "{":
            new_node = GemNode(None)
            stack[-1].children.append(new_node)
            stack.append(new_node)
        elif token == "}":
            if len(stack) > 1:
                stack.pop()
        else:
            val = token
            # Strip quotes if it's a quoted string
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]

            current_node = stack[-1]
            if current_node.name is None:
                current_node.name = val
            else:
                current_node.values.append(val)

    return root.children


def parse_gem_file(file_path: str) -> list[GemNode]:
    """
    Reads and parses a GEM engine format file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_gem(content)
