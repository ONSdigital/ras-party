"""create trading_as and name fields in business_attributes

So that search speed can be improved

"""
import sys
import os
import time

parent_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_path)
import psycopg2
from config import Config


def migrate_name_and_trading_as():
    """Populate the name and trading as columns in batches so as to cope with large table size"""
    first_id = 0
    batch_size = 1000
    last_id = first_id + batch_size

    maximum_id = _get_maximum_id()
    print(f"{maximum_id} records to update")
    error = None

    while first_id <= maximum_id and not error:
        try:
            print(f"first_id={first_id} , last_id={last_id} batch_size={batch_size}")

            connection = psycopg2.connect(Config.DATABASE_URI)
            cursor = connection.cursor()

            sql_query = f"SELECT * FROM partysvc.business_attributes WHERE id > {first_id} AND id < {last_id}"
            cursor.execute(sql_query)
            result = cursor.fetchall()
            for row in result:
                # named columns not returned so use positional
                trading_as = row[4].get('trading_as', '')

                name = row[4].get('name', '')

                insert_sql = f"UPDATE partysvc.business_attributes " \
                             f"SET trading_as = '{trading_as}', name = '{name}'" \
                             f" WHERE id={row[0]}"
                cursor.execute(insert_sql)

            first_id = last_id
            last_id += batch_size
            connection.commit()

        except(Exception, psycopg2.Error) as error:
            print("Failed updating business attributes", error)
        finally:
            cursor.close()
            connection.close()
            print(f"script complete, connections closed")


def _get_maximum_id():
    """ Get the maximum number of the id to look for """

    connection = psycopg2.connect(Config.DATABASE_URI)
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(id) from partysvc.business_attributes")
    maximum_id = cursor.fetchone()[0]  # returns a tuple
    cursor.close()
    connection.close()
    return maximum_id


if __name__ == '__main__':
    migrate_name_and_trading_as()
