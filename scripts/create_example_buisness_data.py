"""Creates example Business and Business Attribute data for testing"""

import os
import sys

parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_path)

import random
import string
import uuid
from datetime import datetime

import psycopg2

from config import Config


def random_char(y):
    return "".join(random.choice(string.ascii_letters) for x in range(y))


try:
    connection = psycopg2.connect(Config.DATABASE_URI)
    cursor = connection.cursor()
    start = datetime.now()
    # auth_insert_query = f"""INSERT INTO auth.user(id, username, hashed_password, account_verified)VALUES(16, 'John16Doe16@example.co.uk', '$2b$12$j58D5I24vCZxrgpt9HseVOWBgaZhAINDvDYK.dbBCCRwxG5s7CHK.', true)"""
    for x in range(26):
        count = x + 1
        name = "steve" + str(count)
        trading_as = "hen" + str(count)
        business_id = uuid.uuid4()
        party_uuid = uuid.uuid4()
        first_name = "John" + str(count)
        last_name = "Doe" + str(count)
        email_address = first_name + last_name + "@example.co.uk"
        status = "ACTIVE"
        business_insert_query = f"""INSERT INTO partysvc.business(party_uuid, business_ref, created_on)VALUES('{business_id}', '{random.randint(10000000000, 99999999999)}', '{datetime.now()}');"""
        business_attributes_insert_query = f"""INSERT INTO partysvc.business_attributes(business_id, sample_summary_id, collection_exercise, "attributes", created_on, "name", trading_as) VALUES('{business_id}', '{uuid.uuid4()}', '{uuid.uuid4()}', '{{"name": "{name}", "trading_as": "{trading_as}"}}', '{datetime.now()}', '{name}', '{trading_as}');"""
        respondent_insert_query = f"""INSERT INTO partysvc.respondent(party_uuid, status, email_address, first_name, last_name, telephone) VALUES('{party_uuid}', '{status}', '{email_address}', '{first_name}', '{last_name}', '07341667945');"""
        # respondent_get_id = f"""SELECT * FROM partysvc.respondent"""
        business_respondent_insert_query = f"""INSERT INTO partysvc.business_respondent(business_id, respondent_id, status, effective_from)VALUES('{business_id}', '{count}', '{status}', '{datetime.now()}' );"""

        cursor.execute(business_insert_query)
        for _ in range(5):
            cursor.execute(str(business_attributes_insert_query))

        cursor.execute(respondent_insert_query)
        cursor.execute(business_respondent_insert_query)
        # cursor.execute(auth_insert_query)
        # connection.commit()
        # respondent_id = cursor.execute(respondent_get_id)

        print(f"Inserting records for [{business_id}].  Processed {x} so far")

    connection.commit()
    print(f"Successfully wrote data to tables. Time elapsed [{datetime.now() - start}] ")

except psycopg2.Error as error:
    print("Something went wrong with the database", error)
except Exception as error:
    print("Something went wrong", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
