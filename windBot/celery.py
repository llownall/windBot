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
    """Remove ForecastDays and related Forecasts."""
    ForecastDay.objects.filter(date__lt=timezone.now().date()).delete()


@app.task(bind=True)
def update_forecasts(self):
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
