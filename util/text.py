import re


def sub_sepr(text: str, sub_token=" ") -> str:
    """Substitute common line separation symbols (`\\n`, `\\r`, `\\t`).

    Args:
        text (str): Input text string to process.
        sub_token (str, optional): A custom token to substitute. Defaults to ' '.

    Returns:
        str: Processed input string.
    """

    return re.sub(r"[\n\r\t]+", sub_token, text)


def sub_numwords(text: str, sub_token="") -> str:
    """Substitute words that contain digits.

    Args:
        text (str): Input text string to process.
        sub_token (str, optional): A custom token to substitute. Defaults to ''.

    Returns:
        str: Processed input string.
    """

    return re.sub(r"\b(\w)*(\d)(\w)*\b", sub_token, text)


def sub_space(text: str, sub_token=" ") -> str:
    """Substitute 2+ adjacent space characters with a single space character.

    Args:
        text (str): Input text string to process.
        sub_token (str, optional): An alternative to a single space character. Defaults to ' '.

    Returns:
        str: Processed input string.
    """

    return re.sub(r"[ ]+", sub_token, text)


def clean_text(text: str | None) -> str | None:
    """Default processing pipeline for the raw string data.

    Args:
        text (str | None): Input text string to process.

    Returns:
        str | None: Processed input string. Returns None if input text is None.
    """

    return sub_space(sub_numwords(sub_sepr(text))).strip() if text is not None else None

