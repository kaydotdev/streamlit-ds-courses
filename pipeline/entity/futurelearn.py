from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType, IntegerType, StringType

from ..common import clean_text_udf, safe_extract_digit


def process_author_field(val: list) -> str | None:
    """Parse the set of course authors, returning the first author.

    Args:
        val (list): Raw value of course authors.

    Returns:
        str | None: First author of course, returns `None` if list is empty.
    """

    return val[0] if val is None or len(val) == 0 else None


def process_rating_field(val: str) -> float | None:
    """Parse rating number with valid range from 0.0 to 5.0.

    Args:
        val (str): Raw value of course rating.

    Returns:
        float | None: Parsed course rating.
    """

    return float(val[:3]) if val is not None else None


def process_votes_field(val: str) -> int | None:
    """Parse votes number field, extracting digits.

    Args:
        val (str): Raw value of course votes.

    Returns:
        int | None: Parsed votes number.
    """

    return int(safe_extract_digit(val.replace(",", ""), 0))


def process_student_field(val: str | None) -> int | None:
    """Parse the student number field.

    Args:
        val (str | None): Raw value of student numbers.

    Returns:
        int | None: Parsed number.
    """

    return int(safe_extract_digit(val.replace(",", ""), 0)) if val is not None else None


def process_duration_field(val: str) -> float | None:
    """Parse duration field, returns `None` if field is not parsable.

    Args:
        val (str): Raw value of course duration.

    Returns:
        float | None: Parsed duration value in hours.
    """

    weeks, hours = tuple(val.split(";"))

    return float(safe_extract_digit(weeks, 0.0)) * 7.0 * 24.0 + \
            float(safe_extract_digit(hours, 0.0))


process_author_field_udf = udf(lambda x: process_author_field(x), StringType())
process_rating_field_udf = udf(lambda x: process_rating_field(x), DoubleType())
process_votes_field_udf = udf(lambda x: process_votes_field(x), IntegerType())
process_student_field_udf = udf(lambda x: process_student_field(x), IntegerType())
process_duration_field_udf = udf(lambda x: process_duration_field(x), DoubleType())


def process_futurelearn_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed Futurelearn dataframe.

    Returns:
        DataFrame: New processed dataframe.
    """

    return df.select(
        clean_text_udf(col("title")).alias("title"),
        process_author_field_udf(col("authors")).alias("author"),
        process_rating_field_udf(col("rating")).alias("rating"),
        process_votes_field_udf(col("votes_count")).alias("votes_count"),
        process_student_field_udf(col("students_count")).alias("students_count"),
        col("level"),
        process_duration_field_udf(col("duration")).alias("duration"),
        col("platform"), col("free")
    )

