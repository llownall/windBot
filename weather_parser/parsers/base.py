from datetime import date
from typing import List

from spots.models import Spot, Forecast


class BaseParser:
    def update_forecasts(self, spot: Spot, dates: List[date]):
        """Implement this for each data provider."""
        raise NotImplementedError
