from rest_framework import viewsets,status
from rms_ins.models import *
from rms_ins.serializers import *
from rms_ins.utils import *
from rest_framework.response import Response
from django.contrib.auth.models import User
from rms_ins.permissions import HasUserPermission
from django.db.models import F,Sum
from rest_framework.decorators import action
from datetime import datetime
from django.http.response import Http404
from rms_ins.exceptions import (EntityNotFoundException, DataValidationException)
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import json
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from rms_ins.serializers import *
from django.core.mail import EmailMessage
from ims.settings import EMAIL_HOST_USER
from num2words import num2words

def order(purchase_order_list):
    for i in purchase_order_list.copy():
        i['order_date'] = i['order_date'].strftime("%d-%m-%Y")
        i['validity_date'] = i['validity_date'].strftime("%d-%m-%Y")
        i['is_tax_included'] =  convert_status(i['is_tax_included'])
        i['is_approved'] = convert_status(i['is_approved'])
        i['status'] = convert_status(i['status'])
        eo_master = entity_order_master.objects.get(id = i['id'])
        i['company'] =  {
                "id": eo_master.entity_company_id.id,
                "name": eo_master.entity_company_id.entity_name
            }
        i['vendor'] =  {
                "id": eo_master.entity_id.id,
                "name": eo_master.entity_id.entity_name
            }
        plant_id=eo_master.entity_consignee_id
        alias_name=entity_plant_detail.objects.get(entity_id=plant_id).plant_alias
        # print(alias_name,"alias name")
        i['plant'] =  {
                "id": eo_master.entity_consignee_id.id,
                "name": eo_master.entity_consignee_id.entity_name,
                "alias":alias_name
            }
        order_list=list(entity_order_detail.objects.filter(entity_order_id=i['id']).values('id','quantity','rate','amount','user_remarks'))
        print(order_list,'order_list')
        balance_list=[]
        for  d in order_list.copy():
            detail=gmr_detail.objects.filter(order_detail=d['id']).aggregate(total_accepted_qty=Sum('accepted_qty'))['total_accepted_qty']
            print(detail,"details")
            if detail is None:
                detail = 0
            balance_qty= d['quantity']-detail
            print(balance_qty,'subbbbbbbbbb')
            if (balance_qty>0):
                print("balance_qty>0")
                eo_detail = entity_order_detail.objects.get(id = d['id'])
                print(eo_detail,"eo_detail")
                d['balance_qty']=balance_qty
                print(d['balance_qty'],"d.balance_qty")
                d['product'] = {'id':eo_detail.product.id,
                    'name':eo_detail.product.name,
                    'quantity': eo_detail.product.quantity,
                    'user_remarks':eo_detail.product.user_remarks,
                    'status': convert_status(eo_detail.product.status),
                    'category': {
                        "id": eo_detail.product.category_detail.id,
                        "name": eo_detail.product.category_detail.entity_name
                    },
                    'unit': {
                        "id": eo_detail.product.unit.id,
                        "name": eo_detail.product.unit.name,
                        "symbol": eo_detail.product.unit.symbol
                    }
                }
                d['tax']={
                    'id':eo_detail.tax.id,
                    'name':eo_detail.tax.name
                }
            else:
                print('balance qty is not greater than zero')
                order_list.remove(d)
        print(len(order_list),order_list,"len(order_list)")
        i['order_list'] =order_list
        if len(order_list) == 0: 
            purchase_order_list.remove(i)
    print(purchase_order_list,"purchase_order_list")
    return purchase_order_list

def send_email(company_id,order_no,prefix):
    try:
        ApprSetting=approval_setting_master.objects.filter(voucher_type='purchase_order')
        if ApprSetting:
            print("ApprSetting exists")
            p=approval_setting_master.objects.get(voucher_type='purchase_order',entity_company_id = company_id)
            print("appr object",p)
            is_mail_needed = p.is_mail_needed
            mail_ids = p.mail_ids
            if is_mail_needed == 1 and mail_ids:
                print(mail_ids,"mail_ids")
                mail_ids_list = mail_ids.split(",") 
                print(mail_ids_list,"Mail_ids_list")
                print(type(mail_ids_list),"type(Mail_ids_list)")
                template = get_template('report/sales_order_pdf_email.html')
                hdr = entity_order_master.objects.get(entity_company_id__id = company_id,order_no = order_no,prefix=prefix,entity_order_type='purchase')
                # print(hdr,"hdr")
                company_detail = entity_company_detail.objects.get(entity_id = company_id)
                plant_detail = entity_plant_detail.objects.get(entity_id = hdr.entity_consignee_id)
                vendor_detail = entity_vendor_detail.objects.get(entity_id= hdr.entity_id)
                items = entity_order_detail.objects.filter(entity_order_id = hdr)
                # print(items,"items")
                context={'items':items,'hdr':hdr,'company_detail':company_detail,
                'plant_detail':plant_detail,'vendor_detail':vendor_detail}
                html=template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
                pdf = result.getvalue()
                # print(pdf,"pdf")
                filename='PurchaseOrder' + '.pdf'
                mail_subject='Purchase order'
                email=EmailMessage('Purchaseorder waiting for approval',  'https://litvikrmcv1.litvik.in/', EMAIL_HOST_USER, mail_ids_list)
                # print("mailids_list")
                email.attach(filename,pdf,'application/pdf')
                email.send(fail_silently= False)
                print("emailsend")
            else:
                print("NO MAIL NEEDED")
    except ObjectDoesNotExist:
        raise DataValidationException('Create entry in approval settings form for voucher type purchase order for this company.',code = 409)
    except approval_setting_master.MultipleObjectsReturned as e:
        raise DataValidationException(str(e),code=409)

def is_approval_settings(company_id):
    try:
        ApprSetting = approval_setting_master.objects.filter(voucher_type='purchase_order')
        if ApprSetting:
            p = approval_setting_master.objects.get(voucher_type='purchase_order', entity_company_id=company_id)
            is_appr_needed = p.is_appr_needed
            if is_appr_needed == 0:
                is_approved = 1
            else:
                is_approved = 0
            print(is_approved,"is_approved")
            return is_approved
        else:
            raise DataValidationException('Create entry in approval settings form for voucher type purchase order for this company.', code=409)
    except ObjectDoesNotExist:
        raise DataValidationException('Create entry in approval settings form for voucher type purchase order for this company.', code=409)
    except approval_setting_master.MultipleObjectsReturned as e:
        raise DataValidationException(str(e), code=409)

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = entity_order_master.objects.filter(entity_order_type='purchase')
    serializer_class = PurchaseOrderMasterSerializer
    for_tracking={'content_type':"PURCHASE ORDER FORM",'module_name':"PURCHASE"}
    
    @action(detail=False)
    def purchase_order_number(self,request):
        try:
            query_date = self.request.query_params.get('purchase_order_date')
            print("purchase_order_date",query_date,type(query_date))
            query_1 = entity_order_master.objects.filter(entity_order_type= 'purchase').last()#.filter(status = 1)
            query_2 = entity_order_master.objects.filter(entity_order_type= 'purchase').values("order_no")
            print(query_1,"query1")
            print(query_2,"query_2")
            needed_params = {'query_date':query_date,'query_1':query_1,'voucher_type':'purchase_order','query_2':query_2,
            'date_field_name':'order_date','slno_field_name':'order_no','form_name':"Purchase order",'date_name':"Purchase order date",
            'exception':EntityNotFoundException,'plant_id':'','query_3':''}
            result = get_slno_prefix(needed_params)
            return Response({'purchase_order_no':result['sl_no'],'prefix':result['prefix']},status = status.HTTP_200_OK)
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)

    def create(self, request, *args, **kwargs):
        try:
            required_perms = ['rmc.add_purchase_order']
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):
                raise DataValidationException("You don't have permission to create Purchase order.",code=403)
            serializer = self.get_serializer(data=request.data)
            data = request.data
            if not 'indent_no' in data.keys() :
                raise DataValidationException("KeyError : indent_no",code=400)
            if not 'quotation_no' in data.keys():
                raise DataValidationException("KeyError : quotation_no",code=400)
            if not 'terms_and_condition' in data.keys():
                raise DataValidationException("KeyError : terms_and_condition",code=400)
            verify_entity_master(data)
            query_1 = entity_order_master.objects.filter(entity_order_type= 'purchase').last()
            print(query_1,"q1")
            query_2 = entity_order_master.objects.filter(entity_order_type= 'purchase').values("order_no")
            print(query_2)
            needed_params = {'query_date': data['order_date'], 'query_1': query_1, 'voucher_type': 'purchase_order',
                            'query_2': query_2,
                            'date_field_name': 'order_date', 'slno_field_name': 'order_no',
                            'form_name': "Purchase order", 'date_name': "Purchase order date",
                            'exception': EntityNotFoundException, 'plant_id': '', 'query_3': ''}
            result = get_slno_prefix(needed_params)
            print("Result", result)
            if data['prefix'] != result['prefix']:
                data['prefix'] = result['prefix']
            if (data['order_no'] != result['sl_no']):
                data['order_no'] = result['sl_no']
            serializer.is_valid(raise_exception=True)
            order_list = data['order_list']
            print(order_list)
            print(order_list)
            if type(order_list) is not list:
                raise DataValidationException('order_list must be a list.',code = 400) 
            elif len(order_list) == 0:
                raise DataValidationException('order_list must not be empty.',code = 409)
            else:
                verify_entity_detail(order_list)
                total_order_amount = sum(float(d.get('amount', 0)) for d in order_list)
                # print(total_order_amount,type(total_order_amount),"total_order_amount")
                # print(data['order_amount'],type(data['order_amount']),"order_amount")
                if float(data['order_amount']) != float(total_order_amount):
                   raise DataValidationException("Total purchase order amount must be equal to sum of product amounts.",code = 409)
            entity_detail_serializer = PurchaseOrderDetailSerializer(data=order_list, many=True)
            entity_detail_serializer.is_valid(raise_exception=True)
            is_approved=1
            # is_approved = is_approval_settings(data["company_id"])
            a = serializer.save(created_by=self.request.user,is_approved=is_approved,entity_order_type='purchase')
            n = entity_detail_serializer.save(created_by=self.request.user, entity_order_id=a)
            created_id_list=[x.id for x in n]
            created_ids=','.join(map(str,created_id_list))
            for_tracking={'id':"entity_order_master_id : "+ str(a.id) +", entity_order_detail_id : "+(created_ids) ,
            'sl_no':a.order_no,'content_type':"PURCHASE ORDER FORM",
            'action':"CREATE",'module_name':"PURCHASE",'plant_name':entity_master.objects.get(id=a.entity_company_id.id)}
            tracking=handle_tracking(self.request,for_tracking)
            send_email(a.entity_company_id.id,a.order_no,a.prefix)
            return Response(status=status.HTTP_201_CREATED, headers=get_success_headers(serializer.data))
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e), code=400)
        except ValueError as e:
            raise DataValidationException(str(e), code=400)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
        except ValidationError as e:
            raise DataValidationException(detail=str(e), exception=e)
        except TypeError as e:
            raise DataValidationException(str(e), code=400)
        
    def list(self, request):
        try:
            required_perms = ['rmc.view_purchase_order']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):     
                return Response({'purchase_order_list': []})
                            
            company_id = request.query_params.get('company_id') 
            print(company_id, "company_id")
            if company_id is not None:
                purchase_order_list = entity_order_detail.objects.filter(entity_order_id__entity_company_id=company_id,entity_order_id__entity_order_type='purchase').order_by('id').values('id', 'product', 'quantity', 'rate', 'amount', 'is_approved', 'status')
            else:
                purchase_order_list = entity_order_detail.objects.filter(entity_order_id__entity_order_type='purchase').order_by('id').values('id', 'product', 'quantity', 'rate', 'amount', 'is_approved', 'status')
            
            for i in purchase_order_list:
                detail = entity_order_detail.objects.get(id=i['id'])
                a = detail.entity_order_id
                print(a,'order_id')
                i['id'] = detail.entity_order_id.id
                i['order_no'] = a.order_no
                i['prefix'] = a.prefix
                i['order_date'] = a.order_date.strftime("%d-%m-%Y")
                i['order_time'] = a.order_time
                i['company'] = {'id': a.entity_company_id.id, 'name': a.entity_company_id.entity_name}
                i['vendor'] = {'id': a.entity_id.id, 'name': a.entity_id.entity_name}
                product = product_master.objects.get(id=i['product'])
                i['product'] = {
                    'id': product.id,
                    'name': product.name,
                    'quantity': product.quantity,
                    'user_remarks': product.user_remarks,
                    'status': convert_status(product.status),
                    'category': {
                        "id": product.category_detail.id,
                        "name": product.category_detail.entity_name
                    },
                    'unit': {
                        "id": product.unit.id,
                        "name": product.unit.name,
                        "symbol": product.unit.symbol
                    }
                }
                i['quantity'] = detail.quantity
                i['rate'] = detail.rate
                i['amount'] = detail.amount
                i['is_approved'] = convert_status(a.is_approved)
                i['status'] = convert_status(a.status)
            return Response({'purchase_order_list': purchase_order_list}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
        except ValueError as e:
            raise DataValidationException(str(e),code = 400)

    def retrieve(self, request, *args, **kwargs):
        try:
            required_perms = ['rmc.view_purchase_order']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):                               
                raise DataValidationException("You don't have permission to view purchase orders.",code=403)
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            plant = entity_plant_detail.objects.get(entity_id = instance.entity_consignee_id)
            details = list(instance.entity_order_detail_set.all().order_by('id').values('id','product',
                    'quantity','rate','amount','user_remarks'))
            for  d in details:
                detail = entity_order_detail.objects.get(id=d['id'])
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
                d['tax'] = {
                    'id':detail.tax.id,
                    'name':detail.tax.name
                    }
            content={
                "id":serializer.data['id'],
                "company": {
                    "id": instance.entity_company_id.id,
                    "name": instance.entity_company_id.entity_name
                },
                "vendor":{
                    "id":instance.entity_id.id,
                    "name":instance.entity_id.entity_name
                },
                "plant":{
                    "id":instance.entity_consignee_id.id,
                    "name":instance.entity_consignee_id.entity_name,
                    "alias":plant.plant_alias
                },
                "order_no":instance.order_no,
                "order_date":instance.order_date.strftime("%d-%m-%Y"),
                "order_time":instance.order_time,
                "prefix":instance.prefix,
                "quotation_no":instance.quotation_no,
                "quotation_date":instance.quotation_date.strftime("%d-%m-%Y"),
                "indent_no":instance.indent_no,
                "indent_date":instance.indent_date.strftime("%d-%m-%Y"),
                "pay_terms":instance.pay_terms,
                "validity_date":instance.validity_date.strftime("%d-%m-%Y"),
                "transport_mode":instance.transport_mode,
                "is_tax_included":serializer.data['is_tax_included'],
                "is_approved":convert_status(serializer.data['is_approved']),
                "status": serializer.data['status'],
                "order_amount":instance.order_amount,
                "terms_and_condition":instance.terms_condition,
                "order_list":details
            }
            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Purchase order with id [{kwargs["pk"]}] not found.')
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
    
    def update(self, request, *args, **kwargs):
        try:
            required_perms = ['rmc.edit_purchase_order']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):                               
                raise DataValidationException("You don't have permission to edit purchase orders.",code=403)
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            old_details_ids =list(instance.entity_order_detail_set.all().values_list('id', flat=True))
            # 'old_details_ids' is a list of this purchase order's detail ids.
            print("old_details_ids",old_details_ids,type(old_details_ids)) 
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            data=request.data 
            is_valid_plant(data['plant_id'])
            print(data["plant_id"])
            if 'company_id' in data and data['company_id']!=instance.entity_company_id:
                data['company_id']=instance.entity_company_id
            
            if 'vendor_id' in data and data['vendor_id']!=instance.entity_id:
                data['vendor_id']=instance.entity_id

            serializer.is_valid(raise_exception=True)
            order_list = data['order_list']
            if type(order_list) is not list:
                raise DataValidationException('order_list must be a list.',code = 400)
            elif len(order_list) == 0:
                raise DataValidationException('Order_list must not be empty.',code = 409)
            else:
                a=verify_entity_detail(order_list)
                total_order_amount = sum(float(d.get('amount', 0)) for d in order_list)
                # print(total_order_amount,type(total_order_amount),"total_order_amount")
                # print(data['order_amount'],type(data['order_amount']),"order_amount")
                if float(data['order_amount']) != float(total_order_amount):
                   raise DataValidationException("Total purchase order amount must be equal to sum of product amounts.",code = 409)
                print(a,"verify entity detail")
            entity_detail_serializer = PurchaseOrderDetailSerializer(data=order_list,many=True)
            entity_detail_serializer.is_valid(raise_exception=True)
            # is_approved = is_approval_settings(data['company_id'])
            is_approved=1
            print(is_approved,"is_approved create")
            a=serializer.save(modified_by=self.request.user.username,is_approved = is_approved)
            actions_done=''
            print(data,"request.data")
            edited_ids_list = []
            newly_created_ids_list = []
            for i in range(len(order_list)):
                if order_list[i]['id']:
                    # update the detail objects with ids
                    print(type(order_list[i]['id']),"type(order_list[i]['id'])")
                    order_detail=entity_order_detail.objects.get(id=order_list[i]['id'])
                    order_detail_serializer = PurchaseOrderDetailSerializer(order_detail,data=order_list[i])
                    order_detail_serializer.is_valid(raise_exception=True)
                    order_detail_serializer.save(modified_by=self.request.user.username)
                    edited_ids_list.append(int(order_list[i]['id']))
                else:
                    detail_serializer = PurchaseOrderDetailSerializer(data=order_list[i])
                    detail_serializer.is_valid(raise_exception=True)
                    n= detail_serializer.save(created_by=self.request.user.username,entity_order_id=instance)
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
                print(to_delete_ids_list,"to_delete_ids_list")
                print(type(to_delete_ids_list),"type(to_delete_ids_list)")
                for i in to_delete_ids_list:
                    print(i,"todelete id")
                    to_delete_id = i
                    a=entity_order_detail.objects.get(id=i)
                    a.delete()
                    deleted_ids_list.append(to_delete_id)
                deleted_ids = ','.join([str(elem) for elem in deleted_ids_list])
                actions_done=actions_done +' ,'+"DELETE PRODUCT DETAILS during edit "
            else:
                deleted_ids = "NO"
            idlist= "Edited PRODUCT DETAIL IDS:" + ' ' + edited_dtl_ids + ' ,' +  "Deleted PRODUCT DETAIL IDS:" + ' ' + deleted_ids + ' ,' +"Created PRODUCT DETAILS IDS:" + ' ' + newly_created_ids
            for_tracking={'id':"entity_order_master_id : "+ str(instance.id) + ", entity_order_detail_id : "+ idlist,
            'sl_no':instance.order_no,'content_type':"PURCHASE ORDER FORM",
            'action':actions_done,'module_name':"PURCHASE",'plant_name':entity_master.objects.get(id=instance.entity_company_id.id)}
            tracking=handle_tracking(self.request,for_tracking)
            send_email(instance.entity_company_id.id,instance.order_no,instance.prefix)
            queryset = self.filter_queryset(self.get_queryset())
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TypeError as e:
            raise DataValidationException(str(e),code=400)
        except NameError as e:
            raise DataValidationException(str(e)+ ' order_list must be a list of dictionaries.')
        except KeyError as e:
            raise DataValidationException("KeyError " + str(e) ,code=400)
        except ValueError as e:
            raise DataValidationException(str(e),code=400)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Purchase order with id [{kwargs["pk"]}] not found.')
        except ValidationError as e:
            raise DataValidationException(detail=(str(e)),exception=e)
    
    def destroy(self, request, *args, **kwargs):
        try:
            required_perms = ['rmc.delete_purchase_order']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):                               
                raise DataValidationException("You don't have permission to delete purchase orders.",code=403)
            instance = self.get_object()
            entity_order_master_id=instance.id
            order_no = instance.order_no
            company_id = instance.entity_company_id.id
            a = entity_order_detail.objects.filter(entity_order_id=entity_order_master_id)
            # print(a,"a")
            entity_order_detail_ids=','.join(map(str,(list(a.values_list('id',flat=True)))))
            for i in a:
                # print(i,"todelete id")
                i.delete() 
            instance.delete()
            for_tracking={'id':"entity_order_master_id : "+ str(entity_order_master_id) + ", entity_order_detail_id : "+ entity_order_detail_ids,
            'sl_no':order_no,'content_type':"PURCHASE ORDER FORM",
            'action':"DELETE",'module_name':"PURCHASE",'plant_name':entity_master.objects.get(id=company_id)}
            tracking=handle_tracking(self.request,for_tracking)
            return Response({'message':"Successfully Deleted"},status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Purchase order with id [{kwargs["pk"]}] not found.')
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))

    @action(detail=False,url_path="(?P<purchase_order_id>[0-9]+)/print_po")
    def print_po(self,request,purchase_order_id):
        try:
            print("purchase_order_id",purchase_order_id)
            if not (entity_order_master.objects.filter(id=purchase_order_id).exists()):
                raise EntityNotFoundException("Purchase order id is Invalid",code=404)
            po = entity_order_master.objects.get(id=purchase_order_id) 

            if po.transport_mode=="customer":
                po.transport_mode="vendor"
            elif po.transport_mode=="own/customer":
                po.transport_mode="own/vendor"
            else:
                po.transport_mode="own"
            cd=entity_master.objects.get(id=po.entity_company_id.id)
            company_detail=entity_company_detail.objects.get(entity_id=cd)
            company_logo=company_detail.logo
            company_state=cd.state.split('(')
            company_state_name=company_state[0].strip()
            company_code=company_state[1].replace(')','').strip()

            sd=entity_master.objects.get(id=po.entity_id.id)
            supplier_state=sd.state.split('(')
            supplier_state_name=supplier_state[0].strip()
            supplier_code=supplier_state[1].replace(')','').strip()
            
            pd=entity_master.objects.get(id=po.entity_consignee_id.id)

            plant_state=pd.state.split('(')
            plant_state_name=plant_state[0].strip()
            plant_code=plant_state[1].replace(')','').strip()

            po_details = entity_order_detail.objects.filter(entity_order_id=purchase_order_id)
            total_quantity=0
            amount=0
            total_1=0
            total_2=0
            unit_list=[]

            for d in po_details:
            
                total_quantity+= d.quantity
                amount+=d.amount
                tax_amount=d.amount
                td=taxform_master.objects.get(id=d.tax.id)
                tax1=td.tax_value1
                print(tax1,"tax1")
                
                tax2=td.tax_value2
                print(tax2,"tax2")
                
                d.tax1_amount=(tax1/100)*tax_amount

                d.tax2_amount=(tax2/100)*tax_amount

                total_1+=tax_amount+d.tax1_amount+d.tax2_amount
                print(d.amount,"amount")
                print(d.tax1_amount,"tax1_amount")
                print(d.tax2_amount,"tax2_amount")
                print(total_1,"1st")
                word1=num2words(total_1)
                
                total_2+=tax_amount+d.tax1_amount
                print(total_2,"2nd")
                word2=num2words(total_2)
                sym=product_master.objects.get(id=d.product.id)
                unit=uom_master.objects.get(id=sym.unit.id)
                d.symbol=unit.symbol
                print(d.symbol,'symbol')
                if d.symbol not in unit_list:
                    unit_list.append(d.symbol)
                if len(set(unit_list)) == 1:
                    unit_1 = unit_list[0]
                else:
                    unit_1=""
                    total_quantity=""
                print(unit_list,"unit1")

            context={"po":po,"c_logo":company_logo,"c_state":company_state_name,
                     "c_code":company_code,"s_state":supplier_state_name,
                     "s_code":supplier_code,"p_state":plant_state_name,
                     "p_code":plant_code,"po_details":po_details,"quantity":total_quantity,
                     "amount":amount,"t1":total_1,"t2":total_2,
                     "symbol":d.symbol,"unit_list":unit_list,"unit_1":unit_1,
                     "tax1_amount":d.tax1_amount,"tax2_amount":d.tax2_amount,
                     "word1":word1,"word2":word2}
            
            pdf = render_to_pdf('report/purchase_order_pdf.html', context)
            return HttpResponse(pdf, content_type = 'application/pdf')
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))

    @action(detail=False)        
    def  goods_receipt_note(self,request, *args, **kwargs):        
        try:
            required_perms = ['rmc.view_purchase_order']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):     
                return Response({'purchase_order_list': []})
            purchase_order_list = list(entity_order_master.objects.filter(is_approved = 1,entity_order_type='purchase',status=1).values('id','order_no',
                'order_date','order_time','prefix','pay_terms','validity_date','transport_mode',
                'is_tax_included','is_approved','status','order_amount',terms_and_conditions=F('terms_condition')))
            purchase_order_list = order(purchase_order_list)
            print(purchase_order_list,"purchase_order_list")
            return Response({'purchase_order_list': purchase_order_list}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))