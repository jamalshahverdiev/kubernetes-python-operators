from psycopg2 import connect
from os import getenv

class PostgresClient:
    def __init__(self, host, username, password, db):
        self.host = host
        self.username = username
        self.__password = password
        self.db = db
        self.__connection = None

    def connect_if_not_connected(self):
        if self.__connection is None:
            self.__connection = connect(database=self.db, user=self.username, password=self.__password, host=self.host)

    def get_connection(self):
        return self.__connection
    
    def insert_row(self, table, primary_id, name, registered, zipcode, country):
        self.connect_if_not_connected()
        db_connection = self.get_connection()

        insert_query = """INSERT INTO {table_name} (id, name, registered, zipcode, country) VALUES ('{id}', '{name}', '{registered}', '{zipcode}', '{country}')""".format(
            table_name=table, 
            id=primary_id, 
            name=name, 
            registered=registered, 
            zipcode=zipcode,
            country=country
        )

        with db_connection.cursor() as cursor:
            cursor.execute(insert_query)
            db_connection.commit()


    def update_row(self, table, primary_id, name, registered, zipcode, country):
        self.connect_if_not_connected()
        db_connection = self.get_connection()

        update_query = """UPDATE {table_name} SET name='{name}', registered='{registered}', zipcode='{zipcode}', country='{country}' WHERE id='{id}'""".format(
            table_name=table, 
            id=primary_id, 
            name=name, 
            registered=registered, 
            zipcode=zipcode,
            country=country
        )

        with db_connection.cursor() as cursor:
            cursor.execute(update_query)
            db_connection.commit()

    def delete_row(self, table, primary_id):
        self.connect_if_not_connected()
        db_connection = self.get_connection()
        delete_query = """DELETE FROM {table_name} WHERE id='{id}'""".format(
            table_name=table, 
            id=primary_id
        )

        with db_connection.cursor() as cursor:
            cursor.execute(delete_query)
            db_connection.commit()
            
def postgres_client_from_env():
    PSQL_HOST = getenv("PSQL_HOST")
    PSQL_USERNAME = getenv("PSQL_USERNAME")
    PSQL_PASSWORD = getenv("PSQL_PASSWORD")
    PSQL_DB = getenv("PSQL_DB")

    client = PostgresClient(db=PSQL_DB, username=PSQL_USERNAME, password=PSQL_PASSWORD, host=PSQL_HOST)
    client.connect_if_not_connected()
    return client