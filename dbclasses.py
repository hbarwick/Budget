import pymysql
import datetime as dt

class DataBaseObject:
    """Base database object to hold connection to
    the MYSQL database and run commands to fetch data
    and update tables."""

    # TODO set up sql server on webserver

    def __init__(self):
        self.connection = pymysql.connect(host="localhost",
                                          user="root",
                                          passwd="",
                                          database="budget")

    def __enter__(self):
        self.connection = pymysql.connect(host="localhost",
                                          user="root",
                                          passwd="",
                                          database="budget")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.connection.close()

    def run_database_command(self, command, args=None):
        cursor = self.connection.cursor()
        cursor.execute(command, args)
        self.connection.commit()
        return cursor

    def fetch_data(self, command, args=None):
        """Applies the fetchall method to the cursor to return output from database"""
        cursor = self.run_database_command(command, args)
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
        user = """INSERT INTO users (username, first_name, last_name, email, password)
        VALUES (%s, %s, %s, %s, %s);
        """
        args = (self.username, self.first_name, self.last_name, self.email, self.password)
        return user, args

    def check_duplicate(self):
        query = "SELECT * FROM users WHERE username = %s"
        args = (self.username)
        usercheck = self.fetch_data(query, args)
        return usercheck == ()

    def update_database(self):
        user, args = self.new_user_sql()
        self.run_database_command(user, args)
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
        query = """INSERT INTO payments (user, date, value, category, extra_details)
        VALUES (%s, %s, %s, %s, %s);"""
        args = (self.user, self.date, self.value, self.category, self.extra_details)
        return query, args

    def update_database(self):
        query, args = self.new_payment_sql()
        self.run_database_command(query, args)
        self.close_database_connection()


class Income(DataBaseObject):
    def __init__(self, user, date, income_name, value, recurring):
        super(Income, self).__init__()
        self.user = user
        self.date = date
        self.income_name = income_name
        self.value = value
        self.recurring = recurring

    def new_income_sql(self):
        query = """INSERT INTO income (user, date, income_name, value, recurring)
        VALUES (%s, %s, %s, %s, %s);"""
        args = (self.user, self.date, self.income_name, self.value, self.recurring)
        return query, args

    def update_database(self):
        query, args = self.new_income_sql()
        self.run_database_command(query, args)
        self.close_database_connection()


class Bill(DataBaseObject):
    def __init__(self, user, date, bill_name, monthly_value):
        super(Bill, self).__init__()
        self.user = user
        self.date = date
        self.bill_name = bill_name
        self.monthly_value = monthly_value

    def new_bill_sql(self):
        query = """INSERT INTO bills (user, date, bill_name, monthly_value)
        VALUES (%s, %s, %s, %s);
        """
        args = (self.user, self.date, self.bill_name, self.monthly_value)
        return query, args

    def update_database(self):
        query, args = self.new_bill_sql()
        self.run_database_command(query, args)
        self.close_database_connection()
