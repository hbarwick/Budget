from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from dbclasses import DataBaseObject, Income
from globalmethods import popup_message
from datetime import date as dt

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
        if self.username == "" or self.password == "":
            popup_message("Warning", "Please enter username and password.")
            return False
        else:
            return True


class MainMenu(Screen):

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
        self.manager.total_spend = f"£{str(round(sum(i[0] for i in userquery), 2))}"

    def logout_button(self):
        self.manager.current = 'logon_screen'

    def payment_button(self):
        self.manager.current = 'payment_screen'

    def income_button(self):
        self.manager.current = 'income_screen'


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
    pass


class IncomeScreen(Screen):

    def get_incomes(self):
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
    total_payments = StringProperty('')
    funds_remaining = StringProperty('')
    pass


class MainApp(App):

    def build(self):
        return RootWidget()


MainApp().run()


