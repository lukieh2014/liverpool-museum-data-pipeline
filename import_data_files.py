import boto3
import csv
import os
import logging
import argparse
import psycopg2
from psycopg2.extras import RealDictCursor
from os import environ
from dotenv import load_dotenv


def command_line_start():
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("--bucket", '-b', help="AWS Bucket Name")
    parser.add_argument("--rows", '-r', help="Number of rows to upload to DB")
    parser.add_argument("--log", '-l', default="term",
                        help="Log to file ('file') or terminal ('term')")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        raise Exception("Invalid input argument(s)")

    if args.rows is not None:
        if (args.rows).isdigit() is False:
            raise Exception("Invalid number of rows. Must be an integer!")

    if args.log not in ["term", "file"]:
        raise Exception(
            "Invalid log output destination argument. Must be 'file' or 'term'.")

    return args


def get_connection():
    """Returns connection"""
    return psycopg2.connect(
        dbname=environ.get("DB_NAME"),
        host=environ.get("HOST"),
        user=environ.get("USERNAME"),
        password=environ.get("PASSWORD")
    )


def get_cursor(conn):
    """Returns cursor object"""
    return conn.cursor(cursor_factory=RealDictCursor)


def load_csv(filename: str) -> list[dict]:
    """function to load csv file"""
    museum_csv = []
    with open(filename, 'r', encoding="utf-8") as f:
        for row in csv.DictReader(f):
            museum_csv.append(row)
    return museum_csv


def set_up_database(connection):
    with open('schema.sql', 'r', encoding="utf-8") as schema:
        schema_sql = schema.read()

    cursor.execute(schema_sql)
    connection.commit()


def import_to_database(museum_csv: list[dict], connection, num_rows) -> None:
    """Imports data loaded from csv into the SQL database"""
    cursor.execute("SET datestyle TO DMY;")
    connection.commit()

    if num_rows is None:
        num_rows = 99999999999

    added_rows = 0
    num_rows = int(num_rows)

    for row in museum_csv:
        if added_rows < num_rows:
            rating_val = row.get('val')

            try:
                rating_val = int(rating_val)
            except ValueError:
                continue

            if rating_val >= 0:
                cursor.execute("""INSERT INTO rating_interaction
                            (exhibition_id, rating_id, event_at)
                            Values
                            (%s, %s, %s);""",
                               (row.get('site'), row.get('val'), row.get('at')))
                connection.commit()
                added_rows += 1

            if rating_val == -1:
                cursor.execute("""INSERT INTO request_interaction
                            (exhibition_id, request_id, event_at)
                            Values
                            (%s, %s, %s);""",
                               (row.get('site'), row.get('type'), row.get('at')))
                connection.commit()
                added_rows += 1

    return "Success :)"


if __name__ == "__main__":

    cl_args = command_line_start()
    bucket_name = cl_args.bucket

    if bucket_name is None:
        bucket_name = input("Enter the S3 bucket name here: ")

    num_rows = cl_args.rows

    load_dotenv()
    conn = get_connection()
    cursor = get_cursor(conn)

    s3 = boto3.client('s3', aws_access_key_id=environ.get(
        "aws_access_key_id"), aws_secret_access_key=environ.get("aws_secret_access_key"))

    csv_file_names = []

    for object_name in s3.list_objects(Bucket=bucket_name)['Contents']:
        object_key = object_name['Key']

        if object_key.count(".") == 0:
            continue

        object_file_type = object_key.split(".")[1]

        if object_file_type in ["csv", "json"]:
            if object_key[:4] == "lmnh":
                s3.download_file(bucket_name, object_key,
                                 f"./museum_downloads/{object_key}")
                if object_file_type == "csv":
                    csv_file_names.append(object_key)

    logging.warning('All files downloaded.')

    with open("./museum_downloads/merged_csv.csv", 'w', newline='', encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        for filename in csv_file_names:
            with open(f"./museum_downloads/{filename}", 'r', encoding="utf-8") as infile:
                reader = csv.reader(infile)
                for row in reader:
                    writer.writerow(row)
            os.remove(f"./museum_downloads/{filename}")

    logging.warning('All CSV files merged into one.')

    # museum_csv = load_csv("./museum_downloads/merged_csv.csv")
    # set_up_database(conn)
    # import_to_database(museum_csv, conn, num_rows)

    # logging.warning('All data imported into museum database.')
