from rms_ins.allviews.Admin import company,groups,user,plant,unit,tax,product,number,approval_settings
from rms_ins.allviews.Accounts import accounting_master
from rms_ins.allviews.store import goods_receipt
from rms_ins.allviews.Purchase import vendor
from rms_ins.allviews.Marketting import sales_order
from rms_ins.allviews.Transport import equipment
from rest_framework.urlpatterns import format_suffix_patterns
app_name = 'ims'
from rms_ins.allviews.Purchase import purchase_order
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from django.conf.urls import (handler404)
# from rmc.utils import error404

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'accounting_master', accounting_master.GroupingViewSet,basename="accounting_masters")

router.register(r'entity_company',company.CompanyViewSet,basename="entity_companys")
router.register(r'entity_plant',plant.PlantViewSet,basename="entity_plants")

router.register(r'groups_and_perms',groups.GroupViewSet,basename="groups_and_perm")
router.register(r'user',user.UserViewSet,basename="users")

router.register(r'unit',unit.UnitViewSet,basename="units")
router.register(r'tax',tax.TaxViewSet,basename="taxes")
router.register(r'products',product.ProductViewSet,basename="products")
router.register(r'vendors',vendor.VendorViewSet,basename="vendors")
router.register(r'number_settings',number.NumberingViewSet,basename="number_settings")

router.register(r'approval_settings',approval_settings.ApprovalViewSet,basename="approval_settings")
router.register(r'sales_orders',sales_order.SalesOrderViewSet,basename="sales_orders")
# router.register(r'quotations',quotation.QuotationViewSet,basename="quotations")
router.register(r'purchase_orders',purchase_order.PurchaseOrderViewSet,basename="purchase_orders")
router.register(r'goods_receipt_notes',goods_receipt.GoodsMovementMasterViewSet,basename="goods_receipt_notes")
router.register(r'equipments',equipment.EquipmentViewSet,basename="equipments")
urlpatterns = [

    path('', include(router.urls)),
]

#router.register(r'goods_receipt_notes',goods_receipt.GoodsMovementMasterViewSet,basename="goods_receipt_notes")
