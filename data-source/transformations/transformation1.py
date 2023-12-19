from pyspark.sql import SparkSession
import sys


def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation1").getOrCreate()

    input_path, output_path = get_input_output_paths()

    # Read data
    input_data = read_data(spark, input_path)
    input_data.show()

    # # Transformation
    # transformed_data = transformation_1(input_data)
    # transformed_data.show()

    # Write the converted data to the output path
    write_data(input_data, output_path)

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
        df = spark.read.csv(input_path, header=True)
    if input_path.lower().endswith(".parquet"):
        df = spark.read.parquet(input_path)
    return df


# def convert_data(input_data):
#     converted_data = input_data.drop('Weight')
#     # input_data.withColumnRenamed("Revenue", "Price")
#     # input_data.withColumn('Total', col('Revenue') * col('Quantity'))
#     return converted_data


# def transformation_1(input_data):
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
#     output_df = input_data.drop('Weight')
#     return output_df


def write_data(data, output_path):
    data.repartition(1).write.mode("overwrite").option("header", "true").json(output_path)


if __name__ == "__main__":
    main()