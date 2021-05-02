import pymysql
import datetime as dt

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
            return False
        else:
            return True

    def update_database(self):
        self.run_database_command(self.new_user_sql())
        self.close_database_connection()


class Payment(DataBaseObject):
    def __init__(self, user, date, value, category, extra_details):
        super(Payment, self).__init__()
        self.user = user
        self.date = date
        self.value = value
        self.category = category
        self.extra_details = extra_details

    def new_payment_sql(self):
        payment = f"""
        INSERT INTO payments (user, date, value, category, extra_details)
        VALUES ('{self.user}', '{self.date}', '{self.value}', '{self.category}', '{self.extra_details}');
        """
        return payment

    def update_database(self):
        self.run_database_command(self.new_payment_sql())
        self.close_database_connection()

class Income(DataBaseObject):
    pass


class Bill(DataBaseObject):
    pass

# db = DataBaseObject()
# userquery = db.fetch_data(
#     f"""SELECT value FROM payments
#         WHERE user = 'hal'
#         AND month(date) = '5'
#         """)
#
# print(userquery)
#
# output = sum(i[0] for i in userquery)
#
#
# print(output)

# currentuser = "hal"
# month = dt.date.today().month
# db = DataBaseObject()
# userquery = db.fetch_data(
#     f"""SELECT value FROM payments
#         WHERE user = '{currentuser}'
#         AND month(date) = '{month}'
#         """)
# db.close_database_connection()
# print(f"£{str(sum(i[0] for i in userquery))}")