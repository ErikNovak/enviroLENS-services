import psycopg2


class PostgresQL:
    """Connection to the PostgresQL database

    Args:
        host (str): The host address. (Default "127.0.0.1")
        port (str): The port number. (Default "5432")

    """

    def __init__(self, host="127.0.0.1", port="5432"):
        self.host = host
        self.port = port


    def connect(self, database, password, user="postgres"):
        """Connects to the database with the provided user and password

        Args:
            database (str): The database name.
            password (str): The password of the user.
            user (str): The postgresql user. (Default "postgres")
        """

        try:
            # create a connection
            self.connection = psycopg2.connect(
                user = user,
                password = password,
                host = self.host,
                port = self.port,
                database = database
            )

            # store the connection cursor
            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.Error) as error:
            # notify the user about the error
            self.cursor = None


    def disconnect(self):
        """Disconnect the postgresql connection to the database"""
        if self.connection:
            self.cursor.close()
            self.connection.close()


    def execute(self, statement):
        """Execute the provided statement

        Args:
            statement (str): The postgresql statement to be executed.

        Returns:
            list: a list of tuples containing the postgresql records.

        """
        if self.cursor is None:
            raise Exception("The connection is not established")
        else:
            self.cursor.execute(statement)
            num_fields = len(self.cursor.description)
            field_names = [i[0] for i in self.cursor.description]
            return [{ field_names[i]: row[i] for i in range(num_fields) } for row in self.cursor.fetchall()]


    def get_documents_from_db(self, document_ids):
        """
        Function receives a list of document ids and returns a list of dictionaries of documents data.

        Parameters:
            documents_ids : list(int)
                list of document ids

        Returns:
            success (boolean), list of dictionaries of document data if the extraction from the database was successful.
        """

        if self.cursor is None:
            return False, {'Error' : 'The connection could not be established'}

        statement = "SELECT * FROM documents WHERE document_id IN %s;"
        try:
            self.cursor.execute(statement, (tuple(document_ids),))
        except:
            return False, {'Error' : 'You provided invalid document ids.'}

        # Enumerating the fields
        num_fields = len(self.cursor.description)
        field_names = [i[0] for i in self.cursor.description]
        documents = [{ field_names[i]: row[i] for i in range(num_fields) } for row in self.cursor.fetchall()]

        # Cleaning the output:
        # - removing fulltext field
        # - slicing down the fulltext_cleaned field to 500 chars
        # - we return only the first 10 results
        for i in range(len(documents)):
            if documents[i]['fulltext_cleaned'] is not None:
                documents[i]['fulltext_cleaned'] = documents[i]['fulltext_cleaned'][:500]
            documents[i].pop('fulltext')

        return True, documents