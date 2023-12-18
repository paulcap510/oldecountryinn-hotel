from django.shortcuts import render
from .models import Room, Reservation, Customer 
from datetime import datetime
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.db.models import Count

def index(request):
    return render(request, 'index.html')


def available_rooms(request):
    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')
    check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
    check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()

    available_rooms = Room.objects.exclude(
        reservation__check_in_date__lt=check_out_date,
        reservation__check_out_date__gt=check_in_date
    ).distinct()

    room_types_available = available_rooms.values('type').annotate(available_count=Count('type')).order_by()

    available_room_types_with_text_and_count = [
        {
            'key': room_type['type'], 
            'value': Room.TYPES_DICT.get(room_type['type'], room_type['type']),
            'count': room_type['available_count']
        }
        for room_type in room_types_available
    ]


    return render(request, 'available_rooms.html', {
        'available_room_types_with_text_and_count': available_room_types_with_text_and_count,
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

    available_room = Room.objects.filter(
        type=room_type
    ).exclude(
        reservation__check_in_date__lt=check_out_date,
        reservation__check_out_date__gt=check_in_date
    ).first()

    if available_room:
        duration = (check_out_date - check_in_date).days
        total_price = duration * available_room.price
    else:
        total_price = 0  

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
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        room_type = request.POST.get('room_type')
        check_in_date = datetime.strptime(request.POST.get('check_in_date'), '%Y-%m-%d').date()
        check_out_date = datetime.strptime(request.POST.get('check_out_date'), '%Y-%m-%d').date()
        total_price = request.POST.get('total_price')
        test_credit_card_number = request.POST.get('test_credit_card_number')
        test_credit_card_expiry = request.POST.get('test_credit_card_expiry')

        available_room = Room.objects.filter(
            type=room_type
        ).exclude(
            reservation__check_in_date__lt=check_out_date,
            reservation__check_out_date__gt=check_in_date
        ).first()

        if available_room:
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={'first_name': first_name, 'last_name': last_name}
            )

            reservation = Reservation.objects.create(
                room=available_room,
                customer=customer,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                payment_processed=True,  # Only in development  
                test_credit_card_number=test_credit_card_number,
                test_credit_card_expiry=test_credit_card_expiry
            )

            context = {
                'reservation': reservation,
                'room': available_room,
                'customer': customer,
                'total_price': total_price  
            }
            return render(request, 'confirm_reservation.html', context)
        else:
            context = {'error_message': 'No room available for the selected dates.'}
            return render(request, 'confirm_reservation.html', context)
    else:
        return HttpResponseRedirect('/make_reservation/')
