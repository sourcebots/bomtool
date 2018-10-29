import decimal
import re
from bs4 import BeautifulSoup
from wimpy import cached_property
from .base import DistributorPart
from ..config import MAX_DISTRIBUTOR_PART_INFO_AGE
from ..util import AvailabilityStatus, PricePoint

class FarnellPart(DistributorPart):
  def __init__(self, order_code, downloader):
    self.order_code = order_code
    self.downloader = downloader

  @property
  def url(self):
    return f"https://uk.farnell.com/-/-/-/dp/{self.order_code}"

  @cached_property
  def _soup(self):
    document = self.downloader.get_content(self.url, max_age = MAX_DISTRIBUTOR_PART_INFO_AGE)
    return BeautifulSoup(document, "html.parser")

  @cached_property
  def _availability(self):
    tag = self._soup.find(class_ = "availabilityHeading")
    if not tag:
      return {"status": AvailabilityStatus.UNKNOWN}
    string = tag.string.strip()

    if string == "Awaiting Delivery":
      return {"status": AvailabilityStatus.AWAITING_DELIVERY}
    if string in ("New product", "No Longer Manufactured", "No Longer Stocked"):
      return {"status": AvailabilityStatus.NOT_STOCKED}

    match = re.match(r"^([0-9,]+) In stock$", string)
    if match:
      quantity = match.group(1)
      return {
        "status": AvailabilityStatus.IN_STOCK,
        "quantity": int(match.group(1).replace(",", "")),
      }

    raise ValueError(f"Farnell availability text did not match any known pattern: {string!r}")

  @property
  def availability_status(self):
    return self._availability["status"]

  @property
  def available_quantity(self):
    return self._availability.get("quantity")

  @cached_property
  def price_points(self):
    tags = self._soup.find_all(class_ = "data-product-pricerow-main-0")
    price_points = []
    for tag in tags:
      qty_str = tag.find(class_ = "qty").string.rstrip("+")
      price_str = tag.find(class_ = "qty_price_range").string.lstrip("£")
      qty = int(qty_str)
      price = decimal.Decimal(price_str)
      price_points.append(PricePoint(qty, price))
    if price_points:
      return price_points
    else:
      return None
