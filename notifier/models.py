import random

from django.db import models

from personal.models import Person
from spots.models import Spot, ForecastDay


class InviteCode(models.Model):
    requester = models.ForeignKey(Person, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_code():
        def _generate_code() -> int:
            return random.randint(100000, 999999)

        code = _generate_code()
        while InviteCode.objects.filter(code=code).exists():
            code = _generate_code()

        return code


class NotificationFact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    forecast_day = models.ForeignKey(ForecastDay, on_delete=models.CASCADE)
