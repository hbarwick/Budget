from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from users import DataBaseObject
from globalmethods import popup_message
from newuserscreen import NewUserScreen

Window.size = (480, 800)

Builder.load_file('KvFiles/frontend.kv')
Builder.load_file('KvFiles/mainmenu.kv')


class LogonScreen(Screen):

    def get_credentials(self):
        self.username = self.manager.current_screen.ids.username.text
        self.password = self.manager.current_screen.ids.password.text

    def logon_button(self):
        self.get_credentials()
        if self.check_inputs():
            if self.check_user_and_pass() != ():
                popup_message("Ok", f"Logon successful as {self.username}")
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

    def logout_button(self):
        self.manager.current = 'logon_screen'

    def payment_button(self):
        self.manager.current = 'payment_screen'


class PaymentScreen(Screen):
    pass



class RootWidget(ScreenManager):
    def login(self):
        self.manager.current = 'main_menu'


class MainApp(App):

    def build(self):
        return RootWidget()


MainApp().run()


