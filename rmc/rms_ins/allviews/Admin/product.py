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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = product_master.objects.all()
    serializer_class = ProductMasterSerializer
    permission_classes =[IsRmcAdminUser]
    for_tracking={'content_type':"PRODUCT FORM",'module_name':"ADMIN"}

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user)
            product_id=product_master.objects.latest('id').id
            for_tracking={'id':product_id,'sl_no':None,'content_type':"PRODUCT FORM",
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
            product_list =  queryset.filter(name__iexact=name).values('id','name','quantity','user_remarks','status','vendor_part_code','hsn_sac_code','hsn_sac_description','prod_gst_type')#category_detail_name=F('category_detail__entity_name'),unit_name=F('unit__name'))
        else:
            product_list = queryset.values('id','name','quantity','user_remarks','status','vendor_part_code','hsn_sac_code','hsn_sac_description','prod_gst_type')#category_detail_name=F('category_detail__entity_name'),unit_name=F('unit__name'))
        for i in product_list:
            print (i,"i")
            product = product_master.objects.get(id=i['id'])
            i['category']={'id':product.category_detail.id,'name':product.category_detail.entity_name}
            i['unit']={'id':product.unit.id,'name':product.unit.name, 'symbol': product.unit.symbol}
            i['tax']={'id':product.tax.id,'name':product.tax.name}
            i['status']=convert_status(i['status'])
        return Response({'product_list':product_list},status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            content={
                "id":serializer.data['id'],
                "category":{"id":instance.category_detail.id,"name":instance.category_detail.entity_name},
                "unit":{"id":instance.unit.id,"name":instance.unit.name},
                "quantity":serializer.data['quantity'],
                "vendor_part_code":serializer.data['vendor_part_code'],
                "is_gst_applicable":serializer.data['is_gst_applicable'],
                "tax":{"id":instance.tax.id,"name":instance.tax.name},
                "hsn_sac_code":serializer.data['hsn_sac_code'],
                "hsn_sac_description":serializer.data['hsn_sac_description'],
                "prod_gst_type":serializer.data['prod_gst_type'],
                "is_batch_report_connected":serializer.data['is_batch_report_connected'],
                "name":serializer.data['name'],
                "user_remarks":serializer.data['user_remarks'],
                "status":serializer.data['status']
            }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Product with id [{kwargs["pk"]}] not found')
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save(modified_by=self.request.user.username)
            for_tracking={'id':instance.id,'sl_no':None,'content_type':"PRODUCT FORM",
            'module_name':"ADMIN",'action':"EDIT",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            # content = serializer.data
            queryset = self.filter_queryset(self.get_queryset())
            if queryset._prefetch_related_lookups:
                instance._prefetched_objects_cache = {}
                prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Product with id [{kwargs["pk"]}] not found')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            product_id = instance.id
            instance.delete()
            for_tracking={'id':product_id,'sl_no':None,'content_type':"PRODUCT FORM",
            'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response({'message':"Successfully Deleted...."},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Product with id [{kwargs["pk"]}] not found')