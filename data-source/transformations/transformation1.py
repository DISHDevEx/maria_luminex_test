from pyspark.sql import SparkSession
import sys

def get_input_output_paths():
    import sys

    # Ensure correct number of command-line arguments
    if len(sys.argv) != 5:
        print("Usage: spark-submit script.py --input <input_path> --output <output_path>")
        sys.exit(1)

    # Get input and output paths from command-line arguments
    input_index = sys.argv.index("--input") + 1
    output_index = sys.argv.index("--output") + 1
    input_path = sys.argv[input_index]
    output_path = sys.argv[output_index]

    return input_path, output_path

def main():

    # Create a Spark session
    spark = SparkSession.builder.appName("RemoveColumn").getOrCreate()
    input_path, output_path = get_input_output_paths()

    # Read the DataFrame from HDFS
    # input_path = "/hdfs/path/csv-to-df-output/"  # Update with the actual HDFS output path from Step 1
    df = spark.read.load(input_path)

    # Remove the second column (index 1)
    df = df.drop(df.columns[1])

    # Write the modified DataFrame to HDFS
    # output_path = "/hdfs/path/remove-column-output/"  # Update with the desired HDFS output path
    df.write.mode("overwrite").save(output_path)

    # Stop the Spark session
    spark.stop()
