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


def process_rating_field(val: str) -> float | None:
    """Parse rating array and compute average value.

    Args:
        val (str): Raw value of course rating.

    Returns:
        float | None: Parsed course rating.
    """

    def parse_rating(raw: str) -> float:
        parsed_rating = raw.replace("%", "")
        rating = float(parsed_rating) / 100.0 if len(parsed_rating) > 0 else 0.0

        return int(rating)

    inner_ratings = val[1:-1]
    parsed_ratings = inner_ratings.split(",")
    return float(np.round(np.sum([parse_rating(rate) for rate in parsed_ratings]), decimals=1))


def process_level_field(val: str) -> str:
    """Parse course level field. If level is not specified, then returns 'Mixed'.

    Args:
        val (str): Raw value of course difficulty level.

    Returns:
        str: Parsed difficulty level, which takes one of the following values: ['Beginner', 'Intermediate', 'Advanced', 'Mixed'].
    """

    if val is None:
        return "Mixed"

    replacement_map = {
        "Advanced level": "Advanced",
        "Intermediate level": "Intermediate",
        "Beginner level": "Beginner",
        "All levels": "Mixed",
        "Beg/Int level": "Mixed",
        "--": "Mixed"
    }

    return replacement_map.get(val, "Mixed")


def process_votes_field(val: str) -> int | None:
    """Parse votes number field, extracting digits.

    Args:
        val (str): Raw value of course votes.

    Returns:
        int | None: Parsed votes number.
    """

    sanitized_votes = val.replace(",", "")
    parsed_votes = re.search(r'\d+', sanitized_votes)

    return int(parsed_votes.group(0)) if parsed_votes is not None else None


def process_student_field(val: str) -> int | None:
    """Parse the student number field.

    Args:
        val (str): Raw value of student numbers.

    Returns:
        int | None: Parsed number.
    """

    sanitized_student_number = val.strip("\n").replace(",", "")
    parsed_student_number = re.search(r'\d+', sanitized_student_number)

    return int(parsed_student_number.group(0)) if parsed_student_number is not None else None


def process_duration_field(val: str) -> float | None:
    """Parse duration field, returns `None` if field is not parsable.

    Args:
        val (str): Raw value of course duration.

    Returns:
        float | None: Parsed duration value in hours.
    """

    if " total hours" in val:
        return float(val.replace(" total hours", ""))
    elif " total hour" in val:
        return float(val.replace(" total hour", ""))
    elif " total mins" in val:
        return float(np.round(float(val.replace(" total mins", "")) / 60.0, decimals=1))
    else:
        return None


process_author_field_udf = udf(lambda x: process_author_field(x), StringType())
process_rating_field_udf = udf(lambda x: process_rating_field(x), DoubleType())
process_level_field_udf = udf(lambda x: process_level_field(x), StringType())
process_votes_field_udf = udf(lambda x: process_votes_field(x), IntegerType())
process_student_field_udf = udf(lambda x: process_student_field(x), IntegerType())
process_duration_field_udf = udf(lambda x: process_duration_field(x), DoubleType())


def process_skillshare_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed Skillshare dataframe.

    Returns:
        DataFrame: New processed dataframe.
    """

    return df.select(
        clean_text_udf(col("title")).alias("title"),
        process_author_field_udf(col("authors")).alias("author"),
        process_rating_field_udf(col("rating")).alias("rating"),
        process_votes_field_udf(col("votes_count")).alias("votes_count"),
        process_student_field_udf(col("students_count")).alias("students_count"),
        process_level_field_udf(col("level")).alias("level"),
        process_duration_field_udf(col("duration")).alias("duration"),
        col("platform"), col("free")
    )

