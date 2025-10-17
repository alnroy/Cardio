from django.db import models

# Create your models here.
class Patient(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    medical_history = models.TextField(blank=True, null=True)
    email=models.CharField(max_length=80,primary_key=True)
    password=models.CharField(max_length=18)

    def __str__(self):
        return self.full_name


class Doctor(models.Model):
    full_name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    available_days = models.CharField(max_length=100)  # E.g., "Mon, Wed, Fri"
    email=models.CharField(max_length=80,primary_key=True)
    password=models.CharField(max_length=18)

    def __str__(self):
        return f"Dr. {self.full_name} - {self.specialty}"

class DoctorBooking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="bookings")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    booking_date = models.DateField()
    booking_sloat = models.IntegerField()
    symptoms = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], default='Pending')
    

    def __str__(self):
        return f"Booking: {self.patient} with {self.doctor} on {self.booking_date} at {self.booking_sloat}"



class Feedback(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="feedbacks")
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Feedback from {self.patient} to {self.doctor} - Rating: {self.rating}"


class Medicines(models.Model):
    bookid=models.ForeignKey(DoctorBooking,on_delete=models.CASCADE)
    symptoms=models.TextField(blank=True, null=True)
    disease=models.TextField(blank=True, null=True)
    prescription=models.TextField(blank=True, null=True)
    remarks=models.TextField(blank=True, null=True)
