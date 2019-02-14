import decimal
import time
from wimpy import cached_property

from ..bom_line import GENERIC

def normalise_cell(x):
  if x is None:
    return ""
  else:
    return str(x)

class GoogleSheetsOutput(object):
  def __init__(self, sheet, boards):
    self.sheet = sheet
    self.boards = boards

  def generate_sheet_name(self):
    timestamp = time.strftime("%Y%m%dT%H%M%SZ")
    return f"bomtool-{timestamp}"

  def output(self, checked_lines):
    self.sheet.clear()
    self.sheet.append(self._to_rows(checked_lines))

  def _to_rows(self, checked_lines):
    yield self._header_row
    for checked_line in checked_lines:
      yield self._to_row(checked_line)

  def _to_row(self, checked_line):
    line = checked_line.line
    notes = "\n".join(checked_line.errors + checked_line.warnings)
    if line.distributor is GENERIC:
      row = [
        line.sr_part_no,
        notes,
        "any",
        "any",
      ] + [line.quantity_per_board.get(board) for board in self.boards] + [
        line.quantity_needed,
        line.quantity_to_buy,
        "",
        "",
      ] + ([""] * len(self.boards)) + [
        line.description,
      ] + [line.sr_line_no_by_board.get(board) for board in self.boards] \
        + [", ".join(line.instances_by_board.get(board, [])) for board in self.boards]
    else:
      row = [
        line.sr_part_no,
        notes,
        line.distributor,
        line.distributor_order_no,
      ] + [line.quantity_per_board.get(board) for board in self.boards] + [
        line.quantity_needed,
        line.quantity_to_buy,
        line.unit_price,
        line.line_price,
      ] + [line.board_cost_contribution.get(board) for board in self.boards] + [
        line.description,
      ] + [line.sr_line_no_by_board.get(board) for board in self.boards] \
        + [", ".join(line.instances_by_board.get(board, [])) for board in self.boards]
    return list(map(normalise_cell, row))

  @cached_property
  def _header_row(self):
    row = [
      "SR part no",
      "Notes",
      "Distributor",
      "Distributor order no",
    ] + [f"Quantity needed per {board.name}" for board in self.boards] + [
      "Quantity needed",
      "Quantity to buy",
      "Unit price",
      "Line price",
    ] + [f"Approx contribution towards cost of {board.name}" for board in self.boards] + [
      "Description",
    ] + [f"Line no in {board.name} BOM" for board in self.boards] \
      + [f"Instances on {board.name}" for board in self.boards]
    return row
