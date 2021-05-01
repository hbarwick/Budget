import pymysql

class DataBaseObject:
    """Base database object to hold connection to
    the MYSQL database and run commands to fetch data
    and update tables."""

    def __init__(self):
        self.connection = pymysql.connect(host="localhost",
                                          user="root",
                                          passwd="",
                                          database="budget")

    def run_database_command(self, command):
        cursor = self.connection.cursor()
        cursor.execute(command)
        self.connection.commit()
        return cursor

    def fetch_data(self, command):
        """Applies the fetchall method to the cursor to return output from database"""
        cursor = self.run_database_command(command)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def close_database_connection(self):
        self.connection.close()


class User(DataBaseObject):
    """User object to create new users in the MYSQL database"""
    def __init__(self, username, first_name, last_name, email, password):
        super(User, self).__init__()
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    def new_user_sql(self):
        user = f"""
        INSERT INTO users (username, first_name, last_name, email, password)
        VALUES ('{self.username}', '{self.first_name}', '{self.last_name}', '{self.email}', '{self.password}');
        """
        return user

    def check_duplicate(self):
        usercheck = self.fetch_data(f"SELECT * FROM users WHERE username = '{self.username}'")
        if usercheck == ():
            return True
        else:
            return False

    def update_database(self):
        if self.check_duplicate():
            self.run_database_command(self.new_user_sql())
        else:
            print("Username already taken")
        self.close_database_connection()

newuser = User("hbarwick90",
               "Hal",
               "Barwick",
               "hallambarwick@hotmail.com",
               "password")

newuser.update_database()

#newuser.run_database_command(newuser.new_user_sql())