import logging
import requests
from ratelimit import limits, sleep_and_retry

class Downloader(object):
  def __init__(self, cache):
    self.cache = cache

  def get_content(self, url, *, max_age=None):
    with self.get_file(url, max_age=max_age) as file:
      return file.read()

  def get_file(self, url, *, max_age=None):
    return open(self.get_path(url, max_age=max_age), "rb")

  def get_path(self, url, *, max_age=None):
    cache_key = f"url:{url}"
    path = self.cache.get(cache_key)
    if path is None:
      content = self.download(url)
      path = self.cache.put(cache_key, content)
    return path

  @sleep_and_retry
  @limits(calls=3, period=10)
  def download(self, url):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    headers = {"user-agent": user_agent}
    logging.info("Fetching %s", url)
    return requests.get(url, headers=headers).content
