import logging
import argparse
from ruamel.yaml import YAML
from .util.cache import Cache
from .util.downloader import Downloader
from .util.google_sheets_api import GoogleSheetsAPI
from .output.google_sheets import GoogleSheetsOutput
from .distributor import DistributorPartFactory
from .distributor.mouser import MouserAPI
from .tasks import load_boms, join, transform, check
from .board_type import BoardType

def parse_cmdline():
  parser = argparse.ArgumentParser()
  parser.add_argument("config_file", help="path to a config.yaml")
  parser.add_argument("output", help="output format specifier in format googlesheet:SPREADSHEET_ID")
  return parser.parse_args()

def parse_config(path):
  yaml = YAML(typ="safe")
  with open(path, "r") as file:
    return yaml.load(file.read())

def parse_boards(config):
  if "boards" not in config:
    raise ValueError("config file does not contain a top-level 'boards' section")

  boards = []
  for board_config in config["boards"]:
    board_class = BoardType.get_by_name(board_config["type"])
    qty = board_config["quantity"]
    if qty == 0:
      continue
    board = board_class(qty, board_config.get("dest_sheet"), board_config.get("exclude", []))
    boards.append(board)
  return boards

def construct_output(spec, boards):
  # TODO: ideally, we shouldn't need to pass 'boards' to this function.
  kind, param = spec.split(":", 1)
  if kind == "googlesheet":
    spreadsheet_id = param
    google_sheets_api = GoogleSheetsAPI()
    spreadsheet = google_sheets_api.spreadsheet(spreadsheet_id)
    return GoogleSheetsOutput(spreadsheet, boards)
  else:
    raise ValueError(f"unsupported output kind: {kind}")

def main():
  logging.basicConfig(level=logging.INFO)

  args = parse_cmdline()
  config = parse_config(args.config_file)
  boards = parse_boards(config)
  output = construct_output(args.output, boards)

  cache = Cache()
  downloader = Downloader(cache)
  mouser_api = MouserAPI(cache)
  distributor_part_factory = DistributorPartFactory(downloader, mouser_api)

  board_boms = load_boms(boards, downloader)
  lines = join(board_boms, distributor_part_factory)
  lines = sorted(lines, key = lambda l: l.sr_part_no)
  lines = transform(lines, config)
  checked_lines = check(lines)
  output.output(checked_lines)

if __name__ == "__main__":
  main()
