from django.shortcuts import render
import datetime
from sqlite3 import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse, response
from .models import *
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings
from django.http import FileResponse
from Admin.models import *
# Create your views here.
from django.contrib.auth import authenticate, login

# Create your views here.

@csrf_exempt
def adminhome(request):
    return render(request,"Admin/base.html")


@csrf_exempt
def AddDoctor(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        specialty = request.POST.get('specialty')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        available_days = request.POST.get('available_days')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not all([full_name, specialty, phone, address, available_days, email, password]):
            return JsonResponse({"msg": "All fields are required."}, status=400)

      
        doctor = Doctor(
            full_name=full_name,
            specialty=specialty,
            phone=phone,
            address=address,
            available_days=available_days,
            email=email,
            password=password  
        )
        doctor.save()

        return JsonResponse({"msg": "Doctor added successfully!", "doctor_id": doctor.email}, status=201)


    return render(request,"Admin/Adddoctor.html")


@csrf_exempt
def ViewDoctor(request):
    D=Doctor.objects.all()
    return render(request,"Admin/viewdoctors.html",{"ob":D})


@csrf_exempt
def ViewAppoinments(request):
    D=DoctorBooking.objects.all()
    return render(request,"Admin/DoctorBooking.html",{"ob":D})



@csrf_exempt
def Patients(request):
    D=Patient.objects.all()
    return render(request,"Admin/viewpatients.html",{"ob":D})



@csrf_exempt
def ViewFeedback(request):
    feed=Feedback.objects.all().order_by('-id')
    return render(request,"Admin/Feedback.html",{'ob':feed})


def admin_medicine_orders(request):
    orders = MedicineOrder.objects.all().order_by('-order_date')  
    return render(request, 'Admin/admin_medicine_orders.html', {'orders': orders})


@csrf_exempt
def delete_doctor(request, doctor_id):
    if request.method == "POST":
        try:
            doctor = Doctor.objects.get(email=doctor_id)
            doctor.delete()
            return JsonResponse({"success": True})
        except Doctor.DoesNotExist:
            return JsonResponse({"success": False, "error": "Doctor not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

@csrf_exempt  # Only use for testing; use proper CSRF protection in production

def delete_patient(request, patient_id):
    if request.method == "POST":
        patient = get_object_or_404(Patient, email=patient_id)
        patient.delete()
        
    return redirect("Patients")  # Redirect to the patient list page

@csrf_exempt
def update_order_status(request, order_id):
    order = get_object_or_404(MedicineOrder, id=order_id)
    
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Processing", "Shipped", "Delivered"]:
            order.status = new_status
            order.save()
    
    return redirect("admin_medicine_orders")  # Redirect to the medicine orders page


from django.core.mail import send_mail
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import date

def send_today_appointment_notifications(request):
    today = date.today()
    bookings_today = DoctorBooking.objects.filter(booking_date=today).exclude(status='Cancelled')

    notified = []

    for booking in bookings_today:
        patient = booking.patient
        subject = "Appointment Reminder"
        message = (
            f"Dear {patient.full_name},\n\n"
            f"This is a reminder for your appointment today with Dr. {booking.doctor.full_name}.\n"
            f"Slot: {booking.booking_sloat}\n"
            f"Symptoms: {booking.symptoms}\n\n"
            "Please be on time.\n\n"
            "Thank you,\nYour Healthcare Team"
        )

        try:
            send_mail(
                subject,
                message,
                'your_email@gmail.com',  # From email
                [patient.email],
                fail_silently=False,
            )
            notified.append(patient.email)
        except Exception as e:
            print(f"Failed to send to {patient.email}: {e}")

    return render(request,"Admin/base.html")