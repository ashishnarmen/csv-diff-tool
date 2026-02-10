from csv_comparer.csv_parser import NullCSVParser
import unittest


class NullCSVParserTest(unittest.TestCase):

    def test_defaults(self):
        parser = NullCSVParser()
        assert parser.list_of_dicts == []
        assert parser.column_names == []
        assert parser.file_text == ""
        assert parser.file_path == "null"
        assert parser.index_column == ""

    def test_noop_methods(self):
        parser = NullCSVParser()
        # None of these should raise
        parser.strip_whitespace()
        parser.apply_transform("col", lambda x: x)
        parser.drop_columns(["col"])
        parser.drop_rows_by(lambda x: True)
        parser.drop_rows("col", ["val"])
        parser.index_column = "anything"
        parser.write_to_file()

    def test_return_values(self):
        parser = NullCSVParser()
        assert parser.row_values_in_column("col") == []
        assert parser.get_value("row", "col") == ""
        assert parser.index_column == ""


if __name__ == "__main__":
    unittest.main()
