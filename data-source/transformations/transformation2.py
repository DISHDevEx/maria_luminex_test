from pyspark.sql import SparkSession
import pyspark.sql.functions as f
import sys


def main():
    """
        Main function which that runs a spark job to convert a dataset into dataframe,
        apply the transformation and next convert the transformed dataframe into json and store to an S3.

    """
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation2").getOrCreate()

    input_path, output_path = get_input_output_paths()

    output_format = "json"

    # Read data
    input_data = read_data(spark, input_path)
    input_data.show()

    # Transformation
    transformed_data = transformation_2(input_data)
    transformed_data.show()

    # Write the converted data to the output path
    pyspark_df_json_upload(transformed_data, output_format, output_path)

    # Stop the Spark session
    spark.stop()


def get_input_output_paths():
    """
        Retrieves the S3 path of the input dataset and the S3 path to save the transformed dataset.

        Returns:
        - input_path: S3 path of the input dataset
        - output_path: S3 path to save the transformed dataset
    """
    if len(sys.argv) != 5:
        print("Usage: spark-submit script.py --input <input_path> --output <output_path>")
        sys.exit(1)

    # Get input and output paths from command-line arguments
    input_index = sys.argv.index("--input") + 1
    output_index = sys.argv.index("--output") + 1
    input_path = sys.argv[input_index]
    output_path = sys.argv[output_index]

    return input_path, output_path


def read_csv_to_df(spark, bucket_folder_path):
    """
    Reads CSV data from an S3 bucket folder path into a Spark DataFrame.

    Parameters:
        bucket_folder_path (str): The S3 bucket folder path containing the CSV files.

    Returns:
        df: A Spark DataFrame representing the CSV data.
    """
    df = spark.read.csv(bucket_folder_path, header=True, inferSchema=True)

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

    return df


def read_data(spark, input_path):
    """
    Reads the input files from an S3 bucket folder and returns a DataFrame.

    Parameters:
    - spark: SparkSession instance
    - input_path: S3 path of the input dataset (folder)

    Returns:
    - dataframe: DataFrame containing the input data from all files in the folder.
    """
    # List files in the S3 bucket folder
    s3_files = spark._jvm.org.apache.hadoop.fs.Path(input_path).getFileSystem(spark._jsc.hadoopConfiguration()).listStatus(spark._jvm.org.apache.hadoop.fs.Path(input_path))

    # Filter files based on the file extension
    json_files = [str(file.getPath()) for file in s3_files if str(file.getPath()).lower().endswith(".json")]
    csv_files = [str(file.getPath()) for file in s3_files if str(file.getPath()).lower().endswith(".csv")]
    parquet_files = [str(file.getPath()) for file in s3_files if str(file.getPath()).lower().endswith(".parquet")]

    # Choose the appropriate method based on the file extension
    if json_files:
        df = spark.read.json(",".join(json_files), multiLine=True)
    elif csv_files:
        df = spark.read.csv(",".join(csv_files), header=True, inferSchema=True)
    elif parquet_files:
        df = spark.read.parquet(",".join(parquet_files))
    else:
        raise ValueError(f"No supported files found in {input_path}")

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

    """
    input_data = input_data.withColumn("SalesPerQuantity", f.col("Revenue") / f.col("Quantity"))
    transformed_data = input_data.withColumn("SalesPerWeight", f.col("Revenue") / f.col("Weight"))

    return transformed_data


def pyspark_df_json_upload(df, output_format, output_path):

    """
    Converts the transformed spark dataframe to desired format and saves the output to s3 bucket.
    df : pyspark dataframe
    output_format : format of the transformed-data
    output_path : output data stored location in s3
    """
    df.repartition(1).write.format(output_format).mode("overwrite").option("header", "true").save(output_path)
    # df.repartition(1).write.mode("overwrite").option("header", "true").csv(output_path)

if __name__ == "__main__":
    main()
