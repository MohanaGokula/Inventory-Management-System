from rest_framework.settings import api_settings
from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.utils import *
from rms_ins.serializers import *
from django.contrib.auth.models import User,Permission,Group
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from django.db.models import ProtectedError
from rms_ins.permissions import IsSuperUser
from rest_framework.decorators import action  
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError

def assign_module_permissions(permissions):
    print(permissions,"permissions_fn")
    accounts=["view_accounts_reports","add_sales_invoice","view_sales_invoice","edit_sales_invoice","delete_sales_invoice",
    "add_grouping","view_grouping","edit_grouping","delete_grouping",
    "add_ledger","view_ledger","edit_ledger", "delete_ledger",
    "add_receipt_master","change_receipt_master","delete_receipt_master","view_receipt_master",
    "add_journal_master","change_journal_master","delete_journal_master","view_journal_master",
    "add_entity_bank_detail","view_entity_bank_detail","change_entity_bank_detail","delete_entity_bank_detail"]
    is_accounts =  any(item in permissions for item in accounts)
    print(is_accounts,"is_accounts")
    marketting=["add_quotation","view_quotation","edit_quotation","delete_quotation","add_sales_order_master",
            "change_sales_order_master","delete_sales_order_master","view_sales_order_master","view_marketting_reports",
            "add_entity_customer_detail","change_entity_customer_detail","view_entity_customer_detail",
            "delete_entity_customer_detail","add_entity_consignee_detail","change_entity_consignee_detail",
            "view_entity_consignee_detail","delete_entity_consignee_detail"]
    is_marketting =  any(item in permissions for item in marketting)
    qty_ctrl = ["add_moisture_correction_master","change_moisture_correction_master",
                "delete_moisture_correction_master","view_moisture_correction_master",
                "add_design_mix_master","change_design_mix_master","delete_design_mix_master",
                "view_design_mix_master","add_compressive_strength_master","change_compressive_strength_master", 
                "delete_compressive_strength_master","view_compressive_strength_master",
                "view_qty_ctrl_reports"]
    is_qty_ctrl =  any(item in permissions for item in qty_ctrl)
    planning=["add_work_schedule_master","change_work_schedule_master","delete_work_schedule_master", 
                "view_work_schedule_master","view_planning_reports"]
    is_planning =  any(item in permissions for item in planning)
    dispatch=["add_pump_clearance","view_pump_clearance","edit_pump_clearance","delete_pump_clearance", 
            "add_del_challan_master","change_del_challan_master","delete_del_challan_master",
            "view_del_challan_master","view_dispatch_reports"] 
    is_dispatch =  any(item in permissions for item in dispatch)
    gate=["view_gate_reports","add_gate_pass_master","change_gate_pass_master","delete_gate_pass_master",
        "view_gate_pass_master"]
    is_gate =  any(item in permissions for item in gate)
    purchase=["add_purchase_order","view_purchase_order","edit_purchase_order",
            "delete_purchase_order","add_purchase_invoice","view_purchase_invoice", 
            "edit_purchase_invoice","delete_purchase_invoice","view_purchase_reports",
            "add_entity_vendor_detail","view_entity_vendor_detail","change_entity_vendor_detail",
            "delete_entity_vendor_detail"]
    is_purchase =  any(item in permissions for item in purchase)
    store = ["view_store_reports","add_grn","change_grn","delete_grn","view_grn"]
    is_store =  any(item in permissions for item in store)
    transport =["view_transport_reports","add_equipment_master","change_equipment_master", 
    "delete_equipment_master","view_equipment_master"]
    is_transport = any(item in permissions for item in transport)
    check_list=[is_marketting,is_qty_ctrl,is_planning,is_dispatch,is_gate,is_accounts,is_transport,is_store,is_purchase]
    modules =["is_marketting","is_qty_ctrl","is_planning","is_dispatch","is_gate","is_accounts","is_transport","is_store","is_purchase"]
    for i in range(len(check_list)):
        if check_list[i]:
            permissions.append(modules[i])
    return permissions

def check_permissions(permissions):
    print(permissions,type(permissions),len(permissions),"permissions,type(permissions),len(permissions)")
    if (type(permissions) != list):
        raise DataValidationException(detail="Permissions must be a list.", code=400)
        
    if ((any(len(e.strip()) == 0 for e in permissions)) or (len(permissions) == 0)):
        raise DataValidationException(detail="Please provide valid permissions.", code=400)
        
    else:
        not_valid_perms_list=[]
        for i in permissions:
            permission_object = Permission.objects.filter(codename=i).exists()
            if not permission_object:
                not_valid_perms_list.append(i)
        if not_valid_perms_list:
            not_valid_perms = ','.join([str(elem) for elem in not_valid_perms_list])
            raise DataValidationException(detail=f"Following permissions are not available[{not_valid_perms}]", code=409)
            
        else:
            content='valid'
            s=status.HTTP_200_OK
            return content,s
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class=GroupSerializer
    permission_classes =[IsSuperUser]
    for_tracking={'content_type':"PERMISSION FORM",'module_name':"ADMIN"}

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            permissions = self.request.data.get("permissions", [])
            print(permissions,type(permissions),len(permissions))
            content,s = check_permissions(permissions)
            print(content,s,"content,s")
            if content == 'valid':
                serializer.save()
                group = Group.objects.latest('id')
                group.permissions.set([])
                permissions=assign_module_permissions(permissions)
                permission_objects = Permission.objects.filter(codename__in=permissions)
                for i in permission_objects:
                    group.permissions.add(i.id)
                # group.permissions.set(permission_objects)
                group_id = group.id
                for_tracking={'id':str(group_id),'sl_no':None,
                'content_type':"PERMISSION FORM",
                'action':"CREATE",'module_name':"ADMIN",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content={"message": f"Created a new group: {group.name}"}
                s=status.HTTP_201_CREATED
            return Response(content,status=s)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
            
    def list(self, request):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        print(name,"name")
        if name is not None:
            group_list = qs.filter(name__iexact=name).values('id','name')
        else:
            group_list = qs.order_by('id').values('id','name')
        return Response({'group_list':group_list},status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            instance.permissions.set([])
            permissions = self.request.data.get("permissions", [])
            content,s = check_permissions(permissions)
            print(content,s,"content,s")
            if content == 'valid':
                serializer.save()
                permissions=assign_module_permissions(permissions)
                permission_objects = Permission.objects.filter(codename__in=permissions)
                for i in permission_objects:
                    instance.permissions.add(i.id)
                for_tracking={'id':str(instance.id),
                'sl_no':None,'content_type':"PERMISSION FORM",
                'action':"EDIT",'module_name':"ADMIN",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content={"message": f"Updated permissions and name for group: {instance.name}"}
                s=status.HTTP_200_OK
            return Response(content,status=s)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Group with id [{kwargs["pk"]}] not found')

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            group_id = instance.id
            print(instance.user_set.all(),"instance.user_set.all()")
            assigned_for_user = instance.user_set.exists()
            if assigned_for_user:
                raise DataValidationException(detail = "Can not delete this group because this group is assigned for user.", code=403);
                
            else:
                instance.delete()
                for_tracking={'id':str(group_id),'sl_no':None,'content_type':"PERMISSION FORM",
                'action':"DELETE",'module_name':"ADMIN",'plant_name':None}
                tracking=handle_tracking(self.request,for_tracking)
                content={'message':"successfully deleted."}
                s=status.HTTP_204_NO_CONTENT
            return Response(content,status=s)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Group with id [{kwargs["pk"]}] not found')
        


                
            
    