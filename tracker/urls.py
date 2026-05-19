from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('', views.home, name='home'),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='tracker/login_new.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login'
        ),
        name='logout'
    ),

    path(
        'add/',
        views.add_expense,
        name='add_expense'
    ),
    path(
    'expenses/',
    views.expense_list,
    name='expense_list'
),

path(
    'edit/<int:expense_id>/',
    views.edit_expense,
    name='edit_expense'
),

path(
    'delete/<int:expense_id>/',
    views.delete_expense,
    name='delete_expense'
),

path(
    'chart/',
    views.expense_chart,
    name='expense_chart'
),
path(
    'download-csv/',
    views.download_csv,
    name='download_csv'
),

]