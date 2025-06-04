from rest_framework.settings import api_settings
from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.serializers import *
from rms_ins.utils import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rms_ins.permissions import IsRmcAdminUser
from django.db.models import F
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = entity_master.objects.filter(entity_type="company")
    serializer_class = EntityMasterSerializer
    permission_classes =[IsRmcAdminUser]
    for_tracking={'content_type':"COMPANY FORM",'module_name':"ADMIN"}
    valid_entity_types=["company"]
    
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
            company_serializer = EntityCompanyDetailSerializer(data=self.request.data)
            company_serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user,entity_type="company")
            entity_id=entity_master.objects.latest('id').id
            company_serializer.save(created_by=self.request.user,entity_id=entity_master.objects.get(id=entity_id))
            entity_company_id=entity_company_detail.objects.latest('id').id
            for_tracking={'id':"entity_id : "+ str(entity_id) + ", entity_company_detail_id : "+ str(entity_company_id),'sl_no':None,
            'content_type':"COMPANY FORM",
            'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            # content=serializer.data
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def list(self, request):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        # print(name,"name")
        if name is not None:
            company_data = queryset.filter(entity_name__iexact=name).values('id','entity_name','address_1','address_2','address_3','status')
        else:
            company_data = queryset.order_by('id').values('id','entity_name','address_1','address_2','address_3','status')
        for i in company_data:
            i['alias']= entity_company_detail.objects.get(entity_id=i['id']).alias
            i['status']=convert_status(i['status'])
        return Response({'company_data':company_data},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            company = entity_company_detail.objects.get(entity_id=instance.id)
            company_serializer = EntityCompanyDetailSerializer(company)
            plants = list(instance.entity_plant_detail_set.all().order_by('id').values('id',name=F('entity_id__entity_name'),alias=F('plant_alias'),address_1=F('entity_id__address_1'),address_2=F('entity_id__address_2'),address_3=F('entity_id__address_3'),status=F('entity_id__status')))
            # print(plants,"plants")
            # Below 'for loop' is to give the id of plant (entity master id),the id in the above lines gives only the
            # plant detail id
            for c in plants:
                c['id'] = entity_plant_detail.objects.get(id=c['id']).entity_id.id
            content={"id": serializer.data['id'],
                    "entity_name": serializer.data['entity_name'],
                    "address_1": serializer.data['address_1'],
                    "address_2": serializer.data['address_2'],
                    "address_3": serializer.data['address_3'],
                    "pincode": serializer.data['pincode'],
                    "state": serializer.data['state'],
                    "phone_number": serializer.data['phone_number'],
                    "email_id": serializer.data['email_id'],
                    "pan_no": serializer.data['pan_no'],
                    "gst_no": serializer.data['gst_no'],
                    "user_remarks": serializer.data['user_remarks'],
                    "status": serializer.data['status'],
                    "mobile_number": serializer.data['mobile_number'],
                    "alias": company_serializer.data['alias'],
                    "web": company_serializer.data['web'],
                    "seal": company_serializer.data['seal'],
                    "logo": company_serializer.data['logo'],
                    "commencement_dt": company_serializer.data['commencement_dt'],
                    "cst_no": company_serializer.data['cst_no'],
                    "lut_no": company_serializer.data['lut_no'],
                    "tan_no": company_serializer.data['tan_no'],
                    "cin_no": company_serializer.data['cin_no'],
                    "opening_dt":company_serializer.data['opening_dt'],
                    "closing_dt": company_serializer.data['closing_dt'],
                    "pf_no":company_serializer.data['pf_no'],
                    "esi_no": company_serializer.data['esi_no'],
                    "is_batching_report_needed": company_serializer.data['is_batching_report_needed'],
                    "plants":plants
                    }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Company with id [{kwargs["pk"]}] not found')
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            data = self.request.data
            new_keys = ['state','pan_no','gst_no']
            for n in range(len(new_keys)):
                if (not new_keys[n] in data.keys()):
                    raise DataValidationException("KeyError : "+new_keys[n],code=400)
            # if (not 'state' in data.keys()):
            #     raise DataValidationException("KeyError : state",code=400)
            serializer.is_valid(raise_exception=True)
            # validate_gst_no(data)
            validate_state(data)
            validate_gst_no_with_state(data)
            company = entity_company_detail.objects.get(entity_id=instance.id)
            company_serializer = EntityCompanyDetailSerializer(company,data=self.request.data)
            company_serializer.is_valid(raise_exception=True)
            serializer.save(modified_by=self.request.user.username)
            company_serializer.save(modified_by=self.request.user.username)
            for_tracking={'id':"entity_id : "+ str(instance.id) + ", entity_company_detail_id : "+ str(company.id),'sl_no':None,
            'content_type':"COMPANY FORM",
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
            raise EntityNotFoundException(detail=f'Company with id [{kwargs["pk"]}] not found')
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            company_id=instance.id
            instance.delete()
            a=entity_company_detail.objects.get(entity_id=company_id)
            company_dtl_id=a.id
            a.delete()    
            for_tracking={'id':"entity_id : "+ str(company_id) + ", entity_company_detail_id : "+ str(company_dtl_id),
            'sl_no':None,'content_type':"COMPANY FORM",
            'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response({'message':"Successfully Deleted...."},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Company with id [{kwargs["pk"]}] not found')
