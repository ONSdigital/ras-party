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
    start = datetime.now()
    for x in range(10):
        name = random_char(10)
        trading_as = random_char(10)
        business_id = uuid.uuid4()
        business_insert_query = f"""INSERT INTO partysvc.business(party_uuid, business_ref, created_on)VALUES('{business_id}', '{random.randint(10000000000, 99999999999)}', '{datetime.now()}');"""
        firstba_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"thing": "abc"}}', '{datetime.now()}', '{name}', '{trading_as}');"""
        secondba_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"thing": "abc"}}', '{datetime.now()}', '{name}', '{trading_as}');"""
        thirdba_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"thing": "abc"}}', '{datetime.now()}', '{name}', '{trading_as}');"""
        fourthba_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"thing": "abc"}}', '{datetime.now()}', '{name}', '{trading_as}');"""
        fifthba_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"thing": "abc"}}', '{datetime.now()}', '{name}', '{trading_as}');"""

        print(f"Inserting {business_id}, which is {x}")
        cursor.execute(business_insert_query)
        cursor.execute(firstba_insert_query)
        cursor.execute(secondba_insert_query)
        cursor.execute(thirdba_insert_query)
        cursor.execute(fourthba_insert_query)
        cursor.execute(fifthba_insert_query)

    end = datetime.now()
    print(f"started at: {start}")
    print(f"ended at: {end}")

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
