import decimal
import re
from bs4 import BeautifulSoup
from wimpy import cached_property
from .base import DistributorPart
from ..config import MAX_DISTRIBUTOR_PART_INFO_AGE
from ..util import AvailabilityStatus, PricePoint

class RSPart(DistributorPart):
  def __init__(self, order_code, downloader):
    self.order_code = order_code
    self.downloader = downloader

  @property
  def url(self):
    order_code = self.order_code.replace("-", "").zfill(7)
    return f"https://uk.rs-online.com/web/p/-/{order_code}/"

  @cached_property
  def _soup(self):
    document = self.downloader.get_content(self.url, max_age = MAX_DISTRIBUTOR_PART_INFO_AGE)
    return BeautifulSoup(document, "html.parser")

  @cached_property
  def _availability(self):
    tag = self._soup.find(class_ = "stock-msg-content")
    if not tag:
      return {"status": AvailabilityStatus.UNKNOWN}
    string = tag.string.strip()

    match = re.match(r"^([0-9]+) In stock for FREE next working day delivery$", string)
    if match:
      quantity = match.group(1)
      return {
        "status": AvailabilityStatus.IN_STOCK,
        "quantity": int(match.group(1).replace(",", "")),
      }

    raise ValueError(f"RS Online availability text did not match any known pattern: {string!r}")

  @property
  def availability_status(self):
    return self._availability["status"]

  @property
  def available_quantity(self):
    return self._availability.get("quantity")

  @cached_property
  def price_points(self):
    tags = self._soup.find_all(class_ = "value-row")
    price_points = []
    for tag in tags:
      qty_str = tag.find(class_ = "breakRangeWithoutUnit").string
      price_str = tag.find(class_ = "unitPrice").string.strip().lstrip("£")
      qty_match = re.match(r"^\s*([0-9]+)\s*(?:\+|-\s*[0-9]+)\s*$", qty_str)
      qty = int(qty_match.group(1))
      price = decimal.Decimal(price_str)
      price_points.append(PricePoint(qty, price))
    if price_points:
      return price_points
    else:
      return None
