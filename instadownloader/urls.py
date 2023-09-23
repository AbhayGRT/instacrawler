from django.urls import path
from . import views

urlpatterns = [
    path('get_instagram_info/', views.get_instagram_info, name='get_instagram_info'),
    path('download_yes/', views.download_yes_view, name='download_yes'),
    path('download_no/', views.download_no_view, name='download_no'),
    path('download_data/', views.download_data_view, name='download_data'),
    path('download_media/',views.download_media_view,name='download_media'),
    path('download_profile_photo/', views.download_profile_photo_view, name='download_profile_photo'),
    path('download-statistics/', views.download_statistics_view, name='download_statistics'),
    path('dashboards', views.dashboard_view, name='dashboards'),
]