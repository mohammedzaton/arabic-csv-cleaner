import argparse
import csv
import json
import sys
from .core import clean_csv

def main():
    parser = argparse.ArgumentParser(description="Clean Arabic CSV files locally without changing numeric types.")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--encoding", default="utf-8-sig", help="Input codec; use cp1256 for legacy Arabic CSV")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--deduplicate", action="store_true", help="Remove identical normalized rows")
    parser.add_argument("--safe-excel", action="store_true", help="Prefix formula-like cells (including headers) with apostrophe")
    args = parser.parse_args()
    try:
        report = clean_csv(args.input, args.output, encoding=args.encoding,
                           delimiter=args.delimiter, deduplicate=args.deduplicate,
                           safe_excel=args.safe_excel)
    except (OSError, ValueError, LookupError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
