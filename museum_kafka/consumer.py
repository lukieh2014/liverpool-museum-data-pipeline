"""An example of a script that reads messages from a Kafka stream."""
import json
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from os import environ
from confluent_kafka import Consumer
import psycopg2
from psycopg2.extras import RealDictCursor

TOPIC = "lmnh"


def get_connection():
    """Returns connection"""
    print(environ.get("HOST"))
    print(environ.get("USERNAME"))
    print(environ.get("PASSWORD"))

    return psycopg2.connect(
        dbname="postgres",
        host=environ.get("HOST"),
        user=environ.get("USERNAME"),
        password=environ.get("PASSWORD")
    )


def get_cursor(conn):
    """Returns cursor object"""
    return conn.cursor(cursor_factory=RealDictCursor)


def set_up_database(connection):
    with open('schema.sql', 'r', encoding="utf-8") as schema:
        schema_sql = schema.read()

    cursor.execute(schema_sql)
    connection.commit()


def command_line_start():
    parser = argparse.ArgumentParser(exit_on_error=False)
    parser.add_argument("--log", '-l', default="term",
                        help="Log to file ('file') or terminal ('term')")
    parser.add_argument("--setup", '-s', default="false",
                        help="Set up empty tables on RDS instance (will delete any existing data!)")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        raise Exception("Invalid input argument(s)")

    if args.log not in ["term", "file"]:
        raise Exception(
            "Invalid log output destination argument. Must be 'file' or 'term'.")

    if args.setup not in ["true", "false"]:
        raise Exception(
            "Invalid 'setup' argument entered. Must be true or false.")

    return args


def convert_to_date_frac(msg_at):
    msg_at_dt = datetime.fromisoformat(msg_at)
    msg_at_hour = msg_at_dt.hour
    msg_at_min = msg_at_dt.minute

    min_fract = msg_at_min / 60
    final_msg_at = msg_at_hour + min_fract
    return final_msg_at


def log_error(error_str, logger, log_dest):
    if log_dest == "file":
        logger.error(error_str)
        return
    print(error_str)
    return


def validate_msg(msg_val_dict, logger, log_dest):
    try:
        msg_at = msg_val_dict['at']
        msg_site = msg_val_dict['site']
        msg_val = msg_val_dict['val']
        msg_type = msg_val_dict.get('type', 99)
        final_msg_at = convert_to_date_frac(msg_at)
    except KeyError:
        log_error("ERROR - Missing some key(s), skipping...", logger, log_dest)
        return {"cont": False}

    try:
        msg_site = int(msg_site)
        msg_val = int(msg_val)
        msg_type = int(msg_type)
    except (ValueError, TypeError):
        log_error("ERROR - Invalid site or value, must be a digit.",
                  logger, log_dest)
        return {"cont": False}

    if (8.75 <= final_msg_at <= 18.25) is False:
        log_error("ERROR - kiosk entry at invalid time.", logger, log_dest)
        return {"cont": False}
    if (-1 <= msg_val <= 4) is False:
        log_error("ERROR - invalid message value.", logger, log_dest)
        return {"cont": False}
    if msg_val == -1:
        if msg_type not in [0, 1]:
            log_error("ERROR - Invalid or missing type of assistance entry.",
                      logger, log_dest)
            return {"cont": False}
    if (0 <= msg_site <= 5) is False:
        log_error("ERROR - Invalid exhibition id.", logger, log_dest)
        return {"cont": False}

    return {"cont": True, "at": msg_at, "site": msg_site, "val": msg_val, "type": msg_type}


def import_to_database(db_at, db_site, db_val, db_type, connection) -> None:
    """Imports data loaded from csv into the SQL database"""

    db_at = db_at.replace("T", " ")

    if db_val >= 0:
        cursor.execute("""INSERT INTO rating_interaction
                    (exhibition_id, rating_id, event_at)
                    Values
                    (%s, %s, %s);""",
                       (db_site, db_val, db_at))
        connection.commit()
        print("RATING ADDED")

    if db_val == -1:
        cursor.execute("""INSERT INTO request_interaction
                    (exhibition_id, request_id, event_at)
                    Values
                    (%s, %s, %s);""",
                       (db_site, db_type, db_at))
        connection.commit()
        print("REQUEST ADDED")

    return "Success :)"


if __name__ == "__main__":
    load_dotenv()
    cl_args = command_line_start()
    log_dest = cl_args.log
    setup_db = cl_args.setup

    conn = get_connection()
    cursor = get_cursor(conn)

    if setup_db == "true":
        print("SETTING UP EMPTY DATABASE")
        set_up_database(conn)

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='logged_errors.txt',
                        encoding='utf-8', level=logging.DEBUG)

    config = {
        # Where is the cluster?
        'bootstrap.servers': environ.get('BOOTSTRAP_SERVERS'),
        "auto.offset.reset": "latest",  # Where do we start from?
        "group.id": 2,
        "security.protocol": environ.get('SECURITY_PROTOCOL'),
        "sasl.mechanisms": environ.get('SASL_MECHANISM'),
        "sasl.username": environ.get('KUSERNAME'),
        "sasl.password": environ.get('KPASSWORD')
    }

    # Create Consumer instance
    consumer = Consumer(config)

    # Subscribe to topic
    consumer.subscribe([TOPIC])
    msg_count = 0

    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("ERROR - invalid message.")
        else:
            msg_body = msg.value().decode('utf-8')
            print(msg_body)
            msg_val_dict = json.loads(msg_body)

            allow_to_cont = validate_msg(msg_val_dict, logger, log_dest)

            if allow_to_cont['cont'] is True:
                db_at = allow_to_cont['at']
                db_site = allow_to_cont['site']
                db_val = allow_to_cont['val']
                db_type = allow_to_cont['type']
                print(
                    f"Consumed event from topic {msg.topic()}. Received at: {db_at}, site: {db_site}, value: {db_val}")
                import_to_database(db_at, db_site, db_val, db_type, conn)
