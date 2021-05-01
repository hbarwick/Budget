from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from users import User
from globalmethods import popup_message

Window.size = (480, 800)

Builder.load_file('KvFiles/frontend.kv')
Builder.load_file('KvFiles/mainmenu.kv')


class LogonScreen(Screen):
    def logon_button(self):
        self.manager.current = 'main_menu'
    def new_user_button(self):
        self.manager.current = 'new_user_screen'


class NewUserScreen(Screen):
    def new_user(self):
        username = self.manager.current_screen.ids.username.text
        first_name = self.manager.current_screen.ids.first_name.text
        last_name = self.manager.current_screen.ids.last_name.text
        email = self.manager.current_screen.ids.email.text
        password = self.manager.current_screen.ids.password.text
        confirm_password = self.manager.current_screen.ids.confirm_password.text
        userdetails = (username, first_name, last_name, email, password, confirm_password)
        return userdetails

    def usercheck(self):
        userdetails = self.new_user()
        if userdetails[4] != userdetails[5]:
            popup_message("Warning", "Passwords do not match")
            return
        elif "" in userdetails:
            popup_message("Warning", "Not all fields populated.")
            return
        else:
            user = User(userdetails[0],
                        userdetails[1],
                        userdetails[2],
                        userdetails[3],
                        userdetails[4])
            if user.check_duplicate():
                popup_message("Warning", "Username is taken")
                return
            user.update_database()
            popup_message("Success!", f"New user '{user.username}' created.")
            self.manager.current = 'logon_screen'


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


