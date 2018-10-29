import datetime
import hashlib
import pathlib

class Cache(object):
  def __init__(self, path=None):
    if path is None:
      path = self.get_default_path()
    self.path = pathlib.Path(path)

  def get(self, key, *, max_age=None):
    path = self.path_for_key(key)
    if not path.exists():
      return None
    elif max_age is not None and older_than(path, max_age):
      return None
    else:
      return path

  def put(self, key, content):
    path = self.path_for_key(key)
    ensure_parent_directory_exists(path)
    with open(path, "wb") as file:
      file.write(content)
    return path

  def path_for_key(self, key):
    hash = hashlib.sha1(key.encode("ascii")).hexdigest()
    return self.path / hash

  @staticmethod
  def get_default_path():
    return pathlib.Path.home() / ".cache" / "sb-bomtool"

def older_than(path, age):
  return path.stat().st_mtime < (datetime.datetime.now() - age).timestamp()

def ensure_parent_directory_exists(path):
  if not path.parent.exists():
    path.parent.mkdir(parents=True)
