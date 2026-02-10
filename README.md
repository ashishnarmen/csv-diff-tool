# csv_compare

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python library for comparing CSV files with detailed output including extra columns, extra rows, and mismatched cell values. Supports automatic encoding detection, data transformations, and flexible input methods.

## Installation

```bash
pip install csv-compare
```

## Quick Start

### Compare two CSV files

```python
from csv_compare import CSVComparer

result = CSVComparer.from_files("report_v1.csv", "report_v2.csv").compare("id")

print(result.match_result)              # True if files are identical
print(result.extra_cols_in_first_file)  # Columns only in first file
print(result.extra_rows_in_second_file) # Rows only in second file
print(result.mismatched_rows)           # Cell-level differences
```

### Compare from in-memory data

```python
from csv_compare import CSVComparer

file_1 = ["id,name,score", "1,Alice,95", "2,Bob,87"]
file_2 = ["id,name,score", "1,Alice,95", "2,Bob,90", "3,Carol,88"]

result = CSVComparer.from_lines(file_1, file_2).compare("id")

print(result)
# First file: init from lines
# Second file: init from lines
# Match result: False
# Extra rows in second file
# 	3
# Mismatched rows
# 	row: 2, column: score, first: 87, second: 90
```

### Transform data before comparing

```python
from csv_compare import CSVComparer

comparer = CSVComparer.from_files("old.csv", "new.csv")

# Strip whitespace from all cells
comparer.strip_whitespace()

# Drop columns you don't care about
comparer.drop_columns(["timestamp", "metadata"])

# Drop specific rows
comparer.drop_rows("status", ["deleted", "archived"])

# Apply custom transforms
comparer.apply_transform("price", lambda row: str(round(float(row["price"]), 2)))

result = comparer.compare("id")
```

### Work with CSVParser directly

```python
from csv_compare import CSVParser

parser = CSVParser.from_file("data.csv")

# Inspect the data
print(parser.column_names)
print(parser.get_row("id", "42"))
print(parser.row_values_in_column("name"))

# Modify and write back
parser.set_value("42", "status", "updated")
parser.write_to_file()
```

## API Overview

### CSVComparer

The main comparison class. Create instances using factory methods:

- `CSVComparer.from_files(first_file, second_file)` - Load from file paths
- `CSVComparer.from_lines(first_lines, second_lines)` - Load from lists of strings
- `CSVComparer.from_csv_parsers(parser1, parser2)` - Load from CSVParser objects

**Transform methods** (applied to both files):
- `strip_whitespace()` - Remove leading/trailing whitespace
- `drop_columns(column_names)` - Remove specified columns
- `drop_rows(column, values)` - Remove rows matching values
- `drop_rows_by(predicate)` - Remove rows matching a function
- `apply_transform(column, func)` - Apply a function to a column

**Compare:**
- `compare(index_column)` - Returns a `CSVCompareOutput` with the results

### CSVParser

Parses CSV data into a list of dictionaries with column-aware operations:

- `CSVParser.from_file(path)` - Load from file (auto-detects encoding)
- `CSVParser.from_lines(lines)` - Load from list of strings
- `CSVParser.from_csv_text(text)` - Load from a single string
- `get_row(column, value)` / `get_rows(column, value)` - Query rows
- `get_value(row_id, column)` / `set_value(row_id, column, value)` - Cell access
- `write_to_file()` - Write modifications back to the source file

### CSVCompareOutput

A dataclass containing comparison results:

| Field | Type | Description |
|-------|------|-------------|
| `match_result` | `bool` | `True` if files are identical |
| `extra_cols_in_first_file` | `List[str]` | Columns only in the first file |
| `extra_cols_in_second_file` | `List[str]` | Columns only in the second file |
| `extra_rows_in_first_file` | `List[str]` | Rows only in the first file |
| `extra_rows_in_second_file` | `List[str]` | Rows only in the second file |
| `mismatched_rows` | `List[Dict]` | Cell-level mismatches with row, column, first, second |

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/ashishnarmen/csv_compare).

```bash
# Clone and install for development
git clone https://github.com/ashishnarmen/csv_compare.git
cd csv_compare
pip install -e ".[test]"

# Run tests with unittest and coverage
coverage run -m unittest discover tests/
coverage report -m

# Or, if you prefer pytest (install separately)
pip install pytest pytest-cov
pytest tests/ -v --cov=csv_compare
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
