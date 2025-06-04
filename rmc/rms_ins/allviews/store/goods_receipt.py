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
from rms_ins.serializers import *


class GoodsMovementMasterViewSet(viewsets.ModelViewSet):
    queryset = gmr_master.objects.all()
    serializer_class = GMRMasterSerializer
    for_tracking={'content_type':"GOODS RECEIPT NOTE",'module_name':"STORE"}

    @action(detail=False)
    def goods_receipt_note_number(self,request):
        try:
            plant_id=self.request.query_params.get('plant_id')
            query_date = self.request.query_params.get('grn_date')
            print("grn_date",query_date,type(query_date))
            print("plant_id",plant_id,type(plant_id))
            if plant_id is None:
                raise DataValidationException("plant id need to be passed in query params.",code=400)
            is_valid_plant(plant_id)
            query_1 = gmr_master.objects.filter(movement_type = 'grn',plant=plant_id).last()#.filter(status = 1)
            query_2 = gmr_master.objects.filter(movement_type = 'grn').values("sl_no")
            query_3 = gmr_master.objects.filter(movement_type = 'grn',plant=plant_id).values("sl_no")
            print(query_1,"query1",query_2,"query_2",query_3,"query 3")
            needed_params = {'query_date':query_date,'plant_id':plant_id,'query_1':query_1,
                             'voucher_type':'goods_reciept_note','query_2':query_2,
                            'date_field_name':'sl_dt','slno_field_name':'sl_no',
                            'form_name':"goods_reciept_note",'date_name':"Goods receipt date",
                                'exception':EntityNotFoundException,'query_3':query_3}
            result = get_slno_prefix(needed_params)
            print(result,"result")
            return Response({'goods_receipt_note_no':result['sl_no'],'prefix':result['prefix']},status = status.HTTP_200_OK)
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
        
    def create(self, request, *args, **kwargs):
        try:
            required_perms = ['rmc.add_gmr_master']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):
                raise DataValidationException("You don't have permission to create Goods receipt note.",code=403)
            serializer = self.get_serializer(data=request.data)
            data = request.data
            if not 'driver_name' in data.keys() :
                raise DataValidationException("KeyError : driver_name",code=400)
            
            if not 'lr_no' in data.keys() :
                raise DataValidationException("KeyError : lr_no",code=400)
            
            if not 'lr_dt' in data.keys() :
                raise DataValidationException("KeyError : lr_dt",code=400)
            
            if not 'driver_mobile_no' in data.keys():
                raise DataValidationException("KeyError : driver_mobile_no",code=400)
            
            if not 'measurement_taken_by' in data.keys() :
                raise DataValidationException("KeyError : measurement_taken_by",code=400)
            
            if not 'authorised_by' in data.keys():
                raise DataValidationException("KeyError : authorised_by",code=400)
            
            if not 'weighment_name' in data.keys() :
                raise DataValidationException("KeyError : weighment_name",code=400)
            
            if not 'received_by' in data.keys():
                raise DataValidationException("KeyError : received_by",code=400)
            
            if not 'weighment_slip_time' in data.keys() :
                raise DataValidationException("KeyError : weighment_slip_time",code=400)
            
            if not 'weighment_slip_no' in data.keys():
                raise DataValidationException("KeyError : weighment_slip_no",code=400)
            
            if not 'user_remarks' in data.keys():
                raise DataValidationException("KeyError : user_remarks",code=400)
            
            detail_list = data['detail_list']#request.data.get('detail_list',[])
            print(detail_list,'detaillllllll idddddddd')
            master_ids=set()
            if type(detail_list) is not list:
                raise DataValidationException('detail_list must be a list.',code = 400) 
            elif len(detail_list) == 0:
                raise DataValidationException('detail_list must not be empty.',code = 409)
            else:
                for d in detail_list:
                    print(d,'d')
                    print(d.keys(),'keys')
                    if not (entity_order_detail.objects.filter(id=d['po_detail_id']).exists()):
                        raise DataValidationException('purchase Detail Id is Invalid.',code=409)
                    detail=entity_order_detail.objects.get(id=d['po_detail_id'])
                    print(detail,'detail')
                    po = detail.entity_order_id
                    
                    if not (entity_order_master.objects.filter(id=po.id,entity_order_type='purchase',status=1,is_approved=1).exists()):
                        raise DataValidationException("Purchase order detail id is invalid.",code=409)
                    master = entity_order_master.objects.filter(id=po.id,entity_order_type='purchase',status=1,is_approved=1).first()
                    master_ids.add(master.id)
                    order_qty=detail.quantity
                    total_accepted_qty=gmr_detail.objects.filter(order_detail=detail.id,gmr__status=1).aggregate(total_accepted_qty=Sum('accepted_qty'))['total_accepted_qty']
                    if total_accepted_qty is not None:
                        balance_qty=order_qty-total_accepted_qty
                    else:
                        balance_qty=order_qty
                    print(balance_qty,'balance_qunatityy')
                    if balance_qty <= 0:
                        raise DataValidationException("Only PO details of balance qty > 0 are  elligible for GRN.")
                    tax=taxform_master.objects.get(id=detail.tax.id)
                    is_tax_included=master.is_tax_included
                    po_rate=detail.rate
                    tax_value1=tax.tax_value1
                    tax_value2=tax.tax_value2
                    tax_value=tax_value1+tax_value2
                    if is_tax_included == 1:
                        d['basic_rate']=(po_rate / (100+(tax_value) / 100))
                    else:
                        d['basic_rate']=po_rate
                    print(d['basic_rate'],'Basic Raate')
                    d['taxable_amt']=d['basic_rate']*d['accepted_qty']
                    print(d['taxable_amt'],'Taxable_amt')
                    d['tax_perc']=tax_value1+tax_value2
                    d['igst_perc']=tax_value1
                    d['igst_amt']=(d['taxable_amt']*tax_value1)/100
                    d['cgst_perc']=tax_value1
                    d['cgst_amt']=(d['taxable_amt']*tax_value1)/100
                    d['sgst_perc']=tax_value2
                    d['sgst_amt']=(d['taxable_amt']*tax_value2)/100
                
            if len(master_ids) > 1:
                raise DataValidationException("Only 1 purchase order can be connected to a Grn.",code=409)
            vendor={
                    'id':master.entity_id.id,
                    'name':master.entity_id.entity_name,
                    'address1':master.entity_id.address_1,
                    'address2':master.entity_id.address_2,
                    'address3':master.entity_id.address_3,
                    'pincode':master.entity_id.pincode,
                    'state':master.entity_id.state,
                    'gstno':master.entity_id.gst_no
                }
            
            # validate plant_id
            if not (entity_master.objects.filter(status = 1,entity_type = 'plant',id=data['plant_id']).exists()):
                raise DataValidationException('Plant id is Invalid.',code=409)
            company = master.entity_company_id
            print(company,"company")
            if not(entity_plant_detail.objects.filter(entity_id=data['plant_id'],entity_company_id =company).exists()):
                raise DataValidationException("Plant id is invalid.Because ,this plant does not belong to related purchase order's company.")
            plant = entity_master.objects.get(id=data['plant_id'])
            consignee_details={
                'id':plant.id,
                'name':plant.entity_name,
                'address1':plant.address_1,
                'address2':plant.address_2,
                'address3':plant.address_3,
                'pincode':plant.pincode,
                'state':plant.state,
                'gstno':plant.gst_no
            }
            query_1 = gmr_master.objects.filter(movement_type='grn',plant=data['plant_id']).last()
            query_2=gmr_master.objects.filter(movement_type='grn').values("sl_no")
            query_3 = gmr_master.objects.filter(movement_type = 'grn',plant=data['plant_id']).values("sl_no")
            print(query_1,"query1",query_2,"query_2",query_3,"query_3")
            needed_params = {'query_date':data['goods_receipt_note_date'],'plant_id':data['plant_id'],
                             'query_1':query_1,
                             'voucher_type':'goods_reciept_note','query_2':query_2,
                            'date_field_name':'sl_dt','slno_field_name':'sl_no',
                            'form_name':"goods_reciept_note",'date_name':"Goods receipt note date",
                                'exception':DataValidationException,'query_3':query_3}
            result = get_slno_prefix(needed_params)
            print(result)
            if data['prefix'] != result['prefix']:
                data['prefix'] = result['prefix']
            if (data['goods_receipt_note_no'] != result['sl_no']):
                data['goods_receipt_note_no'] = result['sl_no']
            
            print(data,'before is_valid')
            verify_gmr_master(data)
            serializer.is_valid(raise_exception=True)
            
            gmr_detail_serializer = GMRDetailSerializer(data=detail_list, many=True)
            gmr_detail_serializer.is_valid(raise_exception=True)     

            a = serializer.save(created_by=self.request.user,
                                movement_type='grn',
                                customer_vendor=master.entity_id,
                                site_plant=plant,
                                invoice_details=vendor,
                                consignee_details=consignee_details,
                                order=master)

            n = gmr_detail_serializer.save(created_by=self.request.user, gmr=a)
            created_id_list=[x.id for x in n]
            created_ids=','.join(map(str,created_id_list))
            for_tracking={'id':"gmr_master_id : "+ str(a.id) +", gmr_detail_id : "+(created_ids) ,
            'sl_no':a.sl_no,'content_type':"GOODS RECEIPT NOTE",
            'action':"CREATE",'module_name':"STORE",'plant_name':a.plant}
            tracking=handle_tracking(self.request,for_tracking)
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
            required_perms = ['rmc.view_gmr_master']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):     
                return Response({'goods_receipt_note_list': []})
                            
            
            goods_receipt_note_list = gmr_detail.objects.all().order_by('id').values('id')
            
            for i in goods_receipt_note_list:
                detail = gmr_detail.objects.get(id=i['id'])
                a = detail.gmr
                print(a,'gmr_id')
                i['goods_receipt_note_no'] = detail.sl_no
                i['goods_receipt_note_date']=a.sl_dt.strftime("%d-%m-%Y")
                i['goods_receipt_note_time']=a.sl_time
                i['prefix'] = a.Prefix
                plant=entity_master.objects.get(id=a.plant.id)
                plant1=entity_plant_detail.objects.get(entity_id=plant)
                print(plant1,'plantttttttttttttt')
                alias=plant1.plant_alias
                print(alias,'aliassssssssss')
                i['plant']={
                    'id':a.plant.id,
                    'name':a.plant.entity_name,
                    'alias_name':alias
                }
                i['weighment_name']=a.weighment_name
                i['transport_mode']=a.transport_mode
                i['weighment_slip_no']=a.weighment_slip_no
                i['vendor']={
                    'id':a.customer_vendor.id,
                    'name':a.customer_vendor.entity_name
                }
                i['gross_weight']=detail.gross_weight
                i['tare_weight']=detail.tare_weight
                i['dc_no']=a.dc_no
                i['dc_dt']=a.dc_dt
                i['invoice']={
                    'id':None,
                    'invoice_no':None,
                    'prefix':None,
                    'invoice_date':None
                }
                i['dc_qty']=detail.dc_qty
                i['deduction_qty']=detail.Deduction_qty
                i['received_qty']=detail.Received_qty
                i['accepted_qty']=detail.accepted_qty
                i['difference_qty']=detail.dc_qty-detail.Received_qty
                i['product']={
                    'id':detail.order_detail.product.id,
                    'name':detail.order_detail.product.name,
                    'unit':{
                        'id':detail.order_detail.product.unit.id,
                        'name':detail.order_detail.product.unit.name,
                        'symbol':detail.order_detail.product.unit.symbol
                    }
                }
            return Response({'goods_receipt_note_list': goods_receipt_note_list}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
   
    def retrieve(self, request, *args, **kwargs):
        try:
            required_perms = ['rmc.view_gmr_master']  
            print(HasUserPermission(request,required_perms),"HasUserPermission(request,required_perms)")
            if not HasUserPermission(request,required_perms):                               
                raise DataValidationException("You don't have permission to view goods receipt note.",code=403)
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            g_id = request.query_params.get('sl_no') 
            print(g_id, "sl_no")
            if g_id is not None:
                goods_receipt_note_list = gmr_detail.objects.filter(gmr=g_id).order_by('id').values('id')
                print(goods_receipt_note_list)
            else:
                goods_receipt_note_list = gmr_detail.objects.all().order_by('id').values('id')
                print(goods_receipt_note_list)
            
            entity_consignee_id = instance.plant
            if entity_consignee_id:
                plant_alias = entity_plant_detail.objects.get(entity_id=entity_consignee_id).plant_alias
                print("Plant Alias:", plant_alias)
            else:
                print("Entity Consignee ID not provided.")

            details = list(instance.gmr_detail_set.all().order_by('id').values('id','gross_weight','tare_weight','net_weight','dc_qty','accepted_qty','user_remarks'))
            for  d in details:
                detail = gmr_detail.objects.get(id=d['id'])
                qty=detail.order_detail.quantity
                acct_qty=gmr_detail.objects.filter(order_detail=d['id']).aggregate(total_accepted_qty=Sum('accepted_qty'))['total_accepted_qty']
                if acct_qty is None:
                    acct_qty = 0
                balance_qty= qty-acct_qty
                if (balance_qty>0):
                    d['balance_qty']=balance_qty
                else:
                    d['balance_qty']=0
                print(detail.order_detail.quantity,'quantityyyyyyyyy')
                d['purchase_order_detail'] = {'id':detail.order_detail.id,
                                'order_quantity':detail.order_detail.quantity,
                                'balance_quantity': balance_qty,
                                'product':{
                                    'id':detail.order_detail.product.id,
                                    'name':detail.order_detail.product.name
                                },
                                'category': {
                                    'id': detail.order_detail.product.category_detail.id,
                                    'name': detail.order_detail.product.category_detail.entity_name
                                },
                                'purchase_order': {
                                    'id':detail.order_detail.entity_order_id.id,
                                    'order_no':detail.order_detail.entity_order_id.order_no,
                                    'order_date':detail.order_detail.entity_order_id.order_date,
                                    'prefix':detail.order_detail.entity_order_id.prefix,
                                    'company':{
                                            'id':detail.order_detail.entity_order_id.entity_company_id.id,
                                            'name':detail.order_detail.entity_order_id.entity_company_id.entity_name
                                        },
                                    'plant':{
                                        'id':detail.order_detail.entity_order_id.entity_consignee_id.id,
                                        'name':detail.order_detail.entity_order_id.entity_consignee_id.entity_name,
                                        'alias':plant_alias
                                    },
                                        'vendor':{
                                        'id':detail.order_detail.entity_order_id.entity_id.id,
                                        'name':detail.order_detail.entity_order_id.entity_id.entity_name
                                    }
                                }
                }
            d['deduction_qty']=detail.Deduction_qty
            d['received_qty']=detail.Received_qty

            content={
                'id':serializer.data['id'],
                 'plant':{
                    'id':instance.plant.id,
                    'name':instance.plant.entity_name,
                    'alias':plant_alias
                },
                'goods_receipt_note_no':instance.sl_no,
                'goods_receipt_note_dtae':instance.sl_dt,
                'goods_receipt_note_time':instance.sl_time,
                'prefix':instance.Prefix,
                'transporter_name':instance.transporter_name,
                'vehicle':{
                    'id':instance.vehicle_own.id,
                    'name':instance.vehicle_own.equip_name
                },
                'invoice':{
                    'id':None,
                    'invoice_no':None,
                    'prefix':None,
                    'invoice_date':None
                },
                'vehicle_others':instance.vehicle_others,
                'driver_name':instance.driver_name,
                'driver_mobile_no':instance.driver_mobile_no,
                'dc_no':instance.dc_no,
                'dc_dt':instance.dc_dt,
                'measurement_taken_by':instance.measurement_taken_by,
                'authorised_by':instance.authorised_by,
                'received_by':instance.received_by,
                'out_time':instance.out_time,
                'in_time':instance.in_time,
                'weighment_name':instance.weighment_name,
                'weighment_slip_no':instance.weighment_slip_no,
                'weighment_slip_date':instance.weighment_slip_date,
                'weighment_slip_time':instance.weighment_slip_time,
                'user_remarks':instance.user_remarks,
                'transport_mode':instance.transport_mode,
                'invoice_details':instance.invoice_details,
                'consignee_details':instance.consignee_details,
                'detail_list':details
            }

            return Response(content,status=status.HTTP_200_OK)
        except Http404 as e:
            raise EntityNotFoundException(detail=f'Goods receipt note with id [{kwargs["pk"]}] not found.')
        except ObjectDoesNotExist as e:
            raise EntityNotFoundException(detail=str(e))
        
    