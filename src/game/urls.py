"""game URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view  
import rest_framework
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="NMM API",
        default_version='v1.1',
        description="Nine Men's Morris",
        terms_of_service="https://alexandros-kalogerakis.com/SLA.pdf",
        contact=openapi.Contact(email="itp20105@hua.gr"),
        license=openapi.License(name="itp20105-itp20111-itp20126"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'), 

    path('web_app/', include('web_app.urls')),

    path('api-auth/', include('rest_framework.urls')),

    path('admin/', admin.site.urls),

]
