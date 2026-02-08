"""Output model for CSV comparison results."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CSVCompareOutput:
    """Contains the results of comparing two CSV files.

    Attributes:
        match_result: True if the files are identical, False otherwise.
        first_file: Path or identifier of the first file.
        second_file: Path or identifier of the second file.
        extra_cols_in_first_file: Columns present in the first file but not the second.
        extra_cols_in_second_file: Columns present in the second file but not the first.
        extra_rows_in_first_file: Rows present in the first file but not the second.
        extra_rows_in_second_file: Rows present in the second file but not the first.
        mismatched_rows: List of dicts describing cell-level mismatches.
    """

    match_result: bool
    first_file: str
    second_file: str
    extra_cols_in_first_file: List[str]
    extra_cols_in_second_file: List[str]
    extra_rows_in_first_file: List[str]
    extra_rows_in_second_file: List[str]
    mismatched_rows: List[Dict[str, str]]

    def to_dict(self) -> Dict:
        """Convert the comparison result to a dictionary.

        Returns:
            Dict: Dictionary representation of the comparison result.
        """
        return {
            "first_file": self.first_file,
            "second_file": self.second_file,
            "match_result": self.match_result,
            "extra_cols_in_first_file": self.extra_cols_in_first_file,
            "extra_cols_in_second_file": self.extra_cols_in_second_file,
            "extra_rows_in_first_file": self.extra_rows_in_first_file,
            "extra_rows_in_second_file": self.extra_rows_in_second_file,
            "mismatched_rows": self.mismatched_rows,
        }

    def __str__(self) -> str:
        """Format the comparison result as a human-readable string.

        Returns:
            str: Multi-line summary of the comparison.
        """
        lines = []
        lines.append(f"First file: {self.first_file}")
        lines.append(f"Second file: {self.second_file}")
        lines.append(f"Match result: {self.match_result}")

        if self.extra_cols_in_first_file:
            lines.append("Extra columns in first file")
            lines.extend([f"\t{x}" for x in self.extra_cols_in_first_file])

        if self.extra_cols_in_second_file:
            lines.append("Extra columns in second file")
            lines.extend([f"\t{x}" for x in self.extra_cols_in_second_file])
        if self.extra_rows_in_first_file:
            lines.append("Extra rows in first file")
            lines.extend([f"\t{x}" for x in self.extra_rows_in_first_file])
        if self.extra_rows_in_second_file:
            lines.append("Extra rows in second file")
            lines.extend([f"\t{x}" for x in self.extra_rows_in_second_file])
        if self.mismatched_rows:
            lines.append("Mismatched rows")
            lines.extend(
                [
                    f"\trow: {x.get('row', '')}, column: {x.get('column', '')}, first: {x.get('first', '')}, second: {x.get('second', '')}"
                    for x in self.mismatched_rows
                ]
            )
        return "\n".join(lines)
