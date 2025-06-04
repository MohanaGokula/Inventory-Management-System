from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.serializers import *
from rms_ins.utils import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rms_ins.permissions import IsRmcAdminUser
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError

class NumberingViewSet(viewsets.ModelViewSet):
    queryset = numberings_master.objects.all()
    serializer_class = NumberingsMasterSerializer
    permission_classes =[IsRmcAdminUser]
    for_tracking={'content_type':"NUMBER SETTINGS FORM",'module_name':"ADMIN"}

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data= self.request.data
            settings_list = data['settings_list']
            if type(settings_list) is not list:
                raise DataValidationException('settings_list must be a list.',code = 400) 
            elif len(settings_list) > 0:
                verify_numbering_detail(settings_list)
            numberings_detail_serializer = NumberingsDetailSerializer(data=self.request.data['settings_list'], many=True)
            numberings_detail_serializer.is_valid(raise_exception=True)
            a=serializer.save(created_by=self.request.user)
            n=numberings_detail_serializer.save(created_by=self.request.user,numsetting_master=a)
            created_id_list=[x.id for x in n]
            created_ids=','.join(map(str,created_id_list))
            for_tracking={'id':"numberings_master_id : "+ str(a.id) + ", numberings_detail_id : "+ created_ids,
            'sl_no':None,'content_type':"NUMBER SETTINGS FORM",
            'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
    
    def list(self, request):
        # Commented on 2.2.24 
        # number_settings_list = numberings_master.objects.all().order_by('id').values('id','entity_plant_id','voucher_type')
        # for i in number_settings_list:
        #     if i['entity_plant_id'] == None:
        #         i['plant']= {'id':None,'name':None,'alias':None}
        #     else:
        #         i['plant']= {'id':i['entity_plant_id'],'name':entity_master.objects.get(id=i['entity_plant_id']).entity_name,'alias':entity_plant_detail.objects.get(entity_id=i['entity_plant_id']).plant_alias}
        #     i['settings_detail_list']=list(numberings_detail.objects.filter(numsetting_master__id=i['id']).values('starting_number','number_of_digits','prefix'))
        number_settings_detail_list = numberings_detail.objects.all().order_by('id').values('id','starting_number','number_of_digits','prefix')
        for i in number_settings_detail_list:
            dtl = numberings_detail.objects.get(id=i['id'])
            if dtl.numsetting_master.entity_plant_id == None:
                i['plant']= {'id':None,'name':None,'alias':None}
            else:
                plant = dtl.numsetting_master.entity_plant_id
                i['plant']= {'id':plant.id,'name':plant.entity_name,'alias':entity_plant_detail.objects.get(entity_id=plant).plant_alias}
            i['voucher_type'] = dtl.numsetting_master.voucher_type
            i['id'] = dtl.numsetting_master.id
            i['valid_from_date'] = dtl.valid_from_date.strftime("%d-%m-%Y")
            i['valid_upto_date'] = dtl.valid_upto_date.strftime("%d-%m-%Y")
        return Response({'number_settings_list':number_settings_detail_list},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            if instance.entity_plant_id == None:
                plant= {'id':None,'name':None}
            else:
                plant= {'id':instance.entity_plant_id.id,'name':instance.entity_plant_id.entity_name}
            content={
                    "id":serializer.data['id'],
                    "plant":plant,
                    "voucher_type":serializer.data['voucher_type'],
                    "settings_list":list(instance.numberings_detail_set.all().values('starting_number','number_of_digits','prefix','valid_from_date','valid_upto_date','user_remarks'))
                    }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Number Setting with id [{kwargs["pk"]}] not found')
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            numberings_detail_serializer = NumberingsDetailSerializer(data=self.request.data['settings_list'], many=True)
            numberings_detail_serializer.is_valid(raise_exception=True)
            old_dtls=numberings_detail.objects.filter(numsetting_master=instance.id)
            deleted_id_list=[x.id for x in old_dtls]
            deleted_ids=','.join(map(str,deleted_id_list))
            for i in old_dtls:
                i.delete()
            serializer.save(modified_by=self.request.user.username,voucher_type=instance.voucher_type,entity_plant_id=instance.entity_plant_id)
            n=numberings_detail_serializer.save(modified_by=self.request.user.username,numsetting_master=instance)
            created_id_list=[x.id for x in n]
            created_ids=','.join(map(str,created_id_list))
            for_tracking={'id':"numberings_master_id : "+ str(instance.id) + ", numberings_detail_id : "+ created_ids +", deleted_ids : "+ deleted_ids,
            'sl_no':None,'content_type':"NUMBER SETTINGS FORM",
            'action':"EDIT",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            queryset = self.filter_queryset(self.get_queryset())
            if queryset._prefetch_related_lookups:
                instance._prefetched_objects_cache = {}
                prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Number Setting with id [{kwargs["pk"]}] not found')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()   
            num_master_id=instance.id
            a=numberings_detail.objects.filter(numsetting_master=num_master_id)
            numberings_detail_ids=','.join(map(str,(list(a.values_list('id',flat=True)))))
            for i in a:
                i.delete() 
            for_tracking={'id':"numberings_master_id : "+ str(num_master_id) + ", numberings_detail_id : "+ numberings_detail_ids,
            'sl_no':None,'content_type':"NUMBER SETTINGS FORM",
            'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response({'message':"Successfully Deleted...."},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Number Setting with id [{kwargs["pk"]}] not found')