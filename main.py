from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from dbclasses import DataBaseObject, Payment
from globalmethods import popup_message
from newuserscreen import NewUserScreen
from datetime import date as dt

Window.size = (480, 800)

Builder.load_file('KvFiles/frontend.kv')
Builder.load_file('KvFiles/mainmenu.kv')

currentuser = "test"

class LogonScreen(Screen):

    def get_credentials(self):
        self.username = self.manager.current_screen.ids.username.text
        self.password = self.manager.current_screen.ids.password.text

    def logon_button(self):
        self.get_credentials()
        if self.check_inputs():
            if self.check_user_and_pass() != ():
                popup_message("Ok", f"Logon successful as {self.username}")
                global currentuser
                currentuser = self.username
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

    @property
    def total_spend(self):
        global currentuser
        user = currentuser
        month = dt.today().month
        db = DataBaseObject()
        userquery = db.fetch_data(
            f"""SELECT value FROM payments 
                WHERE user = '{currentuser}'
                AND month(date) = '{month}'
                """)
        db.close_database_connection()
        return f"£{str(round(sum(i[0] for i in userquery),2))}"

    def logout_button(self):
        self.manager.current = 'logon_screen'

    def payment_button(self):
        self.manager.current = 'payment_screen'


class PaymentScreen(Screen):

    def submit_payment(self):
        global currentuser
        user = currentuser
        date = dt.today().isoformat()
        value = self.manager.current_screen.ids.value.text
        category = self.manager.current_screen.ids.category.text
        extra_details = self.manager.current_screen.ids.extra_details.text

        payment = Payment(user, date, value, category, extra_details)
        payment.update_database()
        popup_message("Success", "New Payment Added"
                                 f"\n {category}\n£{value}\n{extra_details}")
        self.manager.current = 'main_menu'


class RootWidget(ScreenManager):
    pass


class MainApp(App):

    def build(self):
        return RootWidget()


MainApp().run()


