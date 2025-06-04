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

class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = approval_setting_master.objects.all()
    serializer_class = ApprovalSettingsMasterSerializer
    permission_classes = [IsRmcAdminUser]
    for_tracking={'content_type':"APPROVAL AND MAIL SETTINGS FORM",'module_name':"ADMIN"}

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            a=serializer.save(created_by=self.request.user)
            for_tracking={'id':str(a.id),
            'sl_no':None,'content_type':"APPROVAL AND MAIL SETTINGS FORM",
            'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
    
    def list(self, request):
        approval_mail_settings_list = approval_setting_master.objects.all().order_by('id').values('id','voucher_type','is_appr_needed','is_so_wait_on_save',
        'is_mail_needed','mail_ids','conditions_for_so_waiting')
        for i in approval_mail_settings_list:
            appr_settings = approval_setting_master.objects.get(id = i['id'])
            i['company']= {'id':appr_settings.entity_company_id.id,'name':appr_settings.entity_company_id.entity_name}
            i['is_appr_needed'] = convert_status(i['is_appr_needed'])
            i['is_so_wait_on_save'] = convert_status(i['is_so_wait_on_save'])
            i['is_mail_needed'] = convert_status(i['is_mail_needed'])
            if i['mail_ids']:
                i['mail_ids'] = i['mail_ids'].split(",")
            else:
                i['mail_ids'] = []
            if i['conditions_for_so_waiting']:
                i['conditions_for_so_waiting'] = i['conditions_for_so_waiting'].split(",")
            else:
                i['conditions_for_so_waiting'] = []
        return Response({'approval_mail_settings_list':approval_mail_settings_list},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            if instance.mail_ids:
                mail_ids = (instance.mail_ids).split(",")
            else:
                mail_ids = []
            if instance.conditions_for_so_waiting:
                conditions_for_so_waiting = (instance.conditions_for_so_waiting).split(",")
            else:
                conditions_for_so_waiting = []
            content={
            "id":serializer.data['id'],
            "company": {"id": instance.entity_company_id.id,
                        "name": instance.entity_company_id.entity_name},
            "voucher_type": serializer.data['voucher_type'],
            "is_appr_needed": serializer.data['is_appr_needed'],
            "is_so_wait_on_save": serializer.data['is_so_wait_on_save'],
            "conditions_for_so_waiting": conditions_for_so_waiting,
            "is_mail_needed": serializer.data['is_mail_needed'],
            "mail_ids": mail_ids
            }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Approval Setting with id [{kwargs["pk"]}] not found')
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save(modified_by=self.request.user.username)
            for_tracking={'id':str(instance.id),'sl_no':None,
            'content_type':"APPROVAL AND MAIL SETTINGS FORM",
            'action':"EDIT",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            queryset = self.filter_queryset(self.get_queryset())
            if queryset._prefetch_related_lookups:
                instance._prefetched_objects_cache = {}
                prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Approval Setting with id [{kwargs["pk"]}] not found')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            appr_settings_id=instance.id
            instance.delete()
            for_tracking={'id':str(appr_settings_id),
            'sl_no':None,'content_type':"APPROVAL AND MAIL SETTINGS FORM",
            'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response({'message':"Successfully Deleted...."},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Approval Setting with id [{kwargs["pk"]}] not found')