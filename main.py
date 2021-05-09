from datetime import date as dt
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from dbclasses import DataBaseObject, Income, Bill, Payment
from globalmethods import popup_message
from newuserscreen import NewUserScreen


Window.size = (480, 800)

Builder.load_file('KvFiles/frontend.kv')
Builder.load_file('KvFiles/mainmenu.kv')
Builder.load_file('KvFiles/popup.kv')

class LogonScreen(Screen):

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
        db = DataBaseObject()
        userquery = db.fetch_data(
            f"""SELECT * FROM users 
                WHERE username = '{self.username}'
                AND password = '{self.password}'
                """)
        return userquery

    def check_inputs(self):
        """Ensures both username and password field are filled in"""
        if self.username == "" or self.password == "":
            popup_message("Warning", "Please enter username and password.")
            return False
        else:
            return True


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
        db = DataBaseObject()
        monthly_incomes = db.fetch_data(
            f"""SELECT value FROM income 
                WHERE user = '{user}'
                AND recurring = '1'
                """)
        one_off_incomes = db.fetch_data(
            f"""SELECT value FROM income 
                WHERE user = '{user}'
                AND recurring = '0'
                AND month(date) = '{month}'
                """)
        db.close_database_connection()
        monthly = float(f"{round(sum(i[0] for i in monthly_incomes), 2)}")
        oneoff = float(f"{round(sum(i[0] for i in one_off_incomes), 2)}")
        self.manager.total_income = str(monthly + oneoff)
        self.manager.current_screen.ids.total_income.text \
            = f"£{(str(self.manager.total_income))}"

    def update_total_spend(self):
        """Return the total of payments for the
        currently logged in user for the current month.
        To be displayed on the main menu summary screen"""
        user = self.manager.current_user
        month = dt.today().month
        db = DataBaseObject()
        userquery = db.fetch_data(
            f"""SELECT value FROM payments 
                WHERE user = '{user}'
                AND month(date) = '{month}'
                """)
        db.close_database_connection()
        self.manager.total_spend = f"{round(sum(i[0] for i in userquery), 2)}"
        self.manager.current_screen.ids.total_spend.text \
            = f"£{str(self.manager.total_spend)}"


    def update_total_bills(self):
        """Queries the database to return all recurring monthly
        bills for the currently logged in user and sum the total
        to display on the summary screen"""
        user = self.manager.current_user
        db = DataBaseObject()
        userquery = db.fetch_data(
            f"""SELECT monthly_value FROM bills 
                WHERE user = '{user}'
                """)
        db.close_database_connection()
        self.manager.total_bills = f"{round(sum(i[0] for i in userquery), 2)}"
        self.manager.current_screen.ids.total_bills.text \
            = f"£{str(self.manager.total_bills)}"

    def update_funds_remaining(self):
        self.manager.funds_remaining = str(round(
            float(self.manager.total_income) - (
            float(self.manager.total_spend) +
            float(self.manager.total_bills)), 2)
        )
        self.manager.current_screen.ids.funds_remaining.text =\
            (f"£{self.manager.funds_remaining}")


    def logout_button(self):
        self.manager.current = 'logon_screen'

    def payment_button(self):
        self.manager.current = 'payment_screen'

    def income_button(self):
        self.manager.current = 'income_screen'

    def bill_button(self):
        self.manager.current = 'bill_screen'


class PaymentScreen(Screen):
    """Kivy Screen to add one off payments"""

    def get_payments_from_db(self):
        """Queries the database and returns the
        total of payments for the currently logged
        in user for the current month."""
        user = self.manager.current_user
        month = dt.today().month
        db = DataBaseObject()
        paymentquery = db.fetch_data(
            f"""SELECT value, category, extra_details FROM payments 
                WHERE user = '{user}'
                AND month(date) = '{month}'
                """)
        db.close_database_connection()
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

    def delete_last_payment(self):
        db = DataBaseObject()
        db.run_database_command(
            "DELETE FROM payments order by UID DESC limit 1")
        db.close_database_connection()

    def delete_button(self):
        self.pop = pop = YesNoPopup(
            title='Are you sure?',
            message='OK ?',
            size_hint=(0.4, 0.3),
            pos_hint={'x': 0.3, 'y': 0.35}
        )
        pop.bind(
            on_yes=self._popup_yes,
            on_no=self._popup_no
        )
        self.pop.open()

    def _popup_yes(self, instance):
        print(f'{instance} on_yes')
        self.delete_last_payment()
        self.get_payments()
        self.pop.dismiss()

    def _popup_no(self, instance):
        print(f'{instance} on_no')
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
        pass


class BillScreen(Screen):

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
        db = DataBaseObject()
        billquery = db.fetch_data(
            f"""SELECT monthly_value, bill_name FROM bills 
                WHERE user = '{user}'
                """)
        db.close_database_connection()
        return billquery

    def delete_button(self):
        pass

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

    def delete_last_bill(self):
        db = DataBaseObject()
        db.run_database_command(
            "DELETE FROM bills order by UID DESC limit 1")
        db.close_database_connection()

    def delete_button(self):
        self.pop = pop = YesNoPopup(
            title='Are you sure?',
            message='OK ?',
            size_hint=(0.4, 0.3),
            pos_hint={'x': 0.3, 'y': 0.35}
        )
        pop.bind(
            on_yes=self._popup_yes,
            on_no=self._popup_no
        )
        self.pop.open()

    def _popup_yes(self, instance):
        print(f'{instance} on_yes')
        self.delete_last_bill()
        self.get_bills()
        self.pop.dismiss()

    def _popup_no(self, instance):
        print(f'{instance} on_no')
        self.pop.dismiss()

    def cancel(self):
        self.manager.current = 'main_menu'

    def reset_input_fields(self):
        self.manager.current_screen.ids.bill_name.text = ""
        self.manager.current_screen.ids.value.text = ""


class IncomeScreen(Screen):

    def get_incomes(self):
        """Fetches all monthly incomes, and all one off incomes from
        the currnet month from the database, displays each plus
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
        db = DataBaseObject()
        incomequery = db.fetch_data(
            f"""SELECT value, income_name FROM income 
                WHERE user = '{user}'
                AND recurring = '1'
                """)
        db.close_database_connection()
        return incomequery


    def get_one_off_incomes(self):
        """Return the one off incomes from the
        current month from the database"""
        user = self.manager.current_user
        month = dt.today().month
        db = DataBaseObject()
        incomequery = db.fetch_data(
            f"""SELECT value, income_name FROM income 
                WHERE user = '{user}'
                AND recurring = '0'
                AND month(date) = '{month}'
                """)
        db.close_database_connection()
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
                                 f"\n {income_name}\n£{value}\n{recurring}")
        self.manager.current = 'main_menu'

    def cancel(self):
        self.manager.current = 'main_menu'

class RootWidget(ScreenManager):
    current_user = StringProperty('')
    total_spend = StringProperty('')
    total_bills = StringProperty('')
    total_payments = StringProperty('')
    funds_remaining = StringProperty('')
    total_income = StringProperty('')
    pass


class MainApp(App):

    def build(self):
        return RootWidget()


MainApp().run()


