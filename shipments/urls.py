from shipments.sync_data import api
from rest_framework import routers
from shipments.views import ShipmentViewSet, ShopViewSet, LoginViewSet

router = routers.DefaultRouter()
router.register(r'shipments-sync', api.ShipmentsSyncViewSet, base_name='ShipmentsSyncViewSet')
router.register(r'shipments', ShipmentViewSet)
router.register(r'shop', ShopViewSet)
router.register(r'login', LoginViewSet, base_name='LoginViewSet')

urlpatterns = router.urls
