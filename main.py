from datetime import date as dt
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from dbclasses import DataBaseObject, Income, Bill, Payment, User

Window.size = (480, 800)

Builder.load_file('KvFiles/frontend.kv')
Builder.load_file('KvFiles/mainmenu.kv')
Builder.load_file('KvFiles/popup.kv')


class LogonScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.username = None
        self.password = None

    def get_credentials(self):
        self.username = self.manager.current_screen.ids.username.text
        self.password = self.manager.current_screen.ids.password.text

    def logon_button(self):
        self.get_credentials()
        if self.check_inputs():
            if self.check_user_and_pass() != ():
                popup_message("Ok", f"Logon successful as {self.username}")
                self.manager.current_user = self.username
                self.manager.current = 'main_menu'
            else:
                popup_message("Warning", "Invalid Username and or password"
                                         "\n Please check and try again."
                                         "\n\nOr click 'Sign up for new account'")

    def new_user_button(self):
        self.manager.current = 'new_user_screen'

    def check_user_and_pass(self):
        with DataBaseObject() as db:
            query ="""SELECT * FROM users 
                   WHERE username = %s
                   AND password = %s
                   """
            args = (self.username, self.password)
            userquery = db.fetch_data(query, args)
            return userquery

    def check_inputs(self):
        """Ensures both username and password field are filled in"""
        if self.username == "" or self.password == "":
            popup_message("Warning", "Please enter username and password.")
            return False
        else:
            return True


class NewUserScreen(Screen):

    """Kivy Screen to create new user and add to
    the MySQL database"""

    def new_user(self):
        username = self.manager.current_screen.ids.username.text
        first_name = self.manager.current_screen.ids.first_name.text
        last_name = self.manager.current_screen.ids.last_name.text
        email = self.manager.current_screen.ids.email.text
        password = self.manager.current_screen.ids.password.text
        confirm_password = self.manager.current_screen.ids.confirm_password.text
        userdetails = {"username": username,
                       "first_name": first_name,
                       "last_name": last_name,
                       "email": email,
                       "password": password,
                       "confirm_password": confirm_password}
        return userdetails

    # TODO implement password hashing

    def usercheck(self):
        userdetails = self.new_user()
        if userdetails["password"] != userdetails["confirm_password"]:
            popup_message("Warning", "Passwords do not match")
            return
        elif "" in userdetails:
            popup_message("Warning", "Not all fields populated.")
            return
        else:
            user = User(userdetails["username"],
                        userdetails["first_name"],
                        userdetails["last_name"],
                        userdetails["email"],
                        userdetails["password"])
            if not user.check_duplicate():
                popup_message("Warning", "Username is taken")
                return
            user.update_database()
            popup_message("Success!", f"New user '{user.username}' created.")
            self.reset_input_fields()
            self.manager.current = 'logon_screen'

    def reset_input_fields(self):
        self.manager.current_screen.ids.username.text = ""
        self.manager.current_screen.ids.first_name.text = ""
        self.manager.current_screen.ids.last_name.text = ""
        self.manager.current_screen.ids.email.text = ""
        self.manager.current_screen.ids.password.text = ""
        self.manager.current_screen.ids.confirm_password.text = ""

    def cancel(self):
        self.manager.current = 'logon_screen'


class MainMenu(Screen):

    def update_summary_totals(self):
        self.update_total_spend()
        self.update_total_bills()
        self.update_total_income()
        self.update_funds_remaining()

    def update_total_income(self):
        """Return the total of monthly income for the
        currently logged in user, plus any one off incomes
        for the current month. To be displayed on
        the main menu summary screen"""
        user = self.manager.current_user
        month = dt.today().month
        with DataBaseObject() as db:
            monthly_incomes = db.fetch_data(
                f"""SELECT SUM(value) FROM income 
                    WHERE user = '{user}'
                    AND recurring = '1'
                    """)
            one_off_incomes = db.fetch_data(
                f"""SELECT SUM(value) FROM income 
                    WHERE user = '{user}'
                    AND recurring = '0'
                    AND month(date) = '{month}'
                    """)
        monthly = monthly_incomes[0][0]
        oneoff = one_off_incomes[0][0]
        if monthly == None:
            monthly = 0
        if oneoff == None:
            oneoff = 0
        self.manager.total_income = str(round(monthly + oneoff, 2))
        self.manager.current_screen.ids.total_income.text \
            = f"£{(str(self.manager.total_income))}"

    def update_total_spend(self):
        """Return the total of payments for the
        currently logged in user for the current month.
        To be displayed on the main menu summary screen"""
        user = self.manager.current_user
        month = dt.today().month
        with DataBaseObject() as db:
            userquery = db.fetch_data(
                f"""SELECT SUM(value) FROM payments 
                    WHERE user = '{user}'
                    AND month(date) = '{month}'
                    """)
        if userquery[0][0] == None:
            self.manager.total_spend = "0"
        else:
            self.manager.total_spend = str(round(userquery[0][0], 2))
        self.manager.current_screen.ids.total_spend.text \
            = f"£{str(self.manager.total_spend)}"

    def update_total_bills(self):
        """Queries the database to return all recurring monthly
        bills for the currently logged in user and sum the total
        to display on the summary screen"""
        user = self.manager.current_user
        with DataBaseObject() as db:
            userquery = db.fetch_data(
                f"""SELECT sum(monthly_value) FROM bills 
                    WHERE user = '{user}'
                    """)
        if userquery[0][0] == None:
            self.manager.total_bills = "0"
        else:
            self.manager.total_bills = str(round(userquery[0][0], 2))
        self.manager.current_screen.ids.total_bills.text \
            = f"£{str(self.manager.total_bills)}"

    def update_funds_remaining(self):
        self.manager.funds_remaining = str(round(
            float(self.manager.total_income) - (
                    float(self.manager.total_spend) +
                    float(self.manager.total_bills)), 2)
        )
        self.manager.current_screen.ids.funds_remaining.text =\
            f"£{self.manager.funds_remaining}"

    def on_logout_button_pressed(self):
        self.manager.current = 'logon_screen'

    def on_payment_button_pressed(self):
        self.manager.current = 'payment_screen'

    def on_income_button_pressed(self):
        self.manager.current = 'income_screen'

    def on_bill_button_pressed(self):
        self.manager.current = 'bill_screen'


class PaymentScreen(Screen):
    """Kivy Screen to add one off payments"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.pop = YesNoPopup(
            title='Are you sure?',
            message='OK ?',
            size_hint=(0.4, 0.3),
            pos_hint={'x': 0.3, 'y': 0.35}
        )

    def get_payments_from_db(self):
        """Queries the database and returns the
        total of payments for the currently logged
        in user for the current month."""
        user = self.manager.current_user
        month = dt.today().month
        with DataBaseObject() as db:
            paymentquery = db.fetch_data(
                f"""SELECT value, category, extra_details FROM payments 
                    WHERE user = '{user}'
                    AND month(date) = '{month}'
                    """)
        return paymentquery

    def get_payments(self):
        """Builds string of payments returned from database
        to display in the payment_string field"""
        payments = self.get_payments_from_db()
        payment_string = ""
        total_payments = 0
        for i in payments:
            payment_string += f"£{i[0]} - {i[1]} - '{i[2]}'\n"
            total_payments += i[0]
        payment_string += f"\n\nTotal - £{total_payments}"
        self.manager.current_screen.ids.month_payments.text = payment_string

    def submit_payment(self):
        """Submits a payment to the database. Takes the value,
        category and Extra details from the Kivy input fields,
        date from today's date, and username from current user
         logged in"""
        user = self.manager.current_user
        date = dt.today().isoformat()
        value = self.manager.current_screen.ids.value.text
        category = self.manager.current_screen.ids.category.text
        extra_details = self.manager.current_screen.ids.extra_details.text

        payment = Payment(user, date, value, category, extra_details)
        payment.update_database()
        popup_message("Success", "New Payment Added"
                                 f"\n {category}\n£{value}\n{extra_details}")
        self.reset_input_fields()
        self.get_payments()

    def cancel(self):
        self.manager.current = 'main_menu'

    @staticmethod
    def delete_last_payment():
        with DataBaseObject() as db:
            db.run_database_command(
                "DELETE FROM payments order by UID DESC limit 1")

    def delete_button(self):
        self.pop.bind(
            on_yes=self._popup_yes
        )
        self.pop.open()

    def _popup_yes(self, instance):
        print(f'{instance} on_yes')
        self.delete_last_payment()
        self.get_payments()
        self.pop.dismiss()

    def reset_input_fields(self):
        self.manager.current_screen.ids.value.text = ""
        self.manager.current_screen.ids.category.text = ""
        self.manager.current_screen.ids.extra_details.text = ""

    # TODO - Strip out any non digit char from value input
    # TODO - Add check for value type in input fields
    # TODO - Add check to ensure fields are filled


class YesNoPopup(Popup):
    __events__ = ('on_yes', 'on_no')

    message = StringProperty('')

    def __init__(self, **kwargs) -> None:
        super(YesNoPopup, self).__init__(**kwargs)
        self.auto_dismiss = False

    def on_yes(self):
        pass

    def on_no(self):
        self.dismiss()


class BillScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.pop = YesNoPopup(
            title='Are you sure?',
            message='OK ?',
            size_hint=(0.4, 0.3),
            pos_hint={'x': 0.3, 'y': 0.35}
        )

    def get_bills(self):
        """Fetches all monthly bills from the database, displays
        each plus a summed total to the BillScreen
        monthly_bills text lines"""
        bills = self.get_all_bills()
        bill_string = ""
        total_bills = 0
        for i in bills:
            bill_string += f"{i[1]} - £{i[0]}\n"
            total_bills += i[0]
        bill_string += f"\n\nTotal of monthly bills:   £{total_bills}"
        self.manager.current_screen.ids.monthly_bills.text = bill_string

    def get_all_bills(self):
        """Return the current monthly bills
        from the database"""
        user = self.manager.current_user
        with DataBaseObject() as db:
            billquery = db.fetch_data(
                f"""SELECT monthly_value, bill_name FROM bills 
                    WHERE user = '{user}'
                    """)
            return billquery

    def submit_bill(self):
        """Submits bill to the database. Takes the value,
        description from the Kivy input fields,
        date from today's date, and username from current user
         logged in"""
        user = self.manager.current_user
        date = dt.today().isoformat()
        bill_name = self.manager.current_screen.ids.bill_name.text
        value = self.manager.current_screen.ids.value.text

        bill = Bill(user, date, bill_name, value)
        bill.update_database()
        popup_message("Success", "New Bill Added"
                                 f"\n {bill_name}\n£{value}")
        self.reset_input_fields()
        self.get_bills()

    @staticmethod
    def delete_last_bill():
        with DataBaseObject() as db:
            db.run_database_command(
                "DELETE FROM bills order by UID DESC limit 1")

    def delete_button(self):
        self.pop.bind(
            on_yes=self._popup_yes
        )
        self.pop.open()

    def _popup_yes(self, instance):
        print(f'{instance} on_yes')
        self.delete_last_bill()
        self.get_bills()
        self.pop.dismiss()

    def cancel(self):
        self.manager.current = 'main_menu'

    def reset_input_fields(self):
        self.manager.current_screen.ids.bill_name.text = ""
        self.manager.current_screen.ids.value.text = ""


class IncomeScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.pop = YesNoPopup(
            title='Are you sure?',
            message='OK ?',
            size_hint=(0.4, 0.3),
            pos_hint={'x': 0.3, 'y': 0.35}
        )

    def get_incomes(self):
        """Fetches all monthly incomes, and all one off incomes from
        the current month from the database, displays each plus
        a summed total to the IncomeScreen current_incomes text lines"""
        monthly = self.get_monthly_incomes()
        one_off = self.get_one_off_incomes()
        income_string = ""
        total_income = 0
        for i in monthly:
            income_string += f"Monthly Income: {i[1]} - £{i[0]}\n"
            total_income += i[0]
        for i in one_off:
            income_string += f"One off Income: {i[1]} - £{i[0]}\n"
            total_income += i[0]
        income_string += f"\n\nTotal Income for Month: - £{total_income}"
        self.manager.current_screen.ids.current_incomes.text = income_string

    def get_monthly_incomes(self):
        """Return the current recurring incomes
        from the database"""
        user = self.manager.current_user
        with DataBaseObject() as db:
            incomequery = db.fetch_data(
                f"""SELECT value, income_name FROM income 
                    WHERE user = '{user}'
                    AND recurring = '1'
                    """)
            return incomequery

    def get_one_off_incomes(self):
        """Return the one off incomes from the
        current month from the database"""
        user = self.manager.current_user
        month = dt.today().month
        with DataBaseObject() as db:
            incomequery = db.fetch_data(
                f"""SELECT value, income_name FROM income 
                    WHERE user = '{user}'
                    AND recurring = '0'
                    AND month(date) = '{month}'
                    """)
            return incomequery

    def submit_income(self):
        """Submits income to the database. Takes the value,
        description from the Kivy input fields, and recurring or
        one off from the radio buttons
        date from today's date, and username from current user
         logged in"""
        user = self.manager.current_user
        date = dt.today().isoformat()
        income_name = self.manager.current_screen.ids.income_name.text
        value = self.manager.current_screen.ids.value.text
        if self.manager.current_screen.ids.recurring.state == 'down':
            recurring = 1
        else:
            recurring = 0

        income = Income(user, date, income_name, value, recurring)
        income.update_database()
        popup_message("Success", "New Income Added"
                                 f"\n {income_name}\n£{value}")
        self.manager.current = 'main_menu'

    @staticmethod
    def delete_last_income():
        with DataBaseObject() as db:
            db.run_database_command(
                "DELETE FROM income order by UID DESC limit 1")

    def delete_button(self):
        self.pop.bind(
            on_yes=self._popup_yes
        )
        self.pop.open()

    def _popup_yes(self, instance):
        print(f'{instance} on_yes')
        self.delete_last_income()
        self.get_incomes()
        self.pop.dismiss()

    def cancel(self):
        self.manager.current = 'main_menu'


class RootWidget(ScreenManager):
    current_user = StringProperty('')
    total_spend = StringProperty('')
    total_bills = StringProperty('')
    total_payments = StringProperty('')
    funds_remaining = StringProperty('')
    total_income = StringProperty('')


class MainApp(App):

    def build(self):
        return RootWidget()

def popup_message(title, message):
    popup = Popup(title=title,
                  content=Label(text=message),
                  size_hint=(None, None), size=(400, 400))
    popup.open()

MainApp().run()
