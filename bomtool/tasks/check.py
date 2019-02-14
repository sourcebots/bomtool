from collections import namedtuple
from ..util import AvailabilityStatus

CheckedLine = namedtuple("CheckedLine", ("line", "errors", "warnings"))

from ..bom_line import GENERIC

def check(lines):
  for line in lines:
    errors = []
    warnings = []

    if line.distributor is GENERIC:
      pass
    elif line.distributor_part is None:
      errors.append(f"can't automatically query distributor: {line.distributor}")
    else:
      status = line.distributor_part.availability_status
      if status == AvailabilityStatus.IN_STOCK:
        if line.distributor_part.available_quantity < line.quantity_to_buy:
          errors.append(f"not enough stock (want {line.quantity_to_buy}, while only {line.distributor_part.available_quantity} are available)")
        elif line.distributor_part.available_quantity < line.quantity_to_buy*2:
          warnings.append(f"low stock (want {line.quantity_to_buy}, while only {line.distributor_part.available_quantity} are available)")
      elif status == AvailabilityStatus.AWAITING_DELIVERY:
        warnings.append("awaiting delivery")
      elif status == AvailabilityStatus.NOT_STOCKED:
        errors.append("not stocked (e.g. part is obsolete)")
      else:
        errors.append(f"unknown availability status ({status})")
    yield CheckedLine(line, errors, warnings)
