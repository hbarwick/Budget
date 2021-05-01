import pymysql

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

execute_database_command(add_payment("2021-04-30", 20.32, "Catfood"))
