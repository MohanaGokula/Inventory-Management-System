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

class VendorViewSet(viewsets.ModelViewSet):
    queryset = entity_master.objects.filter(entity_type='supplier')
    serializer_class = EntityMasterSerializer
    permission_classes =[CheckPermission]
    required_perms = {
        'GET': ['rmc_ins.view_entity_vendor_detail'],
        'POST': ['rmc_ins.add_entity_vendor_detail'],
        'PUT': ['rmc_ins.change_entity_vendor_detail'],
        'DELETE': ['rmc_ins.delete_entity_vendor_detail']
    }
    for_tracking={'content_type':"VENDOR FORM",'module_name':"PURCHASE"}
    valid_entity_types=["supplier"]
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            vendor_serializer = EntityVendorDetailSerializer(data=self.request.data)
            vendor_serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user,entity_type="supplier")
            entity_id=entity_master.objects.latest('id').id
            vendor_serializer.save(created_by=self.request.user,entity_id=entity_master.objects.get(id=entity_id))
            entity_vendor_id=entity_vendor_detail.objects.latest('id').id
            for_tracking={'id':"entity_id : "+ str(entity_id) + ", entity_vendor_detail_id : "+ str(entity_vendor_id),'sl_no':None,
            'content_type':"VENDOR FORM",'module_name':"PURCHASE",
            'action':"CREATE",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            content=serializer.data
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def list(self, request):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        print(name,"name")
        if name is not None:
            vendor_list =  queryset.filter(entity_name__iexact=name).values('id','entity_name','address_1','address_2','address_3','status','phone_number','mobile_number','email_id')
        else:
            vendor_list = queryset.values('id','entity_name','address_1','address_2','address_3','status','phone_number','mobile_number','email_id')
        for i in vendor_list:
            i['status']=convert_status(i['status'])
        return Response({'vendor_list':vendor_list},status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            vendor = entity_vendor_detail.objects.get(entity_id=instance.id)
            content={"id": serializer.data['id'],
                    "entity_name": serializer.data['entity_name'],
                    "address_1": serializer.data['address_1'],
                    "address_2": serializer.data['address_2'],
                    "address_3": serializer.data['address_3'],
                    "pincode": serializer.data['pincode'],
                    "state": serializer.data['state'],
                    "phone_number": serializer.data['phone_number'],
                    "mobile_number": serializer.data['mobile_number'],
                    "email_id": serializer.data['email_id'],
                    "pan_no": serializer.data['pan_no'],
                    "gst_no": serializer.data['gst_no'],
                    "user_remarks": serializer.data['user_remarks'],
                    "status": serializer.data['status'],
                    "contact_person":serializer.data['contact_person'],
                    "contact_mobile_no":serializer.data['contact_mobile_no'],
                    "contact_email_id":serializer.data['contact_email_id'],
                    "contact_designation":serializer.data['contact_designation'],
                    "ven_bank_name":vendor.ven_bank_name,
                    "ven_bank_branch":vendor.ven_bank_branch,
                    "ven_bank_acc_no":vendor.ven_bank_acc_no,
                    "ven_bank_ifsc":vendor.ven_bank_ifsc,
                    "vendor_type":{"id":vendor.vendor_type.id ,"name":vendor.vendor_type.entity_name}
                    }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Vendor with id [{kwargs["pk"]}] not found')
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            vendor = entity_vendor_detail.objects.get(entity_id=instance.id)
            vendor_serializer = EntityVendorDetailSerializer(vendor,data=self.request.data)
            vendor_serializer.is_valid(raise_exception=True)
            serializer.save(modified_by=self.request.user.username)
            vendor_serializer.save(modified_by=self.request.user.username)
            for_tracking={'id':"entity_id : "+ str(instance.id) + ", entity_vendor_detail_id : "+ str(vendor.id),'sl_no':None,
            'content_type':"VENDOR FORM",'module_name':"PURCHASE",
            'action':"EDIT",'plant_name':None}
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
            raise EntityNotFoundException(detail=f'Vendor with id [{kwargs["pk"]}] not found')
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            vendor_id=instance.id
            instance.delete()
            a=entity_vendor_detail.objects.get(entity_id=vendor_id)
            vendor_dtl_id=a.id
            a.delete()    
            for_tracking={'id':"entity_id : "+ str(vendor_id) + ", entity_vendor_detail_id : "+ str(vendor_dtl_id),
            'sl_no':None,'content_type':"VENDOR FORM",'module_name':"PURCHASE",
            'action':"DELETE",'plant_name':None}
            tracking=handle_tracking(self.request,for_tracking)
            return Response({'message':"Successfully Deleted...."},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Vendor with id [{kwargs["pk"]}] not found')
