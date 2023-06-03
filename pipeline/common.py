from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

from util.text import clean_text

clean_text_udf = udf(lambda x: clean_text(x), StringType())

