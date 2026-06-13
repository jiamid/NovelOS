def count_words(text: str) -> int:
    if not text:
        return 0
    # Chinese characters + whitespace-separated words
    chinese = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other = len([w for w in text.split() if w.strip()])
    return chinese + other if chinese else other


def make_summary(content: str, max_length: int = 500) -> str:
    text = content.strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
