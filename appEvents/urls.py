from django.urls import path

from . import views

urlpatterns = [

    path('rooms', views.rooms, name='rooms'),
    path('sessions', views.sessions, name='sessions'),
    path('venues', views.venues, name='venues'),
    path('tickets', views.tickets, name='tickets'),

    #Rooms Info for specific Venue 
    path('venues/<int:venues_id>/rooms', views.roomVenues, name='roomVenues'),

    #Tickets Info for specific room 
    path('rooms/<int:room_id>/ticketsRoom/', views.ticketsRoom, name='ticketsRoom'),


    #Users' related pages --> Login, Logout, Signup
    path('login', views.login_action, name='login'), 
    path('logout', views.logout_action, name='logout'),
    path('registration', views.register_action, name='registration'),

    #Events
    #If the path is events, we call the function views.events and the name of the page will be events
    path('events', views.events, name='events'), 
    path('events/<int:event_id>/', views.eventDetails, name='eventDetails'),

    #Search Events
    path('events/searchEvent/', views.searchEvent, name='searchEvent'),

    #Buy processing: 
    path('events/<int:event_id>/choose_session/', views.choose_session, name='choose_session'),
    path('events/<int:event_id>/choose_session/<int:session_id>', views.choose_tickets, name='choose_tickets'),
    path('events/<int:event_id>/choose_session/<int:session_id>/<int:ticket_id>', views.choose_qty_seats, name='choose_qty_seats'),
    path('events/<int:event_id>/choose_session/<int:session_id>/<int:ticket_id>/choose_seats/', views.choose_seats, name='choose_seats'),
    path('events/<int:event_id>/choose_session/<int:session_id>/<int:ticket_id>/choose_seats/confirmation', views.confirm_purchase, name='confirm'),
    path('events/<int:event_id>/choose_session/<int:session_id>/<int:ticket_id>/choose_seats/confirmation/execution', views.execute_purchase, name='execution'),


]




