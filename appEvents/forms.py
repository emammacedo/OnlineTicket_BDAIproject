from django import forms
from .models import User, Seat, Purchase, PurchaseSeat

"""
Login
"""
class LoginForm(forms.Form):
    username = forms.CharField(max_length = 100)
    password = forms.CharField(widget = forms.PasswordInput())

"""
Registration
"""
class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=50, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'phonenumber', 'nif']
        widgets = {
            'password': forms.PasswordInput()
        }
        labels = {
            'username': 'Username',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            'email': 'Email',
            'phonenumber': 'Phone Number',
            'nif': 'NIF',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phonenumber'].required = False

"""
Selecting Seats Quantity
"""
class SeatQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label='Quantidade')
    
    def __init__(self, *args, **kwargs):
        self.session_id = kwargs.pop('session', None)
        self.ticket_id = kwargs.pop('ticket', None)
        super(SeatQuantityForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        quantity = self.cleaned_data['quantity']
        available_seats = getAvailableTickets(self.session_id, self.ticket_id)
        max_quantity = available_seats.count()

        #limit to 10 seats per purchase    
        if max_quantity < 10 and quantity > max_quantity:
            raise forms.ValidationError(f"Quantidade máxima disponível é {max_quantity}")
        elif quantity > 10:
            raise forms.ValidationError(f"Cada compra é limitada a 10 bilhetes.")    
        return cleaned_data
    
        
"""
Selecting Seats
"""
class SeatSelectionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.session_id = kwargs.pop('session', None)
        self.ticket_id = kwargs.pop('ticket', None)
        self.quantity = kwargs.pop('quant', None)
        super(SeatSelectionForm, self).__init__(*args, **kwargs)

        available_seats = getAvailableTickets(self.session_id, self.ticket_id)
        seat_choices = [(seat.id, seat.seatname) for seat in available_seats]

        for i in range(self.quantity):
            self.fields[f'seat_{i + 1}'] = forms.ChoiceField(
                choices=seat_choices,
                label=f'Lugar {i + 1}',
                widget=forms.Select(attrs={'class': 'form-control'})
            )

"""
Auxiliary Function
Get the available seats for one specific session of one specific ticket type
"""
def getAvailableTickets(session_id, ticket_id):
    mySession_purchases = Purchase.objects.filter(sessions_id = session_id) #every purchase of that session
        
    sold_seat_ids = [] #id's of every seat that appears in every purchaseSeat of every Purchase of that session
    for purchase in mySession_purchases:
        mySession_purchaseSeats = PurchaseSeat.objects.filter(purchase_id = purchase.id)
        for purchaseSeat in mySession_purchaseSeats:
            sold_seat_ids.append(purchaseSeat.seats_id)
    
    #Selecting the seats not sold of that specific ticket type
    available_seats = Seat.objects.filter(ticket_id = ticket_id).exclude(id__in=sold_seat_ids)

    return available_seats


