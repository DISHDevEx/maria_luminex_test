from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, year, month


def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation3").getOrCreate()

    input_path, output_path = get_input_output_paths()

    # Reading data
    input_data = read_data(spark, input_path)
    input_data.show()

    # Transformation
    transformed_data = transformation_3(input_data)
    transformed_data.show()

    # Write the converted data to the output path
    write_data(transformed_data, output_path)

    # Stop the Spark session
    spark.stop()


def get_input_output_paths():
    import sys

    if len(sys.argv) != 5:
        print("Usage: spark-submit script.py --input <input_path> --output <output_path>")
        sys.exit(1)

    # Get input and output paths from command-line arguments
    input_index = sys.argv.index("--input") + 1
    output_index = sys.argv.index("--output") + 1
    input_path = sys.argv[input_index]
    output_path = sys.argv[output_index]

    return input_path, output_path


def read_data(input_path):
    """
    Main function to initiate the S3 data processing.
    """
    process_s3_data(input_path)


def read_csv_to_df(spark, bucket_folder_path):
    """
    Reads CSV data from an S3 bucket folder path into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The S3 bucket folder path containing the CSV files.

    Returns:
        df: A Spark DataFrame representing the CSV data.
    """
    df = spark.read.csv(bucket_folder_path, header=True, inferSchema=True)
    spark.stop()

    return df

def read_json_to_df(spark, bucket_folder_path):
    """
    Reads data from a JSON file into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The file path of the JSON file.

    Returns:
        df: A Spark DataFrame representing the JSON data.
    """
    df = spark.read.json(bucket_folder_path, multiLine=True)
    spark.stop()

    return df

def read_parquet_to_df(spark, bucket_folder_path):
    """
    Reads data from a Parquet file into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The file path of the Parquet file.

    Returns:
        df: A Spark DataFrame representing the Parquet data.
    """
    df = spark.read.parquet(bucket_folder_path)
    spark.stop()

    return df


def process_s3_data(bucket_folder_path):
    """
    Processes data in an S3 bucket based on the file extension.

    Parameters:
        bucket_folder_path (str): The S3 bucket folder path containing the data files.

    Returns:
        None
    """

    # Choose the appropriate method based on the file extension
    if bucket_folder_path.lower().endswith(".json"):
        read_json_to_df(bucket_folder_path)
    if bucket_folder_path.lower().endswith(".csv"):
        read_csv_to_df(bucket_folder_path)
    if bucket_folder_path.lower().endswith(".parquet"):
        read_parquet_to_df(bucket_folder_path)


def transformation_3(input_df):
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
            - 'Year': Extracted from the 'Date' column.
            - 'Month': Extracted from the 'Date' column.
            - 'TotalSales_Product': Total sales for each product.
            - 'TotalSales_Category': Total sales for each category.
            - 'SalesPercentage_Product': Sales percentage for each product.
            - 'SalesPercentage_Category': Sales percentage for each category.

    """
    # Convert 'Date' column to timestamp format
    input_df = input_df.withColumn('Date', col('Date').cast('timestamp'))

    # Extract 'Year' and 'Month' from 'Date'
    input_df = input_df.withColumn('Year', year('Date'))
    input_df = input_df.withColumn('Month', month('Date'))

    # Calculate total sales for each product and category
    total_sales_per_product = input_df.groupBy('Product').agg(sum('Revenue').alias('TotalSales_Product'))
    total_sales_per_category = input_df.groupBy('Category').agg(sum('Revenue').alias('TotalSales_Category'))

    # Merge total sales back into the main DataFrame
    input_df = input_df.join(total_sales_per_product, on='Product')
    input_df = input_df.join(total_sales_per_category, on='Category')

    # Calculate sales percentage for each product and category
    input_df = input_df.withColumn('SalesPercentage_Product', (col('Revenue') / col('TotalSales_Product')) * 100)
    input_df = input_df.withColumn('SalesPercentage_Category', (col('Revenue') / col('TotalSales_Category')) * 100)

    # Drop temporary columns used for calculation
    input_df = input_df.drop('TotalSales_Product', 'TotalSales_Category')

    return input_df


def write_data(data, output_path):
    data.repartition(1).write.mode("overwrite").option("header", "true").csv(output_path)

