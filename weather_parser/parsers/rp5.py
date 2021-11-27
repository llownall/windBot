import datetime
from typing import List, Dict, Any
import pytz

import requests
from bs4 import BeautifulSoup

from weather_parser.parsers.base import BaseParser
from spots.models import Spot, Forecast, ForecastDay, WindDirection

WIND_DIRECTION_MAPPINGS = {
    'С': WindDirection.N,
    'С-В': WindDirection.NE,
    'В': WindDirection.E,
    'Ю-В': WindDirection.SE,
    'Ю': WindDirection.S,
    'Ю-З': WindDirection.SW,
    'З': WindDirection.W,
    'С-З': WindDirection.NW,
}


class RP5Parser(BaseParser):
    def __init__(self):
        self.forecasts: Dict[datetime.date, Any] = {}

    def _get_current_day(self, el) -> datetime.date:
        date_from_page = el.get_text().split(',')[-1].split(' ')[1]
        current_day = datetime.datetime.now().date()
        current_day = current_day.replace(day=int(date_from_page))
        return current_day

    def update_forecasts(self, spot: Spot, dates: List[datetime.date]):
        page = requests.get(spot.link_rp5)

        self.soup = BeautifulSoup(page.text, 'html.parser')
        table = self.soup.select_one('table#forecastTable_1_3')

        indexes = []

        for index, tr in enumerate(table.select('tr')):
            text = tr.td.get_text()
            if 'Сегодня,' in text:
                indexes.append(index)
            elif 'Местное время' in text:
                indexes.append(index)
            elif 'Осадки' in text:
                indexes.append(index)
            elif 'Температура' in text:
                indexes.append(index)
            elif 'Ветер: скорость' in text:
                indexes.append(index)
            elif 'порывы' in text:
                indexes.append(index)
            elif 'направление' in text:
                indexes.append(index)

        if len(indexes) != 7:
            raise Exception

        td_dates = table.select('tr')[indexes[0]].select('td')
        td_times = table.select('tr')[indexes[1]].select('td')
        # td_rains = table.select('tr')[indexes[2]].select('td')
        td_temperatures = table.select('tr')[indexes[3]].select('td')
        td_wind_min_speed = table.select('tr')[indexes[4]].select('td')
        td_wind_max_speed = table.select('tr')[indexes[5]].select('td')
        td_wind_directions = table.select('tr')[indexes[6]].select('td')

        site_local_date = self._get_current_day(td_dates[0])
        previous_time = None
        for index, td_time in enumerate(td_times):
            print(index)

            text = td_time.get_text()
            try:
                time = int(text)
            except ValueError:
                continue

            print(f'time is {time}')

            if previous_time is not None and previous_time > time:
                # Date change: 23 -> 00
                site_local_date = site_local_date + datetime.timedelta(days=1)
            previous_time = time

            if time not in [10, 13, 16]:
                continue

            if site_local_date not in dates:
                continue

            # is_raining = td_rains[index].div.div['class'] != ['wp_0']
            temperature = int(td_temperatures[index].div.get_text())

            try:
                min_wind_speed = int(td_wind_min_speed[index].div.get_text())
            except:
                min_wind_speed = 0

            if td_wind_max_speed[index].div.get_text() == '':
                max_wind_speed = min_wind_speed
            else:
                max_wind_speed = int(td_wind_max_speed[index].div.get_text())
            direction = td_wind_directions[index].get_text()

            forecast_day, _ = ForecastDay.objects.get_or_create(date=site_local_date)

            print(f'\t{time}. {min_wind_speed}-{max_wind_speed} м/c {direction}')
            print(f'\t\t{temperature} C : {site_local_date}')
            # print(f'\t\t{temperature} C : Дождь? {is_raining} : {site_local_date}')

            forecast_time = datetime.time(hour=time)

            # Delete old forecasts at this time
            Forecast.objects.filter(forecast_day=forecast_day, time=forecast_time).delete()

            Forecast.objects.create(
                time=forecast_time,
                temperature=temperature,
                wind_speed_min=min_wind_speed,
                wind_speed_max=max_wind_speed,
                wind_direction=WIND_DIRECTION_MAPPINGS.get(direction, WindDirection.NO_WIND),
                forecast_day=forecast_day,
                spot=spot,
            )
