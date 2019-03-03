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
  def __init__(self, spreadsheet, boards):
    self.spreadsheet = spreadsheet
    self.boards = boards

  def generate_sheet_name(self):
    timestamp = time.strftime("%Y%m%dT%H%M%SZ")
    return f"bomtool-{timestamp}"

  def output(self, checked_lines):
    sheet_rows = self._to_rows(checked_lines)
    for sheet_name, rows in sheet_rows:
      sheet = self.spreadsheet.sheet(sheet_name)
      sheet.clear()
      sheet.append(rows)

  def _to_rows(self, checked_lines):
    combined_rows = [self._combined_header_row]
    board_rows = {board: [self._board_header_row(board)] for board in self.boards}
    for checked_line in checked_lines:
      row = self._to_combined_row(checked_line)
      combined_rows.append(row)
      for board in checked_line.line.sr_line_no_by_board.keys():
        row = self._to_board_row(checked_line, board)
        board_rows[board].append(row)
    return [("Combined", combined_rows)] + [(board.dest_sheet, rows) for board, rows in board_rows.items()]

  def _to_combined_row(self, checked_line):
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
  def _combined_header_row(self):
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

  def _to_board_row(self, checked_line, board):
    line = checked_line.line
    notes = "\n".join(checked_line.errors + checked_line.warnings)
    if line.distributor is GENERIC:
      row = [
        line.sr_line_no_by_board.get(board),
        line.sr_part_no,
        "any",
        "any",
        line.quantity_per_board.get(board),
        line.description,
        ", ".join(line.instances_by_board.get(board, [])),
        notes,
      ]
    else:
      row = [
        line.sr_line_no_by_board.get(board),
        line.sr_part_no,
        line.distributor,
        line.distributor_order_no,
        line.quantity_per_board.get(board),
        line.description,
        ", ".join(line.instances_by_board.get(board, [])),
        notes,
      ]
    return list(map(normalise_cell, row))

  def _board_header_row(self, board):
    row = [
      f"Line no in {board.name} BOM",
      "SR part no",
      "Distributor",
      "Distributor order no",
      f"Quantity per {board.name}",
      "Description",
      f"Instances on {board.name}",
      "Notes",
    ]
    return row
