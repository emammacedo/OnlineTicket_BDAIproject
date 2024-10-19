from django.db import models
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator, MaxValueValidator

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager

# Create your models here.

class Venue(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=150)
    number = models.CharField(max_length=10)
    postal_code = models.CharField(max_length=8, validators=[
        MinLengthValidator(8, message='Postal code must be exactly 8 characters'),
        MaxLengthValidator(8, message='Postal code must be exactly 8 characters')
        ])
    phonenumber = models.BigIntegerField(null=True)
    email = models.CharField(max_length=50, null=True)
    def __str__(self):
        return self.name + " (" + self.city + ")"

class Room(models.Model):
    name = models.CharField(max_length=100)
    seatingchart = models.URLField(max_length=500)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    def __str__(self):
        return self.name + " (" + self.venue.name + ")"

class Ticket(models.Model):
    type = models.CharField(max_length=100)
    price = models.IntegerField(validators = [MinValueValidator(0)])
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    def __str__(self):
        return self.type + " (" + self.room.name + ")"
    
class Event(models.Model):
    name = models.CharField(max_length=150)
    duration = models.IntegerField(validators = [MinValueValidator(0)])
    type = models.CharField(max_length=50, choices = [('Teatro & Arte', 'Teatro & Arte'), ('Cinema', 'Cinema'), ('Stand-up', 'Stand-up'),('Música', 'Música'),('Infantil','Infantil'), ('Formação & Educação', 'Formação & Educação')])
    summary = models.CharField(max_length=750, null=True)
    description = models.TextField(null=True)
    minimumage = models.IntegerField(validators = [MinValueValidator(0)])
    poster = models.URLField(max_length=500)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    nif = models.BigIntegerField(unique=True, null=True, validators=[
        MinValueValidator(100000000, message='NIF must be exactly 9 digits'),
        MaxValueValidator(999999999, message='NIF must be exactly 9 digits')
    ])
    phonenumber = models.BigIntegerField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
    
class Session(models.Model):
    datesession = models.DateField()
    hour = models.TimeField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.datesession) + " at " + str(self.hour) + " (" + self.event.name + ")"

class Purchase(models.Model):
    datepurchase = models.DateField()
    hour = models.TimeField()
    sessions = models.ForeignKey(Session, on_delete=models.CASCADE)
    users_nif = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.datepurchase) + "(session: " + self.sessions.event.name + ", username: " + str(self.users_nif.username) + ")"

class Seat(models.Model):
    seatname = models.CharField(max_length=10)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    def __str__(self):
        return self.seatname + "(ticket: " + self.ticket.type + ", room: " + self.ticket.room.name + ")"

class PurchaseSeat(models.Model):
    seats = models.ForeignKey(Seat, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    def __str__(self):
        return self.seats.seatname + ", " + str(self.purchase.datepurchase)
