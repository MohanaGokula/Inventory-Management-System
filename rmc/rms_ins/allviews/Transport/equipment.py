from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.serializers import *
from rms_ins.utils import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rms_ins.permissions import CheckPermission
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = equipment_master.objects.all()
    serializer_class = EquipmentMasterSerializer
    for_tracking={'content_type':"EQUIPMENT FORM",'module_name':"TRANSPORT"}
    permission_classes =[CheckPermission]
    required_perms = {
        'GET': ['rmc.view_equipment_master'],
        'POST': ['rmc.add_equipment_master'],
        'PUT': ['rmc.change_equipment_master'],
        'DELETE': ['rmc.delete_equipment_master']
    }

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            a=serializer.save(created_by=self.request.user,is_equip_ready=1,co_open_km = serializer.validated_data['meter_reading'],co_open_hm=serializer.validated_data['equip_open_hm'])
            for_tracking={'id': str(a.id),
            'sl_no':None,'content_type':"EQUIPMENT FORM",
            'action':"CREATE",'module_name':"TRANSPORT",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
    
    def list(self, request):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        # print(name,"name")
        if name is not None:
            name = name.replace(" ", "")
            # print(name,"name striped")
            equipment_list =  queryset.filter(equip_name__iexact=name).order_by('id').values('id','equip_name','capacity','insurance_date','permit_date','fc_date',
            'user_remarks','co_open_km','co_open_hm')
        else:
            equipment_list = queryset.order_by('id').values('id','equip_name','capacity','insurance_date','permit_date','fc_date',
            'user_remarks','co_open_km','co_open_hm')
        for i in equipment_list:
            equipment = equipment_master.objects.get(id=i['id'])
            i['meter_status'] = convert_status(equipment.meter_status)
            i['status'] = convert_status(equipment.status)
            i['is_equip_ready'] =convert_status(equipment.is_equip_ready)
            i['system_field'] = convert_status(equipment.system_field)
            i['vendor'] = {'id':equipment.entity_vendor_id.id,'name':equipment.entity_vendor_id.entity_name}
            i['equip_type'] = {'id':equipment.equip_grp_code.id,'name':equipment.equip_grp_code.entity_name}
            if (equipment.equip_grp_code.entity_name == 'TRANSIT MIXER'):
                i['is_valid'] = check_vehicle_validity(equipment)
            else:
                i['is_valid'] = True
        return Response({'equipment_list':equipment_list},status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            if (instance.equip_grp_code.entity_name == 'TRANSIT MIXER'):
                is_valid = check_vehicle_validity(instance)
            else:
                is_valid = True
            content={
                "id":serializer.data['id'],
                "equip_type": {"id":instance.equip_grp_code.id,"name":instance.equip_grp_code.entity_name},
                "equip_name": serializer.data['equip_name'],
                "mode": serializer.data['mode'],
                "vendor": {"id":instance.entity_vendor_id.id,"name":instance.entity_vendor_id.entity_name},
                "is_tax_applicable": serializer.data['is_tax_applicable'],
                "insurance_date":serializer.data['insurance_date'],
                "permit_date": serializer.data['permit_date'],
                "fc_date": serializer.data['fc_date'],
                "capacity": serializer.data['capacity'],
                "fuel_type": serializer.data['fuel_type'],
                "meter_status": serializer.data['meter_status'],
                "meter_reading":serializer.data['meter_reading'],
                "equip_open_hm": serializer.data['equip_open_hm'],
                "user_remarks": serializer.data['user_remarks'],
                "status": serializer.data['status'],
                "is_equip_ready" :convert_status(instance.is_equip_ready),
                "co_open_km": serializer.data['co_open_km'],
                "co_open_hm": serializer.data['co_open_hm'],
                "is_valid":is_valid 
            }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Equipment with id [{kwargs["pk"]}] not found')
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if instance.system_field == 0:
                serializer.is_valid(raise_exception=True)
                if instance.equip_grp_code.entity_name == 'TRANSIT MIXER':
                    dc_list=goods_movement_master.objects.filter(vehicle=instance,status=1)
                    customer_status=['partial_accepted','accepted']
                    if dc_list:
                        is_checked_in=[]
                        for i in dc_list:
                            if not (gate_pass_master.objects.filter(gmm=i,customer_status__in=customer_status).exists()):
                                is_checked_in.append(0)
                        print(is_checked_in,"is_checked_in")
                        if len(is_checked_in) > 0:
                            is_equip_ready = 0
                        else:
                            is_equip_ready = 1
                    else:
                        is_equip_ready = 1
                else:
                    is_equip_ready = 1
                serializer.save(modified_by=self.request.user.username,is_equip_ready=is_equip_ready,co_open_km = serializer.validated_data['meter_reading'],co_open_hm=serializer.validated_data['equip_open_hm'])
                for_tracking={'id':instance.id,'sl_no':None,'content_type':"EQUIPMENT FORM",
                'module_name':"TRANSPORT",'action':"EDIT",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                queryset = self.filter_queryset(self.get_queryset())
                if queryset._prefetch_related_lookups:
                    instance._prefetched_objects_cache = {}
                    prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                raise DataValidationException(detail="Default/System data cannot be edited.", code=403)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Equipment with id [{kwargs["pk"]}] not found')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.system_field == 0:
                equipment_id = instance.id
                instance.delete()
                for_tracking={'id':equipment_id,'sl_no':None,'content_type':"EQUIPMENT FORM",
                'action':"DELETE",'module_name':"TRANSPORT",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                return Response({'message':"Successfully Deleted...."},status=status.HTTP_200_OK)
            else:
                raise DataValidationException(detail="Default/System data cannot be deleted.", code=403)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Equipment with id [{kwargs["pk"]}] not found')
