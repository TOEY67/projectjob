from django.urls import path
from .views import *
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('profileedit/', profileedit_view, name='profileedit'),         
    path('status/', status_view, name='status'),
    path("<int:user_id>/", chat_view, name="chat"),
    path("inbox/", chat_list, name="chat_list"),   
    path('book/', views.create_order, name='book_appointment'),
    path('order/success/', views.order_success, name='order_success'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('Admin_Order_History/', views.order_history_view, name='Admin_Order_History'),
    path('order-history/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('tasks/', views.task_list_view, name='task_list'),
    path("chat-room/", admin_chat_room, name="admin_chat_room"),
    path('update/', views.update_view, name='update'),
    path('update/success/', views.update_success, name='update_success'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)