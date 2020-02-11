from setuptools import setup

setup(
  name = "sb-bomtool",
  version = "0.1",
  packages = [
    "bomtool",
    "bomtool.distributor",
    "bomtool.tasks",
    "bomtool.util",
  ],
  entry_points = {
    "console_scripts": [
      "bomtool = bomtool.main:main",
    ],
  },
  install_requires = [
    "beautifulsoup4",
    "google-api-python-client",
    "google-auth-httplib2",
    "google-auth-oauthlib",
    "ratelimit",
    "ruamel.yaml",
    "requests",
    "wimpy",
    "xlrd",
    "zeep",
  ],
)
