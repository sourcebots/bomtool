import logging
import re

def dereel(lines):
  for line in lines:
    if line.distributor == "farnell" and line.distributor_order_no.endswith("RL"):
      line = line._replace(
        distributor_order_no = line.distributor_order_no[:-2],
      )
    yield line

def perform_substitutions(lines, config):
  subs = {}
  for sub_config in config.get("substitutions", []):
    old = sub_config["replace"]
    new = sub_config["with"]
    old_d, old_oc = old.split(None, 1)
    new_d, new_oc = new.split(None, 1)
    subs[(old_d, old_oc)] = (new_d, new_oc)
  for old_pair, new_pair in subs.items():
    if new_pair in subs:
      raise ValueError(f"double substitution (please update the original substitution instead!): {old_pair} -> {new_pair} -> {subs[new_pair]}")
  for line in lines:
    key = (line.distributor, line.distributor_order_no)
    if key in subs:
      new_distr, new_order_no = subs[key]
      logging.info("Substituting %s %s with %s %s", line.distributor, line.distributor_order_no, new_distr, new_order_no)
      line = line._replace(
        distributor = new_distr,
        distributor_order_no = new_order_no,
      )
    yield line

def transform(lines, config):
  lines = dereel(lines)
  lines = perform_substitutions(lines, config)
  return lines
