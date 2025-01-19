from textwrap import wrap


def textwrap(text: str, width: int = 80, prefix: str | None = None) -> str:
    """
    Wrap the given text to a certain width.

    :param text: The text to wrap.
    :param width: The width to wrap the text to.
    :param prefix: The prefix to add to each line.
    :return: The wrapped text.
    """
    new_text = "\n".join(wrap(text, width=width, replace_whitespace=False,))
    new_text = new_text.replace("\n", "\n" + (prefix if prefix is not None else ""))
    return new_text