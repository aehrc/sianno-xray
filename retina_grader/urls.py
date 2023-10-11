from django.urls import path

from . import views

urlpatterns = [
 	path('', views.index, name='index'),
 	path('index_json/', views.index_json, name='index_json'),

    path('detail/', views.detail, name='detail'),
	path('data_export/', views.data_export, name='data_export'),
    path('new_files/', views.new_files, name='new_files'),
    path('get_image/', views.get_image, name='get_image'),
]