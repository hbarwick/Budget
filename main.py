from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window

Window.size = (480, 800)

Builder.load_file('frontend.kv')
Builder.load_file('mainmenu.kv')


class LogonScreen(Screen):
    def logon_button(self):
        self.manager.current = 'main_menu'


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


