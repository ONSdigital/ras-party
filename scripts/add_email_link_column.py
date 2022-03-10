import os
import sys

parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_path)

from datetime import datetime

import psycopg2

from config import Config

try:
    connection = psycopg2.connect(Config.DATABASE_URI)
    cursor = connection.cursor()
    start = datetime.now()
    # create_email_link_column = f"""ALTER TABLE partysvc.respondent ADD change_email_link text NULL;"""
    create_email_link_column = f"""ALTER TABLE partysvc.respondent DROP verification_tokens;"""
    cursor.execute(create_email_link_column)
    end = datetime.now()
    print(f"started at: {start}")
    print(f"ended at: {end}")

    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into mobile table")

except (Exception, psycopg2.Error) as error:
    if connection:
        print("Failed to insert record into mobile table", error)

finally:
    # closing database connection.
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
