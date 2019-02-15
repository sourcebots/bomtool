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
    return self._availability["status"]

  @property
  def available_quantity(self):
    return self._availability.get("quantity")

  @cached_property
  def _price_table_soup(self):
    html = self._product_json.get("PriceTpl")
    assert html is not None, "Unexpected response from TME AJAX endpoint"
    return BeautifulSoup(html, "html.parser")

  @cached_property
  def price_points(self):
    print(self._price_table_soup.prettify())
    tags = self._price_table_soup.find("tbody").find_all("tr")
    price_points = []
    for tag in tags:
      tds = tag.find_all("td")
      assert len(tds) == 3
      qty_str = tds[0].string.strip().rstrip("+")
      price_str = tds[2].find("span").string.strip().lstrip("£ ")
      qty = int(qty_str)
      price = decimal.Decimal(price_str)
      price_points.append(PricePoint(qty, price))
    if price_points:
      return price_points
    else:
      return None
