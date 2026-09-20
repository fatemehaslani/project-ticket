from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('tickets', index, name='tickets'),
    path('tickets/create', ticket_create, name='tickets-create'),
    path('tickets/<int:id>/detail', ticket_detail, name='tickets-detail'),
    path('tickets/edit/<int:id>', ticket_edit, name='tickets-update'),
    path('tickets/delete/<int:id>', ticket_delete, name='tickets-delete'),
    path('tickets/clear', tickets_clear, name='tickets-clear'),
    path('attachments/<int:id>/delete/', attachment_delete, name='attachment_delete'),
    path('register/', register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("assignee/", assignee_ticket_list, name="assignee_list"),
    path("assignee/<int:pk>/", assignee_ticket_detail, name="assignee_detail"),

   # path('change/mode', color_mode, name="color_mode"),

]