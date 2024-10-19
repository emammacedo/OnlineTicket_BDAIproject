from django.contrib import admin

# Register your models here.
from .models import Venue
from .models import Room
from .models import Ticket
from .models import Event
from .models import User
from .models import Session
from .models import Purchase
from .models import Seat
from .models import PurchaseSeat

admin.site.register(Venue)
admin.site.register(Room)
admin.site.register(Ticket)
admin.site.register(Event)
admin.site.register(User)
admin.site.register(Session)
admin.site.register(Purchase)
admin.site.register(Seat)
admin.site.register(PurchaseSeat)


