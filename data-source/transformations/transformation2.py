from pyspark.sql import SparkSession

def main():
    # Create a Spark session
    spark = SparkSession.builder.appName("Transformation2").getOrCreate()

    input_path, output_path = get_input_output_paths()

    # Read data
    input_data = read_data(spark, input_path)
    input_data.show()
    converted_data = convert_data(input_data)
    converted_data.show()

    # Write the converted data to the output path
    write_data(converted_data, output_path)

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

def convert_data(input_data):
    converted_data = input_data.withColumnRenamed("Revenue", "Price")
    return converted_data

def write_data(data, output_path):
    data.write.mode("overwrite").csv(output_path)

if __name__ == "__main__":
    main()