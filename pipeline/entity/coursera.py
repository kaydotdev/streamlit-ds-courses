import re

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType, IntegerType, StringType

from ..common import clean_text_udf


def process_student_field(val: str) -> int:
    """Parse the student number field in the exponential form, where "k" = 1.000 (kilo) and "m" = 1.000.000 (mega).

    Args:
        val (str): Raw value of student numbers.

    Returns:
        int: Parsed number.
    """

    base = float(val[:-1])
    exponent = val[-1]

    if exponent == 'm':
        return int(base * 1_000_000)
    elif exponent == 'k':
        return int(base * 1_000)
    else:
        return int(base)


def process_author_field(val: list) -> str | None:
    """Parse the set of course authors, returning the first author.

    Args:
        val (list): Raw value of course authors.

    Returns:
        str | None: First author of course, returns `None` if list is empty.
    """

    return val[0] if len(val) > 0 else None


def process_votes_field(val: str) -> int:
    """Parse votes number field, extracting digits.

    Args:
        val (str): Raw value of course votes.

    Returns:
        int: Parsed votes number.
    """

    return int(val[1:-1].replace(',', ''))


def process_duration_field(val: str) -> float | None:
    """Parse duration field, returns `None` if field does not have fixed numerial value (if equals to `Approx`).

    Args:
        val (str): Raw value of course duration.

    Returns:
        float | None: Parsed duration value in hours.
    """

    if "Approx" in val:
        return None

    weeks_and_hours = re.findall(r'\d+', val)
    hours_of_weeks = 4.0 * 24.0 * float(weeks_and_hours[0])
    hours = float(weeks_and_hours[1])

    return hours_of_weeks + hours if len(weeks_and_hours) > 1 else hours


process_student_field_udf = udf(lambda x: process_student_field(x), IntegerType())
process_author_field_udf = udf(lambda x: process_author_field(x), StringType())
process_votes_field_udf = udf(lambda x: process_votes_field(x), IntegerType())
process_duration_field_udf = udf(lambda x: process_duration_field(x), DoubleType())


def process_coursera_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed Coursera dataframe.

    Returns:
        DataFrame: New processed dataframe.
    """

    return df.select(
        clean_text_udf(col("title")).alias("title"),
        process_author_field_udf(col("authors")).alias("author"),
        col("rating"),
        process_votes_field_udf(col("votes_count")).alias("votes_count"),
        process_student_field_udf(col("students_count")).alias("students_count"),
        col("level"),
        process_duration_field_udf(col("duration")).alias("duration"),
        col("platform"),
        col("free")
    )

