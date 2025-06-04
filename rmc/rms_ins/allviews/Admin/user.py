from rest_framework.settings import api_settings
from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.utils import *
from rms_ins.serializers import *
from django.contrib.auth.models import User,Permission,Group
from rest_framework.response import Response
from rest_framework.decorators import action
from rms_ins.permissions import IsSuperUser
from django.db.models import F
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError

class UserViewSet(viewsets.ModelViewSet):
    queryset = profiles_master.objects.all()
    serializer_class = ProfilesMasterSerializer
    permission_classes =[IsSuperUser]
    for_tracking={'content_type':"USER REGISTRATION FORM",'module_name':"ADMIN"}

    def create(self, request, *args, **kwargs):
        try :
            user_serializer = UserSerializer(data=self.request.data)
            user_serializer.is_valid(raise_exception=True)
            check_serializer = ProfilesMasterValidationSerializer(data=self.request.data)
            check_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            user = User.objects.latest('id')
            profile =profiles_master.objects.get(user_id=user)
            serializer = ProfilesMasterSerializer(profile,data={'user_mobile_no':request.data['user_mobile_no'],
    'user_valid_from':request.data['user_valid_from'],'is_mfa_needed':request.data['is_mfa_needed'],
    'user_valid_upto':request.data['user_valid_upto'],'is_location_auth_needed':request.data['is_location_auth_needed']
    ,'user_remarks':request.data['user_remarks'],'user':user.id,'plants':request.data['plants']})
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=request.user.username)
            plant_ids = ','.join(map(str,request.data['plants']))
            group_ids = ','.join(map(str,request.data['groups']))
            for_tracking={'id':"user_id : "+ str(user.id) + ", profiles_master_id : "+ str(profile.id) + ", plant_ids : "+ plant_ids + ", group_ids : " + group_ids,'sl_no':None,
            'content_type':"USER REGISTRATION FORM",
            'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            # content=serializer.data
            return Response(status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def list(self, request):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        print(name,"name")
        if name is not None:
            user = User.objects.filter(username__iexact=name).first()
            if user:
                user_list =  queryset.filter(user=user.id).values('id','user')
            else:
                user_list = []
        else:
            user_list = queryset.order_by('id').values('id','user')
        for i in user_list:
            profile = profiles_master.objects.get(id=i['id'])
            user= User.objects.get(id=i['user'])
            i['username']= user.username
            i['is_active']=user.is_active
            i['is_superuser']=user.is_superuser
            i['email']=user.email
            i['group_list']=list(user.groups.values('id','name'))
            i['plant_list']=list(profile.plant.all().values('id',name=F('entity_name')))
            for j in i['plant_list']:
                j['alias']=entity_plant_detail.objects.get(entity_id=j['id']).plant_alias
        return Response({'user_list':user_list},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            user=User.objects.get(id=serializer.data["user"])
            if user.is_superuser:
                plant_list = entity_master.objects.filter(entity_type='plant',status=1).values('id',name=F('entity_name'))
            else:
                plant_list=user.profiles_master.plant.values('id',name=F('entity_name'))
            for d in plant_list:
                d['alias']=entity_plant_detail.objects.get(entity_id=d['id']).plant_alias
            content={"id":serializer.data["id"],
            "username":user.username,
            "password":user.password,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "is_active":user.is_active,
            "is_superuser":user.is_superuser,
            "email":user.email,
            "user_mobile_no":serializer.data["user_mobile_no"],
            "user_valid_from":serializer.data["user_valid_from"],
            "user_valid_upto":serializer.data["user_valid_upto"],
            "user_remarks":serializer.data["user_remarks"],
            "is_mfa_needed":serializer.data['is_mfa_needed'],
            "is_location_auth_needed":serializer.data['is_location_auth_needed'],
            "plant_list":plant_list,
            "group_list":list(user.groups.values('id','name'))
            }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'User with id [{kwargs["pk"]}] not found')

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            user= User.objects.get(id=instance.user.id)
            otp_enabled = instance.otp_enabled
            otp_verified = instance.otp_verified
            otp_base32 = instance.otp_base32
            otp_auth_url = instance.otp_auth_url 
            user_serializer = UserSerializer(user,data=self.request.data)
            print(self.request.data,"self.request.data user update")
            serializer = self.get_serializer(instance, data={'user_mobile_no':request.data['user_mobile_no'],
            'user_valid_from':request.data['user_valid_from'],'is_mfa_needed':request.data['is_mfa_needed'],
            'user_valid_upto':request.data['user_valid_upto'],'is_location_auth_needed':request.data['is_location_auth_needed']
            ,'user_remarks':request.data['user_remarks'],'user':user.id,'plants':request.data['plants']}, partial=partial)
            user_serializer.is_valid(raise_exception=True)
            serializer.is_valid(raise_exception=True)
            print(serializer.validated_data['is_mfa_needed'],"is_mfa_needed")
            is_mfa_needed=serializer.validated_data['is_mfa_needed']
            if (is_mfa_needed == False):
                otp_enabled = 0
                otp_verified = 0
                otp_base32 = None
                otp_auth_url = None
            user_serializer.save()
            serializer.save(modified_by=request.user.username,otp_enabled = otp_enabled,
                otp_verified = otp_verified,
                otp_base32 = otp_base32,
                otp_auth_url=otp_auth_url)
            group_ids_list = request.data['groups']
            group_ids = ','.join(map(str,group_ids_list))
            plant_ids = ','.join(map(str,request.data['plants']))
            for_tracking={'id':"user_id : "+ str(user.id) + ", profiles_master_id : "+ str(instance.id) + ", plant_ids : "+ plant_ids + ", group_ids : " + group_ids,'sl_no':None,
            'content_type':"USER REGISTRATION FORM",
            'action':"EDIT",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'User with id [{kwargs["pk"]}] not found')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e) ,code=400)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            profile_id=instance.id
            user_id = instance.user.id
            user=User.objects.get(id=user_id)
            if user.is_superuser:
                raise DataValidationException("You can't delete Superuser.",code = 403)
            user.delete()
            # instance.delete()
            # User.objects.filter(id=user_id).update(is_active=False)
            for_tracking={'id':"user_id : "+ str(user_id) + ", profiles_master_id : "+ str(profile_id),
            'sl_no':None,'content_type':"USER REGISTRATION FORM",
            'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content={'message':"Successfully Deleted...."}
            s=status.HTTP_200_OK
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'User with id [{kwargs["pk"]}] not found')
        except ProtectedError:
            raise DataValidationException("You can't delete this. Because it is being used by groups.",code = 403)
   

