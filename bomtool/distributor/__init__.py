from .base import DistributorPart
from .farnell import FarnellPart
from .rs import RSPart
from .mouser import MouserPart
from .tme import TMEPart
from .rapid import RapidPart

class DistributorPartFactory(object):
  def __init__(self, downloader, mouser_api):
    self.downloader = downloader
    self.mouser_api = mouser_api

  def get(self, distributor, order_code):
    if distributor == "farnell":
      return FarnellPart(order_code, self.downloader)
    elif distributor == "rs":
      return RSPart(order_code, self.downloader)
    elif distributor == "mouser":
      return MouserPart(order_code, self.mouser_api)
    elif distributor == "tme":
      return TMEPart(order_code)
    elif distributor == "rapid":
      return RapidPart(order_code, self.downloader)
    else:
      raise Exception(f"cannot query distributor: {distributor}")
