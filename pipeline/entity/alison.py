import re

import numpy as np
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType, IntegerType, StringType

from ..common import clean_text_udf


def process_author_field(val: list) -> str | None:
    """Parse the set of course authors, returning the first author.

    Args:
        val (list): Raw value of course authors.

    Returns:
        str | None: First author of course, returns `None` if list is empty.
    """

    return val[0] if val is None or len(val) == 0 else None


def process_student_field(val: str) -> int:
    """Parse the student number field.

    Args:
        val (str): Raw value of student numbers.

    Returns:
        int: Parsed number.
    """

    return int(val.replace(",", ""))


def process_duration_field(val: str) -> float:
    """Parse duration field. Returns sum of approximate hours of video and text data.

    Args:
        val (str): Raw value of course duration.

    Returns:
        float: Parsed duration value in hours.
    """

    parsed_minutes = re.findall(r"[\d.]+", val)
    total_duration = np.sum([float(x) for x in parsed_minutes]) / 2.0

    return float(np.round(total_duration, decimals=1))


def process_level_field(val: str) -> str:
    """Parse course level field. If level is not specified, then returns 'Mixed'.

    Args:
        val (str): Raw value of course difficulty level.

    Returns:
        str: Parsed difficulty level, which takes one of the following values: ['Beginner', 'Intermediate', 'Advanced', 'Mixed'].
    """

    return "Mixed" if val is None else val


process_author_field_udf = udf(lambda x: process_author_field(x), StringType())
process_student_field_udf = udf(lambda x: process_student_field(x), IntegerType())
process_duration_field_udf = udf(lambda x: process_duration_field(x), DoubleType())
process_level_field_udf = udf(lambda x: process_level_field(x), StringType())


def process_alison_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed Alison dataframe.

    Returns:
        DataFrame: New processed dataframe.
    """

    return df.select(
        clean_text_udf(col("title")).alias("title"),
        process_author_field_udf(col("authors")).alias("author"),
        col("rating"), col("votes_count"),
        process_student_field_udf(col("students_count")).alias("students_count"),
        process_level_field_udf(col("level")).alias("level"),
        process_duration_field_udf(col("duration")).alias("duration"),
        col("platform"), col("free")
    )

