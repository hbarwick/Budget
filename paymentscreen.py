from datetime import date as dt
from kivy.uix.screenmanager import Screen
from dbclasses import DataBaseObject, Payment
from globalmethods import popup_message
from main import YesNoPopup


class PaymentScreen(Screen):
    """Kivy Screen to add one off payments"""

    def get_payments_from_db(self):
        """Return the total of payments for the
        currently logged in user for the current month."""
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