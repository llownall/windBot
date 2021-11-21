"""windBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path

from personal.views import settings_view

urlpatterns = [
    path('settings/', settings_view, name='settings'),
    # path('create/', SpotCreateView.as_view(), name='spots_create'),
    # path('<int:pk>/update/', SpotUpdateView.as_view(), name='spots_update'),
    #
    # path('<int:spot_id>/conditions/', ConditionList.as_view(), name='conditions_list'),
    # path('<int:spot_id>/conditions/create/', ConditionCreateView.as_view(), name='conditions_create'),
    # path('<int:spot_id>/conditions/<int:pk>/update/', ConditionUpdateView.as_view(), name='conditions_update'),
]
