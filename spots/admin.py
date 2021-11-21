from django.contrib import admin

from spots.models import Spot, ForecastDay, Forecast, Condition

admin.site.register(Spot)
admin.site.register(ForecastDay)
admin.site.register(Forecast)
admin.site.register(Condition)
