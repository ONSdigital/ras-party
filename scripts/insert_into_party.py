import sys
import os
parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_path)

import psycopg2
import uuid
import random
import string
from datetime import datetime

from config import Config

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

try:
    connection = psycopg2.connect(Config.DATABASE_URI)
    cursor = connection.cursor()

    business_id = uuid.uuid4()
    business_insert_query = f"""INSERT INTO partysvc.business(party_uuid, business_ref, created_on)VALUES('{business_id}', '{random.randint(10000000000, 99999999999)}', '{datetime.now()}');"""
    postgres_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"thing": "abc"}}', '{datetime.now()}', '{random_char(5)}', '{random_char(5)}');"""
    print(business_insert_query)
    print(postgres_insert_query)
    cursor.execute(business_insert_query)
    cursor.execute(postgres_insert_query)

    connection.commit()
    count = cursor.rowcount
    print (count, "Record inserted successfully into mobile table")

except (Exception, psycopg2.Error) as error:
    if(connection):
        print("Failed to insert record into mobile table", error)

finally:
    #closing database connection.
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
