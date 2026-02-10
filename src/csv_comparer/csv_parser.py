"""CSV parsing module for reading, transforming, and writing CSV data."""

import csv
import io
import logging
import os
from collections import defaultdict
from typing import Callable, Dict, List, Optional

import chardet


class CSVParser:
    """Parses CSV data from files, text, or lines into a list of dictionaries.

    Supports encoding detection, column/row manipulation, transforms,
    and writing modified data back to files.
    """

    def __init__(self) -> None:
        self.list_of_dicts: List[Dict[str, str]] = []
        self.column_names: List[str] = []
        self.file_text: str = ""
        self._index_column: str = ""
        self.file_path: str = ""
        self._encoding: str = "utf-8"

    @staticmethod
    def get_encoding(file_path: str) -> Optional[str]:
        """Detect the encoding of the file.

        Args:
            file_path (str): File path of the text file.

        Returns:
            Optional[str]: Detected encoding, or None if detection fails.
        """
        with open(file_path, "rb") as f:
            rawdata = b"".join(f.readlines())
        return chardet.detect(rawdata)["encoding"]

    @classmethod
    def from_file(cls, file_path: str, column_names: Optional[List[str]] = None) -> "CSVParser":
        """Create an instance of CSVParser from a file.

        Args:
            file_path (str): File Path (CSV file).
            column_names: Optional list of column names. If None or empty, uses the CSV header row.

        Returns:
            CSVParser: A CSVParser object with the parsed file content.

        Raises:
            FileNotFoundError: If the file_path does not exist.
            TypeError: If column_names contains non-string elements.
            UnicodeDecodeError: If the file cannot be decoded with the detected encoding.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            encoding = cls.get_encoding(file_path) or "utf-8"
        except (OSError, LookupError) as e:
            encoding = "utf-8"
            logging.warning(f"Warning: Encoding detection failed, using utf-8: {e}")

        file_text = ""
        try:
            with open(file_path, encoding=encoding) as file:
                file_text = file.read()
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                f"Failed to decode {file_path} with encoding {encoding}: {e.reason}",
            ) from e

        csv_parser = CSVParser.from_csv_text(file_text, column_names)
        csv_parser.file_path = file_path
        csv_parser._encoding = encoding
        return csv_parser

    @classmethod
    def from_lines(cls, csv_lines: List[str], column_names: Optional[List[str]] = None) -> "CSVParser":
        """Create an instance of CSVParser from a list of text lines.

        Args:
            csv_lines (List[str]): List of text lines.
            column_names: Optional list of column names. If None or empty, uses the CSV header row.

        Returns:
            CSVParser: A CSVParser object with the parsed file content.
        """
        file_text = "\n".join(csv_lines)
        csv_parser = CSVParser.from_csv_text(file_text, column_names)
        csv_parser.file_path = "init from lines"
        return csv_parser

    @classmethod
    def from_csv_text(cls, file_text: str, column_names: Optional[List[str]] = None) -> "CSVParser":
        """Create an instance of CSVParser from CSV text as a string.

        Args:
            file_text (str): CSV content as text.
            column_names: Optional list of column names. If None or empty, uses the CSV header row.

        Returns:
            CSVParser: A CSVParser object with the parsed file content.
        """
        if column_names is not None and column_names:
            if not all(isinstance(col, str) for col in column_names):
                raise TypeError("All column names must be strings")
        csv_parser = cls()
        csv_parser.file_path = "init from text"
        csv_parser.file_text = file_text
        csv_parser.column_names = (
            csv_parser._get_column_names_from_header_row(file_text)
            if not column_names
            else column_names
        )
        with io.StringIO(file_text) as file:
            dict_reader = csv.DictReader(file, column_names)
            csv_parser.list_of_dicts = list(dict_reader)
        return csv_parser

    def _get_column_names_from_header_row(self, file_text: str) -> List[str]:
        """Extract column names from the first row of CSV text.

        Args:
            file_text (str): CSV content as text.

        Returns:
            List[str]: List of column names, with duplicates made unique.
        """
        with io.StringIO(file_text) as file:
            reader = csv.reader(file)
            try:
                header_row = next(reader)
            except StopIteration:
                return []
        return self._unique_vals(header_row)

    def strip_whitespace(self) -> None:
        """Strip leading and trailing whitespace from all keys and values."""
        self.list_of_dicts = [
            {
                (key.strip() if isinstance(key, str) else key): (
                    value.strip() if isinstance(value, str) else value
                )
                for key, value in item.items()
            }
            for item in self.list_of_dicts
        ]
        self.column_names = [x.strip() for x in self.column_names if isinstance(x, str)]
        if isinstance(self._index_column, str):
            self._index_column = self._index_column.strip()

    def apply_transform(self, column_name: str, func: Callable) -> None:
        """Apply a transform on a column on each row of the CSV file.

        Args:
            column_name (str): Column name on which the transform is to be applied.
            func (Callable): Transformer function to execute on each row.
        """
        self.list_of_dicts = [
            {**item, column_name: func(item)} for item in self.list_of_dicts
        ]
        if column_name not in self.column_names:
            self.column_names.append(column_name)

    def get_row(self, column_name: str, row_value: str) -> Dict[str, str]:
        """Get the contents of the first matching row as a dictionary.

        Args:
            column_name (str): Column name to search.
            row_value (str): Value to match in the specified column.

        Returns:
            Dict[str, str]: Dictionary representation of the first matching row
                or an empty dictionary if a match is not found.
        """
        row: Dict[str, str] = {}
        rows = self.get_rows(column_name, row_value)
        if rows:
            row = rows[0]
        return row

    def get_rows(self, column_name: str, row_value: str) -> List[Dict[str, str]]:
        """Get the contents of matching rows as a list of dictionaries.

        Args:
            column_name (str): Column name to search.
            row_value (str): Value to match in the specified column.

        Returns:
            List[Dict[str, str]]: List of dictionaries of the matching rows
                or an empty list if a match is not found.
        """
        rows: List[Dict[str, str]] = []
        if column_name in self.column_names:
            matching_row = lambda row: row.get(column_name) == row_value
            rows = list(filter(matching_row, self.list_of_dicts))
        return rows

    @property
    def has_error(self) -> bool:
        """Check if there are any errors in the CSV file.

        Returns:
            bool: True if there are any errors (e.g., inconsistent column counts),
                otherwise False.
        """
        reader = csv.reader(io.StringIO(self.file_text))
        try:
            header = next(reader)
        except StopIteration:
            return False
        expected_cols = len(header)
        for _, row in enumerate(reader, start=2):
            if len(row) != expected_cols:
                return True
        return False

    def drop_columns(self, column_names: List[str]) -> None:
        """Drop (remove) the columns.

        Args:
            column_names (List[str]): List of column names to drop (remove).
        """
        list_of_dicts = []
        for dict_row in self.list_of_dicts:
            list_of_dicts.append(
                {
                    key: value
                    for key, value in dict_row.items()
                    if key not in column_names
                }
            )
        self.list_of_dicts = list_of_dicts
        self.column_names = [
            col_name for col_name in self.column_names if col_name not in column_names
        ]

    def drop_rows_by(self, predicate: Callable) -> None:
        """Drop (remove) rows based on a predicate function that is applied on the row.

        Args:
            predicate (Callable): Predicate function applied on each row to determine
                if it will be dropped.
        """
        self.list_of_dicts = [
            dict_row for dict_row in self.list_of_dicts if not predicate(dict_row)
        ]

    def drop_rows(self, column_name: str, row_values: List[str]) -> None:
        """Drop (remove) the rows with matching values in a specified column.

        Args:
            column_name (str): Column name to search.
            row_values (List[str]): Values to match in the specified column.
        """
        if column_name not in self.column_names:
            return
        row_val_check = lambda x: x[column_name] in row_values
        self.drop_rows_by(row_val_check)

    def row_values_in_column(self, column_name: str) -> List[str]:
        """Get a list of row values in the specified column.

        Args:
            column_name (str): Column name.

        Returns:
            List[str]: List of all the row values in that column.
        """
        row_values: List[str] = []
        if column_name in self.column_names:
            row_values = [x.get(column_name, "") for x in self.list_of_dicts]
        return row_values

    def _unique_vals(self, values: List[str]) -> List[str]:
        """Make duplicate values unique by appending numeric suffixes.

        Args:
            values (List[str]): List of values that may contain duplicates.

        Returns:
            List[str]: List with duplicates renamed (e.g., col, col.1, col.2).
        """
        result = list(values)
        unique_values = set()
        suffix_counts = defaultdict(int)
        for idx, val in enumerate(result):
            if val not in unique_values:
                unique_values.add(val)
            else:
                while True:
                    suffix_counts[val] += 1
                    new_val = f"{val}.{suffix_counts[val]}"
                    if new_val not in unique_values:
                        unique_values.add(new_val)
                        result[idx] = new_val
                        break
        return result

    @property
    def index_column(self) -> str:
        """Get the index column.

        Returns:
            str: Column name.
        """
        if not self.column_names:
            raise ValueError("No columns available to set or get the index column")
        return self._index_column or self.column_names[0]

    @index_column.setter
    def index_column(self, value: str) -> None:
        """Set the index column. If there are duplicate column names, append a numeric
        index to the column name (col, col.1, col.2).

        Args:
            value (str): Column name.
        """
        if not self.column_names:
            raise ValueError("No columns available to set the index column")
        if value not in self.column_names:
            raise ValueError(f"Column '{value}' not found in column names")
        self._index_column = value
        row_vals = self._unique_vals(self.row_values_in_column(self._index_column))
        for idx, row in enumerate(self.list_of_dicts):
            row[self.index_column] = row_vals[idx]

    def get_value(self, row_value_in_index_column: str, column_name: str) -> str:
        """Get value of the cell in the specified row and column.

        Args:
            row_value_in_index_column (str): Row identifier.
            column_name (str): Column name.

        Returns:
            str: Value contained in the cell.
        """
        row = self.get_row(self.index_column, row_value_in_index_column)
        return row.get(column_name, "")

    def set_value(self, row_value_in_index_column: str, column_name: str, new_value: str) -> None:
        """Set value of cell in the specified row and column.

        Args:
            row_value_in_index_column (str): Row identifier.
            column_name (str): Column name.
            new_value (str): New value to set for the cell.
        """
        row = self.get_row(self.index_column, row_value_in_index_column)
        if row and column_name in row:
            row[column_name] = new_value

    def write_to_file(self) -> None:
        """Write the CSV data back to the source file.

        Raises:
            ValueError: If the CSVParser was not initialized from a file.
        """
        if not os.path.isfile(self.file_path):
            raise ValueError(
                f"Cannot write: '{self.file_path}' is not a valid file path. "
                "write_to_file is only supported when initialized via from_file."
            )
        with open(self.file_path, "w", newline="", encoding=self._encoding) as f:
            writer = csv.DictWriter(f, fieldnames=self.column_names)
            writer.writeheader()
            normalized_rows = [
                {key: value for key, value in row.items() if key in self.column_names}
                for row in self.list_of_dicts
            ]
            writer.writerows(normalized_rows)


class NullCSVParser(CSVParser):
    """Null Object implementation of CSVParser.

    All mutation methods are no-ops. Used as a default placeholder
    when no CSV data has been loaded yet.
    """

    def __init__(self) -> None:
        self.list_of_dicts: List[Dict[str, str]] = []
        self.column_names: List[str] = []
        self.file_text: str = ""
        self._index_column: str = ""
        self.file_path: str = "null"
        self._encoding: str = "utf-8"

    def strip_whitespace(self) -> None:
        pass

    def apply_transform(self, column_name: str, func: Callable) -> None:
        pass

    def drop_columns(self, column_names: List[str]) -> None:
        pass

    def drop_rows_by(self, predicate: Callable) -> None:
        pass

    def drop_rows(self, column_name: str, row_values: List[str]) -> None:
        pass

    def row_values_in_column(self, column_name: str) -> List[str]:
        return []

    def get_value(self, row_value_in_index_column: str, column_name: str) -> str:
        return ""

    def set_value(self, row_value_in_index_column: str, column_name: str, new_value: str) -> None:
        pass

    @property
    def index_column(self) -> str:
        return self._index_column

    @index_column.setter
    def index_column(self, value: str) -> None:
        pass

    def write_to_file(self) -> None:
        pass
