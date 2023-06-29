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

    if val is None or len(val) == 0:
        return None

    return val[0].replace("Institutions: ", "")\
            .replace("Institution: ", "")


def process_student_field(val: str) -> int | None:
    """Parse the student number field.

    Args:
        val (str): Raw value of student numbers.

    Returns:
        int: Parsed number.
    """

    if val is None:
        return None

    student_num_parsed = re.findall(r'\d+', val)

    if len(student_num_parsed) == 0:
        return None

    return int("".join(student_num_parsed))


def process_level_field(val: str) -> str:
    """Parse course level field, replacing 'Introductory' field with 'Beginner'.

    Args:
        val (str): Raw value of course difficulty level.

    Returns:
        str: Parsed difficulty level, which takes one of the following values: ['Beginner', 'Intermediate', 'Advanced', 'Mixed']
    """

    val = val.replace("Level: ", "")

    if val == "Introductory":
        return "Beginner"
    else:
        return val


def process_duration_field(val: str) -> float:
    """Parse duration field, spliting weeks and hours values and calculating hours.

    Args:
        val (str): Raw value of course duration.

    Returns:
        float: Parsed duration value.
    """

    if '\n' in val:
        weeks_and_hours = val.split('\n')
        weeks, hours = weeks_and_hours[0], weeks_and_hours[1]

        weeks_parsed = int(re.findall(r'\d+', weeks)[0])
        hours_parsed = np.sum([float(int(n)) for n in re.findall(r'\d+', hours)]) / 2.0

        return weeks_parsed * 4.0 + hours_parsed
    else:
        return int(re.findall(r'\d+', val)[0]) * 1.0


process_author_field_udf = udf(lambda x: process_author_field(x), StringType())
process_student_field_udf = udf(lambda x: process_student_field(x), IntegerType())
process_level_field_udf = udf(lambda x: process_level_field(x), StringType())
process_duration_field_udf = udf(lambda x: process_duration_field(x), DoubleType())


def process_edx_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed EdX dataframe.

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

