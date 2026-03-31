import re


def strip_markup(text: str) -> str:
    """
    Removes GEM engine color markup tags like <c(FFFFFF)> and </c>
    to return plain, clean text. Useful for list displays.
    """
    if not text:
        return ""

    # Remove opening <c(...)> tags
    clean_text = re.sub(r"<c\([^)]+\)>", "", text)
    # Remove closing </c> tags
    clean_text = clean_text.replace("</c>", "")

    return clean_text


def to_html(text: str) -> str:
    """
    Converts GEM engine color markup into Qt-compatible HTML/Rich Text.
    e.g., <c(B22222)>Text</c> becomes <span style="color:#B22222;">Text</span>
    Also converts newline characters to <br> tags for proper rendering.
    """
    if not text:
        return ""

    # Replace opening <c(HEX)> with HTML span tags
    html_text = re.sub(r"<c\(([^)]+)\)>", r'<span style="color:#\1;">', text)
    # Replace closing </c> tags with closing span tags
    html_text = html_text.replace("</c>", "</span>")
    # Convert literal \n or actual newlines to HTML breaks
    html_text = html_text.replace("\\n", "<br>").replace("\n", "<br>")

    return html_text
