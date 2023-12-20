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


def read_data(spark, input_path):
    """
        Reads the input file from an S3 bucket and returns a DataFrame.

        Parameters:
        - input_path: S3 path of the input dataset

        Returns:
        - dataframe: Dataframe containing the input data.
    """
    df = None
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
    df.repartition(1).write.format(output_format).mode("overwrite").save(output_path)


if __name__ == "__main__":
    main()
