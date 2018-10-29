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

```sh
pipenv run python -m bomtool path/to/config.yaml
```

See `configs/smallpeice2019.yaml` for an example of a `config.yaml`.
