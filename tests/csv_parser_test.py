from csv_comparer import CSVParser
import io
import os
import unittest


class CSVParserTest(unittest.TestCase):
    def _write_file(self, content, file_name, file_encoding):
        with io.open(file_name, "w", encoding=file_encoding) as csvfile:
            csvfile.write(content)

    def test_csv_parser_from_file(self):
        file_content = "column 1,column 2,column 3\n" "row 1,row 1:2,row 1:3\n"
        file_name = "file.csv"
        self._write_file(file_content, file_name, "utf-16")
        assert os.path.exists(file_name)
        csv_parser = CSVParser.from_file(file_name)
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]
        os.remove(file_name)

    def test_csv_parser_from_non_existent_file(self):
        file_name = "non_existent_file.csv"
        assert not os.path.exists(file_name)
        with self.assertRaises(FileNotFoundError):
            CSVParser.from_file(file_name)

    def test_csv_parser_from_lines(self):
        lines = ["column 1,column 2,column 3", "row 1,row 1:2,row 1:3"]
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]
        assert not csv_parser.has_error

    def test_csv_parser_with_column_names(self):
        lines = ["row 1,row 1:2,row 1:3"]
        columns = ["column 1", "column 2", "column 3"]
        csv_parser = CSVParser.from_lines(lines, columns)
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]

        file_content = "row 1,row 1:2,row 1:3\n"
        file_name = "file.csv"
        self._write_file(file_content, file_name, "utf-16")
        assert os.path.exists(file_name)
        csv_parser = CSVParser.from_file(file_name, columns)
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]
        os.remove(file_name)

    def test_csv_parser_with_invalid_column_name_type(self):
        lines = ["row 1,row 1:2,row 1:3"]
        columns = ["column 1", 2, "column 3"]
        with self.assertRaises(TypeError):
            CSVParser.from_lines(lines, columns)

    def test_strip_whitespace(self):
        lines = [
            " column 1 , column 2 , column 3 ",
            " row 1,row 1:2,row 1:3 ",
            " row 2,row 2:2,row 2:3 ",
        ]
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.column_names == [" column 1 ", " column 2 ", " column 3 "]
        assert csv_parser.get_value(" row 1", " column 3 ") == "row 1:3 "
        csv_parser.strip_whitespace()
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]
        assert csv_parser.get_value("row 1", "column 3") == "row 1:3"

    def test_parsing_duplicate_column_names(self):
        lines = ["column 1,column 2,column 1", "row 1,row 1:2,row 1:1"]
        metadata = CSVParser.from_lines(lines)
        assert metadata.column_names == ["column 1", "column 2", "column 1.1"]

    def test_apply_transform(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 1,row 1:2,row 1:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        merge_columns = lambda row: row["column 1"] + row["column 2"]
        csv_parser.apply_transform("column_new", merge_columns)
        assert csv_parser.column_names == [
            "column 1",
            "column 2",
            "column 3",
            "column_new",
        ]

    def test_fetch_row(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        row = csv_parser.get_row("column 1", "row 1")
        expected = {"column 1": "row 1", "column 2": "row 1:2", "column 3": "row 1:3"}
        assert row == expected

        assert not csv_parser.get_row("column nonexistent", "row 1")
        assert not csv_parser.get_row("column 1", "row nonexistent")

    def test_fetch_rows(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        row = csv_parser.get_rows("column 1", "row 1")
        expected = [
            {"column 1": "row 1", "column 2": "row 1:2", "column 3": "row 1:3"},
            {"column 1": "row 1", "column 2": "row 1:2", "column 3": "row 1:3"},
        ]
        assert row == expected
        assert not csv_parser.get_rows("column nonexistent", "row 1")
        assert not csv_parser.get_rows("column 1", "row nonexistent")

    def test_drop_rows(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        csv_parser.drop_rows("column 1", ["row 1"])
        rows = csv_parser.get_rows("column 1", "row 2")
        expected = [{"column 1": "row 2", "column 2": "row 2:2", "column 3": "row 2:3"}]
        assert rows == expected
        assert not csv_parser.get_rows("column 1", "row 1")
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]
        csv_parser.drop_rows("column 5", ["row 1"])
        assert csv_parser.column_names == ["column 1", "column 2", "column 3"]
        assert csv_parser.row_values_in_column("column 1") == ["row 2"]
        assert csv_parser.row_values_in_column("column 2") == ["row 2:2"]
        assert csv_parser.row_values_in_column("column 3") == ["row 2:3"]

    def test_drop_rows_by(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        drop_row = lambda x: "row 1" in x.get("column 1", "")
        csv_parser.drop_rows_by(drop_row)
        assert csv_parser.row_values_in_column("column 1") == ["row 2"]

    def test_drop_columns(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        csv_parser.drop_columns(["column 2"])
        assert csv_parser.column_names == ["column 1", "column 3"]
        assert csv_parser.get_value("row 1", "column 3") == "row 1:3"

    def test_invalid_csv(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3,row 1:4",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.has_error
        lines = ["column 1,column 2,column 3", "row 1,row 1:2,row 1:3,row 1:4"]
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.has_error

    def test_csv_with_no_content(self):
        lines = []
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.column_names == []
        text = ""
        csv_parser = CSVParser.from_csv_text(text)
        assert csv_parser.column_names == []

    def test_unique_vals(self):
        vals = ["column1", "column1", "column2", "column2", "column3", "column1"]
        csv_parser = CSVParser()
        expected = [
            "column1",
            "column1.1",
            "column2",
            "column2.1",
            "column3",
            "column1.2",
        ]
        actual = csv_parser._unique_vals(vals)
        assert expected == actual

        vals = ["column1", "column1", "column1"]
        expected = ["column1", "column1.1", "column1.2"]
        actual = csv_parser._unique_vals(vals)
        assert expected == actual

        vals = ["column1", "column1.1", "column1"]
        expected = ["column1", "column1.1", "column1.2"]
        actual = csv_parser._unique_vals(vals)
        assert expected == actual

    def test_first_column_is_default_index(self):
        lines = [
            "column 1,column 2, column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.get_value("row 2", "column 2") == "row 2:2"

    def test_index(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        csv_parser.index_column = "column 2"
        assert csv_parser.get_value("row 1:2", "column 3") == "row 1:3"
        with self.assertRaises(ValueError):
            csv_parser.index_column = "column nonexistent"

    def test_get_and_set_value(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        assert csv_parser.get_value("row 1", "column 3") == "row 1:3"
        csv_parser.set_value("row 1", "column 3", "new_value row 1:3")
        assert csv_parser.get_value("row 1", "column 3") == "new_value row 1:3"

    def test_write_to_file(self):
        file_content = "column 1,column 2,column 3\n" "row 1,row 1:2,row 1:3\n"
        file_name = "file.csv"
        self._write_file(file_content, file_name, "utf-16")
        assert os.path.exists(file_name)
        csv_parser = CSVParser.from_file(file_name)
        assert csv_parser.get_value("row 1", "column 3") == "row 1:3"
        csv_parser.set_value("row 1", "column 3", "new_value row 1:3")
        csv_parser.write_to_file()
        csv_parser_new = CSVParser.from_file(file_name)
        assert csv_parser_new.get_value("row 1", "column 3") == "new_value row 1:3"
        os.remove(file_name)

    def test_write_to_file_fails(self):
        lines = [
            "column 1,column 2,column 3",
            "row 1,row 1:2,row 1:3",
            "row 2,row 2:2,row 2:3",
        ]
        csv_parser = CSVParser.from_lines(lines)
        with self.assertRaises(ValueError):
            csv_parser.write_to_file()

    def test_check_empty_file(self):
        lines = []
        csv_parser = CSVParser.from_lines(lines, [])
        assert csv_parser.column_names == []
        with self.assertRaises(ValueError):
             assert csv_parser.index_column == "", "Index column (getter) should raise error"
        with self.assertRaises(ValueError):
            csv_parser.index_column = "any_column"
        assert not csv_parser.has_error, "Empty CSV should not have errors"


if __name__ == "__main__":
    unittest.main()
