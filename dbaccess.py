import pymysql
import datetime as dt

def execute_database_command(command):
    """Opens database connection, pass in the sql command to be executed"""
    connection = pymysql.connect(host="localhost", user="root", passwd="", database="budget")
    cursor = connection.cursor()
    cursor.execute(command)
    connection.commit()
    connection.close()
    return cursor

def add_payment(date, value, category, extra_details=None):
    payment = f"""
    INSERT INTO payments (date, value, category, extra_details)
    VALUES ('{date}', {value}, '{category}', '{extra_details}');
    """
    return payment



currentuser = "hal"
month = dt.today().month
db = DataBaseObject()
userquery = db.fetch_data(
    f"""SELECT value FROM payments 
        WHERE user = '{currentuser}'
        AND month(date) = '{month}'
        """)
db.close_database_connection()
print(f"£{str(sum(i[0] for i in userquery))}")