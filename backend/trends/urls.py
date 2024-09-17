"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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


# Correct usage in urls.py
# from django.contrib import admin
# from django.urls import include, path
# from .views import StockNewsView  # make sure you're importing your view

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('stock.urls')), 
# ]

from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from .views import StockNewsViewSet
from .views import AveragePricesGraph
from .views import CompanyDescription
from .views import FinancialMetricsViewSet

# Create the router and register your viewsets
router = DefaultRouter()
router.register(r'stocknews', StockNewsViewSet, basename='stocknews')
router.register(r'averageprices', AveragePricesGraph, basename='averageprices')
router.register(r'companydescription', CompanyDescription, basename='companydescription')
router.register(r'financialmetrics', FinancialMetricsViewSet, basename='financialmetrics')

# URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),  # Include admin URLs with a trailing slash
    path("", include(router.urls)),  # Include the router's URLs
]
