import decimal
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from wimpy import cached_property
from .base import DistributorPart
from ..config import MAX_DISTRIBUTOR_PART_INFO_AGE
from ..util import AvailabilityStatus, PricePoint

class RapidPart(DistributorPart):
  def __init__(self, order_code, downloader):
    self.order_code = order_code
    self.downloader = downloader

  @property
  def url(self):
    return f"https://www.rapidonline.com/Catalogue/Search?Query={quote_plus(self.order_code)}"

  @cached_property
  def _soup(self):
    document = self.downloader.get_content(self.url, max_age = MAX_DISTRIBUTOR_PART_INFO_AGE)
    return BeautifulSoup(document, "html.parser")

  @cached_property
  def _availability(self):
    tag = self._soup.find(class_ = "stock-message-text")
    if not tag:
      return {"status": AvailabilityStatus.UNKNOWN}
    assert len(tag.contents) >= 2
    assert tag.contents[1].name == "span"
    string = tag.contents[1].contents[0].strip()

    #if string == "Awaiting Delivery":
    #  return {"status": AvailabilityStatus.AWAITING_DELIVERY}
    #if string in ("New product", "No Longer Manufactured", "No Longer Stocked"):
    #  return {"status": AvailabilityStatus.NOT_STOCKED}

    match = re.match(r"^([0-9]+)\s+In\s+Stock", string, re.IGNORECASE)
    if match:
      quantity = match.group(1)
      return {
        "status": AvailabilityStatus.IN_STOCK,
        "quantity": int(match.group(1)),
      }

    raise ValueError(f"Rapid Online availability text did not match any known pattern: {string!r}")

  @property
  def availability_status(self):
    return self._availability["status"]

  @property
  def available_quantity(self):
    return self._availability.get("quantity")

  @cached_property
  def price_points(self):
    table = self._soup.find(class_ = "largePriceTable striped mConnectors")
    row_tags = table.find_all("tr")
    price_points = []
    for row_tag in row_tags:
      cell_tags = list(row_tag.find_all("td"))
      if not cell_tags:  # skip header row, which uses <th> instead
        continue
      qty_str = cell_tags[0].string.rstrip("+")
      price_str = cell_tags[1].find("strong").string.lstrip("£")
      qty = int(qty_str)
      price = decimal.Decimal(price_str)
      price_points.append(PricePoint(qty, price))
    if price_points:
      return price_points
    else:
      return None
