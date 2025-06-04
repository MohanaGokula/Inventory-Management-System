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

class UnitViewSet(viewsets.ModelViewSet):
    queryset = uom_master.objects.all()
    serializer_class = UomMasterSerializer
    permission_classes =[IsRmcAdminUser]
    for_tracking={'content_type':"UNIT FORM",'module_name':"ADMIN"}

    def __init__(self, *args, **kwargs):
        super(UnitViewSet, self).__init__(*args, **kwargs)
        self.serializer_action_classes = {
            'list':UomListSerializer
        }

    def get_serializer_class(self, *args, **kwargs):
        """Instantiate the list of serializers per action from class attribute (must be defined)."""
        kwargs['partial'] = True
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(UnitViewSet, self).get_serializer_class()

    def get_queryset(self):
        queryset =  super().get_queryset()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset =  queryset.filter(name__iexact=name)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'unit_list':serializer.data})
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            unit_id=uom_master.objects.latest('id').id
            for_tracking={'id':unit_id,'sl_no':None,'content_type':"UNIT FORM",
            'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content=serializer.data
            s=status.HTTP_201_CREATED
            headers = self.get_success_headers(serializer.data)
            return Response(content,status=s, headers=headers)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            content={
                    "id": serializer.data['id'],
                    "name":serializer.data['name'],
                    "symbol":serializer.data['symbol'],
                    "quantity":serializer.data['quantity'],
                    "decimal_place":serializer.data['decimal_place'],
                    "user_remarks":serializer.data['user_remarks'],
                    "status":serializer.data['status'],
                    "system_field":convert_status(instance.system_field)
                    }
            s=status.HTTP_200_OK
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Unit with id [{kwargs["pk"]}] not found')

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if instance.system_field == 0:
                serializer.is_valid(raise_exception=True)
                serializer.save(modified_by=self.request.user.username)
                for_tracking={'id':instance.id,'sl_no':None,'content_type':"UNIT FORM",
                'module_name':"ADMIN",'action':"EDIT",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content = serializer.data
                s=status.HTTP_200_OK
                queryset = self.filter_queryset(self.get_queryset())
                if queryset._prefetch_related_lookups:
                    instance._prefetched_objects_cache = {}
                    prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
                return Response(content,status=s)
            else:
                raise DataValidationException(detail="Default/System data cannot be edited.", code=403)   
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Unit with id [{kwargs["pk"]}] not found')

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.system_field == 0:
                unit_id = instance.id
                instance.delete()
                for_tracking={'id':unit_id,'sl_no':None,'content_type':"UNIT FORM",
                'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content={'message':"Successfully Deleted...."}
                s=status.HTTP_200_OK 
                return Response(content,status=s)
            else:
                raise DataValidationException(detail="Default/System data cannot be deleted.", code=403)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Unit with id [{kwargs["pk"]}] not found')

