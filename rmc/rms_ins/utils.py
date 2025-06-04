from django.shortcuts import render,redirect,HttpResponse,get_object_or_404,HttpResponseRedirect,reverse
from io import BytesIO
from django.http import HttpResponse
from rest_framework.response import Response
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
import urllib.request
import urllib.parse
from rms_ins.models import *
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.utils import serializer_helpers
from rest_framework.settings import api_settings
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import NotAuthenticated
from datetime import date,datetime,timedelta
def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        print(ip,"ip")
        return ip

def convert_status(status):
    return  int(status) == 1

def get_success_headers(data):
    try:
        return {'Location': str(data[api_settings.URL_FIELD_NAME])}
    except (TypeError, KeyError):
        return {}


def validate_state(data):
    valid_states = ['Andaman & Nicobar Islands(35)','Andhra Pradesh(28)','Andhra Pradesh New(37)','Arunachal Pradesh(12)',
    'Assam(18)','Bihar(10)','Chandigarh(04)','Chattisgarh(22)','Dadra & Nagar Haveli(26)','Daman & Diu(25)',
    'Delhi(07)','Goa(30)','Gujarat(24)','Haryana(06)','Himachal Pradesh(02)',
    'Jammu & Kashmir(01)','Jharkhand(20)','Karnataka(29)','Kerala(32)','Lakshadweep Islands(31)',
    'Madhya Pradesh(23)','Maharashtra(27)','Manipur(14)','Meghalaya(17)',
    'Mizoram(15)','Nagaland(13)','Odisha(21)','Pondicherry(34)','Punjab(03)','Rajasthan(08)','Sikkim(11)',
    'TamilNadu(33)','Telangana(36)','Tripura(16)','Uttar Pradesh(09)','Uttarakhand(05)',
    'West Bengal(19)']
    if data['state'] not in valid_states:
        raise DataValidationException("Not a valid state.",code=409)

def validate_gst_no_with_state(data):
    state_code = data['state'][-3:-1]
    gst_no_state_code = data['gst_no'][0:2]
    if state_code != gst_no_state_code:
        raise DataValidationException("State code " +state_code+" must match first two characters of gst no "+gst_no_state_code+".",code=409)



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None



def handle_tracking(request,for_tracking):
    if 'latitude' in for_tracking.keys():
        latitude = for_tracking['latitude']
    else:
        latitude = 0
    if 'longitude' in for_tracking.keys():
        longitude = for_tracking['longitude']
    else:
        longitude = 0
    user_tracking.objects.create(user= User.objects.get(id=request.user.id),
            user_ip_addr=get_ip(request),
            content_type=for_tracking['content_type'],
            action_done=for_tracking['action'],
            object_id=for_tracking['id'],
            created_by = request.user.username,
            module_name=for_tracking['module_name'],
            plant=for_tracking['plant_name'],
            sl_no=for_tracking['sl_no'],
            session_id=request.session._session_key,
            latitude = latitude,
            longitude= longitude)

def get_entity_type(child_id):
    print(child_id,"child_id")
    child = entity_master.objects.get(id = child_id)
    if child.parent_id:
            entity_type = get_entity_type(child.parent_id.id)
    else:
            entity_type = child.entity_type
    return entity_type


def construct_error_response(message, status_code, headers, detail=[]):
    error_message = {
        "code": status_code,
        "message": message,
        "detail": detail
    }
    return Response(error_message, status=status_code, headers=headers)

def get_message_ok():
    return {'message':'OK'}

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc,context)

    if isinstance(exc, NotAuthenticated):
        return construct_error_response(exc.detail,status_code=401, headers=response.headers)

    print(response, type(exc), exc,"response, type(exc), exc")
    request=context['request']
    for_tracking=getattr(context['view'], "for_tracking", {})
    print(for_tracking,"for_tracking")
    print(request.user,request.user.username,"request.userrequest.user.username")
    print(request.user.id,"request.user.id")
    trace = [] # To get the details of the error
    tb = exc.__traceback__ 
    while tb is not None:
        trace.append({
            "file_name": tb.tb_frame.f_code.co_filename,
            "function_name": tb.tb_frame.f_code.co_name,
            "line_no": tb.tb_lineno
        })
        tb = tb.tb_next
    error_msg={
        'type': type(exc).__name__,
        'message': str(exc),
        'trace': trace
    }
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        created_by = request.user.username
    else:
        user = None
        created_by = None
    user_tracking.objects.create(user= user,
        user_ip_addr=get_ip(request),
        content_type= for_tracking['content_type'],
        action_done="DURING EXCEPTION",
        created_by = created_by,
        module_name=for_tracking['module_name'],
        session_id= request.session._session_key,
        error_msg=error_msg)
    if response is None:
        return Response(str(exc), status=400)
    if response is not None:
            if isinstance(exc, ValidationError):
                print(exc,type(exc),"exc,type")
                # print("(exc.detail),type(exc.detail)",exc.detail,type(exc.detail))
                # print(response.status_code,"response.status_code_before")
                # Below code is to customise the status code
                if type(exc.detail) == serializer_helpers.ReturnDict:
                    code=exc.detail[str(list(exc.detail.keys())[0])][0].code
                    # print(code,type(code),"code")
                    if type(code) is int:
                        response.status_code = code
                response = construct_error_response(
                    'Data validation error', 
                    status_code=code, 
                    headers=response.headers)
                # print(response.status_code,"response.status_code after")
            elif isinstance(exc, EntityNotFoundException):
                response = construct_error_response(exc.detail,status_code=404, headers=response.headers)
            elif isinstance(exc, DataValidationException):
                if (exc.exception is not None):
                    error_details = list()
                    # print(list(exc.exception.detail.keys()),"exc.exception.detail.keys()")
                    for field in list(exc.exception.detail.keys()):
                        # print(field,"field")
                        # print(str(exc.exception.detail[field]),"str(exc.exception.detail[field]")
                        error_details.append({field:str(exc.exception.detail[field][0]) })
                    print(error_details)
                    response = construct_error_response("Invalid Data supplied",status_code=exc.code, headers=response.headers, detail=error_details)
                else:
                    response = construct_error_response(exc.detail,status_code=exc.code, headers=response.headers)
    return response
    # def get_ip(request):
    #     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #     if x_forwarded_for:
    #         ip = x_forwarded_for.split(',')[0]
    #     else:
    #         ip = request.META.get('REMOTE_ADDR')
    #     print(ip,"ip")
    #     return ip

def get_slno_prefix(needed_params):
    try:
        print(needed_params,"needed_params")
        query_date = needed_params['query_date']
        plant_id = needed_params['plant_id']
        query_1 = needed_params['query_1']
        voucher_type = needed_params['voucher_type']
        query_2 = needed_params['query_2']
        date_field_name = needed_params['date_field_name']
        slno_field_name = needed_params['slno_field_name']
        form_name = needed_params['form_name']
        date_name = needed_params['date_name']
        exception = needed_params['exception']
        query_3 = needed_params['query_3']
        # is_plant_id_needed = needed_params['is_plant_id_needed']
        today=date.today()
        # print(today,"today")
        # print(type(today),"typetoday")
        # print(len(query_date.strip()),"len(query_date.strip())",query_date,(query_date.strip()))

        if query_date is None:
            query_date  = today
            # print(query_date,"if")
        else:
            # print(query_date,"else")
            try:
                query_date = (datetime.strptime(query_date, "%d-%m-%Y").date())
                print("query_date 2",query_date,type(query_date))
                if query_date > today:
                    raise exception(date_name + ' is Invalid.. Because, '+ date_name +' must not be a future date.')
                print(query_1,"query_1")
                if query_1:
                    last_date = getattr(query_1,date_field_name)
                    print(last_date,"last_date")
                    # print(query_date ,query_1.date_field_name,"order_date < sales_order.order_date)")
                    if (query_date < last_date):
                        raise exception(date_name + '  is Invalid. Because, '+ date_name + '  must not be prior to last '+ date_name +'.')
                else:
                    print("else")
            except ValueError as e:
                raise exception(str(e))
                # raise exception(date_name + '  is Invalid. Because,'+date_name + '  must be in the format of dd-MM-yyyy.Ex:31-07-2023')
        print(query_date,"query_date")
        master = numberings_master.objects.filter(voucher_type = voucher_type)
        if master:
            for g in master:
                comp=g.entity_plant_id
                print("comp",comp)
                if comp == None:
                    is_common_for_all_plants = 'yes'
                    print("common for all plants")
                else:
                    is_common_for_all_plants = 'no'
                    print("created individually")
            if is_common_for_all_plants == 'yes':
                numexist=numberings_detail.objects.filter(numsetting_master__voucher_type= voucher_type,valid_from_date__lte=query_date,valid_upto_date__gte=query_date)
                if numexist:
                    # print("proceed")
                    count = numexist.count()
                    # print(count,"count")
                    if count > 1:
                        raise exception('There are more than 1 number settings available  for voucher type '+form_name + '  and '+ date_name + ' '+ query_date.strftime("%d-%m-%Y") +'.')
                    else:
                        for g in numexist:
                            prefix = g.prefix
                            start_no=g.starting_number
                            # print(start_no,"start_no_All")
                            no_of_digits=g.number_of_digits
                            # print("no_of_digits_All",no_of_digits)
                            if query_2:
                                cval=[]
                                for i in query_2:
                                    c=i.get(slno_field_name,None)
                                    cval.append(c)
                                # print(cval)
                                value1=[int(x) for x in cval]
                                # print(value1)
                                val=max(value1)+1
                                order_no=str(val).zfill(no_of_digits)
                                # print(order_no,"value1")
                            else:
                                order_no=str(start_no).zfill(no_of_digits)
                                # print(order_no,"value2")
                else:
                    raise exception('In number settings form, create a number settings for voucher type '+ form_name +' valid for '+ date_name + ' ' +query_date.strftime("%d-%m-%Y") +'.')
            else:
                numexist=numberings_detail.objects.filter(numsetting_master__voucher_type= voucher_type,valid_from_date__lte=query_date,valid_upto_date__gte=query_date,numsetting_master__entity_plant_id__id=plant_id)
                if numexist:
                    # print("proceed")
                    count = numexist.count()
                    # print(count,"count")
                    if count > 1:
                        raise exception('There are more than 1 number settings available  for voucher type '+form_name + '  , plant id '+ str(plant_id) +' and '+ date_name + ' '+ query_date.strftime("%d-%m-%Y") +'.')
                    else:
                        for g in numexist:
                            prefix = g.prefix
                            start_no=g.starting_number
                            # print(start_no,"start_no_All")
                            no_of_digits=g.number_of_digits
                            # print("no_of_digits_All",no_of_digits)
                            if query_3:
                                cval=[]
                                for i in query_3:
                                    c=i.get(slno_field_name,None)
                                    cval.append(c)
                                # print(cval)
                                value1=[int(x) for x in cval]
                                # print(value1)
                                val=max(value1)+1
                                order_no=str(val).zfill(no_of_digits)
                                # print(order_no,"value1")
                            else:
                                order_no=str(start_no).zfill(no_of_digits)
                                # print(order_no,"value2")
                else:
                    raise exception('In number settings form, create a number settings for voucher type '+ form_name +' valid for '+ date_name + ' ' +query_date.strftime("%d-%m-%Y") +' for this plant id '+str(plant_id) +' .')
        else:
            raise exception("Create a number settings for voucher type "+form_name +".")
        return {"sl_no": order_no,"prefix": prefix}
    except ValidationError as e:
        raise DataValidationException(detail=(str(e)),exception=e)
def check_vehicle_validity(equipment):
    print(equipment,"equipment")
    # sl_dt = sl_dt + timedelta(days=30)
    sl_dt = date.today()
    print(sl_dt,"sldt after")
    ins_dt = equipment.insurance_date
    print(type(ins_dt),"type vehicle.equipInsurDt")
    ins=(sl_dt-ins_dt).days
    print(ins,"ins")
    fc_dt = equipment.fc_date
    print(fc_dt,"fc_dt")
    print(type(fc_dt),"type vehicle.equipfcDt")
    fc=(sl_dt-fc_dt).days
    print(fc,"fc")
    permit_dt=equipment.permit_date
    print(permit_dt,"permit_dt")
    print(type(permit_dt),"type vehicle.equippermitDt")
    permit=(sl_dt-permit_dt).days
    print(permit,"permit")
    Expired=[]
    Can_Be_Used=[]
    valid=[ins,fc,permit]
    for i in range(len(valid)):
        print(i,"i")
        if i == 0:
            tax_type = "Insurance"
        elif i == 1:
            tax_type = "FC"
        else:
            tax_type = "Permit"

        if valid[i] > 0:
            print(valid[i],"valid greater than 0")
            status="Vehicle's "+ tax_type +" Expired "+ str(valid[i])+" days ago..."
            Expired.append(status)
        else:
            status="Can be used"
            Can_Be_Used.append(tax_type)
            Can_Be_Used.append(status)
    print(Expired,"Expired")	
    print(Can_Be_Used,"Can_Be_Used")
    if len(Expired) > 0:
        is_valid = False
    else:
        is_valid = True	
    return is_valid
