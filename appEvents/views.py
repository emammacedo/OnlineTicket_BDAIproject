from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseServerError
from django.shortcuts import render, redirect, reverse
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from datetime import datetime  

from .models import Venue
from .models import Room
from .models import Ticket
from .models import Event
from .models import User
from .models import Session
from .models import Purchase
from .models import Seat
from .models import PurchaseSeat
from .forms import LoginForm, RegisterForm, SeatQuantityForm, SeatSelectionForm


# Create your views here.

""" 
Venues
"""
def venues(request):
    template = loader.get_template('appEvents/venues.html')
    items = Venue.objects.order_by('name')[0:]
    context = {
        'venues':items
    }
    return HttpResponse(template.render(context, request))


""" 
Rooms
"""
def rooms(request):
    template = loader.get_template('appEvents/rooms.html')
    items = Room.objects.order_by('name')[0:]
    context = {
        'rooms':items,
    }
    return HttpResponse(template.render(context, request))


""" 
Rooms for each Venue
"""
def roomVenues(request, venues_id):
    template = loader.get_template('appEvents/roomVenues.html')
    try:
        specific_venue = Venue.objects.get(pk=venues_id)
        specific_rooms = Room.objects.filter(venue=venues_id)
        context = {'rooms' : specific_rooms, 'venue' : specific_venue}
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    return HttpResponse(template.render(context, request))

""" 
Tickets for each room
"""
def ticketsRoom(request, room_id):
    template = loader.get_template('appEvents/ticketsRoom.html')
    try:
        specific_room = Room.objects.get(pk=room_id)
        specific_tickets = Ticket.objects.filter(room=room_id)
        context = {'tickets' : specific_tickets, 'room' : specific_room}
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    return HttpResponse(template.render(context, request))

""" 
Sessions
"""
def sessions(request):
    template = loader.get_template('appEvents/sessions.html')
    items = Session.objects.all()
    context = {'sessions':items
    }
    return HttpResponse(template.render(context, request))

""" 
Tickets
"""
def tickets(request):
    template = loader.get_template('appEvents/tickets.html')
    tickets = Ticket.objects.all()
    rooms = Room.objects.order_by('name')[0:]
    context = {'tickets':tickets, 'rooms': rooms,
    }
    return HttpResponse(template.render(context, request))


@login_required
def events(request):
    user = request.user
    template = loader.get_template('appEvents/events.html')
    items = Event.objects.order_by('name')[0:]
    context = {
        'events':items,
    }
    return HttpResponse(template.render(context, request))
@login_required
def eventDetails(request, event_id):
    user = request.user
    template = loader.get_template('appEvents/eventDetails.html')
    try:
        myEvent = Event.objects.get(pk=event_id)
        myEventSessions = Session.objects.filter(event = event_id)
        context = {'event' : myEvent, 'sessions' : myEventSessions}
    except Event.DoesNotExist:
        raise Http404("Event does not exist")

    return HttpResponse(template.render(context, request))

def searchEvent(request):
    template = loader.get_template("appEvents/searchEvent.html")
    if request.method == 'GET':
        event_choosen = request.GET.get('search')
        myResult = Event.objects.all().filter(name__icontains=event_choosen)
        context = {'result' : myResult}
        return HttpResponse(template.render(context, request))
    

""" COMEÇA AQUIII"""

""" 
Buy 1st Page --> choosing the session
"""
@login_required
def choose_session(request, event_id):
    template = loader.get_template('appEvents/chooseSession.html')
    try:
        myEvent = Event.objects.get(pk=event_id)
        myEventSessions = Session.objects.filter(event = event_id)
        context = {'event' : myEvent, 'sessions' : myEventSessions}
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    except Session.DoesNotExist:
        raise Http404("Session does not exist.")
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred. Please try again later.")
    return HttpResponse(template.render(context, request))

""" 
Buy 2nd Page --> choosing the ticket type
"""
@login_required
def choose_tickets(request, session_id, event_id):
    template = loader.get_template('appEvents/chooseTickets.html')
    try:
        myEvent = Event.objects.get(pk=event_id)
        context = {'event' : myEvent, 'id_my_session': session_id}
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred. Please try again later.")
    return HttpResponse(template.render(context, request))

""" 
Buy 3rd Page --> choosing seats quantity
"""
@login_required
def choose_qty_seats(request, ticket_id, session_id, event_id):
    myEvent = Event.objects.get(pk=event_id)
    try:
        myEvent = Event.objects.get(pk=event_id)

        if request.method == 'POST':
                form = SeatQuantityForm(request.POST, session=session_id, ticket=ticket_id)
                if form.is_valid():
                    quantity = form.cleaned_data['quantity']
                    request.session['selected_quantity'] = quantity  # Storing quantity in session
                    return HttpResponseRedirect (reverse('choose_seats', args=(event_id, session_id, ticket_id)))
                else: #form is not valid, handle errors
                    for errors in form.errors.values():
                        for error in errors:
                            messages.error(request, error)
        else:
            form = SeatQuantityForm(session=session_id, ticket=ticket_id)
    
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred. Please try again later.")
    
    return render(request, 'appEvents/chooseQtySeats.html', {'form': form, 'event' : myEvent })

""" 
Buy 4th Page --> choosing seats
"""
@login_required
def choose_seats(request, ticket_id, session_id, event_id):
    
    try:

        myEvent = Event.objects.get(pk=event_id)
        qty = request.session.get('selected_quantity')  # Retrieve quantity from session

        if request.method == 'POST':
                form = SeatSelectionForm(request.POST, session=session_id, ticket=ticket_id, quant=qty)
                if form.is_valid():
                    selected_seats = []
                    for i in range(qty):
                        seat_id = form.cleaned_data[f'seat_{i + 1}']
                        selected_seats.append(seat_id)
                    
                    request.session['selected_seats_id'] = selected_seats 
                    return HttpResponseRedirect(reverse('confirm', args=(event_id, session_id, ticket_id))) 
                else:
                    for errors in form.errors.values():
                        for error in errors:
                            messages.error(request, error)
                
        else:
            form = SeatSelectionForm(session=session_id, ticket=ticket_id,  quant=qty)

    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred. Please try again later.")
   
    return render(request, 'appEvents/chooseSeats.html', {'form': form, 'event' : myEvent })
    
""" 
Buy 5th Page --> confirm purchase
"""
@login_required
def confirm_purchase(request, ticket_id, session_id, event_id):
    template = loader.get_template('appEvents/confirmPurchase.html')
    try:
        myEvent = Event.objects.get(pk=event_id)
        mySession = Session.objects.get(pk=session_id)
        myTicket = Ticket.objects.get(pk=ticket_id)
        seats_id = request.session.get('selected_seats_id')  
        mySeats = Seat.objects.filter(id__in=seats_id)

        priceTotal = myTicket.price * len(seats_id)
        
        context = {'event' : myEvent, 'session' : mySession, 'ticket': myTicket, 'seats': mySeats, 'price' : priceTotal}

    except Event.DoesNotExist:
        raise Http404("Event does not exist.")
    except Session.DoesNotExist:
        raise Http404("Session does not exist.")
    except Ticket.DoesNotExist:
        raise Http404("Ticket does not exist.")
    except Seat.DoesNotExist:
        raise Http404("One or more selected seats do not exist.")
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred. Please try again later.")

    return HttpResponse(template.render(context, request))

""" 
Buy 6th Page --> execute purchase
"""
@login_required
def execute_purchase(request, ticket_id, session_id, event_id):
    
    try:
        seats_id = request.session.get('selected_seats_id')
        myUser = request.user
        mySeats = Seat.objects.filter(id__in=seats_id)

        mySession = Session.objects.get(pk=session_id)
        purchase = Purchase.objects.create(
            datepurchase=datetime.now().date(),  
            hour=datetime.now().time(),  
            sessions=mySession,  
            users_nif=myUser 
        )
        purchase.save()
        for seat in mySeats:
            purchase_seat = PurchaseSeat.objects.create(
                seats=seat,  
                purchase=purchase  )
            purchase_seat.save()
            
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred. Please try again later.")

    return render(request, 'appEvents/executePurchase.html', {})

""" 
Login Page
"""
def login_action(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None: #authentication successful 
                login(request, user)
                next_url = request.POST.get('next') or reverse('events')
                return HttpResponseRedirect(next_url)
            else: # Invalid login
                return render(request, 'appEvents/login.html', {'form': form, 'error_message': 'Invalid username or password. Try again or register a new account.'})
    else:
        form = LoginForm()
    return render(request, 'appEvents/login.html', {'form': form})


""" 
Logout Page
"""
def logout_action(request):
    logout(request)
    return redirect('events')


""" 
Registration Page
"""
def register_action(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            nif = form.cleaned_data['nif']
            phonenumber = form.cleaned_data['phonenumber']

            user = User.objects.create_user(username=username, email=email, password=password, nif=nif)

            if phonenumber: #Check if phonenumber is provided
                user.phonenumber = phonenumber
                user.save()
            return HttpResponseRedirect(reverse('login'))
        else: #form is not valid, handle errors
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)            
    else:
        form = RegisterForm()
    return render(request, 'appEvents/registration.html', {'form': form})
