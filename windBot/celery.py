import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "windBot.settings")
django.setup()

import datetime
from typing import List

from celery import Celery
from django.utils import timezone

app = Celery('windBot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from notifier.models import NotificationFact
from notifier.service import TelegramBot
from personal.models import Person
from spots.models import Spot, ForecastDay
from weather_parser.parsers.base import BaseParser
from weather_parser.parsers.rp5 import RP5Parser

DAYS_FORWARD_AMOUNT = 4


@app.task(bind=True)
def clean_up_database(self):
    # def clean_up_database():
    """Remove ForecastDays and related Forecasts."""
    ForecastDay.objects.filter(date__lt=timezone.now().date()).delete()


@app.task(bind=True)
def update_forecasts(self):
    # def update_forecasts():
    """Gets forecasts for each spot for some days forward except today."""

    # logging.info('update_forecasts start')

    parsers_cls: List[type(BaseParser)] = [
        RP5Parser,
    ]

    for spot in Spot.objects.filter(condition__isnull=False):
        # DAYS_FORWARD_AMOUNT from tomorrow
        dates = [timezone.now().date() + datetime.timedelta(days=i) for i in range(1, DAYS_FORWARD_AMOUNT + 1)]

        for parser_cls in parsers_cls:
            parser_cls().update_forecasts(spot, dates)

    # logging.info('update_forecasts end')


@app.task(bind=True)
def notify_users(self):
    # def notify_users():
    """Notifies users based on theirs spot conditions."""

    for person in Person.objects.filter(spot__isnull=False, telegram_id__isnull=False):
        for spot in person.spot_set.filter(condition__isnull=False):
            for forecast in spot.forecasts.filter(forecast_day__notificationfact__isnull=True):
                is_any_condition_passed = any(
                    [condition.is_proper(forecast) for condition in spot.condition_set.filter(is_active=True)]
                )
                if is_any_condition_passed:
                    TelegramBot().send_message(
                        chat_id=person.telegram_id,
                        text=forecast.get_telegram_text(),
                    )

                    NotificationFact.objects.create(
                        person=person,
                        spot=spot,
                        forecast_day=forecast.forecast_day,
                    )

                    # Go to next spot
                    break

# @app.task(bind=True)
# def update_forecasts(self):
#     logging.info('update_forecasts start')
#
#     for spot in Spot.objects.all():
#         local_forecasts = weather_parser.get_forecasts(spot)
#
#         for forecast_day in local_forecasts:
#             if not forecast_day.forecasts:
#                 continue
#
#             day_was_notified = models.ForecastDay.select() \
#                                    .where(models.ForecastDay.spot_name == spot.name,
#                                           models.ForecastDay.date == forecast_day.date).count() > 0
#
#             if not day_was_notified:
#                 wind_min_max = max([forecast.wind_min_speed for forecast in forecast_day.forecasts])
#                 wind_max_max = max([forecast.wind_max_speed for forecast in forecast_day.forecasts])
#                 temperature_max = max([forecast.temperature for forecast in forecast_day.forecasts])
#
#                 has_right_direction = False
#                 for forecast in forecast_day.forecasts:
#                     if weather_parser.rp5_directions[forecast.wind_direction] in spot.directions:
#                         has_right_direction = True
#                         break
#
#                 if wind_min_max >= conditions['min_wind_speed'] and \
#                         temperature_max >= conditions['min_temperature'] and has_right_direction:
#                     models.ForecastDay.create(
#                         date=forecast_day.date,
#                         spot_name=spot.name,
#                     )
#
#                     context.bot.send_photo(
#                         CHAT_ID,
#                         spot.image,
#                         reply_markup=InlineKeyboardMarkup(
#                             [[InlineKeyboardButton('Сайт rp5.ru', url=spot.link)]]
#                         )
#                     )
#                     context.bot.send_poll(
#                         CHAT_ID,
#                         '%s - Катальный день!\n'
#                         'Фон до %s м/c, порывы до %s м/c\n'
#                         'Макс. температура +%s°C' % (humanize_day_delta(forecast_day.date), wind_min_max,
#                                                      wind_max_max, temperature_max),
#                         ['Едем!', 'Пропускаю :('],
#                         is_anonymous=False,
#                     )
#                     time.sleep(5)
#                     break
#
#     logging.info('update_forecasts end')
