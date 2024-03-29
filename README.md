# Meltano and singer are not usable for us, so this tap has been moved to the archive.

# tap-dataai

`tap-dataai` is a Singer tap for API of the data.ai service. Now it can download such reports as: `app-performance`.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPi:

```bash
pipx install tap-dataai
```

Install from GitHub:

```bash
pipx install git+https://github.com/ORG_NAME/tap-dataai.git@main
```

-->

## Configuration

### Accepted Config Options

| Setting             | Required | Default | Description                                             |
|:--------------------|:--------:|:-------:|:--------------------------------------------------------|
| auth_token          | True     | None    | The token to authenticate against the API service       |
| type_report         | True     | None    | Must be product_id or company_id.                       |
| type_values         | True     | None    | Ids of the products or companies (comma separated string).               |
| granularity         | True     | None    | The granularity of the report (monthly, weekly, daily). |
| countries           | True     | None    | Countries in the report (comma separated string).                        |
| bundles             | True     | None    | Bundles in the report.                                  |
| devices             | False    | all_supported | Devices in the report.                                  |
| start_date          | True     | None    | The earliest record date to sync                        |
| end_date            | True     | None    | The latest record date to sync                          |

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-dataai --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

<!--
Developer TODO: If your tap requires special access on the source system, or any special authentication requirements, provide those here.
-->

## Usage

You can easily run `tap-dataai` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-dataai --version
tap-dataai --help
tap-dataai --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_dataai/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-dataai` CLI interface directly using `poetry run`:

```bash
poetry run tap-dataai --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-dataai
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-dataai --version
# OR run a test `elt` pipeline:
meltano elt tap-dataai target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
