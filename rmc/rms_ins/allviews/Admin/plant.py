from rest_framework.settings import api_settings
from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.serializers import *
from rms_ins.utils import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rms_ins.permissions import IsRmcAdminUser
from rest_framework.decorators import action
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError

class PlantViewSet(viewsets.ModelViewSet):
    queryset = entity_master.objects.filter(entity_type="plant")
    serializer_class = EntityMasterSerializer
    permission_classes =[IsRmcAdminUser]
    for_tracking={'content_type':"PLANT FORM",'module_name':"ADMIN"}
    valid_entity_types=["plant"]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            data = self.request.data
            # if (not 'state' in data.keys()):
            #     raise DataValidationException("KeyError : state",code=400)
            new_keys = ['state','pan_no','gst_no']
            for n in range(len(new_keys)):
                if (not new_keys[n] in data.keys()):
                    raise DataValidationException("KeyError : "+new_keys[n],code=400)
            serializer.is_valid(raise_exception=True)
            # validate_gst_no(data)
            validate_state(data)
            validate_gst_no_with_state(data)
            plant_serializer = EntityPlantDetailSerializer(data=self.request.data)
            plant_serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user,entity_type="plant")
            entity_id=entity_master.objects.latest('id').id
            plant_serializer.save(created_by=self.request.user,entity_id=entity_master.objects.get(id=entity_id))
            entity_plant_id=entity_plant_detail.objects.latest('id').id
            for_tracking={'id':"entity_id : "+ str(entity_id) + ", entity_plant_detail_id : "+ str(entity_plant_id),'sl_no':None,
            'content_type':"PLANT FORM",
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
            plant = entity_plant_detail.objects.filter(plant_alias__iexact=name).first()
            if plant:
                plant_list = queryset.filter(id=plant.entity_id.id).values('id','entity_name','address_1','address_2','address_3','status')
            else:
                plant_list = []
        else:
            plant_list = queryset.order_by('id').values('id','entity_name','address_1','address_2','address_3','status')
        for i in plant_list:
            i['plant_alias']=entity_plant_detail.objects.get(entity_id=i['id']).plant_alias
            i['status']=convert_status(i['status'])
        return Response({'plant_list':plant_list},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            plant = entity_plant_detail.objects.get(entity_id=instance.id)
            plant_serializer = EntityPlantDetailSerializer(plant)
            content={"id": serializer.data['id'],
                    "entity_name": serializer.data['entity_name'],
                    "address_1": serializer.data['address_1'],
                    "address_2": serializer.data['address_2'],
                    "address_3": serializer.data['address_3'],
                    "pincode": serializer.data['pincode'],
                    "state": serializer.data['state'],
                    "phone_number": serializer.data['phone_number'],
                    "user_remarks": serializer.data['user_remarks'],
                    "email_id": serializer.data['email_id'],
                    "pan_no": serializer.data['pan_no'],
                    "gst_no": serializer.data['gst_no'],
                    "status": serializer.data['status'],
                    "mobile_number": serializer.data['mobile_number'],
                    "plant_alias": plant_serializer.data['plant_alias'],
                    "plant_web":plant_serializer.data['plant_web'],
                    "plant_commence_dt":plant_serializer.data['plant_commence_dt'],
                    "plant_cst_no":plant_serializer.data['plant_cst_no'],
                    "plant_lut_no":plant_serializer.data['plant_lut_no'],
                    "plant_tan_no":plant_serializer.data['plant_tan_no'],
                    "account_opening_dt":plant_serializer.data['account_opening_dt'],
                    "account_closing_dt":plant_serializer.data['account_closing_dt'],
                    "plant_mixer_capacity":plant_serializer.data['plant_mixer_capacity'],
                    "plant_pfno":plant_serializer.data['plant_pfno'],
                    "plant_esino":plant_serializer.data['plant_esino'],
                    "plant_serial_no":plant_serializer.data['plant_serial_no'],
                    "plant_model":plant_serializer.data['plant_model'],
                    "plant_make":plant_serializer.data['plant_make'],
                    "plant_seal":plant_serializer.data['plant_seal'],
                    "plant_logo":plant_serializer.data['plant_logo'],
                    "plant_br_logo":plant_serializer.data['plant_br_logo'],
                    "entity_company_id":plant_serializer.data['entity_company_id'],
                    "company":{'id':plant.entity_company_id.id,'name':plant.entity_company_id.entity_name}
                    }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Plant with id [{kwargs["pk"]}] not found')

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            data = self.request.data
            # if (not 'state' in data.keys()):
            #     raise DataValidationException("KeyError : state",code=400)
            new_keys = ['state','pan_no','gst_no']
            for n in range(len(new_keys)):
                if (not new_keys[n] in data.keys()):
                    raise DataValidationException("KeyError : "+new_keys[n],code=400)
            serializer.is_valid(raise_exception=True)
            # validate_gst_no(data)
            validate_state(data)
            validate_gst_no_with_state(data)
            plant = entity_plant_detail.objects.get(entity_id=instance.id)
            plant_serializer = EntityPlantDetailSerializer(plant,data=self.request.data)
            plant_serializer.is_valid(raise_exception=True)
            serializer.save(modified_by=self.request.user.username)
            plant_serializer.save(modified_by=self.request.user.username)
            for_tracking={'id':"entity_id : "+ str(instance.id) + ", entity_plant_detail_id : "+ str(plant.id),'sl_no':None,
            'content_type':"PLANT FORM",
            'action':"EDIT",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            # content = serializer.data
            queryset = self.filter_queryset(self.get_queryset())
            if queryset._prefetch_related_lookups:
                instance._prefetched_objects_cache = {}
                prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Plant with id [{kwargs["pk"]}] not found')
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            group_id=instance.id
            assigned_for_user=instance.profiles_master_set.exists()
            print(instance.profiles_master_set.all(),"instance.profiles_master_set.all()")
            print(assigned_for_user,"assigned_for_user")
            if assigned_for_user:
                content={'message':"Can not delete this plant..because this plant is assigned for user.."}
                s= status.HTTP_400_BAD_REQUEST
            else:
                instance.delete()
                a=entity_plant_detail.objects.get(entity_id=group_id)
                plant_dtl_id=a.id
                a.delete()    
                for_tracking={'id':"entity_id : "+ str(group_id) + ", entity_plant_detail_id : "+ str(plant_dtl_id),
                'sl_no':None,'content_type':"PLANT FORM",
                'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content={'message':"Successfully Deleted...."}
                s=status.HTTP_200_OK
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Plant with id [{kwargs["pk"]}] not found')

    @action(detail=False)
    def user_allowed(self,request):
        try:
            queryset = super().get_queryset()
            if not (request.user.is_superuser):
                plant_list = list(request.user.profiles_master.plant.values('id','entity_name','address_1','address_2','address_3','status'))
            else:
                plant_list = queryset.order_by('id').values('id','entity_name','address_1','address_2','address_3','status')
            print(plant_list,"plant_list")
            for i in plant_list:
                i['plant_alias']=entity_plant_detail.objects.get(entity_id=i['id']).plant_alias
                i['status']=convert_status(i['status'])
            return Response({'plant_list':plant_list},status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
    