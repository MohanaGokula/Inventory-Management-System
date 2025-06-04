from rest_framework.settings import api_settings
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

class GroupingViewSet(viewsets.ModelViewSet):
    queryset=entity_master.objects.filter(entity_type__in=["income","assets","expenses","liabilities","others"]) | entity_master.objects.filter(entity_type = None)
    serializer_class = EntityMasterSerializer
    permission_classes =[CheckPermission]
    required_perms = {
        'GET': ['rmc.view_grouping'],
        'POST': ['rmc.add_grouping'],
        'PUT': ['rmc.edit_grouping'],
        'DELETE': ['rmc.delete_grouping']
    }
    for_tracking={'content_type':"ACCOUNTS GROUPING",'module_name':"ACCOUNTS"}
    valid_entity_types=["income","assets","expenses","liabilities","others"]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            group_id=entity_master.objects.latest('id').id
            for_tracking={'id':group_id,'sl_no':None,'content_type':"ACCOUNTS GROUPING",
            'action':"CREATE",'module_name':"ACCOUNTS",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content=serializer.data
            s=status.HTTP_201_CREATED
            headers = self.get_success_headers(serializer.data)
            return Response(content,status=s, headers=headers)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)), code=400, exception=e)

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
            queryset =  queryset.filter(entity_name__iexact=name).order_by('id').values('id','entity_name','parent_id','system_field')#,entity_type__in=["income","assets","expenses","liabilities","others"]
        else:
            queryset = queryset.order_by('id').values('id','entity_name','parent_id','system_field')#,'status'
            print(queryset,"queryset")
        for i in queryset:
            em = entity_master.objects.get(id=i['id'])
            if i['parent_id']:
                parent= entity_master.objects.get(id=i['parent_id'])
                i['parent']= {'id':parent.id,"name":parent.entity_name}
                print(i['parent'])
                i['entity_type'] = get_entity_type(em.id)
            else:
                i['parent']=i['parent_id']
                i['entity_type'] = em.entity_type
        return Response({'accounts_grouping_list':queryset},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(instance,"instance")
            serializer = self.get_serializer(instance)
            if instance.parent_id:
                parent={'id':instance.parent_id.id,"name":instance.parent_id.entity_name}
                entity_type = get_entity_type(instance.id)
            else:
                parent=serializer.data['parent_id']
                entity_type = serializer.data['entity_type']
            content={
                    "id": serializer.data['id'],
                    "entity_name":serializer.data['entity_name'],
                    "entity_type":entity_type,
                    "parent_id":serializer.data['parent_id'],
                    "parent":parent,
                    "system_field":serializer.data['system_field'],
                    }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Entry with id [{kwargs["pk"]}] not found')

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if instance.system_field == 0:
                serializer.is_valid(raise_exception=True)
                serializer.save(modified_by=self.request.user.username)
                for_tracking={'id':instance.id,'sl_no':None,'content_type':"ACCOUNTS GROUPING",
                'action':"EDIT",'module_name':"ACCOUNTS",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content = serializer.data
                s=status.HTTP_200_OK
            else:
                raise DataValidationException(detail="Default/System data cannot be edited.", code=403)
            queryset = self.filter_queryset(self.get_queryset())
            if queryset._prefetch_related_lookups:
                instance._prefetched_objects_cache = {}
                prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Entry with id [{kwargs["pk"]}] not found')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)), code=400, exception=e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.system_field == 0:
                group_id= instance.id
                instance.delete()
                for_tracking={'id':group_id,'sl_no':None,'content_type':"ACCOUNTS GROUPING",
                'action':"DELETE",'module_name':"ACCOUNTS",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content={'message':"Successfully Deleted...."}
                s=status.HTTP_200_OK
            else:
                raise DataValidationException(detail="Default/System data cannot be deleted.", code=403)
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Entry with id [{kwargs["pk"]}] not found')
    
    