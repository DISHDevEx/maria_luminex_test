from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation3").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    input_path, output_path = get_input_output_paths()

    # Read data
    input_data = read_data(spark, input_path)
    input_data.show()
    spark.sparkContext.setLogLevel("ERROR")
    # converted_data = convert_data(input_data)
    # converted_data.show()

    # # Write the converted data to the output path
    # write_data(input_data, output_path)

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

def read_data(spark, input_path):
    return spark.read.csv(input_path, header=True)

# def convert_data(spark, input_data):
#     # converted_data = input_data.withColumn("Weight", col("Weight")*100)
#     # # df.withColumn("salary",col("salary")*100)
#     input_data.createOrReplaceTempView("input_data")
#     converted_data = spark.sql("SELECT *, (Weight * 2) AS Total FROM input_data").show()
#     return converted_data

# def write_data(data, output_path):
#     # data.repartition(1).write().mode("overwrite").csv(output_path)
#     data.repartition(1).write.mode("overwrite").option("header", "true").csv(output_path)
