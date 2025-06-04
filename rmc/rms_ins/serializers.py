from rest_framework import serializers
from rms_ins.models import *
from django.contrib.auth.models import Group,Permission,User
from rest_framework import status
import re
from rest_framework.validators import * #UniqueValidator
from rms_ins.exceptions import DataValidationException,EntityNotFoundException
from datetime import date,datetime,timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
import pandas as pd

def is_user_allowed_plant(request,plant_id):
    if not (request.user.is_superuser):
        allowed_plant_list = list(request.user.profiles_master.plant.values_list('id',flat=True))
        if not (int(plant_id) in allowed_plant_list):
            raise DataValidationException(detail = "You don't have permission for this plant.", code=403)

def is_mobile_no(value):
    mobile_regex="^(0|91)?[6-9][0-9]{9}$"
    if not re.match(mobile_regex,value):
        raise DataValidationException(detail=f'Mobile number {value} is Invalid.')
    return value

def is_phone_no(value):
    phone_regex = "^\+?[0-9]+(\s|\-)?\(?\d{2,6}\)?(\s|\-)?[0-9]+(\s|\-)?[0-9]+$"
    if ',' in  value:
        value_list = value.split(",")
        for i in value_list:
            if not re.match(phone_regex,i):
                raise DataValidationException(detail=f'Phone number {i} is Invalid.')
    else:
        if not re.match(phone_regex,value):
            raise DataValidationException(detail=f'Phone number {value} is Invalid.')
    return value

def is_company(company_id):
    # To validate company id
    if not (entity_master.objects.filter(status = 1,entity_type = 'company',id=company_id).exists()):
        raise DataValidationException("Company Id is invalid",code=409)

def is_customer(customer_id):
    # To validate customer id
    if not (entity_master.objects.filter(status = 1,entity_type = 'customer',id=customer_id).exists()):
        raise DataValidationException("Customer Id is invalid",code=409)

def is_quotation(quotation_id):
    # To validate quotation id
    if not (entity_enquiry_master.objects.filter(status = 1,id=quotation_id).exists()):
        raise DataValidationException("Quotation Id is invalid",code=409)

def is_consignee(consignee_id):
    # To validate consignee(site) id
    if not (entity_master.objects.filter(id=consignee_id,status = 1,entity_type='plant').exists()):
        raise DataValidationException('Consignee id is Invalid.',code=409)

def is_plant(plant_id):
    if not (entity_master.objects.filter(id=plant_id,status = 1,entity_type='plant').exists()):
        raise DataValidationException('Plant id is Invalid.',code=409)
    
def is_supplier(vendor_id):
    if not entity_master.objects.filter(id=vendor_id,status=1,entity_type='supplier').exists():
                raise DataValidationException('Vendor id is Invalid',code =400)

def is_pincode(value):
    pincode_regex="^[1-9][0-9]{5}$"
    if not re.match(pincode_regex,value):
        raise DataValidationException(detail=f'Pincode {value} is Invalid.')
    return value

def is_pan_no(value):
    pan_no_regex ="^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
    # Convert the input value to uppercase
    value = value.upper()
    if not re.match(pan_no_regex,value):
        raise DataValidationException(detail=f'PAN No {value} is Invalid.')
    return value

def is_gst_no(value):
    gst_no_regex = "^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    # Convert the input value to uppercase
    value = value.upper()
    if not re.match(gst_no_regex,value):
        raise DataValidationException(detail=f'GST No {value} is Invalid.')
    return value

def is_mail_valid(value):
    mail_regex = "^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$"
    #"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
    if not re.match(mail_regex,value):
        raise DataValidationException(detail=f'Email address {value} is Invalid.')
    return value

def is_valid_plant(plant_id):
    if not (entity_master.objects.filter(status = 1,entity_type = 'plant',id=plant_id).exists()):
        raise DataValidationException('Plant id is Invalid.',code=409)

class EntityMasterSerializer(serializers.ModelSerializer):
    status=serializers.BooleanField()
    class Meta:
        model = entity_master
        fields = "__all__"

    def to_internal_value(self, data):
        ## this is done to change the status field value from boolean to integer if and if not 'status'
        # is present in data
        if 'status' in data.keys():
            # data['status'] = bool(data['status'])
            if data['status'] == True:
                data['status'] = 1
            elif data['status'] == False:
                data['status'] =  0
        else:
            data['status'] = 1
        if 'name' in data.keys():
            data['entity_name'] = data['name']
        return super().to_internal_value(data)

    def validate(self, data):
        form_name=getattr(self.context['view'], "for_tracking", {})['content_type']
        # print(self,"self entity_master")
        # print(getattr(self.context['view'], "for_tracking", {})['content_type'])
        valid_entity_types=getattr(self.context['view'], "valid_entity_types", [])
        method = self.context['request'].method
        if  ((method == 'POST') and (form_name != 'PLANT FORM') and (form_name != 'CONSIGNEE REGISTRATION FORM')):
            is_exists=entity_master.objects.filter(entity_name__iexact=data['entity_name'],entity_type__in=valid_entity_types).exists()
            if is_exists:
                raise DataValidationException(detail=f'Name [{data["entity_name"]}] already exists. Please choose a different name.')
        elif ((method == 'PUT') and (form_name != 'PLANT FORM') and (form_name != 'CONSIGNEE REGISTRATION FORM')):
            is_exists=entity_master.objects.filter(entity_name__iexact=data['entity_name'],entity_type__in=valid_entity_types).exclude(id=self.instance.id).exists()
            if is_exists:
                raise DataValidationException(detail=f'Name [{data["entity_name"]}] already exists. Please choose a different name.')
        
        if 'contact_mobile_no' in data.keys():
            if data['contact_mobile_no'] :
                data['contact_mobile_no'] = is_mobile_no(data['contact_mobile_no'])
        if ('mobile_number' in data.keys()):
            if data['mobile_number']:
                data['mobile_number'] = is_mobile_no(data['mobile_number'])
        if 'phone_number' in data.keys():
            if data['phone_number']:
                data['phone_number'] = is_phone_no(data['phone_number'])
        if 'pincode' in data.keys():
            if data['pincode']:
                data['pincode']=is_pincode(data['pincode'])
        if 'pan_no' in data.keys():
            if data['pan_no']:
                data['pan_no']=is_pan_no(data['pan_no'])
            elif ((form_name == 'COMPANY FORM') or (form_name == 'PLANT FORM')):
                raise DataValidationException(detail='PAN No is required')
        if 'gst_no' in data.keys():
            if data['gst_no']:
                data['gst_no']=is_gst_no(data['gst_no'])
            elif ((form_name == 'COMPANY FORM') or (form_name == 'PLANT FORM')):
                raise DataValidationException(detail='GST No is required')
        
        if form_name == 'ACCOUNTS GROUPING':
            # if data['entity_type'] in valid_entity_types:
            #     # print((data['entity_type']))
            #     if data['parent_id']:
            #         # print(data['parent_id'])
            #         nature_of_group=data['parent_id'].entity_type
            #         if nature_of_group in valid_entity_types:
            #             if not data['entity_type'] == nature_of_group:
            #                 raise DataValidationException(detail=f'The entity type must be {nature_of_group}')
            #         else:
            #             raise DataValidationException(detail="Entity type is invalid.")
            # else:
            #     raise DataValidationException(detail="Entity type is invalid")
            if data['parent_id']:
                data['entity_type'] = None
            else:
                if not data['entity_type'] in valid_entity_types:
                    raise DataValidationException(detail="Entity type is invalid")
        return data
        

class UserTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_tracking
        fields = "__all__" 


def validate_image_size(value):
    """
    Validate that the uploaded image size is less than or equal to 100 KB.
    """
    max_size_kb = 100  # Maximum size in kilobytes

    if value.size > max_size_kb * 1024:  # Convert max_size_kb to bytes
        raise DataValidationException(f"Image size must be at most {max_size_kb} KB.",code=409)

class EntityCompanyDetailSerializer(serializers.ModelSerializer):
    is_batching_report_needed =  serializers.BooleanField()
    seal = serializers.ImageField(validators=[validate_image_size], required=False)
    logo = serializers.ImageField(validators=[validate_image_size], required=False)
    class Meta:
        model = entity_company_detail
        fields = "__all__"
    
    def validate(self,data):
        if not ((data['closing_dt']) >= (data['opening_dt'])):
            raise DataValidationException(detail='Closing date must be greater than or equal to opening date.')
        return data


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'   

class TagListingField(serializers.RelatedField):
    def to_representation(self, value):
        return value.codename

class GroupSerializer(serializers.ModelSerializer):
    # permissions = PermissionSerializer(read_only=True, many=True)
    # permissions = serializers.StringRelatedField(many=True)
    permissions=TagListingField(many=True, read_only=True)
    name = serializers.CharField()
    class Meta:
        model = Group
        fields = ('id','name','permissions')

    def validate(self,data):
        method = self.context['request'].method
        if len(data['name']) > 100:
            raise DataValidationException('Group name cannot exceed 100 characters')
        if method == 'POST':
            is_exists=Group.objects.filter(name__iexact=data['name']).exists()
        elif method == 'PUT':
            # id= self.initial_data['id']
            is_exists=Group.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
        if is_exists:
            raise DataValidationException(detail=f'Category name {data["name"]}  already exist.')
        return data

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), lookup='iexact',message='Username already exist..')])
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), lookup='iexact')])
    groups = serializers.PrimaryKeyRelatedField(many=True,allow_empty=True,queryset=Group.objects.all())
    # groups = serializers.PrimaryKeyRelatedField(many=True,allow_empty=False,queryset=Group.objects.all())
    class Meta:
        model = User
        fields = '__all__'
    def create(self, validated_data):
        groups = validated_data.pop('groups')
        user = User.objects.create_user(**validated_data)
        user.groups.set(groups)
        return user  
    def update(self, model_instance, validated_data):
        groups = validated_data.pop('groups')
        # we have to upate password separately from other data
        # so pop the password if it is available 
        hashed_password=model_instance.password
        password = validated_data.pop('password', None)
        # update all other fields in the model
        user = super().update(model_instance, validated_data)
        if ((password) and (password == hashed_password)):
            print("do nothing")
        else: 
            user.set_password(password)
            user.save()
        user.groups.set(groups)
        return user  

class ProfilesMasterSerializer(serializers.ModelSerializer):
    is_mfa_needed = serializers.BooleanField()
    is_location_auth_needed = serializers.BooleanField()
    plant = serializers.PrimaryKeyRelatedField(many=True,allow_empty=False,queryset=entity_master.objects.filter(entity_type='plant',status=1))
    class Meta:
        model = profiles_master
        fields = '__all__'

    def to_internal_value(self, data):
        data['plant'] = data['plants']
        return super().to_internal_value(data) 

    def validate(self,data):
        if not ((data['user_valid_upto']) >= (data['user_valid_from'])):
            raise DataValidationException(detail='Valid upto date must be greater than or equal to valid from date.')
        if data['user_mobile_no'] :
            data['user_mobile_no'] = is_mobile_no(data['user_mobile_no'])
        return data

class ProfilesMasterValidationSerializer(serializers.ModelSerializer):
    # This serializer is for validating profile master table details without user object (before creating user object)
    is_mfa_needed = serializers.BooleanField()
    is_location_auth_needed = serializers.BooleanField()
    plant = serializers.PrimaryKeyRelatedField(many=True,allow_empty=False,queryset=entity_master.objects.filter(entity_type='plant',status=1))
    class Meta:
        model = profiles_master
        fields = ['user_mobile_no','user_valid_from','user_valid_upto','user_remarks','is_mfa_needed','is_location_auth_needed',
                    'plant']

    def to_internal_value(self, data):
        data['plant'] = data['plants']
        return super().to_internal_value(data) 

    def validate(self,data):
        if not ((data['user_valid_upto']) >= (data['user_valid_from'])):
            raise DataValidationException(detail='Valid upto date must be greater than or equal to valid from date.')
        if data['user_mobile_no'] :
            data['user_mobile_no'] = is_mobile_no(data['user_mobile_no'])
        return data

class EntityPlantDetailSerializer(serializers.ModelSerializer):
    plant_seal = serializers.ImageField(validators=[validate_image_size], required=False)
    plant_logo = serializers.ImageField(validators=[validate_image_size], required=False)
    plant_br_logo = serializers.ImageField(validators=[validate_image_size], required=False)
    class Meta:
        model = entity_plant_detail
        fields = "__all__"   

    def validate(self,data):
        if not (entity_master.objects.filter(status = 1,entity_type = 'company',id=data['entity_company_id'].id).exists()):
            raise serializers.ValidationError({'entity_company_id':'Invalid..'},code=409)
        if not ((data['account_closing_dt']) >= (data['account_opening_dt'])):
            raise serializers.ValidationError({'closing_dt':
            'closing_dt must be greater than or equal to opening_dt...'},code=409)
        if self.instance:
            is_exists=entity_plant_detail.objects.filter(plant_alias__iexact=data['plant_alias']).exclude(id=self.instance.id).exists()
        else:
            is_exists=entity_plant_detail.objects.filter(plant_alias__iexact=data['plant_alias']).exists()
        if is_exists:
            raise DataValidationException(detail=f'Plant alias [{data["plant_alias"]}] already exist.')
        return data    


class EntityVendorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = entity_vendor_detail
        fields = "__all__"  
    
    def to_internal_value(self, data):
        data['vendor_type'] = data['vendor_type_id']
        return super().to_internal_value(data)

    def validate(self,data):
        products=entity_master.objects.filter(status = 1,entity_type = 'others',entity_name='PRODUCT',system_field=1).first()
        if products:
            if not (entity_master.objects.filter(status = 1,id=data['vendor_type'].id,parent_id=products.id,system_field=1).exists()):#,entity_type = 'others'
                raise DataValidationException('Vendor Type is invalid')
        else:
            raise DataValidationException('Vendor Type is invalid')  
        return data   

class UomMasterSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField()#validators=[is_status])
    class Meta:
        model = uom_master
        fields = "__all__"
    
    def validate(self, data):
        method = self.context['request'].method
        if method == 'POST':
            is_exists=uom_master.objects.filter(name__iexact=data['name']).exists()
        elif method == 'PUT':
            is_exists=uom_master.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
        if is_exists:
            raise DataValidationException(f'Unit Name [{data["name"]}]already exists')
        return data

class UomListSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField()
    system_field = serializers.BooleanField()
    class Meta:
        model = uom_master
        fields = ['id','name','symbol','user_remarks','status','system_field']

class TaxformMasterSerializer(serializers.ModelSerializer):
    status =  serializers.BooleanField()#validators=[is_status])
    class Meta:
        model = taxform_master
        fields = "__all__"
    
    def validate(self,data):
        method = self.context['request'].method
        if method == 'POST':
            is_exists=taxform_master.objects.filter(name__iexact=data['name']).exists()
        elif method == 'PUT':
            is_exists=taxform_master.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
        if is_exists:
            raise DataValidationException(f'Tax Name [{data["name"]}]already exists')
        if ((data['tax_type'] != 'gst') and (data['tax_value2'] > 0)):
            raise DataValidationException(detail='Tax-Value2 cannot be greater than 0 ,if type is not GST')
        if not ((data['valid_upto']) >= (data['valid_from'])):
            raise DataValidationException(detail='Valid upto date must be greater than or equal to Valid from date.')
        return data

class TaxformMasterListSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField()
    class Meta:
        model = taxform_master
        fields = ['id','name','tax_value1','tax_value2','tax_type','valid_from','valid_upto','user_remarks','status','system_field']

class ProductMasterSerializer(serializers.ModelSerializer):
    status =  serializers.BooleanField()#validators=[is_status])
    is_gst_applicable =  serializers.BooleanField()
    is_batch_report_connected =  serializers.BooleanField()
    prod_gst_type = serializers.ChoiceField(choices = ['Goods','Services'],allow_blank=False)
    class Meta:
        model = product_master
        fields = "__all__"
    
    def to_internal_value(self, data):
        data['category_detail'] = data['category_id']
        data['tax'] = data['tax_id']
        data['unit'] = data['unit_id']
        return super().to_internal_value(data)

    def validate(self,data):
        method = self.context['request'].method
        if method == 'POST':
            is_exists=product_master.objects.filter(name__iexact=data['name']).exists()
        elif method == 'PUT':
            is_exists=product_master.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
        if is_exists:
            raise DataValidationException(f'Product Name [{data["name"]}]already exists')
       
        if data['is_gst_applicable'] == True:
            if not (taxform_master.objects.filter(status = 1,id=data['tax'].id).exists()):
                raise DataValidationException(detail='Tax is invalid')
        else:
            if not (taxform_master.objects.filter(status = 1,system_field=1,name='NO TAX',tax_type='gst',id=data['tax'].id).exists()):
                raise DataValidationException(detail='Tax is invalid')
        if not (uom_master.objects.filter(status = 1,id=data['unit'].id).exists()):
            raise DataValidationException(detail='Unit is invalid')
        products=entity_master.objects.filter(status = 1,entity_type = 'others',entity_name='PRODUCT',system_field=1).first()
        if products:
            if not (entity_master.objects.filter(status = 1,id=data['category_detail'].id,parent_id=products.id,system_field=1).exists()):#,entity_type = 'others'
                raise DataValidationException(detail='Category Detail is invalid')
        else:
            raise DataValidationException(detail='Category Detail is invalid')
        return data

class NumberingsMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = numberings_master
        fields = "__all__"

    def to_internal_value(self, data):
        if data['plant_id'] == -1:
            data['plant_id'] = ""
        data['entity_plant_id'] = data['plant_id']
        return super().to_internal_value(data)     
    
    def validate(self,data):
        if self.instance:
            print("do nothing")
        else:
            valid_voucher_types = ['quotation','sales_order','delivery_challan','invoice','receipt_voucher','credit_note','purchase_order','goods_reciept_note','cube_test_report']
            if data['voucher_type'] in valid_voucher_types:
                # print("data['voucher_type'] valid")
                test=numberings_master.objects.filter(voucher_type= data['voucher_type']).values('entity_plant_id')
                # print(test,"test")
                if data['entity_plant_id']:
                    # print("plant id is not all")
                    is_exists= entity_master.objects.filter(entity_type='plant',status=1,id=data['entity_plant_id'].id).exists()
                    if is_exists:
                        # print("data['entity_plant_id'] is valid")
                        is_user_allowed_plant(self.context['request'],data['entity_plant_id'].id)
                        if ((data['voucher_type'] == 'sales_order') or (data['voucher_type'] == 'purchase_order') or (data['voucher_type'] == 'quotation')):
                            raise DataValidationException('For voucher types(Quotation, SalesOrder & PurchaseOrder), individual Plant cannot be selected.')    
                        else:
                            if test:
                                for i in test:
                                    c=i.get('entity_plant_id',None)
                                    # print(c,"c")
                                    if c == None:
                                        raise DataValidationException('For this voucher type, Number Setting is configured for all Plants. Cannot be set for individual Plant.')
                                    else:
                                        check= numberings_master.objects.filter(voucher_type= data['voucher_type'],entity_plant_id=data['entity_plant_id'].id).exists()
                                        if check:
                                            raise DataValidationException('For this voucher type and Plant, Number Setting already exists.')
                                        else:
                                            # print("can create...")
                                            return data
                            else:
                                print("can create")
                    else:
                        raise DataValidationException('Plant Id is invalid.')    
                else:
                    # print("data['entity_plant_id']  is all")
                    if test:
                        for i in test:
                            c=i.get('entity_plant_id',None)
                            # print(c,"c")
                            if c == None:
                                raise DataValidationException('For this voucher type, Number Setting is already configured for all Plants.')# Cannot be set for individual Plant.
                            else:
                                raise DataValidationException('For this voucher type and plant, Number Setting already exists. You cannot create for all Plants.')
                    else:
                        print("can create")
            else:
                raise DataValidationException('Voucher Type is invalid.',code=409)
        return data

class NumberingsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = numberings_detail
        fields = "__all__"

    def validate(self,data):
        if not ((data['valid_upto_date']) >= (data['valid_from_date'])):
            raise DataValidationException('Valid upto date must be greater than or equal to valid from date.')
        return data


class ApprovalSettingsMasterSerializer(serializers.ModelSerializer):
    entity_company_id = serializers.PrimaryKeyRelatedField(queryset=entity_master.objects.filter(entity_type='company',status=1))
    voucher_type = serializers.ChoiceField(choices = ['sales_order','purchase_order'],allow_blank=False)
    is_appr_needed = serializers.BooleanField()
    is_so_wait_on_save = serializers.BooleanField()
    is_mail_needed = serializers.BooleanField()
    mail_ids = serializers.ListField(child = serializers.CharField(),allow_empty=True,allow_null=True)
    conditions_for_so_waiting = serializers.MultipleChoiceField(choices = ['advance_amount','credit_limit'],allow_blank=True,allow_null=True)
    class Meta:
        model = approval_setting_master
        fields = "__all__"
        validators = [UniqueTogetherValidator(queryset=approval_setting_master.objects.all(),
                fields=['entity_company_id', 'voucher_type'])] # to block duplicate entry

    def to_internal_value(self, data):
        data['entity_company_id'] = data['company_id']
        if self.instance:
            data['voucher_type']=self.instance.voucher_type
            data['entity_company_id']=self.instance.entity_company_id
        if data['is_mail_needed'] == 0:
            data['mail_ids'] = None
        if (((data['voucher_type'] == 'sales_order') and (data['is_appr_needed'] == 0)) or (data['voucher_type'] == 'purchase_order')):
            data['is_so_wait_on_save'] = 0
            data['conditions_for_so_waiting'] = None
        return super().to_internal_value(data)

    def validate(self,data):
        # valid_voucher_types = ['sales_order','purchase_order']
        # if not data['voucher_type'] in valid_voucher_types:
        #     raise serializers.ValidationError({'voucher_type':'sales_order and purchase_order are the only valid voucher types...'},code=409)
        
        if data['is_mail_needed'] == 1:
            print("mail needed")
            if (len(data['mail_ids']) == 0):
                raise DataValidationException('Mail ids cannot not be empty if Mail is required.')
            else:
                for i in data['mail_ids']:
                    i = is_mail_valid(i)
                data['mail_ids'] = ','.join(map(str,data['mail_ids']))
        
        if ((data['voucher_type'] == 'sales_order') and (data['is_appr_needed'] == 1)):
            if ((data['is_so_wait_on_save'] == 1) and (len(data['conditions_for_so_waiting'])>0)):
                raise DataValidationException('Invalid input because for sales order , if is_appr_needed is true ,then is_so_wait_on_save may be true or valid conditions_for_so_waiting.')
            if not((data['is_so_wait_on_save'] == 1) or (len(data['conditions_for_so_waiting'])>0)):
                raise DataValidationException('Invalid input because for sales order , if is_appr_needed is true ,then is_so_wait_on_save must be true or valid conditions_for_so_waiting.')
            data['conditions_for_so_waiting'] = ','.join(map(str,data['conditions_for_so_waiting']))
        return data


class EntityOrderMasterSerializer(serializers.ModelSerializer):
    is_tax_included  = serializers.BooleanField()
    status  = serializers.BooleanField()
    is_advance_payment  = serializers.BooleanField()
    transport_mode = serializers.ChoiceField(choices = ['own','customer','own/customer'])
    order_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    validity_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    
    class Meta:
        model = entity_order_master
        fields = "__all__" 
    
    def to_internal_value(self, data):
        print(data,"data eom iv")
        data['entity_company_id'] = data['company_id']
        data['entity_consignee_id'] = data['consignee_id']
        data['enquiry_id'] = data['quotation_id']
        data['receipt'] = data['receipt_id']
        if data['order_amount'] == '':
            data['order_amount'] = 0
        if data['validity_date'] == '':
            data['validity_date'] = datetime.strptime(data['order_date'], "%d-%m-%Y").date() + timedelta(days=30)
        return super().to_internal_value(data)

    def validate(self,data):
        print(data,"data eomaster")
        if not (float(data['order_amount']) > 0):
            raise DataValidationException('Total Sales order amount must be greater than zero.')
        if self.instance:
            print("self.instance")
            data['order_no'] = self.instance.order_no
            data['order_date'] = self.instance.order_date
            data['order_time'] = self.instance.order_time
            data['prefix'] = self.instance.prefix
        else:
            print("validate else")
        if data['is_advance_payment']:
            print("advance true")
            if data['receipt']:
                print("receipt")
                if not (receipt_master.objects.filter(status = 1,id=data['receipt'].id,receipt_against='advance').exists()):
                    raise DataValidationException("Receipt Id is invalid.",code=409)
            else:
                raise DataValidationException("Receipt Id is required If advance payment is true.",code=409)
        else:
            print("advance false")
            data['receipt'] = None
        return data

def verify_eo_master(data):
    print(data,"data verify_eo_master")
    if data['quotation_id']:
        print("data verify_eo_master if ")
        is_quotation(data['quotation_id'])
        quotation = entity_enquiry_master.objects.get(id = data['quotation_id'])
        print(data['company_id'],type(data['company_id']),"data['company_id']")
        print(quotation,"quotation verify_eo_master",quotation.entity_company_id.id,type(quotation.entity_company_id.id))
        if not (int(data['company_id']) == quotation.entity_company_id.id):
            raise DataValidationException("Company Id is invalid..Because this company is not included in this Quotation.",code=409)
        if not (int(data['consignee_id']) == quotation.entity_consignee_id.id):
            raise DataValidationException('Site id is Invalid.Because this site is not included in this Quotation.',code=409)
    else:
        is_company(data['company_id'])
        is_consignee(data['consignee_id'])


class EntityOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = entity_order_detail
        fields = "__all__"  

    def to_internal_value(self, data):
        if self.instance:
            print("during save")
        else:
            data['balance_qty'] = data['quantity']
        data['product'] = data['product_id']
        data['tax'] = data['tax_id']
        data['concrete_structure'] = data['concrete_structure_id']
        return super().to_internal_value(data)

    def validate(self,data):
        if not (data['amount'] == data['rate']*data['quantity']):
            raise DataValidationException('Amount is not valid. It should be (rate * quantity).')
        if not (data['rate'] > 0):
            raise DataValidationException('Rate must be greater than zero.')
        if not (data['quantity'] > 0):
            raise DataValidationException('Quantity must be greater than zero.')
        return data

def is_valid_product(product_id):
    if not (product_master.objects.filter(status = 1,id=product_id).exists()):
        raise DataValidationException('Product id is Invalid.',code=409)

def is_valid_tax(tax_id):
    if not (taxform_master.objects.filter(status = 1,id=tax_id).exists()):
        raise DataValidationException('Tax id is Invalid.',code=409)
    
def is_valid_concrete_structure(concrete_structure_id):
    if not (entity_master.objects.filter(status = 1,system_field = 0,parent_id__entity_name='CONCRETE STRUCTURE',parent_id__system_field=1,parent_id__entity_type ='others',parent_id__parent_id = None,parent_id__status = 1,id=concrete_structure_id).exists()):#entity_type = 'others',
        raise DataValidationException('Concrete structure id is Invalid.',code=409)

# def check_duplicate_products(order_list):
    # df = pd.DataFrame(order_list)
    # df.drop_duplicates(subset=['product_id','tax_id','delivery_mode','concrete_structure_id'], keep='last', inplace=True)
    # new_ol = df.to_dict("records")
    # print(new_ol,type(new_ol),len(new_ol),"new_ol")
    # print(order_list,type(order_list),len(order_list),"order_list after")
    # if len(new_ol) != len(order_list):
    #     raise DataValidationException('Duplicate rows of  product,tax,concrete structure,delivery mode combination is not allowed.',code=409)
def check_duplicate_products(order_list,test_fields,fields_name):
    df = pd.DataFrame(order_list)
    df.drop_duplicates(subset=test_fields,keep='last',inplace=True)
    # ['product_id','tax_id','delivery_mode','concrete_structure_id'], keep='last', inplace=True)
    new_ol = df.to_dict("records")
    print(new_ol,type(new_ol),len(new_ol),"new_ol")
    print(order_list,type(order_list),len(order_list),"order_list after")
    if len(new_ol) != len(order_list):
        # raise DataValidationException('Duplicate rows of  product,tax,concrete structure,delivery mode combination is not allowed.',code=409)
        raise DataValidationException('Duplicate rows of '+ fields_name + ' combination is not allowed.',code=409)
def is_valid_delivery_mode(delivery_mode):
    valid_delivery_modes = ['manual','pump','manual/pump','not applicable']
    if not delivery_mode in valid_delivery_modes:
        raise DataValidationException('Delivery_mode is Invalid.',code=409)

def verify_enquiry_detail(order_list):
    for i in range(len(order_list)):
        is_valid_product(order_list[i]['product_id'])
        is_valid_tax(order_list[i]['tax_id'])
        is_valid_concrete_structure(order_list[i]['concrete_structure_id'])
        is_valid_delivery_mode(order_list[i]['delivery_mode'])
        if 'id' in order_list[i].keys() and order_list[i]['id']:
            if not (entity_enquiry_detail.objects.filter(id=order_list[i]['id']).exists()):
                raise DataValidationException('Detail Id is Invalid.',code=409)
    check_duplicate_products(order_list)

def verify_numbering_detail(settings_list):
    for i in range(len(settings_list)):
        if ((type(settings_list[i]['starting_number']) is not int) or (type(settings_list[i]['number_of_digits'])is not int)):
                raise DataValidationException('starting_number and number_of_digits must be integer.',code=409)

# def verify_eo_detail(order_list,data):
    # valid_delivery_modes = ['manual','pump','manual/pump','not applicable']
    # # print(order_list,type(order_list),"order_list fn")
    # print(data,type(data),"data,type(data),")
    # for i in range(len(order_list)):
    #     if 'id' in order_list[i].keys() and order_list[i]['id']:
    #         if not (entity_order_detail.objects.filter(id=order_list[i]['id']).exists()):
    #             raise DataValidationException('Sales order Detail Id is Invalid.',code=409)
    #     if data['quotation_id']:
    #         print("with quotation")
            # Following lines of code are used to check whether the SO details are as same as quotation. This will be 
            # implemented in the future.
            # quotation = entity_enquiry_master.objects.get(id = data['quotation_id'])
            # a = entity_enquiry_detail.objects.filter(enquiry_master_id=quotation.id)
            # print(order_list[i]['product_id'],type(order_list[i]['product_id']),"order_list[i]['product_id']")
            # try:
            #     so_detail = entity_enquiry_detail.objects.get(enquiry_master_id=quotation.id,product__id=order_list[i]['product_id'],concrete_structure__id = order_list[i]['concrete_structure_id'],tax__id=order_list[i]['tax_id'],rate=order_list[i]['rate'],delivery_mode=order_list[i]['delivery_mode'])#__gte
            # except ObjectDoesNotExist:
            #     raise DataValidationException('For a salesorder connected with quotation,product  details must be as same as quotation except quantity.',code=409)
            # except entity_enquiry_detail.MultipleObjectsReturned as e:
            #     raise DataValidationException(str(e),code=409)
    #     else:
    #         is_valid_product(order_list[i]['product_id'])
    #         is_valid_tax(order_list[i]['tax_id'])
    #         is_valid_concrete_structure(order_list[i]['concrete_structure_id'])
    #         is_valid_delivery_mode(order_list[i]['delivery_mode'])
    # check_duplicate_products(order_list)
def verify_eo_detail(order_list,data):
    valid_delivery_modes = ['manual','pump','manual/pump','not applicable']
    # print(order_list,type(order_list),"order_list fn")
    print(data,type(data),"data,type(data),")
    for i in range(len(order_list)):
        if 'id' in order_list[i].keys() and order_list[i]['id']:
            if not (entity_order_detail.objects.filter(id=order_list[i]['id']).exists()):
                raise DataValidationException('Sales order Detail Id is Invalid.',code=409)
        if data['quotation_id']:
            print("with quotation")
            # Following lines of code are used to check whether the SO details are as same as quotation. This will be 
            # implemented in the future.
            # quotation = entity_enquiry_master.objects.get(id = data['quotation_id'])
            # a = entity_enquiry_detail.objects.filter(enquiry_master_id=quotation.id)
            # print(order_list[i]['product_id'],type(order_list[i]['product_id']),"order_list[i]['product_id']")
            # try:
            #     so_detail = entity_enquiry_detail.objects.get(enquiry_master_id=quotation.id,product__id=order_list[i]['product_id'],concrete_structure__id = order_list[i]['concrete_structure_id'],tax__id=order_list[i]['tax_id'],rate=order_list[i]['rate'],delivery_mode=order_list[i]['delivery_mode'])#__gte
            # except ObjectDoesNotExist:
            #     raise DataValidationException('For a salesorder connected with quotation,product  details must be as same as quotation except quantity.',code=409)
            # except entity_enquiry_detail.MultipleObjectsReturned as e:
            #     raise DataValidationException(str(e),code=409)
        else:
            is_valid_product(order_list[i]['product_id'])
            is_valid_tax(order_list[i]['tax_id'])
            is_valid_concrete_structure(order_list[i]['concrete_structure_id'])
            is_valid_delivery_mode(order_list[i]['delivery_mode'])
    test_fields = ['product_id','tax_id','delivery_mode','concrete_structure_id']
    check_duplicate_products(order_list,test_fields,"Product ,Tax, Delivery mode ,Concrete structure")

def is_grade_valid(product_id,grade_name): 
    if not (product_master.objects.filter(status = 1,id=product_id,category_detail__entity_name='FINISHED GOODS').exists()):
        raise DataValidationException(grade_name +' id is Invalid.' ,code=409)

def is_valid_qty(qty,name):
    if (qty < 0):
        raise DataValidationException(name + ' must be greater than zero.',code=409)


def is_valid_rate(rate):
    if not (rate > 0):
            raise DataValidationException('Rate must be greater than zero.')

def is_valid_quantity(quantity):
    if (quantity < 0):
        raise DataValidationException('Quantity must be greater than zero.',code=409)  
    
def validate_weight(data):
    if ((type(data['net_weight'])is not int) or (type(data['gross_weight'])is not int) or (type(data['tare_weight']) is not int)):
        raise DataValidationException('Data type of net_weight,gross_weight,tare_weight must be integer.',code=400) 
    if ((data['net_weight'] < 0) or (data['gross_weight'] < 0) or (data['tare_weight'] < 0)):
        raise DataValidationException('net_weight,gross_weight,tare_weight must be greater than or equal to zero.',code=409)
    net_weight = data['gross_weight']-data['tare_weight']
    if data['net_weight'] != net_weight:
        raise DataValidationException('Net weight must be equal to Gross weight-Tare weight.',code=409)

def verify_entity_master(data):
    print(data,"data verify_entity_master")
    is_company(data['company_id'])
    is_valid_plant(data['plant_id'])
    print(data["plant_id"])
    is_vendor(data['vendor_id'])
    print(data['vendor_id'])
    is_valid_qty(data['order_amount'],"Total Order Amount")
    is_valid_qty(data['pay_terms'],"Pay terms")

def is_vendor(vendor_id):
    if not entity_master.objects.filter(id=vendor_id,status=1,entity_type='supplier').exists():
        raise DataValidationException('Vendor id is Invalid',code =409)

def verify_entity_detail(order_list):
    for i in range(len(order_list)): 
        is_valid_tax(order_list[i]['tax_id'])
        is_valid_product(order_list[i]['product_id'])
    test_fields = ['product_id','tax_id','rate']
    check_duplicate_products(order_list,test_fields,"Product ,Tax, Rate")
        # is_valid_qty(order_list[i]['quantity'],"Order Quantity")
        # is_valid_qty(order_list[i]['rate'],"Rate")
        # quantity = order_list[i]['quantity']
        # rate = order_list[i]['rate']
        # amount = order_list[i]['amount']
        # is_valid_amount(amount,quantity,rate)
       
class PurchaseOrderMasterSerializer(serializers.ModelSerializer):
    is_tax_included  = serializers.BooleanField()
    status  = serializers.BooleanField()
    transport_mode = serializers.ChoiceField(choices = ['own','customer','own/customer'])
    order_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    validity_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    indent_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    quotation_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])

    class Meta:
        model = entity_order_master
        fields = "__all__" 
    
    def to_internal_value(self, data):
        #data['amount'] = data['amount']
        data['entity_company_id'] = data['company_id']
        data['entity_consignee_id'] = data['plant_id']
        data['entity_id'] = data['vendor_id']

        if data['order_amount'] == '':
            data['order_amount'] = 0
        
        if data['pay_terms'] == '':
            data['pay_terms'] = 0

        if data['validity_date'] == '':
            data['validity_date'] = datetime.strptime(data['order_date'], "%d-%m-%Y").date() + timedelta(days=30)
        
        today=date.today()
        indent_date = (datetime.strptime(data['indent_date'], "%d-%m-%Y").date())
        if indent_date > today:
            raise DataValidationException(data['indent_date'] + ' is Invalid.. Because, '+ data['indent_date'] +' must not be a future date.')
        
        quotation_date = (datetime.strptime(data['quotation_date'], "%d-%m-%Y").date())
        if quotation_date > today:
            raise DataValidationException(data['quotation_date'] + ' is Invalid.. Because, '+ data['quotation_date'] +' must not be a future date.')
        
        data['terms_condition'] = data['terms_and_condition']
        return super().to_internal_value(data)
        
    def validate(self,data):
        if self.instance:
            print("self.instance")
            data['order_no'] = self.instance.order_no
            data['order_date'] = self.instance.order_date
            data['order_time'] = self.instance.order_time
            data['prefix'] = self.instance.prefix
            # data['pay_terms']=self.instance.pay_terms
        else:
            print("validate else")
        return data

class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = entity_order_detail
        fields = "__all__"  

    def to_internal_value(self, data):
        if self.instance:
            print("during save")
        else:
            concrete_structure_entity = entity_master.objects.filter(
                    entity_name='NOT APPLICABLE', status=1, system_field=1, parent_id__entity_name='CONCRETE STRUCTURE'
                ).last()
            if concrete_structure_entity:
                    data['concrete_structure'] = concrete_structure_entity
            else:
                raise EntityNotFoundException("NOT APPLICABLE object is not present",code=404)
            data['delivery_mode']='not applicable'
        data['product'] = data['product_id']
        data['tax'] = data['tax_id']
        return super().to_internal_value(data)

    def validate(self,data):
        if not (data['rate'] > 0):
            raise DataValidationException('Rate must be greater than zero.')
        if not (data['quantity'] > 0):
            raise DataValidationException('Quantity must be greater than zero.')
        if not (data['amount'] == data['rate']*data['quantity']):
            raise DataValidationException('Amount is not valid. It should be (rate * quantity).')
        return data

class EquipmentMasterSerializer(serializers.ModelSerializer):
    is_tax_applicable = serializers.BooleanField()
    status = serializers.BooleanField()
    meter_status = serializers.BooleanField()
    entity_vendor_id = serializers.PrimaryKeyRelatedField(allow_empty=False,queryset=entity_master.objects.filter(entity_type='supplier',status=1))
    equip_name = serializers.CharField(validators=[UniqueValidator(queryset=equipment_master.objects.all(), lookup='iexact',message='Vehicle name already exist..')])
    class Meta:
        model = equipment_master
        fields = "__all__"

    def to_internal_value(self, data):
        data['entity_vendor_id'] = data['vendor_id']
        data['equip_grp_code'] = data['equip_type_id']
        data['equip_name'] = data['equip_name'].replace(" ", "")
        if data['insurance_date'] == '':
            data['insurance_date'] = None
        if data['permit_date'] == '':
            data['permit_date'] = None
        if data['fc_date'] == '':
            data['fc_date'] = None
        if data['is_tax_applicable'] == 0:
            data['insurance_date'] = None
            data['permit_date'] = None
            data['fc_date']  = None
        return super().to_internal_value(data) 

    def validate(self,data):
        valid_modes = ['hire','own']
        if not data['mode'] in valid_modes:
            raise DataValidationException('Mode is invalid. hire and own are only the valid modes.')
        valid_fuel_types = ['diesel','petrol']
        if not data['fuel_type'] in valid_fuel_types:
            raise DataValidationException('Fuel Type is invalid. diesel and petrol are only the valid fuel types.')
        equipments=entity_master.objects.filter(status = 1,entity_type = 'others',entity_name='EQUIPMENT',system_field=1).first()
        if equipments:
            if not (entity_master.objects.filter(status = 1,id=data['equip_grp_code'].id,parent_id=equipments.id,system_field=1).exists()):#,entity_type = 'others'
                raise DataValidationException('Equipment Type is invalid')
        else:
            raise serializers.ValidationError('Equipment Type is invalid') 
        if  ((data['equip_grp_code'].entity_name == 'TRANSIT MIXER') and  (data['is_tax_applicable'] == 0)):
            raise DataValidationException('If Equipment Type is TRANSIT MIXER , then is_tax_applicable must be true.')
        if data['is_tax_applicable'] == 1:
            # print("yes tax applicable") 
            if not(data['insurance_date'] and  data['permit_date'] and data['fc_date']):
                raise DataValidationException('If Tax is applicable , then Permit date ,FC date and Insurance date are required.')
        return data   
    
class GMRMasterSerializer(serializers.ModelSerializer):   
    # weighment_slip_date=serializers.DateField(required=False,format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    sl_dt = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    dc_dt= serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    # lr_dt=serializers.DateField(required=False,format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
   
    class Meta:
        model = gmr_master
        fields = "__all__" 

    def to_internal_value(self, data):
        data['sl_no']=data['goods_receipt_note_no']
        data['sl_dt']=data['goods_receipt_note_date']
        data['sl_time']=data['goods_receipt_note_time']
        data['plant']=data['plant_id']
        data['sl_time']=data['goods_receipt_note_time']
        data['vehicle_own']=data['vehicle_id']
        if data['lr_dt'] == '':
            data['lr_dt'] = None
        else:
            print(data['lr_dt'],type(data['lr_dt']))
            #lr_dt is converted to yyyy-MM-dd format
            data['lr_dt'] =(datetime.strptime(data['lr_dt'], "%d-%m-%Y").date()).strftime("%Y-%m-%d")
        if data['weighment_slip_date'] == '':
            data['weighment_slip_date'] = date.today()
        else:
            print(data['weighment_slip_date'],type(data['weighment_slip_date']))
            #weighment slip date is converted to yyyy-MM-dd format
            data['weighment_slip_date'] =(datetime.strptime(data['weighment_slip_date'], "%d-%m-%Y").date()).strftime("%Y-%m-%d")
        
        return super().to_internal_value(data)
    
    def validate(self,data):
        if self.instance:
            print("self.instance")
            data['goods_receipt_note_no']=self.instance.sl_no
            data['goods_receipt_note_date'] = self.instance.sl_dt
            data['plant_id'] = self.instance.plant
            data['prefix'] = self.instance.prefix
        
        today=date.today()
        print(data['dc_dt'],type(data['dc_dt']),"data['dc_dt']")
        if data['dc_dt']>today:
            raise DataValidationException('DC date is Invalid.. Because, DC date must not be a future date.',code=409)

        if 'weighment_slip_date' in data.keys() and data['weighment_slip_date'] == '':
            data['weighment_slip_date'] = date.today().strftime('%d-%m-%Y')
        print(data['weighment_slip_date'],'slip date serializerrr')
        if data['weighment_slip_date']>today:
            raise DataValidationException('weighment_slip_date is Invalid.. Because, it must not be a future date.',code=409)
        return data

def verify_gmr_master(data):
        print(data,"data verify gmr master")
        detail_list = data['detail_list']
        print(detail_list,'detail_list')
        for detail in detail_list:
            d=detail['po_detail_id']
            po_detail = entity_order_detail.objects.get(id=d)
            print('detail serializer',po_detail)
            master = po_detail.entity_order_id
            print(master.transport_mode,'master.transport_mode')
            print('master serializer',master)

        master_transport_mode = master.transport_mode
        supplier=master.entity_id

        if master_transport_mode == 'own':
            if data['transport_mode'] != 'own':
                raise DataValidationException("Transport mode must be 'own' .Because related po has 'own' transport mode",code=409)
        elif master_transport_mode == 'customer':
            if data['transport_mode'] != 'customer':
                raise DataValidationException("Transport mode must be 'vendor'.Because related po has  'vendor' transport mode",code=409)
        elif master_transport_mode =='own/customer':
            if data['transport_mode'] not in ['own', 'customer']:
                raise DataValidationException("Invalid transport mode it should be either own or customer",code=409)
        
        grn_dt=(datetime.strptime(data['goods_receipt_note_date'], "%d-%m-%Y"))
        
        # To validate vehicle 
        if data['transport_mode']=='own':
            own=data['vehicle_id']
            if not(data['vehicle_others']==''):
                raise DataValidationException("vehicle_others should be empty if transport mode is own.",code=409)
            elif own=='':
                raise DataValidationException("vehicle id should not be empty if transport mode is own.",code=409)
            else:
                transit_mixer=entity_master.objects.get(entity_name='TRANSIT MIXER')
                vehicle=equipment_master.objects.filter(equip_grp_code=transit_mixer,id=own,is_equip_ready=1,status=1,fc_date__gte=grn_dt,permit_date__gte=grn_dt,insurance_date__gte=grn_dt)
                if not(vehicle).exists():
                    raise DataValidationException("vehicle_id is invalid.")
        if data['transport_mode']=='customer':
            if not(data['vehicle_id']== ''):
                raise DataValidationException("vehicle_id should be empty if transport mode is customer.")
            elif data['vehicle_others']=='':
                raise DataValidationException('vehicle_others should not be empty if transport_mode is customer.')

        # validate driver_mobile_no
        if data['driver_mobile_no']:
            if type(data['driver_mobile_no']) is not str:
                raise DataValidationException('Data type of driver_mobile_no must be string.',code=409)
            data['driver_mobile_no'] = is_mobile_no(data['driver_mobile_no'])
        
        if grn_dt.month < 4:
            print("if")
            financial_year_start=grn_dt.replace(day = 1, month=4 ,year=((grn_dt.year)-1))
            financial_year_end = datetime(grn_dt.year, 3, 31)
        else:
            print("else")
            financial_year_start=grn_dt.replace(day = 1, month=4)
            financial_year_end = datetime(grn_dt.year + 1, 3, 31)
        print(financial_year_start,"financial_year_start",grn_dt,"data['sl_dt']")
        print(financial_year_end,"financial_year_end")
        gmr=list(gmr_master.objects.filter(sl_dt__gte=financial_year_start,sl_dt__lte=financial_year_end,customer_vendor=supplier,status=1,movement_type='grn').values_list('dc_no',flat=True))
        print(gmr,'gmr for dc_no')
        if (data['dc_no'] == ''):
            raise DataValidationException(' Dc no  is required',code = 409)
        else:
            if gmr and data['dc_no'] in gmr:
                raise DataValidationException('This Dc_no  already exist for this year,vendor.',code = 409)
        if data['in_time'] == '':
            raise DataValidationException(' In time  is required',code = 409)
        if data['out_time'] == '':
            raise DataValidationException(' Out time  is required',code = 409)

            
class GMRDetailSerializer(serializers.ModelSerializer):   
    class Meta:
        model = gmr_detail
        fields = "__all__" 

    def to_internal_value(self, data):
            data['order_detail']=data['po_detail_id']
            return super().to_internal_value(data)    

    def validate(self,data):
        d=data['order_detail'].id
        detail_id = entity_order_detail.objects.get(id=d)
        print('detail serializer',detail_id)
        master = detail_id.entity_order_id
        print('master serializer',master)
        qty=detail_id.quantity
        print(qty,'quantity')
        accepted_qty=gmr_detail.objects.filter(order_detail=detail_id,gmr__status=1).aggregate(total_accepted_qty=Sum('accepted_qty'))['total_accepted_qty']
        print(accepted_qty,'goods accepted qty')
        if accepted_qty is not None:
            balance_qty=qty-accepted_qty
        else:
            balance_qty=qty
        print(balance_qty,'balance_qunatity')
        data['order_detail']=detail_id

        if (data['gross_weight']<0 or data['tare_weight']<0):
            raise DataValidationException('gross_weight and tare_weight should not be less the zero ',code=409)
        
        if ((data['gross_weight']>0 and data['tare_weight']==0) or (data['gross_weight']==0 and data['tare_weight']>0)):
            raise DataValidationException('if gross or tare wt is greater than 0,then other must be greater than 0',code=409)

        if not (data['net_weight']==data['gross_weight']-data['tare_weight'] ):
            raise DataValidationException('net_weight is not valid. It should be (gross_weight-tare_weight).',code=409)
    
        if data['dc_qty']<0 or data['dc_qty'] == 0 :
            raise DataValidationException('dc_qty should be greater than zero',code=409)
        
        if not (data['received_qty']==data['net_weight']-data['deduction_qty']):
            raise DataValidationException('Received_qty is not valid. It should be (net_weight-deduction_qty).',code=409)
        
        if data['accepted_qty']==None or data['accepted_qty']== '':
            data['accepted_qty']=data['received_qty']
        
        if data['accepted_qty'] == 0 or data['accepted_qty'] < 0:
            raise DataValidationException('accepted_qty should  be greater than zero.',code=409)

        if data['accepted_qty']>balance_qty:
            raise DataValidationException('accepted_qty should not be greater than balance_qty',code=409)
        return data











   




# from rest_framework import serializers
# from rms_ins.models import *
# from django.contrib.auth.models import Group,Permission,User
# from rest_framework import status
# import re
# from rest_framework.validators import * #UniqueValidator
# from rms_ins.exceptions import DataValidationException
# from datetime import date,datetime,timedelta
# from django.core.exceptions import ObjectDoesNotExist
# import pandas as pd

# def is_user_allowed_plant(request,plant_id):
#     if not (request.user.is_superuser):
#         allowed_plant_list = list(request.user.profiles_master.plant.values_list('id',flat=True))
#         if not (int(plant_id) in allowed_plant_list):
#             raise DataValidationException(detail = "You don't have permission for this plant.", code=403)

# def is_mobile_no(value):
#     mobile_regex="^(0|91)?[6-9][0-9]{9}$"
#     if not re.match(mobile_regex,value):
#         raise DataValidationException(detail=f'Mobile number {value} is Invalid.')
#     return value

# def is_phone_no(value):
#     # phone_regex = "^\+?[0-9]+(\s|\-)?\(?\d{2,6}\)?(\s|\-)?[0-9]+(\s|\-)?[0-9]+$"
#     phone_regex = r"^\+?[0-9]+(\s|\-)?\(?\d{2,6}\)?(\s|\-)?[0-9]+(\s|\-)?[0-9]+$"
# # mail_regex = r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$"

#     if ',' in  value:
#         value_list = value.split(",")
#         for i in value_list:
#             if not re.match(phone_regex,i):
#                 raise DataValidationException(detail=f'Phone number {i} is Invalid.')
#     else:
#         if not re.match(phone_regex,value):
#             raise DataValidationException(detail=f'Phone number {value} is Invalid.')
#     return value

# def is_company(company_id):
#     # To validate company id
#     if not (entity_master.objects.filter(status = 1,entity_type = 'company',id=company_id).exists()):
#         raise DataValidationException("Company Id is invalid",code=409)

# def is_customer(customer_id):
#     # To validate customer id
#     if not (entity_master.objects.filter(status = 1,entity_type = 'customer',id=customer_id).exists()):
#         raise DataValidationException("Customer Id is invalid",code=409)

# def is_quotation(quotation_id):
#     # To validate quotation id
#     if not (entity_enquiry_master.objects.filter(status = 1,id=quotation_id).exists()):
#         raise DataValidationException("Quotation Id is invalid",code=409)

# def is_consignee(consignee_id):
#     # To validate consignee(site) id
#     if not (entity_master.objects.filter(id=consignee_id,status = 1,entity_type='consignee').exists()):
#         raise DataValidationException('Consignee id is Invalid.',code=409)

# def is_pincode(value):
#     pincode_regex="^[1-9][0-9]{5}$"
#     if not re.match(pincode_regex,value):
#         raise DataValidationException(detail=f'Pincode {value} is Invalid.')
#     return value

# def is_pan_no(value):
#     pan_no_regex ="^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
#     # Convert the input value to uppercase
#     value = value.upper()
#     if not re.match(pan_no_regex,value):
#         raise DataValidationException(detail=f'PAN No {value} is Invalid.')
#     return value

# def is_gst_no(value):
#     gst_no_regex = "^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
#     # Convert the input value to uppercase
#     value = value.upper()
#     if not re.match(gst_no_regex,value):
#         raise DataValidationException(detail=f'GST No {value} is Invalid.')
#     return value

# def is_mail_valid(value):
#     # mail_regex = "^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$"
#     mail_regex = r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$"

#     #"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
#     if not re.match(mail_regex,value):
#         raise DataValidationException(detail=f'Email address {value} is Invalid.')
#     return value

# def is_valid_plant(plant_id):
#     if not (entity_master.objects.filter(status = 1,entity_type = 'plant',id=plant_id).exists()):
#         raise DataValidationException('Plant id is Invalid.',code=409)

# class EntityMasterSerializer(serializers.ModelSerializer):
#     status=serializers.BooleanField()
#     class Meta:
#         model = entity_master
#         fields = "__all__"

#     def to_internal_value(self, data):
#         ## this is done to change the status field value from boolean to integer if and if not 'status'
#         # is present in data
#         if 'status' in data.keys():
#             # data['status'] = bool(data['status'])
#             if data['status'] == True:
#                 data['status'] = 1
#             elif data['status'] == False:
#                 data['status'] =  0
#         else:
#             data['status'] = 1
#         if 'name' in data.keys():
#             data['entity_name'] = data['name']
#         return super().to_internal_value(data)

#     def validate(self, data):
#         form_name=getattr(self.context['view'], "for_tracking", {})['content_type']
#         # print(self,"self entity_master")
#         # print(getattr(self.context['view'], "for_tracking", {})['content_type'])
#         valid_entity_types=getattr(self.context['view'], "valid_entity_types", [])
#         method = self.context['request'].method
#         if  ((method == 'POST') and (form_name != 'PLANT FORM') and (form_name != 'CONSIGNEE REGISTRATION FORM')):
#             is_exists=entity_master.objects.filter(entity_name__iexact=data['entity_name'],entity_type__in=valid_entity_types).exists()
#             if is_exists:
#                 raise DataValidationException(detail=f'Name [{data["entity_name"]}] already exists. Please choose a different name.')
#         elif ((method == 'PUT') and (form_name != 'PLANT FORM') and (form_name != 'CONSIGNEE REGISTRATION FORM')):
#             is_exists=entity_master.objects.filter(entity_name__iexact=data['entity_name'],entity_type__in=valid_entity_types).exclude(id=self.instance.id).exists()
#             if is_exists:
#                 raise DataValidationException(detail=f'Name [{data["entity_name"]}] already exists. Please choose a different name.')
        
#         if 'contact_mobile_no' in data.keys():
#             if data['contact_mobile_no'] :
#                 data['contact_mobile_no'] = is_mobile_no(data['contact_mobile_no'])
#         if ('mobile_number' in data.keys()):
#             if data['mobile_number']:
#                 data['mobile_number'] = is_mobile_no(data['mobile_number'])
#         if 'phone_number' in data.keys():
#             if data['phone_number']:
#                 data['phone_number'] = is_phone_no(data['phone_number'])
#         if 'pincode' in data.keys():
#             if data['pincode']:
#                 data['pincode']=is_pincode(data['pincode'])
#         if 'pan_no' in data.keys():
#             if data['pan_no']:
#                 data['pan_no']=is_pan_no(data['pan_no'])
#             elif ((form_name == 'COMPANY FORM') or (form_name == 'PLANT FORM')):
#                 raise DataValidationException(detail='PAN No is required')
#         if 'gst_no' in data.keys():
#             if data['gst_no']:
#                 data['gst_no']=is_gst_no(data['gst_no'])
#             elif ((form_name == 'COMPANY FORM') or (form_name == 'PLANT FORM')):
#                 raise DataValidationException(detail='GST No is required')
        
#         if form_name == 'ACCOUNTS GROUPING':
#             # if data['entity_type'] in valid_entity_types:
#             #     # print((data['entity_type']))
#             #     if data['parent_id']:
#             #         # print(data['parent_id'])
#             #         nature_of_group=data['parent_id'].entity_type
#             #         if nature_of_group in valid_entity_types:
#             #             if not data['entity_type'] == nature_of_group:
#             #                 raise DataValidationException(detail=f'The entity type must be {nature_of_group}')
#             #         else:
#             #             raise DataValidationException(detail="Entity type is invalid.")
#             # else:
#             #     raise DataValidationException(detail="Entity type is invalid")
#             if data['parent_id']:
#                 data['entity_type'] = None
#             else:
#                 if not data['entity_type'] in valid_entity_types:
#                     raise DataValidationException(detail="Entity type is invalid")
#         return data
        

# class UserTrackingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = user_tracking
#         fields = "__all__" 


# def validate_image_size(value):
#     """
#     Validate that the uploaded image size is less than or equal to 100 KB.
#     """
#     max_size_kb = 100  # Maximum size in kilobytes

#     if value.size > max_size_kb * 1024:  # Convert max_size_kb to bytes
#         raise DataValidationException(f"Image size must be at most {max_size_kb} KB.",code=409)

# class EntityCompanyDetailSerializer(serializers.ModelSerializer):
#     is_batching_report_needed =  serializers.BooleanField()
#     seal = serializers.ImageField(validators=[validate_image_size], required=False)
#     logo = serializers.ImageField(validators=[validate_image_size], required=False)
#     class Meta:
#         model = entity_company_detail
#         fields = "__all__"
    
#     def validate(self,data):
#         if not ((data['closing_dt']) >= (data['opening_dt'])):
#             raise DataValidationException(detail='Closing date must be greater than or equal to opening date.')
#         return data


# class PermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Permission
#         fields = '__all__'   

# class TagListingField(serializers.RelatedField):
#     def to_representation(self, value):
#         return value.codename

# class GroupSerializer(serializers.ModelSerializer):
#     # permissions = PermissionSerializer(read_only=True, many=True)
#     # permissions = serializers.StringRelatedField(many=True)
#     permissions=TagListingField(many=True, read_only=True)
#     name = serializers.CharField()
#     class Meta:
#         model = Group
#         fields = ('id','name','permissions')

#     def validate(self,data):
#         method = self.context['request'].method
#         if len(data['name']) > 100:
#             raise DataValidationException('Group name cannot exceed 100 characters')
#         if method == 'POST':
#             is_exists=Group.objects.filter(name__iexact=data['name']).exists()
#         elif method == 'PUT':
#             # id= self.initial_data['id']
#             is_exists=Group.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
#         if is_exists:
#             raise DataValidationException(detail=f'Category name {data["name"]}  already exist.')
#         return data

# class UserSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all(), lookup='iexact',message='Username already exist..')])
#     email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all(), lookup='iexact')])
#     groups = serializers.PrimaryKeyRelatedField(many=True,allow_empty=True,queryset=Group.objects.all())
#     # groups = serializers.PrimaryKeyRelatedField(many=True,allow_empty=False,queryset=Group.objects.all())
#     class Meta:
#         model = User
#         fields = '__all__'
#     def create(self, validated_data):
#         groups = validated_data.pop('groups')
#         user = User.objects.create_user(**validated_data)
#         user.groups.set(groups)
#         return user  
#     def update(self, model_instance, validated_data):
#         groups = validated_data.pop('groups')
#         # we have to upate password separately from other data
#         # so pop the password if it is available 
#         hashed_password=model_instance.password
#         password = validated_data.pop('password', None)
#         # update all other fields in the model
#         user = super().update(model_instance, validated_data)
#         if ((password) and (password == hashed_password)):
#             print("do nothing")
#         else: 
#             user.set_password(password)
#             user.save()
#         user.groups.set(groups)
#         return user  

# class ProfilesMasterSerializer(serializers.ModelSerializer):
#     is_mfa_needed = serializers.BooleanField()
#     is_location_auth_needed = serializers.BooleanField()
#     plant = serializers.PrimaryKeyRelatedField(many=True,allow_empty=False,queryset=entity_master.objects.filter(entity_type='plant',status=1))
#     class Meta:
#         model = profiles_master
#         fields = '__all__'

#     def to_internal_value(self, data):
#         data['plant'] = data['plants']
#         return super().to_internal_value(data) 

#     def validate(self,data):
#         if not ((data['user_valid_upto']) >= (data['user_valid_from'])):
#             raise DataValidationException(detail='Valid upto date must be greater than or equal to valid from date.')
#         if data['user_mobile_no'] :
#             data['user_mobile_no'] = is_mobile_no(data['user_mobile_no'])
#         return data

# class ProfilesMasterValidationSerializer(serializers.ModelSerializer):
#     # This serializer is for validating profile master table details without user object (before creating user object)
#     is_mfa_needed = serializers.BooleanField()
#     is_location_auth_needed = serializers.BooleanField()
#     plant = serializers.PrimaryKeyRelatedField(many=True,allow_empty=False,queryset=entity_master.objects.filter(entity_type='plant',status=1))
#     class Meta:
#         model = profiles_master
#         fields = ['user_mobile_no','user_valid_from','user_valid_upto','user_remarks','is_mfa_needed','is_location_auth_needed',
#                     'plant']

#     def to_internal_value(self, data):
#         data['plant'] = data['plants']
#         return super().to_internal_value(data) 

#     def validate(self,data):
#         if not ((data['user_valid_upto']) >= (data['user_valid_from'])):
#             raise DataValidationException(detail='Valid upto date must be greater than or equal to valid from date.')
#         if data['user_mobile_no'] :
#             data['user_mobile_no'] = is_mobile_no(data['user_mobile_no'])
#         return data

# class EntityPlantDetailSerializer(serializers.ModelSerializer):
#     plant_seal = serializers.ImageField(validators=[validate_image_size], required=False)
#     plant_logo = serializers.ImageField(validators=[validate_image_size], required=False)
#     plant_br_logo = serializers.ImageField(validators=[validate_image_size], required=False)
#     class Meta:
#         model = entity_plant_detail
#         fields = "__all__"   

#     def validate(self,data):
#         if not (entity_master.objects.filter(status = 1,entity_type = 'company',id=data['entity_company_id'].id).exists()):
#             raise serializers.ValidationError({'entity_company_id':'Invalid..'},code=409)
#         if not ((data['account_closing_dt']) >= (data['account_opening_dt'])):
#             raise serializers.ValidationError({'closing_dt':
#             'closing_dt must be greater than or equal to opening_dt...'},code=409)
#         if self.instance:
#             is_exists=entity_plant_detail.objects.filter(plant_alias__iexact=data['plant_alias']).exclude(id=self.instance.id).exists()
#         else:
#             is_exists=entity_plant_detail.objects.filter(plant_alias__iexact=data['plant_alias']).exists()
#         if is_exists:
#             raise DataValidationException(detail=f'Plant alias [{data["plant_alias"]}] already exist.')
#         return data    


# class EntityVendorDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = entity_vendor_detail
#         fields = "__all__"  
    
#     def to_internal_value(self, data):
#         data['vendor_type'] = data['vendor_type_id']
#         return super().to_internal_value(data)

#     def validate(self,data):
#         products=entity_master.objects.filter(status = 1,entity_type = 'others',entity_name='PRODUCT',system_field=1).first()
#         if products:
#             if not (entity_master.objects.filter(status = 1,id=data['vendor_type'].id,parent_id=products.id,system_field=1).exists()):#,entity_type = 'others'
#                 raise DataValidationException('Vendor Type is invalid')
#         else:
#             raise DataValidationException('Vendor Type is invalid')  
#         return data   

# class UomMasterSerializer(serializers.ModelSerializer):
#     status = serializers.BooleanField()#validators=[is_status])
#     class Meta:
#         model = uom_master
#         fields = "__all__"
    
#     def validate(self, data):
#         method = self.context['request'].method
#         if method == 'POST':
#             is_exists=uom_master.objects.filter(name__iexact=data['name']).exists()
#         elif method == 'PUT':
#             is_exists=uom_master.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
#         if is_exists:
#             raise DataValidationException(f'Unit Name [{data["name"]}]already exists')
#         return data

# class UomListSerializer(serializers.ModelSerializer):
#     status = serializers.BooleanField()
#     system_field = serializers.BooleanField()
#     class Meta:
#         model = uom_master
#         fields = ['id','name','symbol','user_remarks','status','system_field']

# class TaxformMasterSerializer(serializers.ModelSerializer):
#     status =  serializers.BooleanField()#validators=[is_status])
#     class Meta:
#         model = taxform_master
#         fields = "__all__"
    
#     def validate(self,data):
#         method = self.context['request'].method
#         if method == 'POST':
#             is_exists=taxform_master.objects.filter(name__iexact=data['name']).exists()
#         elif method == 'PUT':
#             is_exists=taxform_master.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
#         if is_exists:
#             raise DataValidationException(f'Tax Name [{data["name"]}]already exists')
#         if ((data['tax_type'] != 'gst') and (data['tax_value2'] > 0)):
#             raise DataValidationException(detail='Tax-Value2 cannot be greater than 0 ,if type is not GST')
#         if not ((data['valid_upto']) >= (data['valid_from'])):
#             raise DataValidationException(detail='Valid upto date must be greater than or equal to Valid from date.')
#         return data

# class TaxformMasterListSerializer(serializers.ModelSerializer):
#     status = serializers.BooleanField()
#     class Meta:
#         model = taxform_master
#         fields = ['id','name','tax_value1','tax_value2','tax_type','valid_from','valid_upto','user_remarks','status','system_field']

# class ProductMasterSerializer(serializers.ModelSerializer):
#     status =  serializers.BooleanField()#validators=[is_status])
#     is_gst_applicable =  serializers.BooleanField()
#     is_batch_report_connected =  serializers.BooleanField()
#     prod_gst_type = serializers.ChoiceField(choices = ['Goods','Services'],allow_blank=False)
#     class Meta:
#         model = product_master
#         fields = "__all__"
    
#     def to_internal_value(self, data):
#         data['category_detail'] = data['category_id']
#         data['tax'] = data['tax_id']
#         data['unit'] = data['unit_id']
#         return super().to_internal_value(data)

#     def validate(self,data):
#         method = self.context['request'].method
#         if method == 'POST':
#             is_exists=product_master.objects.filter(name__iexact=data['name']).exists()
#         elif method == 'PUT':
#             is_exists=product_master.objects.filter(name__iexact=data['name']).exclude(id=self.instance.id).exists()
#         if is_exists:
#             raise DataValidationException(f'Product Name [{data["name"]}]already exists')
       
#         if data['is_gst_applicable'] == True:
#             if not (taxform_master.objects.filter(status = 1,id=data['tax'].id).exists()):
#                 raise DataValidationException(detail='Tax is invalid')
#         else:
#             if not (taxform_master.objects.filter(status = 1,system_field=1,name='NO TAX',tax_type='gst',id=data['tax'].id).exists()):
#                 raise DataValidationException(detail='Tax is invalid')
#         if not (uom_master.objects.filter(status = 1,id=data['unit'].id).exists()):
#             raise DataValidationException(detail='Unit is invalid')
#         products=entity_master.objects.filter(status = 1,entity_type = 'others',entity_name='PRODUCT',system_field=1).first()
#         if products:
#             if not (entity_master.objects.filter(status = 1,id=data['category_detail'].id,parent_id=products.id,system_field=1).exists()):#,entity_type = 'others'
#                 raise DataValidationException(detail='Category Detail is invalid')
#         else:
#             raise DataValidationException(detail='Category Detail is invalid')
#         return data

# class NumberingsMasterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = numberings_master
#         fields = "__all__"

#     def to_internal_value(self, data):
#         if data['plant_id'] == -1:
#             data['plant_id'] = ""
#         data['entity_plant_id'] = data['plant_id']
#         return super().to_internal_value(data)     
    
#     def validate(self,data):
#         if self.instance:
#             print("do nothing")
#         else:
#             valid_voucher_types = ['quotation','sales_order','delivery_challan','invoice','receipt_voucher','credit_note','purchase_order','goods_reciept_note','cube_test_report']
#             if data['voucher_type'] in valid_voucher_types:
#                 # print("data['voucher_type'] valid")
#                 test=numberings_master.objects.filter(voucher_type= data['voucher_type']).values('entity_plant_id')
#                 # print(test,"test")
#                 if data['entity_plant_id']:
#                     # print("plant id is not all")
#                     is_exists= entity_master.objects.filter(entity_type='plant',status=1,id=data['entity_plant_id'].id).exists()
#                     if is_exists:
#                         # print("data['entity_plant_id'] is valid")
#                         is_user_allowed_plant(self.context['request'],data['entity_plant_id'].id)
#                         if ((data['voucher_type'] == 'sales_order') or (data['voucher_type'] == 'purchase_order') or (data['voucher_type'] == 'quotation')):
#                             raise DataValidationException('For voucher types(Quotation, SalesOrder & PurchaseOrder), individual Plant cannot be selected.')    
#                         else:
#                             if test:
#                                 for i in test:
#                                     c=i.get('entity_plant_id',None)
#                                     # print(c,"c")
#                                     if c == None:
#                                         raise DataValidationException('For this voucher type, Number Setting is configured for all Plants. Cannot be set for individual Plant.')
#                                     else:
#                                         check= numberings_master.objects.filter(voucher_type= data['voucher_type'],entity_plant_id=data['entity_plant_id'].id).exists()
#                                         if check:
#                                             raise DataValidationException('For this voucher type and Plant, Number Setting already exists.')
#                                         else:
#                                             # print("can create...")
#                                             return data
#                             else:
#                                 print("can create")
#                     else:
#                         raise DataValidationException('Plant Id is invalid.')    
#                 else:
#                     # print("data['entity_plant_id']  is all")
#                     if test:
#                         for i in test:
#                             c=i.get('entity_plant_id',None)
#                             # print(c,"c")
#                             if c == None:
#                                 raise DataValidationException('For this voucher type, Number Setting is already configured for all Plants.')# Cannot be set for individual Plant.
#                             else:
#                                 raise DataValidationException('For this voucher type and plant, Number Setting already exists. You cannot create for all Plants.')
#                     else:
#                         print("can create")
#             else:
#                 raise DataValidationException('Voucher Type is invalid.',code=409)
#         return data

# class NumberingsDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = numberings_detail
#         fields = "__all__"

#     def validate(self,data):
#         if not ((data['valid_upto_date']) >= (data['valid_from_date'])):
#             raise DataValidationException('Valid upto date must be greater than or equal to valid from date.')
#         return data


# class ApprovalSettingsMasterSerializer(serializers.ModelSerializer):
#     entity_company_id = serializers.PrimaryKeyRelatedField(queryset=entity_master.objects.filter(entity_type='company',status=1))
#     voucher_type = serializers.ChoiceField(choices = ['sales_order','purchase_order'],allow_blank=False)
#     is_appr_needed = serializers.BooleanField()
#     is_so_wait_on_save = serializers.BooleanField()
#     is_mail_needed = serializers.BooleanField()
#     mail_ids = serializers.ListField(child = serializers.CharField(),allow_empty=True,allow_null=True)
#     conditions_for_so_waiting = serializers.MultipleChoiceField(choices = ['advance_amount','credit_limit'],allow_blank=True,allow_null=True)
#     class Meta:
#         model = approval_setting_master
#         fields = "__all__"
#         validators = [UniqueTogetherValidator(queryset=approval_setting_master.objects.all(),
#                 fields=['entity_company_id', 'voucher_type'])] # to block duplicate entry

#     def to_internal_value(self, data):
#         data['entity_company_id'] = data['company_id']
#         if self.instance:
#             data['voucher_type']=self.instance.voucher_type
#             data['entity_company_id']=self.instance.entity_company_id
#         if data['is_mail_needed'] == 0:
#             data['mail_ids'] = None
#         if (((data['voucher_type'] == 'sales_order') and (data['is_appr_needed'] == 0)) or (data['voucher_type'] == 'purchase_order')):
#             data['is_so_wait_on_save'] = 0
#             data['conditions_for_so_waiting'] = None
#         return super().to_internal_value(data)

#     def validate(self,data):
#         # valid_voucher_types = ['sales_order','purchase_order']
#         # if not data['voucher_type'] in valid_voucher_types:
#         #     raise serializers.ValidationError({'voucher_type':'sales_order and purchase_order are the only valid voucher types...'},code=409)
        
#         if data['is_mail_needed'] == 1:
#             print("mail needed")
#             if (len(data['mail_ids']) == 0):
#                 raise DataValidationException('Mail ids cannot not be empty if Mail is required.')
#             else:
#                 for i in data['mail_ids']:
#                     i = is_mail_valid(i)
#                 data['mail_ids'] = ','.join(map(str,data['mail_ids']))
        
#         if ((data['voucher_type'] == 'sales_order') and (data['is_appr_needed'] == 1)):
#             if ((data['is_so_wait_on_save'] == 1) and (len(data['conditions_for_so_waiting'])>0)):
#                 raise DataValidationException('Invalid input because for sales order , if is_appr_needed is true ,then is_so_wait_on_save may be true or valid conditions_for_so_waiting.')
#             if not((data['is_so_wait_on_save'] == 1) or (len(data['conditions_for_so_waiting'])>0)):
#                 raise DataValidationException('Invalid input because for sales order , if is_appr_needed is true ,then is_so_wait_on_save must be true or valid conditions_for_so_waiting.')
#             data['conditions_for_so_waiting'] = ','.join(map(str,data['conditions_for_so_waiting']))
#         return data


# class EntityOrderMasterSerializer(serializers.ModelSerializer):
#     is_tax_included  = serializers.BooleanField()
#     status  = serializers.BooleanField()
#     is_advance_payment  = serializers.BooleanField()
#     transport_mode = serializers.ChoiceField(choices = ['own','customer','own/customer'])
#     order_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
#     validity_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y',])
    
#     class Meta:
#         model = entity_order_master
#         fields = "__all__" 
    
#     def to_internal_value(self, data):
#         print(data,"data eom iv")
#         data['entity_company_id'] = data['company_id']
#         data['entity_consignee_id'] = data['consignee_id']
#         data['enquiry_id'] = data['quotation_id']
#         data['receipt'] = data['receipt_id']
#         if data['order_amount'] == '':
#             data['order_amount'] = 0
#         if data['validity_date'] == '':
#             data['validity_date'] = datetime.strptime(data['order_date'], "%d-%m-%Y").date() + timedelta(days=30)
#         return super().to_internal_value(data)

#     def validate(self,data):
#         print(data,"data eomaster")
#         if not (float(data['order_amount']) > 0):
#             raise DataValidationException('Total Sales order amount must be greater than zero.')
#         if self.instance:
#             print("self.instance")
#             data['order_no'] = self.instance.order_no
#             data['order_date'] = self.instance.order_date
#             data['order_time'] = self.instance.order_time
#             data['prefix'] = self.instance.prefix
#         else:
#             print("validate else")
#         if data['is_advance_payment']:
#             print("advance true")
#             if data['receipt']:
#                 print("receipt")
#                 if not (receipt_master.objects.filter(status = 1,id=data['receipt'].id,receipt_against='advance').exists()):
#                     raise DataValidationException("Receipt Id is invalid.",code=409)
#             else:
#                 raise DataValidationException("Receipt Id is required If advance payment is true.",code=409)
#         else:
#             print("advance false")
#             data['receipt'] = None
#         return data

# def verify_eo_master(data):
#     print(data,"data verify_eo_master")
#     if data['quotation_id']:
#         print("data verify_eo_master if ")
#         is_quotation(data['quotation_id'])
#         quotation = entity_enquiry_master.objects.get(id = data['quotation_id'])
#         print(data['company_id'],type(data['company_id']),"data['company_id']")
#         print(quotation,"quotation verify_eo_master",quotation.entity_company_id.id,type(quotation.entity_company_id.id))
#         if not (int(data['company_id']) == quotation.entity_company_id.id):
#             raise DataValidationException("Company Id is invalid..Because this company is not included in this Quotation.",code=409)
#         if not (int(data['consignee_id']) == quotation.entity_consignee_id.id):
#             raise DataValidationException('Site id is Invalid.Because this site is not included in this Quotation.',code=409)
#     else:
#         is_company(data['company_id'])
#         is_consignee(data['consignee_id'])


# class EntityOrderDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = entity_order_detail
#         fields = "__all__"  

#     def to_internal_value(self, data):
#         if self.instance:
#             print("during save")
#         else:
#             data['balance_qty'] = data['quantity']
#         data['product'] = data['product_id']
#         data['tax'] = data['tax_id']
#         data['concrete_structure'] = data['concrete_structure_id']
#         return super().to_internal_value(data)

#     def validate(self,data):
#         if not (data['amount'] == data['rate']*data['quantity']):
#             raise DataValidationException('Amount is not valid. It should be (rate * quantity).')
#         if not (data['rate'] > 0):
#             raise DataValidationException('Rate must be greater than zero.')
#         if not (data['quantity'] > 0):
#             raise DataValidationException('Quantity must be greater than zero.')
#         return data

# def is_valid_product(product_id):
#     if not (product_master.objects.filter(status = 1,id=product_id).exists()):
#         raise DataValidationException('Product id is Invalid.',code=409)

# def is_valid_tax(tax_id):
#     if not (taxform_master.objects.filter(status = 1,id=tax_id).exists()):
#         raise DataValidationException('Tax id is Invalid.',code=409)
    
# def is_valid_concrete_structure(concrete_structure_id):
#     if not (entity_master.objects.filter(status = 1,system_field = 0,parent_id__entity_name='CONCRETE STRUCTURE',parent_id__system_field=1,parent_id__entity_type ='others',parent_id__parent_id = None,parent_id__status = 1,id=concrete_structure_id).exists()):#entity_type = 'others',
#         raise DataValidationException('Concrete structure id is Invalid.',code=409)

# def check_duplicate_products(order_list):
#     df = pd.DataFrame(order_list)
#     df.drop_duplicates(subset=['product_id','tax_id','delivery_mode','concrete_structure_id'], keep='last', inplace=True)
#     new_ol = df.to_dict("records")
#     print(new_ol,type(new_ol),len(new_ol),"new_ol")
#     print(order_list,type(order_list),len(order_list),"order_list after")
#     if len(new_ol) != len(order_list):
#         raise DataValidationException('Duplicate rows of  product,tax,concrete structure,delivery mode combination is not allowed.',code=409)

# def is_valid_delivery_mode(delivery_mode):
#     valid_delivery_modes = ['manual','pump','manual/pump','not applicable']
#     if not delivery_mode in valid_delivery_modes:
#         raise DataValidationException('Delivery_mode is Invalid.',code=409)

# def verify_enquiry_detail(order_list):
#     for i in range(len(order_list)):
#         is_valid_product(order_list[i]['product_id'])
#         is_valid_tax(order_list[i]['tax_id'])
#         is_valid_concrete_structure(order_list[i]['concrete_structure_id'])
#         is_valid_delivery_mode(order_list[i]['delivery_mode'])
#         if 'id' in order_list[i].keys() and order_list[i]['id']:
#             if not (entity_enquiry_detail.objects.filter(id=order_list[i]['id']).exists()):
#                 raise DataValidationException('Detail Id is Invalid.',code=409)
#     check_duplicate_products(order_list)

# def verify_numbering_detail(settings_list):
#     for i in range(len(settings_list)):
#         if ((type(settings_list[i]['starting_number']) is not int) or (type(settings_list[i]['number_of_digits'])is not int)):
#                 raise DataValidationException('starting_number and number_of_digits must be integer.',code=409)

# def verify_eo_detail(order_list,data):
#     valid_delivery_modes = ['manual','pump','manual/pump','not applicable']
#     # print(order_list,type(order_list),"order_list fn")
#     print(data,type(data),"data,type(data),")
#     for i in range(len(order_list)):
#         if 'id' in order_list[i].keys() and order_list[i]['id']:
#             if not (entity_order_detail.objects.filter(id=order_list[i]['id']).exists()):
#                 raise DataValidationException('Sales order Detail Id is Invalid.',code=409)
#         if data['quotation_id']:
#             print("with quotation")
#             # Following lines of code are used to check whether the SO details are as same as quotation. This will be 
#             # implemented in the future.
#             # quotation = entity_enquiry_master.objects.get(id = data['quotation_id'])
#             # a = entity_enquiry_detail.objects.filter(enquiry_master_id=quotation.id)
#             # print(order_list[i]['product_id'],type(order_list[i]['product_id']),"order_list[i]['product_id']")
#             # try:
#             #     so_detail = entity_enquiry_detail.objects.get(enquiry_master_id=quotation.id,product__id=order_list[i]['product_id'],concrete_structure__id = order_list[i]['concrete_structure_id'],tax__id=order_list[i]['tax_id'],rate=order_list[i]['rate'],delivery_mode=order_list[i]['delivery_mode'])#__gte
#             # except ObjectDoesNotExist:
#             #     raise DataValidationException('For a salesorder connected with quotation,product  details must be as same as quotation except quantity.',code=409)
#             # except entity_enquiry_detail.MultipleObjectsReturned as e:
#             #     raise DataValidationException(str(e),code=409)
#         else:
#             is_valid_product(order_list[i]['product_id'])
#             is_valid_tax(order_list[i]['tax_id'])
#             is_valid_concrete_structure(order_list[i]['concrete_structure_id'])
#             is_valid_delivery_mode(order_list[i]['delivery_mode'])
#     check_duplicate_products(order_list)


# def is_grade_valid(product_id,grade_name): 
#     if not (product_master.objects.filter(status = 1,id=product_id,category_detail__entity_name='FINISHED GOODS').exists()):
#         raise DataValidationException(grade_name +' id is Invalid.' ,code=409)

# def is_valid_qty(qty,name):
#     if (qty < 0):
#         raise DataValidationException(name + ' must be greater than zero.',code=409)


# def validate_weight(data):
#     if ((type(data['net_weight'])is not int) or (type(data['gross_weight'])is not int) or (type(data['tare_weight']) is not int)):
#         raise DataValidationException('Data type of net_weight,gross_weight,tare_weight must be integer.',code=400) 
#     if ((data['net_weight'] < 0) or (data['gross_weight'] < 0) or (data['tare_weight'] < 0)):
#         raise DataValidationException('net_weight,gross_weight,tare_weight must be greater than or equal to zero.',code=409)
#     net_weight = data['gross_weight']-data['tare_weight']
#     if data['net_weight'] != net_weight:
#         raise DataValidationException('Net weight must be equal to Gross weight-Tare weight.',code=409)