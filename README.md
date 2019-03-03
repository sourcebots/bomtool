# bomtool

Given a list of board types and their required quantities, this tool:

* Downloads the original bills of materials from the respective Github repositories.
* Combines the bills of materials into a single "shopping list".
* Fetches prices and availability information from the listed distributors (currently supports Farnell, RS and Mouser).
* Decides how many of each part we should order, taking into account minimum order quantities, spares, and favourable price breaks.
* Exports all of this information into a Google spreadsheet.

In the future, this will hopefully:

* Generate a costing breakdown for each board.

## Usage

Check out this repo and `cd` to it.

Install dependencies by running `pipenv install --pre`. `--pre` is required because currently only pre-release versions of `pyyaml` are [considered secure](https://nvd.nist.gov/vuln/detail/CVE-2017-18342).

Set up environment variables:

* `SB_BOMTOOL_MOUSER_API_KEY`: A valid [Mouser API](https://www.mouser.co.uk/apihome/) key.
* `SB_BOMTOOL_GOOGLE_API_CREDS`: Filename of a Google API `credentials.json` file (containing client ID, client secret and metadata). You can generate one on the [Google Cloud Platform Console](https://console.cloud.google.com/apis/credentials).

Execute `bomtool` by running:

```sh
pipenv run python -m bomtool path/to/config.yaml OUTPUT_SPEC
```

where currently the only valid form of `OUTPUT_SPEC` is `googlesheet:SPREADSHEET_ID`. Here, `SPREADSHEET_ID` should be replaced with the long alphanumeric identifier present in the URL of the spreadsheet.

For example:

```sh
pipenv run python -m bomtool configs/smallpeice2019.yaml googlesheet:1eTEkgsXN6JzumoYiGoEkO7YOBuCE3r4QvOJFlK_qb0s
```
