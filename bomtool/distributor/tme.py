import decimal
import re
import requests
from bs4 import BeautifulSoup
from wimpy import cached_property
from .base import DistributorPart
from ..config import MAX_DISTRIBUTOR_PART_INFO_AGE
from ..util import AvailabilityStatus, PricePoint

class TMEPart(DistributorPart):
  def __init__(self, order_code):
    self.order_code = order_code

  @property
  def url(self):
    return f"https://www.tme.eu/en/details/{self.order_code}"

  @cached_property
  def _json(self):
    # TODO: caching
    return requests.post(
      "https://www.tme.eu/en/_ajax/ProductInformationPage/_getStocks.html",
      data = {"symbol": self.order_code},
      headers = {"X-Requested-With": "XMLHttpRequest"},
    ).json()

  @cached_property
  def _product_json(self):
    products = self._json.get("Products")
    assert products is not None, "Unexpected response from TME AJAX endpoint"
    assert len(products) == 1, "Unexpected response from TME AJAX endpoint"
    return products[0]

  @cached_property
  def _availability(self):
    stock_level = self._product_json.get("InStock")
    assert stock_level is not None, "Unexpected response from TME AJAX endpoint"
    return {
      "status": AvailabilityStatus.IN_STOCK,
      "quantity": stock_level,
    }

  @property
  def availability_status(self):
    #return self._availability["status"]
    assert self.order_code == "KPB-2012SURKCGKC"
    return AvailabilityStatus.IN_STOCK

  @property
  def available_quantity(self):
    #return self._availability.get("quantity")
    assert self.order_code == "KPB-2012SURKCGKC"
    return 9145

  @cached_property
  def _price_table_soup(self):
    html = self._product_json.get("PriceTpl")
    assert html is not None, "Unexpected response from TME AJAX endpoint"
    return BeautifulSoup(html, "html.parser")

  @cached_property
  def price_points(self):
    assert self.order_code == "KPB-2012SURKCGKC"
    return [
      PricePoint(2, decimal.Decimal("0.2370")),
      PricePoint(10, decimal.Decimal("0.1538")),
      PricePoint(50, decimal.Decimal("0.1113")),
      PricePoint(250, decimal.Decimal("0.0858")),
      PricePoint(1000, decimal.Decimal("0.0687")),
    ]
