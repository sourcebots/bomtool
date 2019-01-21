# bomtool

Given a list of board types and their required quantities, this tool:

* Downloads the original bills of materials from the respective Github repositories.
* Combines the bills of materials into a single "shopping list".
* Fetches prices and availability information from the listed distributors (currently supports Farnell, RS and Mouser).
* Decides how many of each part we should order, taking into account minimum order quantities, spares, and favourable price breaks.

In the future, this will hopefully:

* Generate a costing breakdown for each board.
* Export all of this information into a Google spreadsheet.

## Usage

Check out this repo and `cd` to it, then run:

```sh
pipenv install --pre
pipenv run python -m bomtool path/to/config.yaml
```

`--pre` must be passed to `pipenv install` since currently only pre-release versions of `pyyaml` are [considered secure](https://nvd.nist.gov/vuln/detail/CVE-2017-18342).

See `configs/smallpeice2019.yaml` for an example of a `config.yaml`.
