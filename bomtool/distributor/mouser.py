import decimal
import os
import pickle
import re
import zeep
from wimpy import cached_property
from .base import DistributorPart
from ..config import MAX_DISTRIBUTOR_PART_INFO_AGE
from ..util import AvailabilityStatus, PricePoint

class MouserPart(DistributorPart):
  def __init__(self, order_code, api):
    self.order_code = order_code
    self.api = api

  @cached_property
  def _part_info(self):
    return self.api.lookup(self.order_code)

  @cached_property
  def url(self):
    return self._part_info.ProductDetailUrl

  @cached_property
  def _availability(self):
    string = self._part_info.Availability
    if string is None:
      if self._part_info.LifecycleStatus == "Obsolete":
        return {"status": AvailabilityStatus.NOT_STOCKED}
      else:
        raise ValueError(f"Mouser lifecycle status text did not match any known pattern: {self._part_info.LifecycleStatus!r}")

    match = re.match(r"^([0-9]+) In Stock$", string)
    if match:
      quantity = match.group(1)
      return {
        "status": AvailabilityStatus.IN_STOCK,
        "quantity": int(match.group(1).replace(",", "")),
      }

    match = re.match(r"^([0-9]+) On Order$", string)
    if match:
      quantity = match.group(1)
      return {"status": AvailabilityStatus.AWAITING_DELIVERY}

    raise ValueError(f"Mouser availability text did not match any known pattern: {string!r}")

  @property
  def availability_status(self):
    return self._availability["status"]

  @property
  def available_quantity(self):
    return self._availability.get("quantity")

  @cached_property
  def price_points(self):
    if self._part_info.PriceBreaks is None:
      return None
    price_points = []
    for pb in self._part_info.PriceBreaks.Pricebreaks:
      min_quantity = pb.Quantity
      unit_price = decimal.Decimal(pb.Price.strip("£"))
      price_points.append(PricePoint(min_quantity, unit_price))
    return price_points

class MouserAPI(object):
  def __init__(self, cache):
    self.cache = cache

  @cached_property
  def client(self):
    client = zeep.Client("http://api.mouser.com/service/searchapi.asmx?WSDL")
    api_key = os.environ["SB_BOMTOOL_MOUSER_API_KEY"]
    account_info_type = client.get_type("{http://api.mouser.com/service}AccountInfo")
    header_type = client.get_element("{http://api.mouser.com/service}MouserHeader")
    account_info_value = account_info_type(PartnerID=api_key)
    header_value = header_type(AccountInfo=account_info_value)
    client.set_default_soapheaders([header_value])
    return client

  def lookup(self, order_code):
    cache_key = f"mouser:{order_code}"
    path = self.cache.get(cache_key, max_age = MAX_DISTRIBUTOR_PART_INFO_AGE)
    if path is None:
      part = self._lookup(order_code)
      self.cache.put(cache_key, pickle.dumps(part))
      return part
    else:
      with open(path, "rb") as file:
        return pickle.load(file)

  def _lookup(self, order_code):
    response = self.client.service.SearchByPartNumber(order_code)
    for part in response.Parts.MouserPart:
      if part.MouserPartNumber == order_code:
        return part
    raise ValueError(f"Mouser API search returned no results: {order_code}")
