from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StringType

from ..common import clean_text_udf


def process_author_field(val: list) -> str | None:
    """Parse the set of course authors, returning the first author.

    Args:
        val (list): Raw value of course authors.

    Returns:
        str | None: First author of course, returns `None` if list is empty.
    """

    return val[0] if len(val) > 0 else None


process_author_field_udf = udf(lambda x: process_author_field(x), StringType())


def process_stepik_df(df: DataFrame) -> DataFrame:
    """Immutable processing of a dataframe.

    Args:
        df (DataFrame): Unprocessed Stepik dataframe.

    Returns:
        DataFrame: New processed dataframe.
    """

    return df.select(
        clean_text_udf(col("title")).alias("title"),
        process_author_field_udf(col("authors")).alias("author"),
        col("rating"), col("votes_count"), col("students_count"),
        col("level"), col("duration"), col("platform"), col("free")
    )

