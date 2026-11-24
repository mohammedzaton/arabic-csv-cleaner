import csv
import io
import unicodedata
from pathlib import Path

_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")

def normalize_cell(value):
    """Normalize Unicode, surrounding whitespace and Arabic/Persian digits.

    Internal spacing, punctuation, leading zeroes and Arabic letters are preserved.
    Cells always remain strings: identifiers are never converted to numbers.
    """
    return unicodedata.normalize("NFC", value).translate(_DIGITS).strip()

def clean_csv(source, destination, *, encoding="utf-8-sig", delimiter=",",
              deduplicate=False, safe_excel=False):
    """Validate the entire CSV before creating a new output; never overwrite files.

    Duplicate counts refer to normalized rows. Entire input is held in memory.
    """
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output must be different files")
    if len(delimiter) != 1 or delimiter in "\r\n\0":
        raise ValueError("Delimiter must be one character other than newline or NUL")
    with source.open(encoding=encoding, newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter, strict=True)
        try:
            original_header = next(reader)
        except StopIteration:
            raise ValueError("CSV is empty") from None
        header = [normalize_cell(c) for c in original_header]
        if not header or any(not c for c in header):
            raise ValueError("Headers must not be empty")
        if len(set(header)) != len(header):
            raise ValueError("Duplicate headers after normalization")
        rows, seen = [], set()
        report = dict(input_rows=0, output_rows=0, duplicate_rows=0,
                      removed_rows=0, changed_cells=sum(a != b for a,b in zip(original_header,header)),
                      blank_rows=0, formula_cells_escaped=0)
        for raw in reader:
            if not raw or all(not c.strip() for c in raw):
                report["blank_rows"] += 1
                continue
            if len(raw) != len(header):
                raise ValueError(f"CSV record ending at line {reader.line_num}: expected {len(header)} columns, got {len(raw)}")
            report["input_rows"] += 1
            row = tuple(normalize_cell(c) for c in raw)
            report["changed_cells"] += sum(a != b for a,b in zip(raw,row))
            if row in seen:
                report["duplicate_rows"] += 1
                if deduplicate:
                    report["removed_rows"] += 1
                    continue
            seen.add(row)
            rows.append(row)
    def escaped(row):
        result=[]
        for cell in row:
            if safe_excel and cell.startswith(("=", "+", "-", "@")):
                cell = "'" + cell
                report["formula_cells_escaped"] += 1
            result.append(cell)
        return result
    # Assemble before opening output, so validation/serialization cannot truncate it.
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=delimiter)
    writer.writerow(escaped(header))
    writer.writerows(escaped(row) for row in rows)
    with destination.open("x", encoding="utf-8-sig", newline="") as output:
        output.write(buffer.getvalue())
    report["output_rows"] = len(rows)
    return report
