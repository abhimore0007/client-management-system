from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.list_or_create_clients, name='list_or_create_clients'),
    path('clients/<int:id>/', views.client_detail_or_update_or_delete, name='client_detail_or_update_or_delete'),
    path('clients/<int:client_id>/projects/', views.create_project, name='create_project'),
    path('projects/', views.user_projects, name='user_projects'),
]
