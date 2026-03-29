from django.urls import path
from django.conf import settings
from . import views
from django.conf.urls.static import static

urlpatterns = [
   
    path('owner/',views.register_owner),
    path('tenent/',views.register_tenent),
    path('login/',views.tenant_login),
    path('verify/',views.owner_login),
    path('details/<path:email>/', views.get_hostel_step3),
    path('owner_props/', views.get_properties_listing),
    path('tenentbeds/', views.registerbeds),
    path('getbeds/', views.get_tenantsbeds),
    path('owner-admin/', views.owner_admin_list),
    path('owner_data/<path:email>/', views.get_owner_full_details),
    path('owner-status/<path:email>/', views.update_owner_status),
    path('check-owner-status/<path:email>/', views.check_owner_status),
    path('get_all_property_basic_details/', views.get_all_property_basic_details),
    path("admin_home/", views.dashboard_counts),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)