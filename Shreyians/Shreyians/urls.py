"""
URL configuration for Shreyians project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/',signup,name='signup'),
    path('signin/',signin,name='signin'),
    path('signout/',signout,name='signout'),
    path('',home,name='home'),
    path('courses/',course_list, name='course_list'),
    path('courses/<slug:slug>/', course_detail, name='course_detail'),
    path('cart/add/<int:course_id>/', add_to_cart, name='add_to_cart'),
    path('add_course/',add_course,name='add_course'),
    path('cart/update/<int:course_id>/<str:action>/', update_cart, name='update_cart'),
    path('cart/', cart_page, name='cart_page'),
    path('checkout/', checkout_page, name='checkout_page'),
    path('confirm_order/', confirm_order, name='confirm_order'),
]
urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
