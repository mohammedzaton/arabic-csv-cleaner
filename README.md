# Arabic CSV Cleaner

[الدليل العربي](README.ar.md)

A small, dependency-free Python tool for cleaning Arabic and mixed-language CSV
exports locally. Useful for inventory lists, item codes and spreadsheet imports.
No API keys, accounts, telemetry or network calls.

## What it does

- Converts Arabic-Indic and Persian digits to ASCII, preserving leading zeroes.
- Normalizes Unicode to NFC and trims surrounding whitespace in cells and headers.
- Counts duplicate normalized rows; optionally removes them, preserving first occurrence.
- Rejects ambiguous headers and malformed row widths before creating output.
- Writes UTF-8 with BOM for spreadsheet compatibility; refuses existing output files.
- Optionally prefixes formula-like cells with apostrophes using `--safe-excel`.
- Prints a JSON summary to stdout, which can be redirected to a report file.

It does not rename Arabic headers to English, alter Arabic letters, infer numeric
formats, change dates, or parse XLSX. Internal whitespace and separators are retained.

## Quick start (Python 3.10+)

From this project folder, with no installation:

```sh
python -m arabic_csv_cleaner examples/input.csv cleaned.csv --deduplicate
```

Install locally for a reusable command (installation may download build tools):

```sh
python -m pip install .
arabic-csv-cleaner examples/input.csv cleaned.csv --deduplicate --safe-excel
```

Legacy encoding and semicolon delimiter:

```sh
python -m arabic_csv_cleaner legacy.csv cleaned.csv --encoding cp1256 --delimiter ";"
```

Save the report using shell redirection:

```sh
python -m arabic_csv_cleaner examples/input.csv cleaned.csv --deduplicate > report.json
```

The example contains three rows; two normalize to the same row. With deduplication,
the output contains item codes `001` and `002`, with quantities `12` and `5`.
Spreadsheet software may still strip zeroes on opening: import item codes as text.
The script preserves them in the CSV itself.

## Python API

```python
from arabic_csv_cleaner import clean_csv
summary = clean_csv("input.csv", "output.csv", deduplicate=True)
```

## Report definitions

`input_rows` excludes blank rows; `output_rows` counts written data rows.
`duplicate_rows` counts repeats after normalization whether removed or retained.
`changed_cells` includes headers and removed duplicate rows, before optional formula
escaping. `blank_rows` counts skipped empty/whitespace records.
`formula_cells_escaped` counts escaped cells actually written, including headers.

## Limits and safety

Input is held in memory; use small and medium exports. UTF-8 is the default, and
encodings must be selected explicitly for other files. Duplicate headers after
normalization are rejected. Output is a new file; no automatic replacement.
`--safe-excel` changes leading minus signs too. It is a best-effort export aid;
review untrusted spreadsheets and import columns as text. An interrupted disk write
may leave a partial output file; remove it before retrying.

## Development

```sh
python -m unittest discover -s tests -v
```

CI is configured for Python 3.10–3.13. This is a new project: no usage or adoption
metrics are claimed. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Source

Source repository: https://github.com/mohammedzaton/arabic-csv-cleaner

No PyPI release has been made.

Maintainer: Mohammed Zaton — mohammed.zaton2@gmail.com

## License

Apache-2.0; see [LICENSE](LICENSE).
