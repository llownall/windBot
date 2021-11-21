from __future__ import annotations

from typing import Union, TYPE_CHECKING
if TYPE_CHECKING:
    from spots.models import ForecastDay

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from telegram import Update

from notifier.utils import extract_user_data_from_update


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=20, null=True, blank=True)

    @property
    def has_telegram(self):
        return self.telegram_id is not None

    @staticmethod
    def get_person(update: Update) -> Union[Person, None]:
        user_data = extract_user_data_from_update(update)
        return Person.objects.filter(telegram_id=user_data['user_id']).first()

    def was_notified(self, forecast_day: ForecastDay):
        return self.notificationfact_set.filter(forecast_day=forecast_day).exists()


@receiver(post_save, sender=User)
def create_person(sender, instance: User, created: bool, **kwargs):
    if created:
        Person.objects.create(
            user=instance
        )
