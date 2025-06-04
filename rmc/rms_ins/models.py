from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError
from datetime import date
from rms_ins.exceptions import DataValidationException

def user_directory_path(instance, filename):
    return '{0}'.format(filename)
class soft_delete_manager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class soft_delete_model(models.Model):
    deleted_at = models.DateTimeField(blank=True,null=True)
    created_by= models.CharField(max_length=100,null=True,blank=True)
    created_dtm= models.DateTimeField(auto_now_add=True,null=True, blank=True)
    modified_by= models.CharField(max_length=100,null=True, blank=True)
    modified_dtm= models.DateTimeField(auto_now=True,null=True, blank=True)
    remarks= models.TextField(max_length=1000,null=True, blank=True)
    dev_remarks= models.TextField(max_length=1000,null=True, blank=True)
    system_field= models.IntegerField(default=0)
    deleted= models.IntegerField(null=True, blank=True)
    
    objects = soft_delete_manager()
    all_objects = models.Manager()
    
    class meta:
        abstract = True
    
    def delete(self):
        object_list = []
        model_name=self._meta.model.__name__
        for relation in self._meta._relation_tree:
            # print(str(relation),"relation")
            on_delete = getattr(relation.remote_field, 'on_delete', models.DO_NOTHING)
            # print(on_delete,"on_delete")
            if on_delete in [None, models.DO_NOTHING]:
                continue
            accounts_grouping=['income','assets','expenses','liabilities','others']
            filter = {relation.name: self}
            related_queryset = relation.model.objects.filter(**filter)
            if on_delete == models.CASCADE:
                print(relation.model.objects.filter(*filter),"cascade")#.delete(*kwargs)
            elif on_delete == models.PROTECT:
                if model_name == 'entity_master':
                    # print(model_name,"model_name") 
                    if ((str(relation) != "rmc.entity_company_detail.entity_id") and (self.entity_type == 'company') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif (((self.entity_type in accounts_grouping) or (self.entity_type == None)) and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif ((str(relation) != "rmc.entity_plant_detail.entity_id") and (self.entity_type == 'plant') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif ((str(relation) != "rmc.entity_gang_detail.entity_id") and (self.entity_type == 'gang') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif ((str(relation) != "rmc.entity_vendor_detail.entity_id") and (self.entity_type == 'supplier') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif ((str(relation) != "rmc.entity_salesrep_detail.entity_id") and (self.entity_type == 'salesrep') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif ((str(relation) != "rmc.entity_customer_detail.entity_id")  and (str(relation) != "rmc.opening_balance_master.ledger_id") and (self.entity_type == 'customer') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                    elif ((str(relation) != "rmc.entity_consignee_detail.entity_id")  and (self.entity_type == 'consignee') and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                elif model_name == 'numberings_master':
                    if ((str(relation) != "rmc.numberings_detail.numsetting_master") and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                elif model_name == 'entity_enquiry_master':
                    if ((str(relation) != "rmc.entity_enquiry_detail.enquiry_master_id") and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                elif model_name == 'entity_order_master':
                    if ((str(relation) != "rmc.entity_order_detail.entity_order_id") and (str(relation) != "rmc.sales_order_master.entity_order_id") and (related_queryset.count() > 0)):
                        object_list.extend(related_queryset)
                else:    
                    object_list.extend(related_queryset)
            else:
                raise(NotImplementedError())
        if len(object_list) > 0:
            print("Cannot delete some instances of model  because they are referenced through a protected foreign key",object_list)
            # raise ProtectedError("Cannot delete some instances of model  because they are referenced through a protected foreign key",object_list)
            raise DataValidationException("You can't delete this because it's being used by groups.",code = 403)
        else:
            self.deleted_at = timezone.now()
            self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self):
        self.delete()

class entity_master(soft_delete_model):
    entity_type= models.CharField(max_length=100,null=True,blank=True)
    parent_id=models.ForeignKey('self',on_delete=models.PROTECT,null=True)
    entity_name= models.CharField(max_length=100,null=False,blank=False)
    address_1= models.CharField(max_length=100,null=True,blank=True)
    address_2= models.CharField(max_length=100,null=True,blank=True)
    address_3= models.CharField(max_length=100,null=True,blank=True)
    location= models.CharField(max_length=100,null=True,blank=True)
    pincode= models.CharField(max_length=6,null=True,blank=True)
    state= models.CharField(max_length=100,null=True,blank=True)
    phone_number= models.CharField(max_length=255,null=True,blank=True)
    email_id= models.EmailField(max_length=100,null=True,blank=True)
    pan_no= models.CharField(max_length=50,null=True,blank=True)
    gst_no= models.CharField(max_length=50,null=True,blank=True)
    user_remarks= models.TextField(max_length=1000,null=True,blank=True)
    status= models.IntegerField(default=1)
    mobile_number= models.CharField(max_length=255,null=True,blank=True)
    contact_person= models.CharField(max_length=100,null=True,blank=True)
    contact_mobile_no= models.CharField(max_length=100,null=True,blank=True)
    contact_email_id= models.EmailField(max_length=100,null=True,blank=True)
    contact_designation= models.CharField(max_length=100,null=True,blank=True)
    gst_type= models.CharField(max_length=50,null=True,blank=True)
    gst_file= models.FileField(upload_to=user_directory_path, null=True, verbose_name="")

class user_tracking(soft_delete_model):
    user=models.ForeignKey(User,on_delete=models.PROTECT,null=True)
    user_ip_addr= models.GenericIPAddressField(protocol='both',null=True,blank=True)
    plant=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True)
    sl_no= models.CharField(max_length=255,null=True,blank=True)
    content_type= models.CharField(max_length=100,null=True,blank=True)
    object_id= models.CharField(max_length=255,null=True,blank=True)
    action_done= models.CharField(max_length=100,null=True,blank=True)
    tracking_dtm= models.DateTimeField(auto_now_add=True,null=True,blank=True)
    module_name= models.CharField(max_length=250,null=True,blank=True)
    session_id= models.CharField(max_length=50,null=True,blank=True)
    error_msg= models.TextField(max_length=1000,null=True,blank=True)
    latitude =models.FloatField(default=0)
    longitude =models.FloatField(default=0)

class entity_vendor_detail(soft_delete_model):
    vendor_type=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False,related_name='vendor_type')
    entity_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True,related_name='vendor_entity_master_id')
    ven_bank_name= models.CharField(max_length=100,null=True, blank=True)
    ven_bank_branch= models.CharField(max_length=100,null=True, blank=True)
    ven_bank_acc_no= models.CharField(max_length=100,null=True, blank=True)
    ven_bank_ifsc= models.CharField(max_length=100,null=True, blank=True)

class entity_company_detail(soft_delete_model):
    alias= models.CharField(max_length=255,null=False,blank=False)
    entity_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True, blank=True)
    web= models.CharField(max_length=100,null=True, blank=True)
    seal= models.ImageField(upload_to=user_directory_path,null=True, blank=True)
    logo= models.ImageField(upload_to=user_directory_path,null=True, blank=True)
    commencement_dt= models.DateField(null=False,blank=False)
    cst_no= models.CharField(max_length=100,null=True, blank=True)
    lut_no= models.CharField(max_length=100,null=True, blank=True)
    tan_no= models.CharField(max_length=100,null=True, blank=True)
    cin_no= models.CharField(max_length=100,null=True, blank=True)
    opening_dt= models.DateField(null=False,blank=False)
    closing_dt= models.DateField(null=False,blank=False)
    pf_no= models.CharField(max_length=100,null=True, blank=True)
    esi_no= models.CharField(max_length=100,null=True, blank=True)
    is_batching_report_needed= models.IntegerField(default=0)

class entity_plant_detail(soft_delete_model):
    entity_company_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False)
    entity_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True,related_name='plant_entity_id')
    plant_alias= models.CharField(max_length=255,null=False,blank=False)
    plant_web= models.CharField(max_length=100,null=True, blank=True)
    plant_commence_dt= models.DateField(null=False,blank=False)
    plant_cst_no= models.CharField(max_length=100,null=True, blank=True)
    plant_lut_no= models.CharField(max_length=100,null=True, blank=True)
    plant_tan_no= models.CharField(max_length=100,null=True, blank=True)
    plant_cin_no= models.CharField(max_length=100,null=True, blank=True)
    account_opening_dt= models.DateField(null=False,blank=False)
    account_closing_dt= models.DateField(null=False,blank=False)
    plant_mixer_capacity= models.FloatField(default=0)
    plant_pfno= models.CharField(max_length=100,null=True, blank=True)
    plant_esino= models.CharField(max_length=100,null=True, blank=True)
    plant_serial_no= models.CharField(max_length=100,null=False,blank=False)
    plant_model= models.CharField(max_length=100,null=True, blank=True)
    plant_make= models.CharField(max_length=100,null=True, blank=True)
    plant_seal= models.ImageField(upload_to=user_directory_path,null=True, blank=True)
    plant_logo= models.ImageField(upload_to=user_directory_path,null=True, blank=True)
    plant_br_logo= models.ImageField(upload_to=user_directory_path,null=True, blank=True)
    # br_report_format_choice = models.CharField(max_length=25,null=False,blank=False)

class numberings_master(soft_delete_model):
    entity_plant_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True)
    voucher_type= models.CharField(max_length=100,null=False, blank=False)
    is_active= models.IntegerField(default=0)

class numberings_detail(soft_delete_model):
    numsetting_master=models.ForeignKey(numberings_master,on_delete=models.PROTECT,null=True)
    starting_number= models.IntegerField(default=0)
    number_of_digits= models.IntegerField(default=0)
    prefix= models.CharField(max_length=100,null=True, blank=True)
    valid_from_date= models.DateField(null=False, blank=False)
    valid_upto_date= models.DateField(null=False, blank=False)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)

class approval_setting_master(soft_delete_model):
    entity_company_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False)
    voucher_type= models.CharField(max_length=100,null=False,blank=False)
    is_appr_needed= models.IntegerField(default=0)
    is_so_wait_on_save= models.IntegerField(default=0)
    conditions_for_so_waiting= models.CharField(max_length=255,null=True,blank=True)
    is_mail_needed= models.IntegerField(default=0)
    mail_ids= models.CharField(max_length=255,null=True, blank=True)

class uom_master(soft_delete_model):
    name= models.CharField(max_length=100,null=False,blank=False)
    symbol= models.CharField(max_length=100,null=False,blank=False)
    quantity= models.FloatField(default=0)
    decimal_place= models.IntegerField(default=0)
    user_remarks= models.TextField(max_length=1000,null=True,blank=True)
    status= models.IntegerField(default=1)

class taxform_master(soft_delete_model):
    name= models.CharField(max_length=255,null=False, blank=False)
    tax_value1= models.FloatField(default=0)
    tax_value2= models.FloatField(default=0)
    tax_type= models.CharField(max_length=10,null=False,blank=False)
    valid_from= models.DateField(null=False,blank=False)
    valid_upto= models.DateField(null=False,blank=False)
    user_remarks= models.TextField(max_length=1000,null=True,blank=True)
    status= models.IntegerField(default=1)

class product_master(soft_delete_model):
    category_detail=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False)
    name= models.CharField(max_length=100,null=False,blank=False)
    unit=models.ForeignKey(uom_master,on_delete=models.PROTECT,null=False,blank=False)
    quantity= models.FloatField(default=1)
    vendor_part_code= models.CharField(max_length=25,null=True, blank=True)
    is_gst_applicable= models.IntegerField(default=0)
    tax=models.ForeignKey(taxform_master,on_delete=models.PROTECT,null=False,blank=False)
    hsn_sac_code= models.CharField(max_length=100,null=True, blank=True)
    hsn_sac_description= models.CharField(max_length=100,null=True, blank=True)
    prod_gst_type= models.CharField(max_length=50,null=True, blank=True)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)
    is_batch_report_connected= models.IntegerField(default=0)
    status= models.IntegerField(default=1)

class entity_order_master(soft_delete_model):
    entity_company_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False,related_name='company_id')
    entity_contact_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True,related_name='contact_id')
    # enquiry_id=models.ForeignKey(entity_enquiry_master,on_delete=models.PROTECT,null=True,related_name='enquiry_id')
    # txn_advance_id=models.ForeignKey(txn_master,on_delete=models.PROTECT,null=True)
    entity_consignee_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False,related_name='entity_consignee_id')
    entity_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True)
    order_no= models.CharField(max_length=200,null=False, blank=False)
    order_date= models.DateField(null=False, blank=False)
    transport_mode= models.CharField(max_length=50,null=False,blank=False)
    order_amount= models.FloatField(default=0)
    pay_terms= models.IntegerField(default=0)
    prefix= models.CharField(max_length=100,null=False, blank=False)
    is_tax_included= models.IntegerField(default=0)
    validity_date= models.DateField(null=False, blank=False)
    freight_charges= models.FloatField(default=0)
    terms_condition= models.TextField(max_length=1000,null=True, blank=True)
    status= models.IntegerField(default=1)
    is_approved= models.IntegerField(default=0)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)
    order_time = models.TimeField(null=False, blank=False)
    is_advance_payment = models.IntegerField(default=0)
    entity_order_type= models.CharField(max_length=20,null=True,blank=True)
    indent_no=models.CharField(max_length=20,null=True, blank=True)
    indent_date=models.DateField(null=True, blank=True)
    quotation_no=models.CharField(max_length=20,null=True, blank=True)
    quotation_date=models.DateField(null=True, blank=True)
    # entity_order_type= models.CharField(max_length=20,null=True,blank=True)
    # receipt = models.ForeignKey(receipt_master,on_delete=models.PROTECT,null=True)

class entity_order_detail(soft_delete_model):
    entity_order_id=models.ForeignKey(entity_order_master,on_delete=models.PROTECT,null=True,blank=True)
    product=models.ForeignKey(product_master,on_delete=models.PROTECT,null=False,blank=False)
    concrete_structure=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False)
    tax=models.ForeignKey(taxform_master,on_delete=models.PROTECT,null=False,blank=False)
    sl_no= models.IntegerField(default=0)
    quantity= models.FloatField(default=0)
    rate= models.FloatField(default=0)
    amount= models.FloatField(default=0)
    delivery_mode= models.CharField(max_length=15,null=False,blank=False)
    tax_rate= models.FloatField(default=0)
    status= models.IntegerField(default=1)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)
    is_approved= models.IntegerField(default=0)
    balance_qty= models.FloatField(default=0)
    scheduled_qty= models.FloatField(default=0)
    accepted_qty= models.FloatField(default=0)
    delivered_qty= models.FloatField(default=0)


class sales_purchase_master(soft_delete_model):
    entity_order_detail_id=models.ForeignKey(entity_order_detail,on_delete=models.PROTECT,null=True)
    bill_period_from= models.DateField(null=True, blank=True)
    bill_period_to= models.DateField(null=True, blank=True)
    invoice_number= models.CharField(max_length=100,null=True, blank=True)
    invoice_dttm= models.DateTimeField(null=True, blank=True)
    prefix= models.CharField(max_length=100,null=True, blank=True)
    purchase_master_file= models.FileField(upload_to=user_directory_path, null=True, verbose_name="")
    invoice_qty= models.FloatField(default=0)
    cgst_amt= models.FloatField(default=0)
    sgst_amt= models.FloatField(default=0)
    igst_amt= models.FloatField(default=0)
    gst_amt= models.FloatField(default=0)
    tcs_perc= models.FloatField(default=0)
    tcs_amt= models.FloatField(default=0)
    taxable_amt= models.FloatField(default=0)
    freight_charges= models.FloatField(default=0)
    discount_per= models.FloatField(default=0)
    discount_amt= models.FloatField(default=0)
    gross_amt= models.FloatField(default=0)
    round_off= models.FloatField(default=0)
    qr_code= models.ImageField(upload_to=user_directory_path,null=True, blank=True)
    taxable_pump= models.FloatField(default=0)
    taxable_transport= models.FloatField(default=0)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)
    status= models.IntegerField(default=1)

class profiles_master(soft_delete_model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    profile_name= models.CharField(max_length=255,null=True, blank=True)
    is_admin= models.IntegerField(default=0)
    user_mobile_no= models.CharField(max_length=100,null=True, blank=True)
    user_valid_from= models.DateField(default=date.today)
    user_valid_upto= models.DateField(default=date.today)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)
    otp_enabled = models.IntegerField(default=0)
    otp_verified = models.IntegerField(default=0)
    otp_base32 = models.CharField(max_length=255,null=True)
    otp_auth_url = models.CharField(max_length=255,null=True)
    is_mfa_needed = models.IntegerField(default=1)
    is_location_auth_needed = models.IntegerField(default=1)
    plant=models.ManyToManyField(entity_master)
    def _str_(self):
        return "%s's profile" % self.user
def create_profiles_master(sender, instance, created, **kwargs):
    try:
        if created:
            profile, created = profiles_master.objects.get_or_create(user=instance)
    except Exception as e:
        print(e)
        pass
post_save.connect(create_profiles_master, sender=User)
@receiver(post_save, sender=User)
def save_profiles_master(sender, instance, **kwargs):
    try:
        instance.profiles_master.save()
    except Exception as e:
        print(e)
        pass

class custom_permissions(models.Model):
    class Meta:
        managed=False # No database table creation
        default_permissions=()
        permissions=(
            ('is_rmc_admin','is rmc admin'),
            ('view_admin_reports','can view admin reports'),
            ('is_marketting','is marketting'),
            ('view_marketting_reports','can view marketting reports'),
            ('is_qty_ctrl','is quality ctrl'),
            ('view_qty_ctrl_reports','can view quality ctrl reports'),
            ('is_planning','is planning'),
            ('view_planning_reports','can view planning reports'),
            ('is_dispatch','is dispatch'),
            ('view_dispatch_reports','can view dispatch reports'),
            ('is_purchase','is purchase'),
            ('view_purchase_reports','can view purchase reports'),
            ('is_accounts','is accounts'),
            ('view_accounts_reports','can view accounts reports'),
            ('is_store','is store'),
            ('view_store_reports','can view store reports'),
            ('is_gate','is gate'),
            ('view_gate_reports','can view gate reports'),
            ('is_transport','is transport'),
            ('view_transport_reports','can view transport reports'),
            ('is_utility','is utility'),
            ('view_utility_reports','can view utility reports'),
            ('add_pump_clearance','can add pump clearance'),
            ('view_pump_clearance','can view pump clearance'),
            ('edit_pump_clearance','can edit pump clearance'),
            ('delete_pump_clearance','can delete pump clearance'),
            ('add_quotation','can add quotation'),
            ('view_quotation','can view quotation'),
            ('edit_quotation','can edit quotation'),
            ('delete_quotation','can delete quotation'),
            ('add_purchase_order','can add purchase order'),
            ('view_purchase_order','can view purchase order'),
            ('edit_purchase_order','can edit purchase order'),
            ('delete_purchase_order','can delete purchase order'),
            ('add_purchase_invoice','can add purchase invoice'),
            ('view_purchase_invoice','can view purchase invoice'),
            ('edit_purchase_invoice','can edit purchase invoice'),
            ('delete_purchase_invoice','can delete purchase invoice'),
            ('add_sales_invoice','can add sales invoice'),
            ('view_sales_invoice','can view sales invoice'),
            ('edit_sales_invoice','can edit sales invoice'),
            ('delete_sales_invoice','can delete sales invoice'),
            ('add_grouping','can add accounts grouping'),
            ('view_grouping','can view  accounts grouping'),
            ('edit_grouping','can edit  accounts grouping'),
            ('delete_grouping','can delete accounts grouping'),
            ('add_ledger','can add ledger'),
            ('view_ledger','can view ledger'),
            ('edit_ledger','can edit ledger'),
            ('delete_ledger','can delete ledger'),
            ('approve_po','can approve po'),
            ('approve_so','can approve so')
            )


class security_policy_master(soft_delete_model):
    ip_addr_category = models.CharField(max_length=25,null=True, blank=True)
    ip_addr= models.GenericIPAddressField(protocol='both',null=True, blank=False)
    user_remarks= models.CharField(max_length=255,null=True, blank=True)
    status= models.IntegerField(default=1)

class sales_order_master(soft_delete_model):
    entity_order_id=models.ForeignKey(entity_order_master,on_delete=models.PROTECT,null=True)
    po_no= models.CharField(max_length=100,null=True, blank=True)
    po_file= models.FileField(upload_to=user_directory_path, null=True, verbose_name="")
    po_dt= models.DateField(null=True, blank=True)
    tax_exemption_no= models.TextField(max_length=500,null=True,blank=True)
    delivery_dt= models.DateField(null=True, blank=True)



class goods_movement_master(soft_delete_model):
    movement_type= models.CharField(max_length=20,null=True, blank=True)
    # txn_id=models.ForeignKey(txn_master,on_delete=models.PROTECT,null=True)
    entity_plant_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True)
    # vehicle=models.ForeignKey(equipment_master,on_delete=models.PROTECT,null=True,blank=True)
    customer_vehicle_no=models.CharField(max_length=100,null=True,blank=True)
    sl_no= models.CharField(max_length=15,null=True, blank=True)
    checkout_no= models.CharField(max_length=15,null=True,blank=True)
    checkin_no= models.CharField(max_length=15,null=True, blank=True)
    sl_dt= models.DateField(null=False, blank=False)
    sl_time= models.TimeField(null=False, blank=False)
    prefix= models.CharField(max_length=100,null=True, blank=True)
    driver_name= models.CharField(max_length=100,null=True, blank=True)
    driver_mobile_no= models.CharField(max_length=100,null=True, blank=True)
    out_time= models.TimeField(null=True, blank=True)
    in_dt= models.DateField(null=True, blank=True)
    in_time= models.TimeField(null=True, blank=True)
    weighment_slip_time= models.TimeField(null=True, blank=True)
    weighment_slip_no= models.CharField(max_length=100,null=True, blank=True)
    weighment_slip_date= models.DateField(null=True, blank=True)
    dc_qty= models.FloatField(default=0)
    gross_weight= models.IntegerField(default=0)
    net_weight= models.IntegerField(default=0)
    tare_weight= models.IntegerField(default=0)
    user_remarks= models.CharField(max_length=255,null=True, blank=True)
    status= models.IntegerField(default=1)
    is_checkout= models.IntegerField(default=0)
    is_checkin= models.IntegerField(default=0)

class equipment_master(soft_delete_model):
    equip_grp_code=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False,related_name='equip_grp_code')
    equip_tax_code=models.ForeignKey(taxform_master,on_delete=models.PROTECT,null=True,related_name='equip_tax_code')
    entity_vendor_id=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False)
    is_tax_applicable= models.IntegerField(default=0)
    equip_name= models.CharField(max_length=100,null=False,blank=False)
    capacity= models.FloatField(default=0)
    mode= models.CharField(max_length=10,null=False,blank=False)
    fuel_type= models.CharField(max_length=15,null=False,blank=False)
    insurance_date= models.DateField(null=True, blank=True)
    permit_date= models.DateField(null=True, blank=True)
    fc_date= models.DateField(null=True, blank=True)
    is_equip_ready= models.IntegerField(default=0)
    meter_status= models.IntegerField(default=0)
    meter_reading= models.IntegerField(default=0)
    co_open_km= models.IntegerField(default=0)
    equip_open_hm= models.IntegerField(default=0)
    co_open_hm= models.IntegerField(default=0)
    user_remarks= models.TextField(max_length=1000,null=True, blank=True)
    status= models.IntegerField(default=1)
    
class gmr_master (soft_delete_model):
    movement_type= models.CharField(max_length=20,null=True, blank=True)
    plant=models.ForeignKey(entity_master,on_delete=models.PROTECT,null=False,blank=False)
    sl_no= models.CharField(max_length=15,null=False, blank=False) 
    sl_dt= models.DateField(null=False, blank=False)          
    sl_time= models.TimeField(null=False, blank=False)
    prefix= models.CharField(max_length=100,null=False, blank=False)
    # work_schedule=models.ForeignKey(work_schedule_master,on_delete=models.PROTECT,null=True,blank=True)
    order=models.ForeignKey(entity_order_master,on_delete=models.PROTECT,null=True,blank=True)
    customer_vendor = models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True,blank=True,related_name='customer_vendor') 
    invoice_details= models.TextField(max_length=2000,null=True, blank=True)
    site_plant= models.ForeignKey(entity_master,on_delete=models.PROTECT,null=True,blank=True,related_name='site_plant') 
    consignee_details= models.TextField(max_length=2000,null=True, blank=True)
    transporter_name= models.CharField(max_length=200,null=False, blank=False)
    vehicle_own=models.ForeignKey(equipment_master,on_delete=models.PROTECT,null=True,blank=True)
    vehicle_others=models.CharField(max_length=100,null=True,blank=True)
    driver_name= models.CharField(max_length=100,null=True, blank=True)
    driver_mobile_no= models.CharField(max_length=100,null=True, blank=True)
    checkout_no= models.CharField(max_length=15,null=True,blank=True)
    out_date= models.DateField(null=True, blank=True)
    out_time= models.TimeField(null=True, blank=True)
    is_checkout= models.IntegerField(default=0)
    checkin_no= models.CharField(max_length=15,null=True, blank=True)
    in_date= models.DateField(null=True, blank=True)
    in_time= models.TimeField(null=True, blank=True)
    is_checkin= models.IntegerField(default=0)
    weighment_name= models.CharField(max_length=200,null=True, blank=True)
    weighment_slip_no= models.CharField(max_length=100,null=True, blank=True)
    weighment_slip_date= models.DateField(null=True, blank=True)
    weighment_slip_time= models.TimeField(null=True, blank=True)
    user_remarks= models.CharField(max_length=255,null=True, blank=True)
    status= models.IntegerField(default=1)
    invoice = models.ForeignKey(sales_purchase_master,on_delete=models.PROTECT,null=True,blank=True)
    dc_no= models.CharField(max_length=100,null=False, blank=False)
    dc_dt= models.DateField(null=False, blank=False)
    measurement_taken_by= models.CharField(max_length=200,null=True, blank=True)
    authorised_by= models.CharField(max_length=200,null=True, blank=True)
    received_by= models.CharField(max_length=200,null=True, blank=True)
    transport_mode= models.CharField(max_length=50,null=False,blank=False)
    lr_no= models.CharField(max_length=100,null=True,blank=True)
    lr_dt= models.DateField(null=True,blank=True)

class gmr_detail(soft_delete_model):
    gmr = models.ForeignKey(gmr_master,on_delete=models.PROTECT,null=True,blank=True)
    sl_no= models.IntegerField(default=0)
    order_detail=models.ForeignKey(entity_order_detail,on_delete=models.PROTECT,null=False,blank=False)
    dc_qty= models.FloatField(default=0)
    gross_weight= models.FloatField(default=0)
    tare_weight= models.FloatField(default=0)
    net_weight= models.FloatField(default=0)
    deduction_qty = models.FloatField(default=0)
    received_qty = models.FloatField(default=0)
    basic_rate = models.FloatField(default=0)
    taxable_amt = models.FloatField(default=0)
    tax_perc =models.FloatField(default=0)
    igst_perc = models.FloatField(default=0)
    igst_amt = models.FloatField(default=0)
    cgst_perc = models.FloatField(default=0)
    cgst_amt = models.FloatField(default=0)
    sgst_perc = models.FloatField(default=0)
    sgst_amt = models.FloatField(default=0)
    accepted_qty = models.FloatField(default=0)
    user_remarks= models.CharField(max_length=255,null=True, blank=True)
    status= models.IntegerField(default=1)
