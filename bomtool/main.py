import sys
import csv
import decimal
import logging
import argparse
import yaml
from .util.cache import Cache
from .util.downloader import Downloader
from .distributor import DistributorPartFactory
from .distributor.mouser import MouserAPI
from .tasks import load_boms, join, transform, check
from .board_type import BoardType

def parse_cmdline():
  parser = argparse.ArgumentParser()
  parser.add_argument("config_file", help="path to a config.yaml")
  return parser.parse_args()

def parse_config(path):
  with open(path, "r") as file:
    return yaml.load(file.read())

def parse_boards(config):
  if "boards" not in config:
    raise ValueError("config file does not contain a top-level 'boards' section")

  boards = []
  for board_config in config["boards"]:
    board_class = BoardType.get_by_name(board_config["type"])
    board = board_class(board_config["quantity"])
    boards.append(board)
  return boards

def main():
  logging.basicConfig(level=logging.INFO)

  args = parse_cmdline()
  config = parse_config(args.config_file)
  boards = parse_boards(config)

  cache = Cache()
  downloader = Downloader(cache)
  mouser_api = MouserAPI(cache)
  distributor_part_factory = DistributorPartFactory(downloader, mouser_api)

  board_boms = load_boms(boards, downloader)
  lines = join(board_boms, distributor_part_factory)
  lines = sorted(lines, key = lambda l: l.sr_part_no)
  lines = transform(lines, config)
  total = decimal.Decimal(0)
  writer = csv.DictWriter(sys.stdout, (
    "SR part no",
    "Notes",
    "Distributor",
    "Distributor order no",
    # "Quantity needed per PB",
    # "Quantity needed per MB",
    # "Quantity needed per SB",
    "Quantity needed",
    "Quantity to buy",
    # "Quantity to buy per PB",
    # "Quantity to buy per MB",
    # "Quantity to buy per SB",
    # "Price point",
    "Unit price excl tax",
    "Line price excl tax",
    "Line price incl tax",
    "Description",
    # "Line no in SR PB BOM",
    # "Line no in SR MB BOM",
    # "Line no in SR SB BOM",
  ))
  writer.writeheader()
  for line, errors, warnings in check(lines):
    notes = "\n".join(errors + warnings)
    writer.writerow({
      "SR part no": line.sr_part_no,
      "Notes": notes,
      "Distributor": line.distributor,
      "Distributor order no": line.distributor_order_no,
      # "Quantity needed per PB": line.quantity_per_board.get(pb, ""),
      # "Quantity needed per MB": line.quantity_per_board.get(mb, ""),
      # "Quantity needed per SB": line.quantity_per_board.get(sb, ""),
      "Quantity needed": line.quantity_needed,
      "Quantity to buy": line.quantity_to_buy,
      # "Quantity to buy per PB": line.quantity_to_buy_per_board.get(pb, ""),
      # "Quantity to buy per MB": line.quantity_to_buy_per_board.get(mb, ""),
      # "Quantity to buy per SB": line.quantity_to_buy_per_board.get(sb, ""),
      # "Price point": line.price_point,
      "Unit price excl tax": f"£{line.unit_price}" if line.unit_price is not None else "",
      "Line price excl tax": f"£{line.line_price}" if line.line_price is not None else "",
      "Line price incl tax": f"£{line.line_price*decimal.Decimal('1.2')}" if line.line_price is not None else "",
      "Description": line.description,
      # "Line no in SR PB BOM": line.sr_line_no_by_board.get(pb, ""),
      # "Line no in SR MB BOM": line.sr_line_no_by_board.get(mb, ""),
      # "Line no in SR SB BOM": line.sr_line_no_by_board.get(sb, ""),
    })
    if line.line_price is not None:
      total += line.line_price
  logging.info("Total: £%s", total)


if __name__ == "__main__":
  main()
