import re

from typing import Any
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

from util.text import clean_text


def safe_extract_digit(val: str, default=None) -> str | Any:
    """Safely extracts a first occuring digits from a given string.

    Args:
        val (str): String to extract the float from.
        default (Any, optional): Default value to return if string does not contain any digits. Defaults to None.

    Returns:
        str | Any: Extracted float value if the operation is successful; otherwise, the default value.
    """

    if val is None:
        return default

    parsed_val = re.search(r'\d+', val)

    return parsed_val.group(0) if parsed_val is not None else default


clean_text_udf = udf(lambda x: clean_text(x), StringType())

