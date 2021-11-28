from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# rp5_directions = {
#     'С': WindDirection.N,
#     'С-В': WindDirection.NE,
#     'В': WindDirection.E,
#     'Ю-В': WindDirection.SE,
#     'Ю': WindDirection.S,
#     'Ю-З': WindDirection.SW,
#     'З': WindDirection.W,
#     'С-З': WindDirection.NW,
# }
from personal.models import Person


class WindDirection(models.IntegerChoices):
    NO_WIND = 0, _('Штиль')
    N = 1, _('Север')
    NE = 2, _('Северо-Восток')
    E = 3, _('Восток')
    SE = 4, _('Юго-Восток')
    S = 5, _('Юг')
    SW = 6, _('Юго-Запад')
    W = 7, _('Запад')
    NW = 8, _('Северо-Запад')


class Precipitation(models.IntegerChoices):
    __empty__ = _('Любые')
    NO = 1, _('Нет')
    LOW = 2, _('Слабые')
    HEAVY = 3, _('Сильные')


class Spot(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='spots_images', null=True, blank=True)
    creator = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)

    link_rp5 = models.URLField()

    # link_windguru = models.URLField()
    # link_gismeteo = models.URLField()

    def __str__(self):
        return f'<Spot: {self.name}>'


class ForecastDay(models.Model):
    date = models.DateField()

    def __str__(self):
        return f'<ForecastDay: {str(self.date)}>'


class Forecast(models.Model):
    time = models.TimeField()
    temperature = models.IntegerField()
    wind_speed_min = models.IntegerField()
    wind_speed_max = models.IntegerField()
    wind_direction = models.IntegerField(choices=WindDirection.choices)
    # precipitation = models.IntegerField(choices=Precipitation.choices)

    forecast_day = models.ForeignKey(ForecastDay, on_delete=models.CASCADE, related_name='forecasts')
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='forecasts')

    def get_telegram_text(self):
        return f'{self.forecast_day.date.strftime("%d.%m.%Y")} - {self.time.strftime("%H:%M")}\n' \
               f'Ветер от {self.wind_speed_min} до {self.wind_speed_max} м/с\n' \
               f'Направление - {self.get_wind_direction_display()}\n' \
               f'Температура {self.temperature}°С'

    def __str__(self):
        return f'<Forecast: {self.time} - {self.forecast_day}>'


class Condition(models.Model):
    sequence_number = models.IntegerField(null=True)
    is_active = models.BooleanField()
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)

    wind_speed_min = models.IntegerField()
    wind_speed_max = models.IntegerField()
    wind_directions = ArrayField(models.IntegerField(choices=WindDirection.choices))

    temperature_min = models.IntegerField()
    temperature_max = models.IntegerField()

    # precipitation = models.IntegerField(choices=Precipitation.choices)

    def is_proper(self, forecast: Forecast):
        return self.wind_speed_min <= forecast.wind_speed_min and \
               forecast.wind_speed_max <= self.wind_speed_max and \
               self.temperature_min <= forecast.temperature <= self.temperature_max

    def __str__(self):
        return f'<Condition: {self.spot}>'


@receiver(post_save, sender=Condition)
def create_condition(sender, instance: Condition, created: bool, **kwargs):
    if created:
        newest_user_condition = Condition.objects.filter(
            spot=instance.spot, sequence_number__isnull=False
        ).last()
        if not newest_user_condition or not newest_user_condition.sequence_number:
            last_number = 0
        else:
            last_number = newest_user_condition.sequence_number
        instance.sequence_number = last_number + 1
        instance.save()
