import math
import logging
import random
import re
from collections import namedtuple
from wimpy import cached_property
from .config import SPARES

class Generic:
  pass
GENERIC = Generic()

OriginalBOMLine = namedtuple("OriginalBOMLine", (
  "line_no",
  "sr_part_no",
  "quantity",
  "description",
  "package",
  "distributor",
  "distributor_order_no",
  "manufacturer",
  "manufacturer_part_no",
  "instances",
))

_JoinedBOMLine_nt = namedtuple("JoinedBOMLine", (
  "sr_line_no_by_board",
  "sr_part_no",
  "quantity_per_board",
  "description",
  "package",
  "distributor",
  "distributor_order_no",
  "instances_by_board",
  "distributor_part_factory",
))

def part_id_to_value(s):
  return s.split("-", 2)[2]

class JoinedBOMLine(_JoinedBOMLine_nt):
  @cached_property
  def value(self):
    return part_id_to_value(self.sr_part_no)

  @cached_property
  def distributor_part(self):
    if self.distributor_part_factory is None:
      return None
    return self.distributor_part_factory.get(self.distributor, self.distributor_order_no)

  @cached_property
  def quantity_needed(self):
    return sum(qty_on_board * board.quantity for board, qty_on_board in self.quantity_per_board.items())

  @cached_property
  def quantity_to_buy(self):
    # Start with the bare minimum quantity.
    qty = self.quantity_needed

    # Add spares.
    qty = math.ceil(qty * (1.0 + SPARES))

    # Find best price point - sometimes we can increase the quantity slightly to lower the price.
    if self.distributor_part and self.distributor_part.price_points:
      best_pp = min(self.distributor_part.price_points, key = lambda pp: max(pp.min_quantity, qty) * pp.unit_price)
      new_qty = best_pp.min_quantity
      if new_qty > qty:
        old_line_price = self.distributor_part.line_price_for(qty)
        new_line_price = self.distributor_part.line_price_for(new_qty)
        if new_line_price < old_line_price:
          logging.info("%s: increasing quantity from %d to %d to reach a better price point (£%s -> £%s)", self.sr_part_no, qty, new_qty, old_line_price, new_line_price)
        qty = new_qty

    return qty

  @cached_property
  def price_point(self):
    if self.distributor_part is None:
      return None
    return self.distributor_part.price_point_for(self.quantity_to_buy)

  @cached_property
  def unit_price(self):
    if self.price_point is None:
      return None
    return self.price_point.unit_price

  @cached_property
  def line_price(self):
    if self.unit_price is None:
      return None
    return self.quantity_to_buy * self.unit_price

  @cached_property
  def board_cost_contribution(self):
    if self.line_price is None:
      return {board: None for board in self.quantity_per_board.keys()}
    res = {}
    for board, quantity_needed_on_board in self.quantity_per_board.items():
      weight = (quantity_needed_on_board * board.quantity) / self.quantity_needed
      contribution_to_board_type = float(self.line_price) * weight
      contribution_to_single_board = contribution_to_board_type / board.quantity
      res[board] = contribution_to_single_board
    return res

  def __str__(self):
    sr_line_no_by_board = ", ".join(f"{board.name}={x}" for board, x in self.sr_line_no_by_board.items())
    quantity_per_board = ", ".join(f"{board.name}={x}" for board, x in self.quantity_per_board.items())
    instances_by_board = ", ".join(f"{board.name}={x}" for board, x in self.instances_by_board.items())
    return "\n".join((
      f"sr_line_no_by_board: {sr_line_no_by_board}",
      f"sr_part_no: {self.sr_part_no}",
      f"quantity_per_board: {quantity_per_board}",
      f"quantity_needed: {self.quantity_needed}",
      f"quantity_to_buy: {self.quantity_to_buy}",
      f"board_cost_contribution: {self.board_cost_contribution}",
      f"price_point: {self.price_point}",
      f"unit_price: £{self.unit_price}",
      f"line_price: £{self.line_price}",
      f"description: {self.description}",
      f"package: {self.package}",
      f"distributor: {self.distributor}",
      f"distributor_order_no: {self.distributor_order_no}",
      f"instances_by_board: {instances_by_board}",
      "-"*50,
    ))
