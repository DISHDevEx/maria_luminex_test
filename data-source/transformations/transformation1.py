from pyspark.sql import SparkSession
from pyspark.sql.functions import sum
import sys


def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation1").getOrCreate()
    print(spark)

    input_path, output_path = get_input_output_paths()
    print(input_path)
    print(output_path)

    # Reading data
    input_data = process_s3_data(spark, input_path)
    input_data.show()
    # input_data = read_data(spark, input_path)
    # input_data.show()

    # # Transformation
    # transformed_data = transformation_1(input_data)
    # transformed_data.show()

    # Write the converted data to the output path
    # write_data(input_data, output_path)

    # Stop the Spark session
    spark.stop()

# def read_data(spark, input_path):
#     return spark.read.csv(input_path, header=True)


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


# def read_data(spark, input_path):
#     """
#     Main function to initiate the S3 data processing.
#     """
#     # print("ksjhcfjkfhgj----------Read data")
#     # print(input_path)
#     # process_s3_data(spark, input_path)
#     return spark.read.csv(input_path, header=True)


def read_csv_to_df(spark, input_path):
    """
    Reads CSV data from an S3 bucket folder path into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The S3 bucket folder path containing the CSV files.

    Returns:
        df: A Spark DataFrame representing the CSV data.
    """
    print("ckhsjchsjh- Read CSV")
    print(input_path)
    df = spark.read.csv(input_path, header=True)

    return df

def read_json_to_df(spark, input_path):
    """
    Reads data from a JSON file into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The file path of the JSON file.

    Returns:
        df: A Spark DataFrame representing the JSON data.
    """
    df = spark.read.json(input_path, multiLine=True)

    return df

def read_parquet_to_df(spark, input_path):
    """
    Reads data from a Parquet file into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The file path of the Parquet file.

    Returns:
        df: A Spark DataFrame representing the Parquet data.
    """
    df = spark.read.parquet(input_path)

    return df


def process_s3_data(spark, input_path):
    """
    Processes data in an S3 bucket based on the file extension.

    Parameters:
        bucket_folder_path (str): The S3 bucket folder path containing the data files.

    Returns:
        None
    """
    df = spark.read.csv(input_path, header=True)
    # df = None
    # df = read_csv_to_df(spark, input_path)

    # Choose the appropriate method based on the file extension
    # if bucket_folder_path.lower().endswith(".json"):
    #     df = read_json_to_df(spark, bucket_folder_path)
    # if bucket_folder_path.lower().endswith(".csv"):
    #     print(bucket_folder_path)
    #     df = read_csv_to_df(spark, bucket_folder_path)
    # if bucket_folder_path.lower().endswith(".parquet"):
    #     df = read_parquet_to_df(spark, bucket_folder_path)

    return df


# def transformation_1(input_df):
#     """
#     Applies a transformation to calculate total sales for each product in a PySpark DataFrame.
#
#     Parameters:
#     -----------
#     input_df : pyspark.sql.DataFrame
#         Input PySpark DataFrame with columns: 'Product', 'Revenue', and other optional columns.
#
#     Returns:
#     --------
#     pyspark.sql.DataFrame
#         Transformed DataFrame with columns:
#             - 'Product': Unique products.
#             - 'TotalSales': Total sales for each product.
#
#     """
#     output_df = input_df.groupBy('Product').agg(sum('Revenue').alias('TotalSales'))
#     return output_df


def write_data(data, output_path):
    data.repartition(1).write.mode("overwrite").option("header", "true").json(output_path)

