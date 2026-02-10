from csv_comparer import CSVComparer, CSVCompareOutput
import unittest


class CSVCompareOutputTest(unittest.TestCase):

    def test_output_formatting(self):
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
        expected_text = "\n".join([
            "First file: init from lines",
            "Second file: init from lines",
            "Match result: False",
            "Mismatched rows",
            "\trow: row 3, column: column 2, first: row 3:2_mismatch, second: row 3:2"
        ])
        assert str(compare_result) == expected_text
        assert compare_result.to_dict() == {
            "first_file": "init from lines",
            "second_file": "init from lines",
            "match_result": False,
            "extra_cols_in_first_file": [],
            "extra_cols_in_second_file": [],
            "extra_rows_in_first_file": [],
            "extra_rows_in_second_file": [],
            "mismatched_rows": [
                {
                    "row": "row 3",
                    "column": "column 2",
                    "first": "row 3:2_mismatch",
                    "second": "row 3:2"
                }
            ],
        }

    def test_str_extra_rows_in_second_file_without_extra_cols(self):
        """Regression test: extra rows in second file should display
        even when there are no extra columns in second file."""
        result = CSVCompareOutput(
            match_result=False,
            first_file="first_file.csv",
            second_file="second_file.csv",
            extra_cols_in_first_file=[],
            extra_cols_in_second_file=[],
            extra_rows_in_first_file=[],
            extra_rows_in_second_file=["row 3", "row 4"],
            mismatched_rows=[],
        )
        output = str(result)
        assert "Extra rows in second file" in output
        assert "\trow 3" in output
        assert "\trow 4" in output

    def test_str_all_sections(self):
        """Test __str__ displays all sections when all fields are populated."""
        result = CSVCompareOutput(
            match_result=False,
            first_file="first_file.csv",
            second_file="second_file.csv",
            extra_cols_in_first_file=["column 1"],
            extra_cols_in_second_file=["column 2"],
            extra_rows_in_first_file=["row 3"],
            extra_rows_in_second_file=["row 4"],
            mismatched_rows=[{"row": "1", "column": "c", "first": "row 3:2_mismatch", "second": "row 3:2"}],
        )
        output = str(result)
        assert "Extra columns in first file" in output
        assert "\tcolumn 1" in output
        assert "Extra columns in second file" in output
        assert "\tcolumn 2" in output
        assert "Extra rows in first file" in output
        assert "\trow 3" in output
        assert "Extra rows in second file" in output
        assert "\trow 4" in output
        assert "Mismatched rows" in output


if __name__ == "__main__":
    unittest.main()
