from csv_diff_tool import CSVComparer, CSVParser
import io
import os
import unittest


class CSVCompareTest(unittest.TestCase):

    def _write_file(self, content, file_name, file_encoding="utf-8"):
        with io.open(file_name, "w", encoding=file_encoding) as csvfile:
            csvfile.write(content)

    def test_extra_columns_in_one_file(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
        ]
        file_2_lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_cols_in_second_file == ["column 3"]
        assert not compare_result.extra_cols_in_first_file
        csv_comparer = CSVComparer.from_lines(file_2_lines, file_1_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_cols_in_first_file == ["column 3"]
        assert not compare_result.extra_rows_in_second_file

    def test_extra_columns_in_both_files(self):
        file_1_lines = [
            "column 1,column 4",
            "row 1,row 1:2",
            "row 2,row 2:2",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_cols_in_first_file == ["column 4"]
        assert compare_result.extra_cols_in_second_file == ["column 2"]
        csv_comparer = CSVComparer.from_lines(file_2_lines, file_1_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_cols_in_first_file == ["column 2"]
        assert compare_result.extra_cols_in_second_file == ["column 4"]

    def test_extra_rows_in_one_files(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_rows_in_second_file == ["row 3"]
        assert compare_result.extra_rows_in_first_file == []
        csv_comparer = CSVComparer.from_lines(file_2_lines, file_1_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_rows_in_first_file == ["row 3"]
        assert compare_result.extra_rows_in_second_file == []

    def test_extra_rows_in_both_files(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 4,row 4:2",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_rows_in_first_file == ["row 4"]
        assert compare_result.extra_rows_in_second_file == ["row 3"]
        csv_comparer = CSVComparer.from_lines(file_2_lines, file_1_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_rows_in_first_file == ["row 3"]
        assert compare_result.extra_rows_in_second_file == ["row 4"]

    def test_mismatched_values_when_rows_and_columns_match(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2_mismatch",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.mismatched_rows == [
            {
                "row": "row 3",
                "column": "column 2",
                "first": "row 3:2_mismatch",
                "second": "row 3:2",
            }
        ]

    def test_mismatched_values_with_extra_columns(self):
        file_1_lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
            "row 3,row 3:2_mismatch,row 3:3",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_cols_in_first_file == ["column 3"]
        assert compare_result.mismatched_rows == [
            {
                "row": "row 3",
                "column": "column 2",
                "first": "row 3:2_mismatch",
                "second": "row 3:2",
            }
        ]

    def test_mismatched_values_with_extra_rows(self):
        file_1_lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
            "row 3,row 3:2_mismatch,row 3:3",
            "row 4,row 4:2,row 4:3",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_rows_in_first_file == ["row 4"]
        assert compare_result.mismatched_rows == [
            {
                "row": "row 3",
                "column": "column 2",
                "first": "row 3:2_mismatch",
                "second": "row 3:2",
            }
        ]
        assert compare_result.extra_cols_in_first_file == ["column 3"]

    def test_drop_columns(self):
        file_1_lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
            "row 3,row 3:2,row 3:3",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        csv_comparer.drop_columns(["column 3"])
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.extra_cols_in_first_file == []
        assert compare_result.match_result

    def test_drop_rows(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
            "row 4,row 4:2",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        csv_comparer.drop_rows("column 1", ["row 4"])
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.match_result

    def test_drop_rows_by_predicate(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
            "row 4,row 4:2",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        csv_comparer.drop_rows_by(lambda row: row["column 1"] == "row 4")
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.match_result

    def test_apply_transform(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
            "row 2,row 2:2",
            "row 3,row 3:2",
            "row 4,row 4:2",
        ]
        file_2_lines = [
            "column 1,column 2,column 3",
            "row 1,row 1,:2",
            "row 2,row 2,:2",
            "row 3,row 3,:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        def merge_columns(row):
            if "column 3" in row:
                return row["column 2"] + row["column 3"]
            return row["column 2"]
        csv_comparer.apply_transform("column 2", merge_columns)
        csv_comparer.drop_columns(["column 3"])
        csv_comparer.drop_rows("column 1", ["row 4"])
        compare_result = csv_comparer.compare("column 1")
        assert compare_result.match_result

    def test_compare_with_invalid_index_column(self):
        file_1_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
        ]
        file_2_lines = [
            "column 1,column 2",
            "row 1,row 1:2",
        ]
        csv_comparer = CSVComparer.from_lines(file_1_lines, file_2_lines)
        with self.assertRaises(ValueError) as ctx:
            csv_comparer.compare("nonexistent")
        self.assertIn("not found in first file", str(ctx.exception))

    def test_from_files(self):
        first_file = "first_file.csv"
        second_file = "second_file.csv"
        try:
            self._write_file("column 1,column 2\nrow 1,row 1:2", first_file)
            self._write_file("column 1,column 2\nrow 1,row 1:2", second_file)
            csv_comparer = CSVComparer.from_files(first_file, second_file)
            result = csv_comparer.compare("column 1")
            assert result.match_result
        finally:
            if os.path.exists(first_file):
                os.remove(first_file)
            if os.path.exists(second_file):
                os.remove(second_file)

    def test_from_csv_parsers(self):
        lines_1 = ["column 1,column 2", "row 1,row 1:2"]
        lines_2 = ["column 1,column 2", "row 1,row 1:2"]
        first_parser = CSVParser.from_lines(lines_1)
        second_parser = CSVParser.from_lines(lines_2)
        csv_comparer = CSVComparer.from_csv_parsers(first_parser, second_parser)
        result = csv_comparer.compare("column 1")
        assert result.match_result


if __name__ == "__main__":
    unittest.main()
