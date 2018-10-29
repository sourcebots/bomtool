from abc import ABCMeta, abstractmethod
from wimpy import cached_property

class DistributorPart(object, metaclass=ABCMeta):
  @property
  @abstractmethod
  def url(self):
    pass

  @property
  @abstractmethod
  def availability_status(self):
    pass

  @property
  @abstractmethod
  def available_quantity(self):
    pass

  @property
  @abstractmethod
  def price_points(self):
    pass

  @cached_property
  def min_order_quantity(self):
    return min(pp.min_quantity for pp in self.price_points)

  def _tailor_for_min_order_quantity(self, quantity):
    return max(quantity, self.min_order_quantity)

  def price_point_for(self, quantity):
    if not self.price_points:
      return None
    quantity = self._tailor_for_min_order_quantity(quantity)
    usable_pps = [pp for pp in self.price_points if quantity >= pp.min_quantity]
    return min(usable_pps, key = lambda pp: quantity * pp.unit_price)

  def unit_price_for(self, quantity):
    if not self.price_points:
      return None
    return self.price_point_for(quantity).unit_price

  def line_price_for(self, quantity):
    if not self.price_points:
      return None
    return self.unit_price_for(quantity) * self._tailor_for_min_order_quantity(quantity)
