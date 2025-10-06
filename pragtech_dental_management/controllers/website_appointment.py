# -*- coding: utf-8 -*-
# from odoo import http
from odoo import http
from datetime import datetime,timedelta,date
from odoo.http import request
from odoo.tools import html_escape
import base64
import json
import re
from odoo.fields import Datetime
import pytz
from pytz import timezone
from odoo.exceptions import ValidationError

# Appointments Page
class AppointmentsPage(http.Controller):
    @http.route('/my_appointments/appointments/page', type="http", auth="public", website=True)
    def render_appointments_page(self, **kwargs):
        return request.render('pragtech_dental_management.appointment_page_template', {})
    
# Doctors Page
class AppointmentsDoctors(http.Controller):
    # @http.route('/my_appointments/doctor/page/<int:apt_id>', type="http", auth="public", website=True)
    @http.route(['/my_appointments/doctor/page', '/my_appointments/doctor/page/<int:apt_id>'], type='http', auth='public', website=True)
    # def render_appointments_doctor_page(self,apt_id, **kwargs):
    def doctor_page(self, apt_id=None, **kw):
        today = datetime.today().weekday()
        today_str = str(today)
        doctors = request.env['doctor.slot'].sudo().search([('weekday', '=', today_str)])
        for rec in doctors:
            weekday_key = rec.weekday
            weekday_label = dict(rec._fields['weekday'].selection).get(weekday_key)
            doctor_name = rec.doctor_id.name
        if apt_id:
            return request.render('pragtech_dental_management.doctor_page_template', {
                'doctors': doctors,
                'apt_id': apt_id,  # pass apt_id only when it exists
            })
        else:
            return request.render('pragtech_dental_management.doctor_page_template', {
                'doctors': doctors,
            })
        # return request.render('pragtech_dental_management.doctor_page_template', {
        #     'doctors': doctors

        # })
    

# Calendar Appointment page
class CalendarAppointment(http.Controller):
    @http.route('/calendar_appointment/<int:doctor_id>', type="http", auth="public", website=True)
    def calendar_appointment_page(self, doctor_id, **kw):
        doctor = request.env['medical.physician'].sudo().browse(doctor_id)
        appointments = request.env['medical.appointment'].sudo().search([
            ('doctor_id', '=', doctor_id)
        ])
        # Get user's timezone (fallback to UTC if not set)
        user_tz_name = request.env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz_name)

        booked_slots_by_date = {}
        app_id = kw.get('apt_id')
        for app in appointments:
            if app.state == 'cancel':
                continue
            if app.appointment_sdate and app.appointment_edate:
                # Convert to user's timezone
                utc_start = pytz.utc.localize(app.appointment_sdate)
                local_start = utc_start.astimezone(user_tz)
                utc_end = pytz.utc.localize(app.appointment_edate)
                local_end = utc_end.astimezone(user_tz)

                date_key = local_start.date().isoformat()  # 'YYYY-MM-DD'

                if date_key not in booked_slots_by_date:
                    booked_slots_by_date[date_key] = []

                booked_slots_by_date[date_key].append({
                    'from': local_start.strftime('%H:%M'),
                    'to': local_end.strftime('%H:%M'),
                })
        
        grouped_slots = {}

        for rec in doctor.slot_ids:
            start_hour = rec.start_hour
            end_hour = rec.end_hour
            weekday_name = dict(rec._fields['weekday'].selection).get(rec.weekday)
            
            start_time = datetime.strptime(f"{int(start_hour)}:{int((start_hour % 1) * 60):02d}", "%H:%M")
            end_time = datetime.strptime(f"{int(end_hour)}:{int((end_hour % 1) * 60):02d}", "%H:%M")


            grouped_slots.setdefault(weekday_name, [])

            while start_time < end_time:
                next_slot = start_time + timedelta(minutes=30)
                grouped_slots[weekday_name].append({
                    'from': start_time.strftime("%I:%M %p"),
                    'to': next_slot.strftime("%I:%M %p"),
                      'doctor': {
                        'id': doctor.id,
                    }
                                
                })
        
                start_time = next_slot
        if app_id:
            
            return request.render('pragtech_dental_management.calendar_appointment_page_template', {
                'doctor': doctor,
                'grouped_slots_json': json.dumps(grouped_slots),
                'booked_slots_json': json.dumps(booked_slots_by_date),
                'app_id_json': json.dumps(app_id),  # <- pass app_id as JSON here
            })
        else:
            return request.render('pragtech_dental_management.calendar_appointment_page_template', {
                'doctor': doctor,
                'grouped_slots_json': json.dumps(grouped_slots),
                'booked_slots_json': json.dumps(booked_slots_by_date),
            })

    
    # check existing user or new user
    @http.route('/my_appointment/new', type="http", auth="public", website=True)
    def new_user_appointment(self, from_time=None, to_time=None, doctor_id=None,**kwargs):
        doctor = None
        if doctor_id:
            doctor = request.env['medical.physician'].sudo().browse(int(doctor_id))
        
        services = request.env['product.product'].sudo().search([('type', '=','service')])


        values = {
            'from_time': from_time,
            'to_time': to_time,
            'doctor': doctor.res_partner_medical_physician_id.name if doctor else '',
            'doctor_id': doctor.id if doctor else '',
            'services':services,
        }


        return request.render('pragtech_dental_management.existing_user_or_not_check_template', values)
    

# New or Existing Patient Appointment Form
class AppointmentForm(http.Controller):
    # New User Appointment Form
    @http.route(['/appointment/appointment_form'], type='http', auth='public', website=True)
    def render_appointments_form_page(self,**kwargs):
        doctor = None
        from_time = request.params.get('from_time')
        to_time = request.params.get('to_time')
        doctor_id = request.params.get('doctor_id')


        if doctor_id:
            doctor = request.env['medical.physician'].sudo().browse(int(doctor_id))
        
        services = request.env['product.product'].sudo().search([('type', '=','service')])



        values = {
            'from_time': from_time,
            'to_time': to_time,
            'doctor': doctor.res_partner_medical_physician_id.name if doctor else '',
            'doctor_id': doctor.id if doctor else '',
            'services':services,
        }

        return request.render('pragtech_dental_management.appointment_form_template',values)
    
    # Existing User Appointment Form
    @http.route(['/appointment/appointment_form2'], type='http', auth='public', website=True)
    def render_appointments_form2_page(self,**kwargs):
        doctor = None
        from_time = request.params.get('from_time')
        to_time = request.params.get('to_time')
        doctor_id = request.params.get('doctor_id')

        if doctor_id:
            doctor = request.env['medical.physician'].sudo().browse(int(doctor_id))
        
        services = request.env['product.product'].sudo().search([('type', '=','service')])

        patients = request.env['medical.patient'].sudo().search([])


        values = {
            'patient_name':patients,
            'from_time': from_time,
            'to_time': to_time,
            'doctor': doctor.res_partner_medical_physician_id.name if doctor else '',
            'doctor_id': doctor.id if doctor else '',
            'services':services,
        }

        return request.render('pragtech_dental_management.appointment_form2_template',values)
    
    @http.route('/search_patient_by_email', type='json', auth='public')
    def search_patient_by_email(self, email=None):
        if not email:
            return {}

        patient = request.env['medical.patient'].sudo().search([('email', '=', email)], limit=1)
        if patient:
            return {
                'id': patient.id,
                'name': patient.partner_id.name,
            }
        return {}
    
    # new user submit appointment backend creation
    @http.route('/appointment/submit', type='http', auth='public', website=True, csrf=False)
    def customer_enquiry_success_new(self, **kw):
        from_time = kw.get('from_time')
        to_time = kw.get('to_time')

        # Get the user's timezone or default to UTC
        user_tz_name = request.env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz_name)

        try:
            if from_time:
                naive_start = datetime.strptime(from_time, '%Y-%m-%dT%H:%M')
                local_start = user_tz.localize(naive_start)
                utc_start = local_start.astimezone(pytz.utc).replace(tzinfo=None,second=52)  # remove tzinfo
            else:
                utc_start = False

            if to_time:
                naive_end = datetime.strptime(to_time, '%Y-%m-%dT%H:%M')
                local_end = user_tz.localize(naive_end)
                utc_end = local_end.astimezone(pytz.utc).replace(tzinfo=None,second=51)  # remove tzinfo
            else:
                utc_end = False

        except ValueError as e:
                return """
            <script>
                alert("Invalid date/time format. Please enter the correct date and time.");
                window.history.back();
            </script>
            """
            # return request.render('pragtech_dental_management.template_error_page', {'error': 'Invalid time format'})

        already_email = request.env['medical.patient'].sudo().search([('email','=',kw.get('email'))])
        if already_email:
             return request.render('pragtech_dental_management.email_exists_page', {
                'email': kw.get('email'),
            })
        # Step 1: Create patient
        partner_name = kw.get('patient_name')
        email = kw.get('email')

        partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': partner_name,
                'email': email,
            })


        # Now create medical.patient with partner_id
        patient = request.env['medical.patient'].sudo().create({
            'partner_id': partner.id,
            'email': email,
        })
        
        # Step 2: Create appointment
        appointment = request.env['medical.appointment'].sudo().create({
            'patient_id': patient.id,
            'doctor_id': int(kw.get('doctor_id')) if kw.get('doctor_id') else False,
            'appointment_sdate': utc_start,
            'appointment_edate': utc_end,
            'service_id': kw.get('service_id'),
        })

        return request.render('pragtech_dental_management.appointment_success_page')
        
    # nexisting ew user submit appointment backend creation
    @http.route('/appointment/submit_existing_patient', type='http', auth='public', website=True, csrf=False)
    def customer_enquiry_success_existing(self, **kw):
        from_time = kw.get('from_time')
        to_time = kw.get('to_time')
        patient_id = kw.get('patient_id')
        patient_name = kw.get('patient_name')
        if patient_name == "":
            return """
            <script>
                alert("Patient Name is not Null");
                window.history.back();
            </script>
            """
        patient_name = ''

        if patient_id:
            patient = request.env['medical.patient'].sudo().browse(int(patient_id))
            # patient_name = patient.name.name  

        # Get the user's timezone or default to UTC
        user_tz_name = request.env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz_name)

        try:
            if from_time:
                naive_start = datetime.strptime(from_time, '%Y-%m-%dT%H:%M')
                local_start = user_tz.localize(naive_start)
                utc_start = local_start.astimezone(pytz.utc).replace(tzinfo=None,second=52)  # remove tzinfo
            else:
                utc_start = False

            if to_time:
                naive_end = datetime.strptime(to_time, '%Y-%m-%dT%H:%M')
                local_end = user_tz.localize(naive_end)
                utc_end = local_end.astimezone(pytz.utc).replace(tzinfo=None,second=51)  # remove tzinfo
            else:
                utc_end = False

        except ValueError as e:
            return """
            <script>
                alert("Invalid date/time format. Please enter the correct date and time.");
                window.history.back();
            </script>
            """
            # return request.render('pragtech_dental_management.template_error_page', {'error': 'Invalid time format'})


        # Step 2: Create appointment
        appointment = request.env['medical.appointment'].sudo().create({
            'patient_id': patient.id,
            'doctor_id': int(kw.get('doctor_id')) if kw.get('doctor_id') else False,
            'appointment_sdate': utc_start,
            'appointment_edate': utc_end,
            'service_id': kw.get('service_id'),
        })

        return request.render('pragtech_dental_management.appointment_success_page')
    


# eisting Appointments Related Class and Functions    
class ExistingAppointments(http.Controller):
    @http.route(['/appointment/existing_appointments'], type='http', auth='public', website=True, csrf=False)
    def render_existing_appointments(self,**kwargs):
        return request.render('pragtech_dental_management.existing_appointment_page_template')
    
    @http.route(['/email/submit'], type='http', auth='public', website=True)
    def existing_user_appointments(self,**kw):
        email = kw.get('email')
        appointments_data = []
        existing_patient = request.env['medical.patient'].sudo().search([('email','=',email)], limit=1)
        if existing_patient:
            existing_appointments = request.env['medical.appointment'].sudo().search([('patient_id','=',existing_patient.id)])
           
            user_tz = request.env.user.tz or 'UTC'
            tz = timezone(user_tz)

    
            for apt in existing_appointments:
                appointment_s_date = ''
                appointment_e_date = ''

                if apt.appointment_sdate:
                    appointment_s_date = apt.appointment_sdate.astimezone(tz).strftime('%Y-%m-%d %H:%M')

                if apt.appointment_edate:
                    appointment_e_date = apt.appointment_edate.astimezone(tz).strftime('%Y-%m-%d %H:%M')

                apt_data = {
                    "apt_id":apt.id,
                    'appointment_id':apt.name,
                    'patient_name':apt.patient_id.partner_id.name,
                    'doctor':apt.doctor_id.res_partner_medical_physician_id.name,
                    'appointment_s_date':appointment_s_date,
                    'appointment_e_date':appointment_e_date,
                    'consultaion_service':apt.service_id.name,
                    'state':apt.state,
                    'is_reshedule':apt.is_reshedule,

                }
                appointments_data.append(apt_data)
        return request.render('pragtech_dental_management.existing_appointment_details_page_template',{'appointments_data': appointments_data})

    # Edit appointment form
    @http.route('/edit_appointment', type='http', auth='public', website=True)
    def edit_appointment(self, apt_id=None,from_time=None, to_time=None, doctor_id=None, **kw):
        apt_id = int(apt_id) if apt_id else None
        appointment = request.env['medical.appointment'].sudo().browse(apt_id)
        if doctor_id:
            doctor = request.env['medical.physician'].sudo().browse(int(doctor_id))
        # edit_appointment = []
        user_tz = request.env.user.tz or 'UTC'
        tz = timezone(user_tz)

        appointment_s_date = ''
        appointment_e_date = ''
        if appointment.appointment_sdate:
            appointment_s_date = appointment.appointment_sdate.astimezone(tz).strftime('%Y-%m-%d %H:%M')

        if appointment.appointment_edate:
            appointment_e_date = appointment.appointment_edate.astimezone(tz).strftime('%Y-%m-%d %H:%M')
        services = request.env['product.product'].sudo().search([('type', '=','service')])
        # psysician = request.env['medical.physician'].search([])
        edit_appointment_value = {
            'apt_id':appointment.id,
            'appointment_id':appointment.name,
            'patient_name':appointment.patient_id.partner_id.name,
            'doctor': doctor.name,
            'doctor_id': doctor.id,
            # 'psysician':psysician,
            'old_doctor_id':appointment.doctor_id.id,
            'appointment_s_date':from_time,
            'appointment_e_date':to_time,
            'appointment_old_s_date':appointment_s_date,
            'appointment_old_e_date':appointment_e_date,
            # 'consultaion_service':appointment.consultations.name,
            'consultaion_service': appointment.service_id.id,
            'services':services,

        }
        # edit_appointment.append(edit_appointment_value)
        return request.render('pragtech_dental_management.edit_existing_appointment_template',edit_appointment_value)
    
    # Existing Appointment Cancel
    @http.route('/cancel_appointment/<int:apt_id>', type='http', auth='public', website=True)
    def cancel_appointment(self, apt_id, **kw):
        appointment = request.env['medical.appointment'].sudo().browse(apt_id)
        appointment.write({'state': 'cancel'})
        return request.render('pragtech_dental_management.cancel_existing_appointment_template_message',{})

    # Edited appointment form submit button
    @http.route('/edit_appointment/submit', type='http', auth='public', website=True)
    def submit_edited_appointment(self, **kw):
        app_id = kw.get('apt_id')
        edited_appointment = request.env['medical.appointment'].sudo().search([('id', '=', app_id)])
        from_time = kw.get('from_time')
        to_time = kw.get('to_time')

        physician_id = kw.get('old_doctor_id')
        doctor_id = kw.get('doctor_id')


        # Safely convert IDs
        physician_id_int = int(doctor_id) if doctor_id and str(doctor_id).isdigit() else False
        doctor_id_int = int(physician_id) if physician_id and str(physician_id).isdigit() else False

        old_doctor = request.env['medical.physician'].sudo().browse(doctor_id_int).exists() if doctor_id_int else False
        new_doctor = request.env['medical.physician'].sudo().browse(int(doctor_id)).exists() if doctor_id else False

        if old_doctor and new_doctor and doctor_id != physician_id:
            edited_appointment.message_post(
                body=f"Physician Name Changed: {old_doctor.res_partner_medical_physician_id.name} => {new_doctor.res_partner_medical_physician_id.name}",
                subtype_id=edited_appointment.env.ref('mail.mt_note').id
            )

        service_id = kw.get('service_id')
        consultaion_service = kw.get('consultaion_service')

        old_service = request.env['product.product'].sudo().browse(int(consultaion_service)) if consultaion_service else False
        new_service = request.env['product.product'].sudo().browse(int(service_id)) if service_id else False

        if old_service and new_service and service_id != consultaion_service:
            edited_appointment.message_post(
                body=f"Consultation Service Changed: {old_service.name} => {new_service.name}",
                subtype_id=edited_appointment.env.ref('mail.mt_note').id
            )

        old_s_date = kw.get('appointment_old_s_date')
        old_e_date = kw.get('appointment_old_e_date')

        if old_s_date and from_time and old_s_date != from_time:
            edited_appointment.message_post(
                body=f"Start time Changed: {old_s_date} => {from_time}",
                subtype_id=edited_appointment.env.ref('mail.mt_note').id
            )

        if old_e_date and to_time and old_e_date != to_time:
            edited_appointment.message_post(
                body=f"End time Changed: {old_e_date} => {to_time}",
                subtype_id=edited_appointment.env.ref('mail.mt_note').id
            )

        user_tz_name = request.env.user.tz or 'UTC'
        user_tz = pytz.timezone(user_tz_name)

        try:
            utc_start = datetime.strptime(from_time, '%Y-%m-%dT%H:%M')
            local_start = user_tz.localize(utc_start)
            utc_start = local_start.astimezone(pytz.utc).replace(second=52, microsecond=0, tzinfo=None)

            utc_end = datetime.strptime(to_time, '%Y-%m-%dT%H:%M')
            local_end = user_tz.localize(utc_end)
            utc_end = local_end.astimezone(pytz.utc).replace(second=51, microsecond=0, tzinfo=None)
            
            # from_dt = datetime.fromisoformat(from_time)
            # to_dt = datetime.fromisoformat(to_time)
            edited_appointment.write({
                'doctor_id': physician_id_int or False,
                'appointment_sdate': utc_start,
                'appointment_edate': utc_end,
                'service_id': int(service_id) if service_id else False,
                'is_reshedule': True,
            })
            return request.render('pragtech_dental_management.edited_appointment_success_page')


            # Format to HH:MM
            # start_hour_str = from_dt.strftime("%H:%M")
            # end_hour_str = to_dt.strftime("%H:%M")
            # start_hour_float = int(start_hour_str.split(':')[0]) + int(start_hour_str.split(':')[1]) / 60
            # end_hour_float = int(end_hour_str.split(':')[0]) + int(end_hour_str.split(':')[1]) / 60

            # if utc_end < utc_start:
            #      return """
            #     <script>
            #         alert("Please add correct time: End time must be after start time.");
            #         window.history.back();
            #     </script>
            #     """
            # Weekday validation with doctor slots
            # dt = datetime.fromisoformat(from_time)
            # weekday_name = dt.strftime('%A')

            # for slot in new_doctor.slot_ids:
            #     weekday_field = slot.fields_get()['weekday']['selection']
            #     weekday_label = dict(weekday_field).get(slot.weekday)
            #     if weekday_label == weekday_name:
            #         if slot.start_hour <= start_hour_float and slot.end_hour >= end_hour_float:
            #             edited_appointment.write({
            #             'doctor_id': physician_id or False,
            #             'appointment_sdate': utc_start,
            #             'appointment_edate': utc_end,
            #             'service_id': int(service_id) if service_id else False,
            #             'is_reshedule': True,
            #         })
            #             return request.render('pragtech_dental_management.edited_appointment_success_page')

            #         else:
            #             return """
            #             <script>
            #                 alert("Time slot is not available");
            #                 window.history.back();
            #             </script>
            #         """
                    
                    #     return request.render('pragtech_dental_management.template_slot_unavailable_error_page', {
                    # })
                  
            # Write the appointment update
            

            
        except ValueError:
            return """
            <script>
                alert("Invalid date/time format. Please enter the correct date and time.");
                window.history.back();
            </script>
            """

        except ValidationError as e:
            return """
            <script>
                alert("Validation error: {str(e).replace('"', '\\"')}");
                window.history.back();
            </script>
        """


