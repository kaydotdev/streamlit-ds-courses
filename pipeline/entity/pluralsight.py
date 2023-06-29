import re
from functools import reduce

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


def process_votes_field(val: str) -> int | None:
    """Parse votes number field, extracting digits.

    Args:
        val (str): Raw value of course votes.

    Returns:
        int | None: Parsed votes number.
    """

    return int(val[1:-1].replace(',', '')) if val is None else None


def process_rating_field(val: str) -> float | None:
    """Parse rating number with valid range from 0.0 to 5.0.

    Args:
        val (str): Raw value of course rating.

    Returns:
        float | None: Parsed course rating.
    """

    if len(val) == 0:
        return None

    return reduce(
        lambda x, y: x + y,
        map(lambda x: 0.5 if x == 'fa fa-star-half-o' else 1.0, val.split(';'))
    )


def process_duration_field(val: str) -> float | None:
    """Parse duration field. Returns sum of approximate hours of video and text data.

    Args:
        val (str): Raw value of course duration.

    Returns:
        float | None: Parsed duration value in hours.
    """

    parsed_minutes = re.findall(r'\d+', val)

    if len(parsed_minutes) == 0:
        return None

    parsed_hours = reduce(lambda x, y: x + y, map(lambda x: float(int(x)), parsed_minutes)) / 60.0
    rounded_hours = float(np.round(parsed_hours, decimals=1))

    return 0.1 if rounded_hours == 0.0 else rounded_hours


process_author_field_udf = udf(lambda x: process_author_field(x), StringType())
process_votes_field_udf = udf(lambda x: process_votes_field(x), IntegerType())
process_rating_field_udf = udf(lambda x: process_rating_field(x), DoubleType())
process_duration_field_udf = udf(lambda x: process_duration_field(x), DoubleType())


def process_pluralsight_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed EdX dataframe.

    Returns:
        DataFrame: New processed dataframe.
    """

    return df.select(
        clean_text_udf(col("title")).alias("title"),
        process_author_field_udf(col("authors")).alias("author"),
        process_rating_field_udf(col("rating")).alias("rating"),
        process_votes_field_udf(col("votes_count")).alias("votes_count"),
        col("students_count"), col("level"),
        process_duration_field_udf(col("duration")).alias("duration"),
        col("platform"), col("free")
    )

