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
)