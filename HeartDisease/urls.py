"""
URL configuration for HeartDisease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Patient import views as v1
from Admin import views as v2
from Doctor import views as v3

urlpatterns = [
    path("admin/", admin.site.urls),

    ### Home,Login,Register

    path('', v1.home, name='home'),
    path('Register/', v1.Register, name='Register'),
    path('Login/', v1.login, name='Login'),
    path('Predict/', v1.Predict, name='Predict'),

    ### User/Patient

    path('userhome', v1.userhome, name='userhome'),
    path('GiveFeedback', v1.GiveFeedback, name='GiveFeedback'),
    path('MyAppoinment', v1.MyAppoinment, name='MyAppoinment'),
    path('TakeAppoinment', v1.TakeAppoinment, name='TakeAppoinment'),
    path('viewmore/<int:id>', v1.viewmore, name='viewmore'),
    path("upload_pdf", v1.upload_pdf, name="upload_pdf"),
    path("generate_diet_plan/", v1.generate_diet_view, name="generate_diet_plan"),
    path("chatbot_page", v1.chatbot_page, name="chatbot_page"), 
    path("chatbot", v1.chatbot, name="chatbot"), 
    path("order-medicine/<int:prescription_id>/", v1.order_medicine, name="order_medicine"),
    path('my-orders/', v1.patient_orders, name='patient_orders'),
    path('appointment/change-date/<int:booking_id>/', v1.change_booking_date, name='change_booking_date'),



    ## Admin
    path('adminhome', v2.adminhome, name='adminhome'),
    path('ViewFeedback', v2.ViewFeedback, name='ViewFeedback'),
    path('ViewDoctor', v2.ViewDoctor, name='ViewDoctor'),
    path('AddDoctor', v2.AddDoctor, name='AddDoctor'),
    path('Patients', v2.Patients, name='Patients'),
    path('ViewAppoinments', v2.ViewAppoinments, name='ViewAppoinments'),
    path('medicine-orders', v2.admin_medicine_orders, name='admin_medicine_orders'),
    path('delete_doctor/<str:doctor_id>/', v2.delete_doctor, name='delete_doctor'),
    path("delete_patient/<str:patient_id>/", v2.delete_patient, name="delete_patient"),
    path("update_order_status/<int:order_id>/", v2.update_order_status, name="update_order_status"),

path('send-email-notifications/', v2.send_today_appointment_notifications, name='send_email_notifications'),



    ### Doctor
    path('doctorhome', v3.doctorhome, name='doctorhome'),
    path('Bookings', v3.Bookings, name='Bookings'),
    path('update_booking_status/', v3.update_booking_status, name='update_booking_status'),
    path('doc_viewmore/<int:id>', v3.doc_viewmore, name='doc_viewmore'),
path('appointment/change-date-ajax/', v3.change_booking_date_ajax, name='change_booking_date_ajax'),

]
