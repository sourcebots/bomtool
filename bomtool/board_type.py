from abc import ABCMeta, abstractmethod
from wimpy import cached_property

class BoardType(object, metaclass=ABCMeta):
  def __init__(self, quantity, dest_sheet, exclude):
    self.quantity = quantity
    self.dest_sheet = dest_sheet
    self.exclude = set(exclude)

  def __str__(self):
    return self.name

  @property
  @abstractmethod
  def name(self):
    pass

  @property
  @abstractmethod
  def bom_xls_url(self):
    pass

  # Automatically keep a list of subclasses of BoardType.
  SUBCLASS_REGISTRY = []

  def __init_subclass__(subclass, **kwargs):
    BoardType.SUBCLASS_REGISTRY.append(subclass)
    super().__init_subclass__(**kwargs)

  @classmethod
  def get_by_name(class_, name):
    for subclass in class_.SUBCLASS_REGISTRY:
      if subclass.name == name:
        return subclass
    return None

class V4PowerBoard(BoardType):
  name = "power-v4"
  bom_xls_url = "https://github.com/sourcebots/power-v4-hw/raw/master/pbv4b_bom.xls"

class V4MotorBoard(BoardType):
  name = "motor-v4"
  bom_xls_url = "https://github.com/sourcebots/motor-v4-hw/raw/master/bom.xls"

class V4ServoBoard(BoardType):
  name = "servo-v4"
  bom_xls_url = "https://github.com/sourcebots/servo-v4-hw/raw/master/sbv4b_bom.xls"
