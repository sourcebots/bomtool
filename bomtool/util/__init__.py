from collections import namedtuple
from enum import Enum, auto
from . import cache, downloader

class AvailabilityStatus(Enum):
  IN_STOCK = auto()
  AWAITING_DELIVERY = auto()
  NOT_STOCKED = auto()
  UNKNOWN = auto()

_PricePoint_nt = namedtuple("PricePoint", ("min_quantity", "unit_price"))

class PricePoint(_PricePoint_nt):
  def __str__(self):
    return f"{self.min_quantity}+ @ £{self.unit_price}/unit"
