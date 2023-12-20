from pyspark.sql import SparkSession
import pyspark.sql.functions as f
import sys


def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation2").getOrCreate()

    input_path, output_path = get_input_output_paths()

    # Read data
    input_data = read_data(spark, input_path)
    input_data.show()

    # Transformation
    transformed_data = transformation_2(input_data)
    transformed_data.show()

    # Write the converted data to the output path
    write_data(transformed_data, output_path)

    # Stop the Spark session
    spark.stop()


def get_input_output_paths():

    if len(sys.argv) != 5:
        print("Usage: spark-submit script.py --input <input_path> --output <output_path>")
        sys.exit(1)

    # Get input and output paths from command-line arguments
    input_index = sys.argv.index("--input") + 1
    output_index = sys.argv.index("--output") + 1
    input_path = sys.argv[input_index]
    output_path = sys.argv[output_index]

    return input_path, output_path


def read_data(spark, input_path):
    # Choose the appropriate method based on the file extension
    if input_path.lower().endswith(".json"):
        df = spark.read.json(input_path, multiLine=True)
    if input_path.lower().endswith(".csv"):
        df = spark.read.csv(input_path, header=True, inferSchema=True)
    if input_path.lower().endswith(".parquet"):
        df = spark.read.parquet(input_path)
    return df


def transformation_2(input_data):
    """
    Applies a transformation to a PySpark DataFrame containing sales data.

    Parameters:
    -----------
    input_df : pyspark.sql.DataFrame
        Input PySpark DataFrame with columns: 'Product', 'Category', 'Date', 'Revenue', 'Quantity',
        'Weight', 'Color', 'Manufacturer', 'Country', 'Rating', and other optional columns.

    Returns:
    --------
    pyspark.sql.DataFrame
        Transformed DataFrame with additional columns:
            - 'SalesPerQuantity': Calculated as 'Revenue' divided by 'Quantity'.
            - 'SalesPerWeight': Calculated as 'Revenue' divided by 'Weight'.
            - 'Date': Converted to timestamp and formatted as 'dd-LLL-yyyy'.

    """
    # input_data = input_data.withColumn("SalesPerQuantity", f.col("Revenue") / f.col("Quantity"))
    transformed_data = input_data.withColumn("SalesPerWeight", f.col("Revenue") / f.col("Weight"))

    return transformed_data


def write_data(data, output_path):
    data.repartition(1).write.mode("overwrite").option("header", "true").csv(output_path)
