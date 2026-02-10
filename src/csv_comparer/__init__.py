"""csv_comparer - A library for comparing CSV files.

Provides tools for parsing, transforming, and comparing CSV files with
detailed output including extra columns, extra rows, and mismatched values.
"""

from .comparer import CSVComparer
from .csv_compare_output import CSVCompareOutput
from .csv_parser import CSVParser

__all__ = ["CSVComparer", "CSVCompareOutput", "CSVParser"]
