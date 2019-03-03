import xlrd
from ..config import MAX_ORIGINAL_BOM_AGE
from ..bom_line import OriginalBOMLine

def load_bom(board, downloader):
  path = downloader.get_path(board.bom_xls_url, max_age = MAX_ORIGINAL_BOM_AGE)
  workbook = xlrd.open_workbook(path)
  sheet = workbook.sheets()[0]
  rows = sheet.get_rows()
  header_row = next(rows)
  expected_header_row = [
    ("Line No.",),
    ("Internal Part No.", "Internal Part Number"),
    ("Qty",),
    ("Value/Description",),
    ("Package",),
    ("Distributor",),
    ("Distributor Order No.", "Distributor Order Number"),
    ("Manufacturer",),
    ("Part No.", "Manufacturer P/N"),
    ("Reference Designators",),
  ]
  for cell, expected_contents in zip(header_row, expected_header_row):
    if cell.ctype != 1 or cell.value not in expected_contents:
      raise ValueError(f"invalid header cell: {cell.value}")
  for row in rows:
    instances = set(refdes.strip() for refdes in row[9].value.split(","))
    instances -= board.exclude
    if not instances:
      logging.info("%s: skipping due to exclusion rules", line.sr_part_no)
      continue
    sr_part_no = row[1].value.strip()
    package = row[4].value.strip()
    # Hack to fix the fact that sr-led-redgreen-0805 is used to identify two different parts in the different upstream BOMs
    if sr_part_no == "sr-led-redgreen-0805" and package != "0805":
      assert package == "0805_split"
      sr_part_no = "sr-led-redgreen-dual"
    yield OriginalBOMLine(
      line_no = int(row[0].value),
      sr_part_no = sr_part_no,
      quantity = int(row[2].value),
      description = row[3].value.strip(),
      package = package,
      distributor = row[5].value.strip(),
      distributor_order_no = row[6].value.strip(),
      manufacturer = row[7].value.strip(),
      manufacturer_part_no = row[8].value.strip(),
      instances = instances,
    )

def load_boms(boards, downloader):
  return {board: load_bom(board, downloader) for board in boards}
