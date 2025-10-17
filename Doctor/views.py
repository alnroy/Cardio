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
def doctorhome(request):
    return render(request,"Doctor/base.html")



@csrf_exempt
def Bookings(request):
    if request.method == 'POST':
        user=request.session['gmail']
        user=Doctor.objects.get(email=user)
        selected_date = request.POST.get('date')
        bookings = DoctorBooking.objects.filter(booking_date=selected_date,doctor=user)
        booking_list = []
        for booking in bookings:
            booking_list.append({
                'id': booking.id,
                'patient_name': booking.patient.full_name,  # Assuming the Patient model has a full_name field
                'symptoms': booking.symptoms,
                'Sloat': booking.booking_sloat,
                'status':booking.status
            })

        print(booking_list)
        return JsonResponse(booking_list, safe=False)
    return render(request,"Doctor/Bookings.html")



@csrf_exempt
def update_booking_status(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_status = request.POST.get('status')

        try:
            booking = DoctorBooking.objects.get(id=booking_id)
            booking.status = new_status
            booking.save()
            return JsonResponse({"status": "success"}, status=200)
        except DoctorBooking.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Booking not found"}, status=404)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def doc_viewmore(request,id):
    booking = DoctorBooking.objects.get(id=id)
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms')
        disease = request.POST.get('disease')
        prescription = request.POST.get('prescription')
        remarks = request.POST.get('remarks')

        # Save prescription details
        Medicines.objects.create(
            bookid=booking,
            symptoms=symptoms,
            disease=disease,
            prescription=prescription,
            remarks=remarks
        )
        booking.status = "Completed"
        booking.save()


        return redirect('Bookings')  # Redirect to the same page after saving

    
    return render(request,"Doctor/doc_viewmore.html",{"booking":booking})



from django.http import JsonResponse
from datetime import datetime

def change_booking_date_ajax(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        new_date = request.POST.get('new_date')

        try:
            booking = DoctorBooking.objects.get(id=booking_id)
            if booking.status not in ['Pending', 'Confirmed']:
                return JsonResponse({'error': 'Cannot change date for this status'}, status=400)

            parsed_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            booking.booking_date = parsed_date
            booking.save()
            return JsonResponse({'message': 'Booking date updated'})
        except DoctorBooking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
