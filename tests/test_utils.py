import unittest
import json
import pandas as pd
from datetime import datetime
from src.utils.utils import (
    concat_dataframes,
    delete_chars,
    lower_strip_df,
    format_date,
    consolidate_clinical_trials_df,
    consolidate_pubmed_df,
    write_dict_to_json,
    find_mentions_in_publications,
    merge_dicts,
)


class TestPipelineUnitFunctions(unittest.TestCase):

    def setUp(self):
        # Sample data used for multiple tests
        self.sample_json_data = """
        [
            {"id": "1", "title": "Study on drug A", "journal": "Journal A", "date": "2024-01-01"},
            {"id": "2", "title": "Drug B analysis", "journal": "Journal B", "date": "2023-12-12"}
        ]
        """
        self.sample_df = pd.DataFrame(
            {
                "id": ["1", "2"],
                "title": ["Study on drug A", "Drug B analysis"],
                "journal": ["Journal A", "Journal B"],
                "date": ["2024-01-01", "2023-12-12"],
            }
        )
        self.drugs_df = pd.DataFrame(
            {"drug": ["drug A", "drug B"], "atccode": ["A01", "B02"]}
        )

    def test_delete_chars(self):
        # Test that delete_chars removes unwanted characters
        df = pd.Series(["\\xc3\\xb1drug™", "normal"])
        clean_df = delete_chars(df)
        self.assertEqual(clean_df[0], "drug")

    def test_concat_multiple_dataframes(self):
        # Create sample DataFrames
        df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        df3 = pd.DataFrame({'A': [9, 10], 'B': [11, 12]})

        # Expected output
        expected = pd.DataFrame({
            'A': [1, 2, 5, 6, 9, 10],
            'B': [3, 4, 7, 8, 11, 12]
        })
        result = concat_dataframes([df1, df2, df3])
        pd.testing.assert_frame_equal(result, expected)


    def test_lower_strip_df(self):
        # Test lower_strip_df behavior
        df = pd.Series(["  TEXT ", "MixedCase", ""])
        clean_df = lower_strip_df(df)
        self.assertEqual(clean_df[0], "text")
        self.assertEqual(clean_df[1], "mixedcase")

    def test_format_date(self):
        df = pd.DataFrame(
            {"mixed_dates": ["2022-01-01", "01/02/2022", "March 3, 2022", "2022.04.04"]}
        )
        # Apply the format_date function
        formatted_df = format_date(df, "mixed_dates")
        # Expected output with dates formatted as YYYY-DD-MM
        expected_dates = ["2022-01-01", "2022-02-01", "2022-03-03", "2022-04-04"]
        # Check if the dates are correctly formatted
        for i in range(len(expected_dates)):
            # Convert to YYYY-DD-MM format
            formatted_date = pd.to_datetime(expected_dates[i]).strftime("%Y-%d-%m")
            self.assertEqual(formatted_df["mixed_dates"][i], formatted_date)

    def test_consolidate_clinical_trials_df(self):
        # Test clinical trials consolidation
        df = pd.DataFrame(
            {
                "title": ["Study on drug A", "Study on drug A"],
                "date_mention": ["2024-01-01", "2024-01-01"],
                "article_type": ["clinical_trials", "clinical_trials"],
                "id": ["1", "1"],
                "journal": ["Journal A", "Journal A"],
            }
        )
        consolidated_df = consolidate_clinical_trials_df(df)
        self.assertEqual(consolidated_df.shape[0], 1)

    def test_consolidate_pubmed_df(self):
        # Test PubMed dataframe consolidation
        df = pd.DataFrame(
            {
                "id": ["1", "", "3"],
                "title": ["Study on drug A", "Study on drug B", "Study on drug C"],
            }
        )
        cleaned_df = consolidate_pubmed_df(df)
        self.assertEqual(cleaned_df.shape[0], 2)
        self.assertEqual(cleaned_df["id"].convert_dtypes().dtype, "Int64")

    def test_write_dict_to_json(self):
        # Test writing dictionary to JSON
        data = {"key": datetime(2024, 1, 1)}
        write_dict_to_json(data, "tests/test_resources/test.json")
        with open("tests/test_resources/test.json", "r") as f:
            json_data = json.load(f)
        self.assertEqual(json_data["key"], "2024-01-01")

    def test_find_mentions_in_publications(self):
        # Test finding mentions of drugs in publications
        pub_df = pd.DataFrame(
            {
                "id": [1, 2],
                "title": ["Study on drug A", "Analysis on drug B"],
                "journal": ["Journal A", "Journal B"],
                "date_mention": ["2024-01-01", "2023-12-12"],
            }
        )
        result = find_mentions_in_publications(self.drugs_df, pub_df, "pubmed")
        self.assertIn("drug A", result)
        self.assertEqual(result["drug A"]["code"], "A01")

    def test_merge_dicts(self):
        # Test merging two dictionaries
        dict1 = {
            "drug A": {
                "journal": [{"date_mention": "2024-01-01", "journal": "Journal A"}]
            }
        }
        dict2 = {
            "drug A": {
                "journal": [{"date_mention": "2023-12-12", "journal": "Journal B"}]
            }
        }
        merged = merge_dicts(dict1, dict2)
        self.assertEqual(len(merged["drug A"]["journal"]), 2)


if __name__ == "__main__":
    unittest.main()
