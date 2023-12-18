from django.shortcuts import render
from .models import Room, Reservation, Customer 
from datetime import datetime
from django.http import HttpResponseBadRequest, HttpResponseRedirect

def index(request):
    return render(request, 'index.html')


def available_rooms(request):

    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')

    print("Check-in Date: ", check_in_date)
    print("Check-out Date: ", check_out_date)

    check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
    check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()

    # Filter available room types
    available_room_types = Room.objects.filter(
        available=True
    ).exclude(
        reservation__check_in_date__lt=check_out_date,
        reservation__check_out_date__gt=check_in_date
    ).distinct().values_list('type', flat=True)

    available_room_types_with_text = [
        {'key': room_type, 'value': Room.TYPES_DICT.get(room_type, room_type)}
        for room_type in available_room_types
    ]

    return render(request, 'available_rooms.html', {
        'available_room_types_with_text': available_room_types_with_text,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date
    })

def make_reservation(request):
    room_type = request.GET.get('room_type')
    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')
    guests = request.GET.get('guests')

    try:
        if check_in_date and check_out_date:
            check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        else:
            return HttpResponseBadRequest("Invalid date format or missing dates")
    except ValueError:
        return HttpResponseBadRequest("Invalid date format")

    duration = (check_out_date - check_in_date).days
    print("Duration: ", duration)
    room = Room.objects.filter(type=room_type, available=True).first()
    print("Found Room: ", room)
    if room:
        print("Room Price: ", room.price)
        total_price = duration * room.price
    else:
        total_price = 0  # Handle the case where no room is available

    print("Total Price: ", total_price)


    context = {
        'room_type': room_type,
        'check_in_date': check_in_date,
        'check_out_date': check_out_date,
        'guests': guests,
        'total_price': total_price
    }
    return render(request, 'make_reservation.html', context)


def confirm_reservation(request):
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        room_type = request.POST.get('room_type')
        check_in_date = datetime.strptime(request.POST.get('check_in_date'), '%Y-%m-%d').date()
        check_out_date = datetime.strptime(request.POST.get('check_out_date'), '%Y-%m-%d').date()
        total_price = request.POST.get('total_price')
        test_credit_card_number = request.POST.get('test_credit_card_number')
        test_credit_card_expiry = request.POST.get('test_credit_card_expiry')

        # Check for room availability
        room = Room.objects.filter(type=room_type, available=True).first()
        if room:
            # Create Customer and Reservation objects
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={'first_name': first_name, 'last_name': last_name}
            )

            reservation = Reservation.objects.create(
                room=room,
                customer=customer,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                payment_processed=True,  # Since this is a test
                test_credit_card_number=test_credit_card_number,
                test_credit_card_expiry=test_credit_card_expiry
            )
            room.mark_as_booked()  # Mark the room as booked

            # Prepare the context for the confirmation message
            context = {
                'reservation': reservation,
                'room': room,
                'customer': customer,
                'total_price': total_price  
            }
            return render(request, 'confirm_reservation.html', context)
        else:
            # No room available, show error on the same page
            context = {'error_message': 'No room available for the selected dates.'}
            return render(request, 'confirm_reservation.html', context)
    else:
        # If not a POST request, redirect to make_reservation page
        return HttpResponseRedirect('/make_reservation/')