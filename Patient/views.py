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
def home(request):
    return render(request,"base.html")


@csrf_exempt
def login(request):
    if request.method == 'POST':
        print("------ Login Request Processing -------")
        userid=request.POST.get('userid')
        password=request.POST.get('password')
        type=request.POST.get('type')
        print(request.POST)
        try:
            if userid=="admin" and password=="admin" and type=="ADMIN":
                return JsonResponse({'status': 1})
            elif type=="USER":
                ob=Patient.objects.get(email=userid,password=password)
                request.session['gmail']=ob.email

                return JsonResponse({'status': 2})
            elif type=="DOCTOR":
                ob=Doctor.objects.get(email=userid,password=password)
                request.session['gmail']=ob.email

                return JsonResponse({'status': 3})
            else:
                ob=Users.objects.get(email=userid,password=password,status=1)
                request.session['gmail']=ob.email
                return JsonResponse({'status': 4})
        except Exception as e:
            print(e)
            return JsonResponse({'status': "failed"})
    return render(request,"LOGIN.html")


@csrf_exempt
def Register(request):
    if request.method == 'POST':
        try:
            print(".................. USER REGISTRATION .....................")
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            date_of_birth = request.POST.get('date_of_birth')
            medical_history = request.POST.get('medical_history', '')  # Optional field
        
            print(password)
            patient = Patient.objects.create(
                full_name=name,
                email=email,
                password=password,
                phone=phone,
                address=address,
                date_of_birth=date_of_birth,
                medical_history=medical_history,
              
            )
            print("success")
            data={"msg":"Successfully Registread"}
            return JsonResponse(data,safe=False)
        except IntegrityError:
            data={"msg":"Already exists"}
            return JsonResponse(data,safe=False)
        except Exception as e:
            print(e)
            data={"msg":"Failed"}
            return JsonResponse(data,safe=False)
    return render(request,"Register.html")






# user home

@csrf_exempt
def userhome(request):
    return render(request,"Patient/base.html")


@csrf_exempt
def viewmore(request,id):
    id=DoctorBooking.objects.get(id=id)
    med=Medicines.objects.filter(bookid=id).first()
    return render(request,"Patient/viewmore.html",{"ob":med})


@csrf_exempt
def GiveFeedback(request):
    if request.method == 'POST':
        user=request.session['gmail']
        user=Patient.objects.get(email=user)
        feedback_text = request.POST.get('feedback_text')

       
        Feedback.objects.create(
            patient=user,
            comment=feedback_text
        )


        return redirect('userhome')  
    return render(request,"Patient/feedback.html")

@csrf_exempt
def MyAppoinment(request):
    user=request.session['gmail']
    user=Patient.objects.get(email=user)
    doc=DoctorBooking.objects.filter(patient=user).order_by('-id')
    return render(request,"Patient/MyAppoinment.html",{"ob":doc})


@csrf_exempt
def TakeAppoinment(request):
    doc=Doctor.objects.all()
    if request.method == 'POST':
        user=request.session['gmail']
        user=Patient.objects.get(email=user)
        doctor_id = request.POST.get('doctor_id')
        booking_date = request.POST.get('booking_date')
        booking_sloat = request.POST.get('booking_sloat')
        symptoms = request.POST.get('symptoms')
        doctor_id=Doctor.objects.get(email=doctor_id)
        existing_booking = DoctorBooking.objects.filter(
            doctor_id=doctor_id,
            booking_date=booking_date,
            booking_sloat=booking_sloat
        ).exists()

        if existing_booking:
            return render(request, "Patient/TakeAppoinment.html",{ "message": "This time slot is already booked.","ob":doc})


        # Create a new booking
        booking = DoctorBooking.objects.create(
            patient=user,
            doctor=doctor_id,
            booking_date=booking_date,
            booking_sloat=booking_sloat,
            symptoms=symptoms
        )
        return render(request, "Patient/TakeAppoinment.html", {"message": "Appointment booked successfully!","ob":doc})
    doc=Doctor.objects.all()
    return render(request,"Patient/TakeAppoinment.html",{"ob":doc})

import re
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
import re
from django.shortcuts import render
from django.conf import settings
import os

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Function to extract health parameters from text
def extract_health_parameters(text):
    patterns = {
        "Fasting Blood Sugar": r"Fasting:\s*(\d+)\s*mg/dL",
        "Postprandial Blood Sugar": r"Postprandial:\s*(\d+)\s*mg/dL",
        "HbA1c": r"HbA1c:\s*(\d+\.\d+)\s*%",
        "Total Cholesterol": r"Total Cholesterol:\s*(\d+)\s*mg/dL",
        "HDL": r"HDL:\s*(\d+)\s*mg/dL",
        "LDL": r"LDL:\s*(\d+)\s*mg/dL",
        "Triglycerides": r"Triglycerides:\s*(\d+)\s*mg/dL",
        "Blood Pressure": r"Blood Pressure:\s*(\d+/\d+)\s*mmHg",
        "Heart Rate": r"Heart Rate:\s*(\d+)\s*bpm",
        "Body Temperature": r"Body Temperature:\s*(\d+\.\d*)\s*°F",
    }

    extracted_values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        extracted_values[key] = match.group(1) if match else "Not Found"

    return extracted_values

# Function to analyze health parameters
def analyze_health_parameters(values):
    analysis = {}
    doctor_consultation_needed = False

    reference_ranges = {
        "Fasting Blood Sugar": (70, 99),
        "Postprandial Blood Sugar": (0, 140),
        "HbA1c": (0, 5.7),
        "Total Cholesterol": (0, 200),
        "HDL": (40, float('inf')),  # Should be greater than 40
        "LDL": (0, 100),
        "Triglycerides": (0, 150),
        "Blood Pressure": (("90/60", "120/80"), "normal"),
        "Heart Rate": (60, 100),
        "Body Temperature": (97, 99)
    }

    for key, value in values.items():
        if value != "Not Found":
            if key in reference_ranges:
                if key == "Blood Pressure":
                    normal_bp = reference_ranges[key][0]
                    if value < normal_bp[0]:
                        analysis[key] = f"{value} (Low)"
                        doctor_consultation_needed = True
                    elif value > normal_bp[1]:
                        analysis[key] = f"{value} (High)"
                        doctor_consultation_needed = True
                    else:
                        analysis[key] = f"{value} (Normal)"
                else:
                    min_val, max_val = reference_ranges[key]
                    num_value = float(value.split()[0])  # Extract numeric value

                    if num_value < min_val:
                        analysis[key] = f"{value} (Low)"
                        doctor_consultation_needed = True
                    elif num_value > max_val:
                        analysis[key] = f"{value} (High)"
                        doctor_consultation_needed = True
                    else:
                        analysis[key] = f"{value} (Normal)"
            else:
                analysis[key] = value  # No specific reference range
        else:
            analysis[key] = "Not Found"

    return analysis, doctor_consultation_needed

# Function to generate personalized Kerala diet plan
def generate_diet_plan(health_conditions):
    diet_plan = {
        "General": [
            "Include more leafy vegetables like spinach, moringa leaves (muringa).",
            "Use coconut-based curries for healthy fats.",
            "Include fermented foods like idli, dosa for gut health."
        ],
        "High Blood Sugar": [
            "Eat high-fiber foods like brown rice, millets, and whole wheat.",
            "Avoid sugary tea, coffee, and soft drinks.",
            "Include bitter gourd (pavakka) in your diet."
        ],
        "High Cholesterol": [
            "Consume fish like sardines (mathi) and mackerel (ayila) for omega-3.",
            "Avoid red meat and deep-fried snacks.",
            "Use coconut oil moderately."
        ],
        "High Blood Pressure": [
            "Reduce salt intake, avoid pickles and processed foods.",
            "Eat potassium-rich foods like bananas and jackfruit.",
            "Drink plenty of tender coconut water."
        ],
    }

    recommended_plan = []
    if "High" in str(health_conditions.values()):
        if "Fasting Blood Sugar" in health_conditions and "High" in health_conditions["Fasting Blood Sugar"]:
            recommended_plan += diet_plan["High Blood Sugar"]
        if "Total Cholesterol" in health_conditions and "High" in health_conditions["Total Cholesterol"]:
            recommended_plan += diet_plan["High Cholesterol"]
        if "Blood Pressure" in health_conditions and "High" in health_conditions["Blood Pressure"]:
            recommended_plan += diet_plan["High Blood Pressure"]

    if not recommended_plan:
        recommended_plan += diet_plan["General"]

    return recommended_plan

# Django View to handle PDF upload and analysis
def upload_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        file_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)

        with open(file_path, "wb") as f:
            for chunk in pdf_file.chunks():
                f.write(chunk)

        text = extract_text_from_pdf(file_path)
        health_data = extract_health_parameters(text)
        analyzed_data, doctor_needed = analyze_health_parameters(health_data)

        request.session["analyzed_data"] = analyzed_data  # Store for diet plan
        request.session["doctor_needed"] = doctor_needed  # Store consultation status

        return render(request, "Patient/result.html", {"data": analyzed_data, "doctor_needed": doctor_needed})

    return render(request, "Patient/upload.html")

# Django View to generate and display diet plan
def generate_diet_view(request):
    analyzed_data = request.session.get("analyzed_data", {})
    doctor_needed = request.session.get("doctor_needed", False)

    diet_plan = generate_diet_plan(analyzed_data)
    meal_plan = {
        "Breakfast": [
            "Puttu with kadala curry (High-fiber, good for diabetics)",
            "Idli with sambar (Fermented, good for digestion)",
            "Oats kanji with coconut (Good for cholesterol management)"
        ],
        "Lunch": [
            "Matta rice with sambar and thoran (Balanced meal with fiber and proteins)",
            "Fish curry with red rice (Good omega-3 for heart health)",
            "Avial with curd (Rich in nutrients and digestion-friendly)"
        ],
        "Evening Snack": [
            "Banana with peanuts (Good for energy and heart health)",
            "Tender coconut water (Hydration and electrolyte balance)",
            "Muringa (drumstick) soup (Boosts immunity)"
        ],
        "Dinner": [
            "Chapati with vegetable stew (Light and easy to digest)",
            "Kanji with payar and coconut (Traditional comfort food, good for digestion)",
            "Grilled fish with vegetables (Protein-rich, good for overall health)"
        ],
    }

    return render(request, "Patient/diet_plan.html", {
        "analyzed_data": analyzed_data,
        "diet_plan": diet_plan,
        "meal_plan": meal_plan,
        "doctor_needed": doctor_needed,
    })
import json
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Define chatbot questions
QUESTIONS = [
    {"id": 1, "text": "Do you have a fever?"},
    {"id": 2, "text": "Do you have a cough?"},
    {"id": 3, "text": "Do you have a headache?"},
    {"id": 4, "text": "Do you feel weak or tired?"},
    {"id": 5, "text": "Do you have chest pain?"},
    {"id": 6, "text": "Do you have difficulty breathing?"},
    {"id": 7, "text": "Do you have a sore throat?"},
    {"id": 8, "text": "Do you have nasal congestion?"},
    {"id": 9, "text": "Do you have muscle or joint pain?"},
    {"id": 10, "text": "Do you have nausea or vomiting?"},
    {"id": 11, "text": "Do you have diarrhea?"},
    {"id": 12, "text": "Do you have dizziness?"},
    {"id": 13, "text": "Do you have blurred vision?"},
    {"id": 14, "text": "Do you have unexplained weight loss?"},
    {"id": 15, "text": "Do you have high or low blood pressure?"},
    {"id": 16, "text": "Do you have frequent urination?"},
    {"id": 17, "text": "Do you have excessive thirst?"},
    {"id": 18, "text": "Do you have a rash or skin irritation?"},
    {"id": 19, "text": "Do you have numbness or tingling in any part of your body?"},
    {"id": 20, "text": "Do you have swelling in your legs or hands?"}
]

# Define condition responses
CONDITIONS = {
    "fever,cough": "You might have a viral infection. Drink fluids and rest.",
    "fever,cough,weakness": "You may have the flu. Consult a doctor.",
    "headache,weakness": "You may have dehydration or stress.",
    "chest pain": "Seek medical attention immediately.",
    "difficulty breathing,fever,cough": "You may have pneumonia or a respiratory infection. Seek medical care.",
    "sore throat,fever": "You might have strep throat or a viral infection.",
    "nasal congestion,cough": "You may have a common cold or allergies.",
    "muscle pain,fever,weakness": "You might have the flu or a viral infection.",
    "nausea,vomiting,diarrhea": "You may have a gastrointestinal infection.",
    "dizziness,blurred vision": "You may have low blood sugar or dehydration.",
    "weight loss,frequent urination,excessive thirst": "Possible diabetes. Get your blood sugar checked.",
    "numbness,tingling,weakness": "Possible neurological issue. Consult a doctor.",
    "swelling in legs or hands,high blood pressure": "Possible kidney or heart condition. Seek medical care."
}

# Initialize speech engine

def speak_text(text):
    engine = pyttsx3.init()
    speech_thread = None  # Track the current speech thread


    def run_speech():
        engine.say(text)
        engine.runAndWait()

    if speech_thread is None or not speech_thread.is_alive():
        speech_thread = threading.Thread(target=run_speech)
        speech_thread.start()

@csrf_exempt
def chatbot(request):
    """Handles chatbot conversation flow."""
    if request.method == "POST":
        data = json.loads(request.body)
        question_id = data.get("question_id", 1)  # Start from question 1
        user_response = data.get("response", "").lower()

        # Initialize session symptoms storage
        if "symptoms" not in request.session:
            request.session["symptoms"] = []

        # Store symptoms if user responds "yes"
        if question_id > 1 and user_response == "yes":
            symptom_text = QUESTIONS[question_id - 2]["text"]
            symptom_key = symptom_text.replace("Do you have a ", "").replace("Do you have ", "").replace("Do you feel ", "").replace("?", "").lower()

            if symptom_key not in request.session["symptoms"]:
                request.session["symptoms"].append(symptom_key)

            request.session.modified = True

        # Send the first question if question_id is 1
        if question_id == 1:
            first_question = QUESTIONS[0]["text"]
            return JsonResponse({"question": first_question, "question_id": 2})

        # Move to the next question
        if question_id <= len(QUESTIONS):
            next_question = QUESTIONS[question_id - 1]["text"]
            return JsonResponse({"question": next_question, "question_id": question_id + 1})

        # Diagnosis
        print(request.session["symptoms"])
        symptoms_key = ",".join(request.session["symptoms"])
        print(symptom_key)
        diagnosis = CONDITIONS.get(symptoms_key, "Based on your symptoms, please consult a doctor for a proper diagnosis.")

        # Clear session after diagnosis
        request.session["symptoms"] = []
        request.session.modified = True

        speak_text(diagnosis)
        return JsonResponse({"diagnosis": diagnosis, "question": None})

    return JsonResponse({"error": "Invalid request"}, status=400)

def chatbot_page(request):
    """Render chatbot page"""
    return render(request, "Patient/chatbot.html")



def order_medicine(request, prescription_id):
    if request.method == "POST":
        prescription = get_object_or_404(Medicines, id=prescription_id)
        delivery_address = request.POST["delivery_address"]
        contact_number = request.POST["contact_number"]

        # Create a new order
        order = MedicineOrder.objects.create(
            patient=prescription.bookid.patient,
            prescription=prescription,
            delivery_address=delivery_address,
            contact_number=contact_number
        )

        return redirect("userhome")  # Redirect to the dashboard or orders page

    prescription = get_object_or_404(Medicines, id=prescription_id)
    return render(request, "Patient/order_medicine.html", {"prescription": prescription})


def patient_orders(request):
    user=request.session['gmail']
    user=Patient.objects.get(email=user)
    orders = MedicineOrder.objects.filter(patient=user).order_by('-order_date')  
    return render(request, "Patient/patient_orders.html", {"orders": orders})




import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier



@csrf_exempt
def Predict(request):
    if request.method == 'POST':

        df = pd.read_csv('static/heart.csv')
        data = df.values
        X = data[:, :-1]
        Y = data[:, -1:]

        value=0

        age = float(request.POST['age'])
        sex = float(request.POST['sex'])
        cp = float(request.POST['cp'])
        trestbps = float(request.POST['trestbps'])
        chol = float(request.POST['chol'])
        fbs = float(request.POST['fbs'])
        restecg = float(request.POST['restecg'])
        thalach = float(request.POST['thalach'])
        exang = float(request.POST['exang'])
        oldpeak = float(request.POST['oldpeak'])
        slope = float(request.POST['slope'])
        ca = float(request.POST['ca'])
        thal = float(request.POST['thal'])

        user_data = np.array(
            (age,
             sex,
             cp,
             trestbps,
             chol,
             fbs,
             restecg,
             thalach,
             exang,
             oldpeak,
             slope,
             ca,
             thal)
        ).reshape(1, 13)
        print(user_data)
        rf = RandomForestClassifier(
            n_estimators=16,
            criterion='entropy',
            max_depth=9
        )

        rf.fit(np.nan_to_num(X), Y.ravel())
        rf.score(np.nan_to_num(X), Y)
        predictions = rf.predict(user_data)

        if int(predictions[0]) == 1:
            value = 1
        elif int(predictions[0]) == 0:
            value = 0
        print("values is ",value)
        return JsonResponse({"value":value})

    return render(request,"predict.html")




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import datetime

def change_booking_date(request, booking_id):
    booking = get_object_or_404(DoctorBooking, id=booking_id)

    if request.method == 'POST':
        if booking.status in ['Pending', 'Confirmed']:
            new_date = request.POST.get('new_date')
            try:
                # Convert and validate date
                parsed_date = datetime.strptime(new_date, '%Y-%m-%d').date()
                booking.booking_date = parsed_date
                booking.save()
                messages.success(request, 'Booking date updated successfully.')
            except ValueError:
                messages.error(request, 'Invalid date format.')
        else:
            messages.error(request, 'Cannot change the date for this appointment.')

    return redirect('MyAppoinment')  # Change to your actual view name

