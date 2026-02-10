"""CSV comparison module for comparing two parsed CSV files."""

from typing import Callable, Dict, List

from .csv_compare_output import CSVCompareOutput
from .csv_parser import CSVParser, NullCSVParser


class CSVComparer:
    """Compares two CSV files and reports differences.

    Supports loading from files, text lines, or pre-built CSVParser objects.
    Provides methods to transform data before comparison.
    """

    first_file: CSVParser
    second_file: CSVParser

    def __init__(self) -> None:
        self.first_file: CSVParser = NullCSVParser()
        self.second_file: CSVParser = NullCSVParser()

    @classmethod
    def from_files(cls, first_file: str, second_file: str) -> "CSVComparer":
        """Create an instance of CSVComparer from two CSV files.

        Args:
            first_file (str): File path of the first CSV file.
            second_file (str): File path of the second CSV file.

        Returns:
            CSVComparer: A CSVComparer object with the parsed file contents.

        Raises:
            FileNotFoundError: If either file_path does not exist.
            UnicodeDecodeError: If either file cannot be decoded with the detected encoding.
        """
        csv_comparer = cls()
        csv_comparer.first_file = CSVParser.from_file(first_file)
        csv_comparer.second_file = CSVParser.from_file(second_file)
        return csv_comparer

    @classmethod
    def from_lines(
        cls, first_file_lines: List[str], second_file_lines: List[str]
    ) -> "CSVComparer":
        """Create an instance of CSVComparer from two lists of CSV text lines.

        Args:
            first_file_lines (List[str]): List of text lines for the first CSV file.
            second_file_lines (List[str]): List of text lines for the second CSV file.

        Returns:
            CSVComparer: A CSVComparer object with the parsed file contents.
        """
        csv_comparer = cls()
        csv_comparer.first_file = CSVParser.from_lines(first_file_lines)
        csv_comparer.second_file = CSVParser.from_lines(second_file_lines)
        return csv_comparer

    @classmethod
    def from_csv_parsers(
        cls, first_file_parser: CSVParser, second_file_parser: CSVParser
    ) -> "CSVComparer":
        """Create an instance of CSVComparer from two CSVParser objects.

        Args:
            first_file_parser (CSVParser): CSVParser object for the first CSV file.
            second_file_parser (CSVParser): CSVParser object for the second CSV file.

        Returns:
            CSVComparer: A CSVComparer object with the parsed file contents.
        """
        csv_comparer = cls()
        csv_comparer.first_file = first_file_parser
        csv_comparer.second_file = second_file_parser
        return csv_comparer

    def strip_whitespace(self) -> None:
        """Strip whitespace from all keys and values in both CSV files.

        This method removes leading and trailing whitespace from column names
        and all cell values in both the first and second CSV files.
        """
        self.first_file.strip_whitespace()
        self.second_file.strip_whitespace()

    def drop_columns(self, column_names: List[str]) -> None:
        """Drop (remove) the specified columns from both CSV files.

        Args:
            column_names (List[str]): List of column names to drop (remove).
        """
        self.first_file.drop_columns(column_names)
        self.second_file.drop_columns(column_names)

    def drop_rows(self, index_column: str, row_values: List[str]) -> None:
        """Drop (remove) the rows with matching values in both CSV files.

        Args:
            index_column (str): Column name to search.
            row_values (List[str]): Values to match in the specified column.
        """
        self.first_file.drop_rows(index_column, row_values)
        self.second_file.drop_rows(index_column, row_values)

    def drop_rows_by(self, predicate: Callable) -> None:
        """Drop (remove) rows based on a predicate function in both CSV files.

        Args:
            predicate (Callable): Predicate function applied on each row to determine
                if it will be dropped.
        """
        self.first_file.drop_rows_by(predicate)
        self.second_file.drop_rows_by(predicate)

    def apply_transform(self, column_name: str, func: Callable) -> None:
        """Apply a transform on a column on each row of the CSV files.

        Args:
            column_name (str): Column name on which the transform is to be applied.
            func (Callable): Transformer function to execute on each row.
        """
        self.first_file.apply_transform(column_name, func)
        self.second_file.apply_transform(column_name, func)

    def compare(self, index_column: str) -> CSVCompareOutput:
        """Compare two CSV files and return detailed comparison results.

        Args:
            index_column (str): Column name to use as the unique row identifier.

        Returns:
            CSVCompareOutput: An object containing match result and detailed comparison
                information including extra/missing columns, extra/missing rows, and
                mismatched cell values.

        Raises:
            ValueError: If index_column does not exist in either CSV file.
        """
        # Validate that index_column exists in both files
        if index_column not in self.first_file.column_names:
            raise ValueError(
                f"Index column '{index_column}' not found in first file. Available columns: {self.first_file.column_names}"
            )
        if index_column not in self.second_file.column_names:
            raise ValueError(
                f"Index column '{index_column}' not found in second file. Available columns: {self.second_file.column_names}"
            )

        # Set the index column for both files
        self.first_file.index_column = index_column
        self.second_file.index_column = index_column

        # Convert to sets for efficient lookups (O(1) instead of O(n))
        first_cols = set(self.first_file.column_names)
        second_cols = set(self.second_file.column_names)
        first_rows = set(self.first_file.row_values_in_column(index_column))
        second_rows = set(self.second_file.row_values_in_column(index_column))

        # Find columns that exist in first file but not in second
        extra_cols_in_first_file = list(first_cols - second_cols)

        # Find columns that exist in second file but not in first
        extra_cols_in_second_file = list(second_cols - first_cols)

        # Find rows that exist in first file but not in second
        extra_rows_in_first_file = list(first_rows - second_rows)

        # Find rows that exist in second file but not in first
        extra_rows_in_second_file = list(second_rows - first_rows)

        # Find columns and rows that exist in both files
        common_columns = list(first_cols & second_cols)
        common_rows = list(first_rows & second_rows)

        # Compare values in common rows and columns to find mismatches
        mismatched_rows = []
        for row in common_rows:
            for column in common_columns:
                first_val = self.first_file.get_value(row, column)
                second_val = self.second_file.get_value(row, column)
                if first_val != second_val:
                    mismatched_rows.append(
                        {
                            "row": row,
                            "column": column,
                            "first": first_val,
                            "second": second_val,
                        }
                    )

        # Determine if files match: true only if there are no differences
        match_result = not any(
            [
                extra_cols_in_first_file,
                extra_cols_in_second_file,
                extra_rows_in_first_file,
                extra_rows_in_second_file,
                mismatched_rows,
            ]
        )

        return CSVCompareOutput(
            match_result=match_result,
            first_file=self.first_file.file_path,
            second_file=self.second_file.file_path,
            extra_cols_in_first_file=extra_cols_in_first_file,
            extra_cols_in_second_file=extra_cols_in_second_file,
            extra_rows_in_first_file=extra_rows_in_first_file,
            extra_rows_in_second_file=extra_rows_in_second_file,
            mismatched_rows=mismatched_rows,
        )
