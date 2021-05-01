from kivy.uix.popup import Popup
from kivy.uix.label import Label

def popup_message(title, message):
    popup = Popup(title=title,
                  content=Label(text=message),
                  size_hint=(None, None), size=(400, 400))
    popup.open()