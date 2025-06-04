from rest_framework.settings import api_settings
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

class SalesRepViewSet(viewsets.ModelViewSet):
    queryset = entity_master.objects.filter(entity_type="salesrep")
    serializer_class = EntityMasterSerializer
    permission_classes =[IsRmcAdminUser]
    for_tracking={'content_type':"SALES REPRESENTATIVE FORM",'module_name':"ADMIN"}
    valid_entity_types=["salesrep"]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            sales_rep_serializer = EntitySalesrepDetailSerializer(data=self.request.data)
            sales_rep_serializer.is_valid(raise_exception=True)
            print("sales_rep_serializer.validated_data",sales_rep_serializer.validated_data)
            serializer.save(created_by=self.request.user,entity_type="salesrep")
            entity_id=entity_master.objects.latest('id').id
            rep_validated_data=sales_rep_serializer.validated_data
            if any(rep_validated_data.values()): 
                sales_rep_serializer.save(created_by=self.request.user,entity_id=entity_master.objects.get(id=entity_id))
                entity_salesrep_id=entity_salesrep_detail.objects.latest('id').id
            else:
                entity_salesrep_id = "NO"
            for_tracking={'id':"entity_id : "+ str(entity_id) + ", entity_salesrep_detail_id : "+ str(entity_salesrep_id),'sl_no':None,'content_type':"SALES REPRESENTATIVE FORM",
            'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content=serializer.data
            s=status.HTTP_201_CREATED
            headers = self.get_success_headers(serializer.data)
            return Response(content,status=s, headers=headers)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e) ,code=400)

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
            salesrep_data =  queryset.filter(entity_name__iexact=name).values('id','entity_name','address_1','address_2','address_3','mobile_number','phone_number','status')
        else:
            salesrep_data = queryset.order_by('id').values('id','entity_name','address_1','address_2','address_3','mobile_number','phone_number','status')
        for i in salesrep_data:
            i['status']=convert_status(i['status'])
        return Response({'salesrep_data':salesrep_data},status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            entity_salesrep=entity_salesrep_detail.objects.filter(entity_id=instance.id).first()#,deleted=None
            if entity_salesrep:
                credit_limit = entity_salesrep.credit_limit
                ref_name = entity_salesrep.ref_name
                ref_mobile_no = entity_salesrep.ref_mobile_no
            else:
                credit_limit = 0
                ref_name = ""
                ref_mobile_no =""
            content = {"id":serializer.data['id'],
                            "entity_name":serializer.data['entity_name'],
                            "alias":entity_salesrep.alias,
                            "category":entity_salesrep.category,
                            "pincode":serializer.data['pincode'],
                            "phone_number":serializer.data['phone_number'],
                            "mobile_number":serializer.data['mobile_number'],
                            "email_id":serializer.data['email_id'],
                            "pan_no":serializer.data['pan_no'],
                            "user_remarks":serializer.data['user_remarks'],
                            "status":serializer.data['status'],
                            "contact_person":serializer.data['contact_person'],
                            "contact_mobile_no":serializer.data['contact_mobile_no'],
                            "contact_email_id":serializer.data['contact_email_id'],
                            "contact_designation":serializer.data['contact_designation'],
                            "credit_limit":credit_limit,
                            "ref_name":ref_name,
                            "ref_mobile_no":ref_mobile_no,
                            "gst_type":serializer.data['gst_type'],
                            "address_1":serializer.data['address_1'],
                            "address_2":serializer.data['address_2'],
                            "address_3":serializer.data['address_3'],
                            "gst_no":serializer.data['gst_no']}
            s=status.HTTP_200_OK
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Sales Representative with id [{kwargs["pk"]}] not found')

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            sales_rep_serializer = EntitySalesrepDetailSerializer(data=self.request.data)
            sales_rep_serializer.is_valid(raise_exception=True)
            serializer.save(modified_by=self.request.user.username)
            rep_validated_data=sales_rep_serializer.validated_data
            sales_rep = entity_salesrep_detail.objects.filter(entity_id=instance.id).first()
            if sales_rep:
                sales_rep_serializer = EntitySalesrepDetailSerializer(sales_rep,data=self.request.data)
                sales_rep_serializer.is_valid(raise_exception=True)
                if any(rep_validated_data.values()):
                    sales_rep_serializer.save(modified_by=self.request.user.username)
                    entity_salesrep_id= sales_rep.id
                else:
                    sales_rep.delete()
                    entity_salesrep_id= "NO"
            elif any(rep_validated_data.values()):
                sales_rep_serializer.save(created_by=self.request.user,entity_id=entity_master.objects.get(id=instance.id))
                entity_salesrep_id=entity_salesrep_detail.objects.latest('id').id
            else:
                entity_salesrep_id= "NO"
            for_tracking={'id':"entity_id : "+ str(instance.id) + ", entity_salesrep_detail_id : "+ str(entity_salesrep_id),
            'sl_no':None,'content_type':"SALES REPRESENTATIVE FORM",
            'action':"EDIT",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content = serializer.data
            s=status.HTTP_200_OK
            queryset = self.filter_queryset(self.get_queryset())
            if queryset._prefetch_related_lookups:
                instance._prefetched_objects_cache = {}
                prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
            return Response(content,status=s)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e) ,code=400)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Sales Representative with id [{kwargs["pk"]}] not found')

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            group_id=instance.id
            instance.delete()
            sales_rep=entity_salesrep_detail.objects.filter(entity_id=group_id).first()#,deleted=None
            if sales_rep:
                entity_salesrep_id= sales_rep.id
                sales_rep.delete()
            else:
                entity_salesrep_id= "NO"
            for_tracking={'id':"entity_id : "+ str(group_id) + ", entity_salesrep_detail_id : "+ str(entity_salesrep_id),
            'sl_no':None,'content_type':"SALES REPRESENTATIVE FORM",
            'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content={'message':"Successfully Deleted...."}
            s=status.HTTP_200_OK
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Sales Representative with id [{kwargs["pk"]}] not found')


