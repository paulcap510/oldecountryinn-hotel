from django.db import models

class Room(models.Model):
    TYPES = [
        ('double', 'Double'),
        ('king', 'King'),
        ('two_double', 'Two Double'),
        ('suite', 'Suite')
    ] 
    TYPES_DICT = dict(TYPES)

    room_no = models.IntegerField(unique=True)
    type = models.CharField(max_length=20, choices=TYPES)    
    price = models.IntegerField()
    available = models.BooleanField(default=True) 
    max_guests = models.IntegerField()

    def __str__(self):
        return f"Room: {self.room_no} - {self.type}"

    def mark_as_booked(self):
        self.available = False
        self.save()

    def mark_as_available(self):
        self.available = True
        self.save()


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()

    # Fields for testing - not production ready
    payment_processed = models.BooleanField(default=False)
    test_credit_card_number = models.CharField(max_length=16, blank=True, null=True)
    test_credit_card_expiry = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"Reservation for {self.customer} - Room No {self.room.room_no}"


