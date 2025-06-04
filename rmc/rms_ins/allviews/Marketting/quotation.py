from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.serializers import *
from rms_ins.utils import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rms_ins.permissions import CheckPermission
from django.db.models import F
from rest_framework.decorators import action
from datetime import datetime
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = entity_enquiry_master.objects.all()
    serializer_class = EntityEnquiryMasterSerializer
    permission_classes =[CheckPermission]
    required_perms = {
         'GET': ['rmc.view_quotation'],
         'POST': ['rmc.add_quotation'],
         'PUT': ['rmc.edit_quotation'],
         'DELETE': ['rmc.delete_quotation']
    }
    for_tracking={'content_type':"QUOTATION FORM",'module_name':"MARKETTING"}
    
    @action(detail=False)
    def quotation_number(self,request):
        try:
            query_date = self.request.query_params.get('quotation_date')
            query_1 = entity_enquiry_master.objects.last()#filter(status = 1).
            query_2 = entity_enquiry_master.objects.values("ref_no")
            print(query_1,"query1")
            print(query_2,"query_2")
            needed_params = {'query_date':query_date,'query_1':query_1,'voucher_type':'quotation','query_2':query_2,
            'date_field_name':'ref_date','slno_field_name':'ref_no','form_name':"Quotation",'date_name':"Quotation date"
            ,'exception':EntityNotFoundException,'plant_id':'','query_3':''}
            result = get_slno_prefix(needed_params)
            return Response({'quotation_no':result['sl_no'],'prefix':result['prefix']},status = status.HTTP_200_OK)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
   
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            print(self.request.data,type(self.request.data),"data before")
            data =self.request.data
            verify_enquiry_master(data)
            enquiry_date = data['enquiry_date']
            if type(enquiry_date) is not str:
                raise DataValidationException('Enquiry_date type must be string.',code =400)
            if enquiry_date:
                print(enquiry_date,type(enquiry_date),"enquiry_date")
                try:
                    enquiry_date = (datetime.strptime(enquiry_date, "%d-%m-%Y").date())
                except ValueError:
                    raise DataValidationException('Enquiry_date is Invalid. Because,Enquiry_date must be in the format of dd-MM-yyyy.Ex:31-07-2023',code =409)
            else:
                print("else enquiry",enquiry_date,type(enquiry_date))
            query_1 = entity_enquiry_master.objects.last()#.filter(status = 1)
            query_2 = entity_enquiry_master.objects.values("ref_no")
            needed_params = {'query_date':data['quotation_date'],'query_1':query_1,'voucher_type':'quotation','query_2':query_2,
            'date_field_name':'ref_date','slno_field_name':'ref_no','form_name':"Quotation",'date_name':"Quotation date"
            ,'exception':DataValidationException,'plant_id':'','query_3':''}
            result = get_slno_prefix(needed_params)
            print(result,"result")
            if ((data['quotation_no'] != result['sl_no'])):
                data['quotation_no'] = result['sl_no']
            if (data['prefix'] != result['prefix']):
                data['prefix'] = result['prefix']
            print(data,"data after")
            serializer.is_valid(raise_exception=True)
            order_list = data['order_list']
            if type(order_list) is not list:
                raise DataValidationException('order_list must be a list.',code = 400) 
            elif len(order_list) == 0:
                raise DataValidationException('order_list must not be empty.',code = 409)
            else:
                verify_enquiry_detail(order_list)
            enquiry_detail_serializer = EntityEnquiryDetailSerializer(data=order_list, many=True)
            enquiry_detail_serializer.is_valid(raise_exception=True)
            a=serializer.save(created_by=self.request.user)
            n=enquiry_detail_serializer.save(created_by=self.request.user,enquiry_master_id=a)
            created_id_list=[x.id for x in n]
            created_ids=','.join(map(str,created_id_list))
            for_tracking={'id':"enquiry_master_id : "+ str(a.id) + ", enquiry_detail_id : "+ created_ids,
            'sl_no':a.ref_no,'content_type':"QUOTATION FORM",
            'action':"CREATE",'module_name':"MARKETTING",'plant_name':entity_master.objects.get(id=a.entity_company_id.id)}
            tracking=handle_tracking(self.request,for_tracking)
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e) ,code=400)
        except ValueError as e:
            raise DataValidationException(str(e),code=400)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except TypeError as e:
            raise DataValidationException(str(e),code=400)

    def list(self, request):
        try:
            quotation_list = entity_enquiry_detail.objects.all().order_by('id').values('id','product','quantity','rate','delivery_mode'
            ,amount=F('amt'))
            for i in quotation_list:
                detail = entity_enquiry_detail.objects.get(id= i['id'])
                i['company']= {'id':detail.enquiry_master_id.entity_company_id.id,'name':detail.enquiry_master_id.entity_company_id.entity_name}
                customer = entity_customer_detail.objects.get(entity_id =detail.enquiry_master_id.entity_id)
                i['customer'] = {'id':customer.entity_id.id,'name':customer.entity_id.entity_name,
                'salesrep':{'id':customer.entity_salesrep_id.id,'name':customer.entity_salesrep_id.entity_name}}
                consignee = entity_consignee_detail.objects.get(entity_id = detail.enquiry_master_id.entity_consignee_id)
                i['consignee'] ={'id':consignee.entity_id.id,'name':consignee.entity_id.entity_name,'project_name':consignee.project_name}
                product = product_master.objects.get(id = i['product'])
                i['product'] = {'id':product.id,'name':product.name}
                i['quotation_no'] = detail.enquiry_master_id.ref_no
                i['prefix'] = detail.enquiry_master_id.prefix
                i['quotation_date'] = detail.enquiry_master_id.ref_date.strftime("%d-%m-%Y")
                i['id'] = detail.enquiry_master_id.id
                i['status'] = convert_status(detail.enquiry_master_id.status)
                i['concrete_structure']={
                    'id':detail.concrete_structure.id,'name':detail.concrete_structure.entity_name
                }
                i['tax']={
                    'id':detail.tax.id,'name':detail.tax.name
                }
            return Response({'quotation_list':quotation_list},status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            if instance.enquiry_date:
                enquiry_date = instance.enquiry_date.strftime("%d-%m-%Y")
            else:
                enquiry_date = serializer.data['enquiry_date']
            details = list(instance.entity_enquiry_detail_set.all().order_by('id').values('id','quantity',
                    'rate','delivery_mode','user_remarks',amount=F('amt')))
            for  d in details:
                detail = entity_enquiry_detail.objects.get(id=d['id'])
                d['concrete_structure'] = {'id': detail.concrete_structure.id,'name': detail.concrete_structure.entity_name}
                d['product'] = {'id':detail.product.id,
                                'name':detail.product.name,
                                'quantity': detail.product.quantity,
                                'user_remarks':detail.product.user_remarks,
                                'status': convert_status(detail.product.status),
                                'category': {
                                    "id": detail.product.category_detail.id,
                                    "name": detail.product.category_detail.entity_name
                                },
                                'unit': {
                                    "id": detail.product.unit.id,
                                    "name": detail.product.unit.name,
                                    "symbol": detail.product.unit.symbol
                                }
                                }
                d['tax'] = {'id':detail.tax.id,'name':detail.tax.name}
            content={
                    "id":serializer.data['id'],
                    "quotation_no": serializer.data['ref_no'],
                    "quotation_date": instance.ref_date.strftime("%d-%m-%Y"),
                    "prefix": serializer.data['prefix'],
                    "enquiry_no": serializer.data['enquiry_no'],
                    "enquiry_date":enquiry_date,
                    "is_tax_included": serializer.data['is_tax_included'],
                    "terms_condition": serializer.data['terms_condition'],
                    "company": {
                        "id": instance.entity_company_id.id,
                        "name": instance.entity_company_id.entity_name
                    },
                    "customer": {
                        "id": instance.entity_id.id,
                        "name": instance.entity_id.entity_name
                    },
                    "consignee": {
                        "id":  instance.entity_consignee_id.id,
                        "name": instance.entity_consignee_id.entity_name
                    },
                    "status": serializer.data['status'],
                    "order_list": details
                    }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Quotation with id [{kwargs["pk"]}] not found.')
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            enquiry_master_id=instance.id
            quotation_no = instance.ref_no
            company = instance.entity_company_id.id
            enquiry = instance.enquiry_id.all()
            if instance.status == 1:
               raise DataValidationException(detail="You can not delete this Quotation as it is active",code = 403)
            elif enquiry:
                raise DataValidationException(detail='You can not delete this Quotation as it is linked to SO.', code=403) 
            else:
                instance.delete()
                a=entity_enquiry_detail.objects.filter(enquiry_master_id=enquiry_master_id)
                enquiry_detail_ids=','.join(map(str,(list(a.values_list('id',flat=True)))))
                for i in a:
                    i.delete() 
                for_tracking={'id':"enquiry_master_id : "+ str(enquiry_master_id) + ", enquiry_detail_id : "+ enquiry_detail_ids,
                'sl_no':quotation_no,'content_type':"QUOTATION FORM",
                'action':"DELETE",'module_name':"MARKETTING",'plant_name':entity_master.objects.get(id= company)}
                tracking=handle_tracking(self.request,for_tracking)
                return Response({'message':"Successfully Deleted"},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Quotation with id [{kwargs["pk"]}] not found.')
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            enquiry = instance.enquiry_id.all()
            print(enquiry,"enquiry")# To check whether this quotation id is connected to SO or not
            if enquiry:
                raise DataValidationException(detail='This quotation is linked to SO .So,You can not edit this Quotation.', code=403) 
            else:
                old_details_ids =list(instance.entity_enquiry_detail_set.all().values_list('id', flat=True))
                # 'old_details_ids' is a list of this quotation's detail ids.
                print(old_details_ids,type(old_details_ids)) 
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                data =self.request.data
                verify_enquiry_master(data)
                enquiry_date = data['enquiry_date']
                if type(enquiry_date) is not str:
                    raise DataValidationException('Enquiry_date type must be string.',code =400)
                if enquiry_date:
                    print(enquiry_date,type(enquiry_date),"enquiry_date")
                    try:
                        enquiry_date = (datetime.strptime(enquiry_date, "%d-%m-%Y").date())
                    except ValueError:
                        raise DataValidationException('Enquiry_date is Invalid. Because,Enquiry_date must be in the format of dd-MM-yyyy.Ex:31-07-2023',code =409)
                else:
                    print("else enquiry",enquiry_date,type(enquiry_date))
                serializer.is_valid(raise_exception=True)
                order_list = data['order_list']
                if type(order_list) is not list:
                    raise DataValidationException('order_list must be a list.',code = 400)
                elif len(order_list) == 0:
                    raise DataValidationException('Order_list must not be empty.',code = 409)
                else:
                    verify_enquiry_detail(order_list)
                enquiry_detail_serializer = EntityEnquiryDetailSerializer(data=order_list,many=True)
                enquiry_detail_serializer.is_valid(raise_exception=True)
                serializer.save(modified_by=self.request.user.username)
                actions_done=''
                print(data,"request.data")
                edited_ids_list = []
                newly_created_ids_list = []
                # to_delete_ids_list = []
                for i in range(len(order_list)):
                    if order_list[i]['id']:
                        # update the detail objects with ids
                        print(type(order_list[i]['id']),"type(order_list[i]['id'])")
                        enquiry_detail=entity_enquiry_detail.objects.get(id=order_list[i]['id'])
                        enquiry_detail_serializer = EntityEnquiryDetailSerializer(enquiry_detail,data=data['order_list'][i])
                        enquiry_detail_serializer.is_valid(raise_exception=True)
                        enquiry_detail_serializer.save(modified_by=self.request.user.username)
                        edited_ids_list.append(int(order_list[i]['id']))
                    else:
                        print("else")
                        # create new detail objects
                        detail_serializer = EntityEnquiryDetailSerializer(data=order_list[i])
                        detail_serializer.is_valid(raise_exception=True)
                        n= detail_serializer.save(created_by=self.request.user.username,enquiry_master_id=instance)
                        newly_created_ids_list.append(n.id)
                        
                if edited_ids_list:
                    print(old_details_ids,"old_details_ids",type(old_details_ids))
                    print(edited_ids_list,"edited_ids_list",type(edited_ids_list))
                    to_delete_ids_list = list(set(old_details_ids) - set(edited_ids_list))  
                    print(to_delete_ids_list,"to_delete_ids_list",type(to_delete_ids_list))
                    edited_dtl_ids = ','.join([str(elem) for elem in edited_ids_list])
                    actions_done=actions_done +' '+ "EDIT" 
                else:
                    edited_dtl_ids = "NO"
                    to_delete_ids_list = old_details_ids
                if newly_created_ids_list:
                    newly_created_ids = ','.join([str(elem) for elem in newly_created_ids_list])
                    actions_done=actions_done + ', ' +"CREATE PRODUCT DETAILS during edit"
                else:
                    newly_created_ids ="NO"
                deleted_ids_list = []
                if to_delete_ids_list:
                    print(to_delete_ids_list,"to_delete_ip_ids_list")
                    print(type(to_delete_ids_list),"type(to_delete_ip_ids_list)")
                    for i in to_delete_ids_list:
                        print(i,"todelete id")
                        to_delete_id = i
                        a=entity_enquiry_detail.objects.get(id=i)
                        a.delete()
                        deleted_ids_list.append(to_delete_id)
                    deleted_ids = ','.join([str(elem) for elem in deleted_ids_list])
                    actions_done=actions_done +' ,'+"DELETE PRODUCT DETAILS during edit "
                else:
                    deleted_ids = "NO"
                idlist= "Edited PRODUCT DETAIL IDS:" + ' ' + edited_dtl_ids + ' ,' +  "Deleted PRODUCT DETAIL IDS:" + ' ' + deleted_ids + ' ,' +"Created PRODUCT DETAILS IDS:" + ' ' + newly_created_ids
                for_tracking={'id':"enquiry_master_id : "+ str(instance.id) + ", enquiry_detail_id : "+ idlist,
                'sl_no':instance.ref_no,'content_type':"QUOTATION FORM",
                'action':actions_done,'module_name':"MARKETTING",'plant_name':entity_master.objects.get(id=instance.entity_company_id.id)}
                tracking=handle_tracking(self.request,for_tracking)
                queryset = self.filter_queryset(self.get_queryset())
                if queryset._prefetch_related_lookups:
                    instance._prefetched_objects_cache = {}
                    prefetch_related_objects([instance], *queryset._prefetch_related_lookups)
                return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e) ,code=400)
        except ValueError as e:
            raise DataValidationException(str(e))
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Quotation with id [{kwargs["pk"]}] not found.')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
        except TypeError as e:
            raise DataValidationException(str(e),code=400)
    
    @action(detail=False,url_path="(?P<quotation_id>[0-9]+)/products")
    def products(self,request,quotation_id):
        try:
            print(quotation_id,"quotation_id")
            instance = entity_enquiry_master.objects.get(id = quotation_id)
            details = list(instance.entity_enquiry_detail_set.all().order_by('id').values('id','quantity',
                'rate','delivery_mode','user_remarks',amount=F('amt')))
            for  d in details:
                detail = entity_enquiry_detail.objects.get(id=d['id'])
                d['concrete_structure'] = {'id': detail.concrete_structure.id,
                'name': detail.concrete_structure.entity_name}
                d['product'] = {
                                'id':detail.product.id,
                                'name':detail.product.name,
                                'quantity':detail.product.quantity,
                                'user_remarks':detail.product.user_remarks,
                                'status':convert_status(detail.product.status),
                                'category':{'id': detail.product.category_detail.id,
                                            'name': detail.product.category_detail.entity_name},
                                'unit':{'id': detail.product.unit.id,
                                        'name': detail.product.unit.name,
                                        'symbol':detail.product.unit.symbol}
                                }
                d['tax'] = {'id':detail.tax.id,'name':detail.tax.name}
            return Response({"quotation_product_list": details},status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=f'Quotation with id [{quotation_id}] not found.')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

