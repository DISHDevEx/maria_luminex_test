from pyspark.sql import SparkSession
import sys
import pyspark.sql.functions as f
from pyspark.sql.functions import cast

def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation3").getOrCreate()

    input_path, output_path = get_input_output_paths()

    # Read data
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


def transformation_3(input_data):
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
    input_data = input_data.withColumn("Date", cast(input_data["Date"], "timestamp"))
    # input_data = input_data.withColumn('Date', col('Date').cast('timestamp'))

    # Calculate total sales for each product and category
    total_sales_per_product = input_data.groupBy("Product").agg(f.sum('Revenue').alias('TotalSales_Product'))
    total_sales_per_category = input_data.groupBy('Category').agg(f.sum('Revenue').alias('TotalSales_Category'))

    # Merge total sales back into the main DataFrame
    input_data = input_data.join(total_sales_per_product, on="Product")
    input_data = input_data.join(total_sales_per_category, on="Category")

    input_data = input_data.withColumn("SalesPercentage_Product", (f.col("Revenue") / f.col("TotalSales_Product")) * 100)
    input_data = input_data.withColumn("SalesPercentage_Category", (f.col("Revenue") / f.col("TotalSales_Category")) * 100)

    # Drop temporary columns used for calculation
    transformed_data = input_data.drop('TotalSales_Product', 'TotalSales_Category')

    return transformed_data


def write_data(data, output_path):
    # data.repartition(1).write().mode("overwrite").csv(output_path)
    data.write.mode("overwrite").csv(output_path)
