from ..bom_line import JoinedBOMLine

def join(board_boms, distributor_part_factory):
  collated = {} # dict of SR part number to dict of board to original line
  for board, original_lines in board_boms.items():
    for original_line in original_lines:
      collated.setdefault(original_line.sr_part_no, {})[board] = original_line
  for original_lines_by_board in collated.values():
    sr_line_no_by_board = {}
    quantity_per_board = {}
    instances_by_board = {}
    for board, original_line in original_lines_by_board.items():
      sr_line_no_by_board[board] = original_line.line_no
      quantity_per_board[board] = original_line.quantity
      instances_by_board[board] = original_line.instances
    some_original_line = next(iter(original_lines_by_board.values()))
    yield JoinedBOMLine(
      sr_line_no_by_board = sr_line_no_by_board,
      sr_part_no = some_original_line.sr_part_no,
      quantity_per_board = quantity_per_board,
      description = some_original_line.description,
      package = some_original_line.package,
      distributor = some_original_line.distributor,
      distributor_order_no = some_original_line.distributor_order_no,
      instances_by_board = instances_by_board,
      distributor_part_factory = distributor_part_factory,
    )
