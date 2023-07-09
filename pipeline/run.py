import argparse

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from .entity.alison import process_alison_df
from .entity.coursera import process_coursera_df
from .entity.edx import process_edx_df
from .entity.futurelearn import process_futurelearn_df
from .entity.pluralsight import process_pluralsight_df
from .entity.skillshare import process_skillshare_df
from .entity.stepik import process_stepik_df
from .entity.udemy import process_udemy_df


def common_struct_fields() -> list:
    return [
        StructField("title", StringType(), True),
        StructField("authors", ArrayType(StringType()), True),
        StructField("level", StringType(), True),
        StructField("platform", StringType(), True),
        StructField("free", BooleanType(), True)
    ]


def main():
    parser = argparse.ArgumentParser(description="Processing pipeline for raw scraped data.")

    parser.add_argument("--coursera", type=str, default="../data/coursera.json", help="File path to the Coursera scraped data.")
    parser.add_argument("--stepik", type=str, default="../data/stepik.json", help="File path to the Stepik scraped data.")
    parser.add_argument("--edx", type=str, default="../data/edx.json", help="File path to the EdX scraped data.")
    parser.add_argument("--pluralsight", type=str, default="../data/pluralsight.json", help="File path to the Pluralsight scraped data.")
    parser.add_argument("--alison", type=str, default="../data/alison.json", help="File path to the Alison scraped data.")
    parser.add_argument("--udemy", type=str, default="../data/udemy.json", help="File path to the Udemy scraped data.")
    parser.add_argument("--skillshare", type=str, default="../data/skillshare.json", help="File path to the Skillshare scraped data.")
    parser.add_argument("--futurelearn", type=str, default="../data/futurelearn.json", help="File path to the Futurelearn scraped data.")

    parser.add_argument("--output", type=str, default="../data/dataframe.csv", help="File path to the processing results.")

    args = parser.parse_args()

    spark = SparkSession.Builder()\
        .appName("Scraped data processing pipeline")\
        .master("local[*]")\
        .config("spark.driver.memory","40G")\
        .config("spark.driver.maxResultSize", "0")\
        .config("spark.kryoserializer.buffer.max", "2000M")\
        .getOrCreate()

    coursera_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", DoubleType(), True),
        StructField("votes_count", StringType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    stepik_schema = StructType([
        *common_struct_fields(),
        StructField("rating", DoubleType(), True),
        StructField("votes_count", DoubleType(), True),
        StructField("students_count", IntegerType(), True),
        StructField("duration", DoubleType(), True)
    ])

    edx_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", DoubleType(), True),
        StructField("votes_count", IntegerType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    pluralsight_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("votes_count", StringType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    alison_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("votes_count", StringType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    udemy_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("votes_count", StringType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    skillshare_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("votes_count", StringType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    futurelearn_schema = StructType([
        *common_struct_fields(),
        StructField("description", StringType(), True),
        StructField("rating", StringType(), True),
        StructField("votes_count", StringType(), True),
        StructField("students_count", StringType(), True),
        StructField("duration", StringType(), True)
    ])

    final_df = process_coursera_df(spark.read.format("json").schema(coursera_schema).load(args.coursera))\
        .union(process_stepik_df(spark.read.format("json").schema(stepik_schema).load(args.stepik)))\
        .union(process_edx_df(spark.read.format("json").schema(edx_schema).load(args.edx)))\
        .union(process_pluralsight_df(spark.read.format("json").schema(pluralsight_schema).load(args.pluralsight)))\
        .union(process_alison_df(spark.read.format("json").schema(alison_schema).load(args.alison)))\
        .union(process_udemy_df(spark.read.format("json").schema(udemy_schema).load(args.udemy)))\
        .union(process_skillshare_df(spark.read.format("json").schema(skillshare_schema).load(args.skillshare)))\
        .union(process_futurelearn_df(spark.read.format("json").schema(futurelearn_schema).load(args.futurelearn)))

    final_df.distinct().toPandas().to_csv(args.output)


if __name__ == "__main__":
    main()

