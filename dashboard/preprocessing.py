import re


re_common_line_separator = re.compile(r'[\n\r\t]+')
re_punctuation = re.compile(r'[!"#$%&\(\)\*\+,\./:;<=>?@\\^_`{|}~\[\]-]+')
re_non_unicode = re.compile(r'[^\u0000-\u007F]+')
re_digits_in_words = re.compile(r'\b(\w)*(\d)(\w)*\b')
re_redundant_spaces = re.compile(r'[ ]+')


def text_preprocessing(text: str) -> str:
    steps = [
        # Convert sentences to lowercase
        lambda text: text.lower(),
        # Substitute common line separator symbols [\n, \r, \t] with spaces
        lambda text: re_common_line_separator.sub(' ', text),
        # Remove punctuation
        lambda text: re_punctuation.sub(' ', text),
        # Remove Unicode symbols
        lambda text: re_non_unicode.sub(' ', text),
        # Remove words that contain digits
        lambda text: re_digits_in_words.sub('', text),
        # Remove redundant spaces between each word
        lambda text: re_redundant_spaces.sub(' ', text),
        # Strip string
        lambda text: text.strip()
    ]

    for step in steps:
        text = step(text)

    return text
