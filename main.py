from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup

Window.size = (480, 800)

Builder.load_file('KvFiles/frontend.kv')
Builder.load_file('KvFiles/mainmenu.kv')


class LogonScreen(Screen):
    def logon_button(self):
        self.manager.current = 'main_menu'
    def new_user_button(self):
        self.manager.current = 'new_user_screen'


class NewUserScreen(Screen):
    def usercheck(self):
        popup = Popup(title='Test popup',
                      content=Label(text='Hello world'),
                      size_hint=(None, None), size=(400, 400))
        popup.open()


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


