from django.urls import path, re_path
from . import views

app_name = 'transactions'

urlpatterns = [
path('records-variations/', views.records_variations, name='records_variations'),   
path('upload/', views.upload_file, name='upload'),
re_path(r'^record/(?P<record_id>[a-fA-F0-9\-]+)/$', views.view_record, name='view_record'),
path('update-variation/<uuid:variation_id>/', views.update_variation, name='update_variation'),
    path('delete-variation/<uuid:variation_id>/', views.delete_variation, name='delete_variation'),
    path('do-update-variation/<uuid:variation_id>/', views.do_update_variation, name='do_update_variation'),
    path('add-variation/<uuid:record_id>/', views.add_variation, name='add_variation'),

     path('disable_variation/<uuid:variation_id>/', views.disable_variation, name='disable_variation'),
   path('generate-test-data/', views.view_variations, name='generate_test_data'),
  # Other URL patterns
]


