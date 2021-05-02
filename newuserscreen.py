from kivy.uix.screenmanager import Screen

from globalmethods import popup_message
from dbclasses import User


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