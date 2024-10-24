import unittest
from unittest.mock import patch, mock_open
import pandas as pd
from io import StringIO
from src.main import start_pipeline, print_max_journal_distinct_drugs

class TestPipeline(unittest.TestCase):

    def setUp(self):
        # Sample dataframes to return when CSVs/JSON are read
        self.drugs_df = pd.DataFrame(
            {"drug": ["Aspirin", "Paracetamol"], "atccode": ["B01AC06", "N02BE01"]}
        )

        self.pubmed_df = pd.DataFrame(
            {
                "id": [1, 2],
                "title": ["Aspirin effects", "Paracetamol usage"],
                "date": ["2022-01-01", "2022-02-01"],
                "journal": ["Journal of Medicine", "Pharmaceutical Journal"],
            }
        )

        self.pubmed_json_df = pd.DataFrame(
            {
                "id": ["3", 4],
                "title": ["Study on drug A", "Drug B analysis"],
                "date": ["2022-01-01", "02/01/2022"],
                "journal": ["Journal A", "Journal B"],
            }
        )

        self.clinical_trials_df = pd.DataFrame(
            {
                "id": [3, 4],
                "title": ["Aspirin Trial", "Paracetamol Study"],
                "date": ["2022-03-01", "2022-04-01"],
                "journal": ["Clinical Trials Journal", "Medical Research"],
            }
        )

        # Expected output dictionary after pipeline processing
        self.expected_mentions_dict = {
            "aspirin": {
                "code": "b01ac06",
                "pubmed": [
                    {
                        "publication_id": 1,
                        "title": "aspirin effects",
                        "date_mention": "2022-01-01",
                        "journal": "journal of medicine",
                    }
                ],
                "clinical_trials": [
                    {
                        "publication_id": 3,
                        "title": "aspirin trial",
                        "date_mention": "2022-03-01",
                        "journal": "clinical trials journal",
                    }
                ],
                "journal": [
                    {"date_mention": "2022-01-01", "journal": "journal of medicine"},
                    {
                        "date_mention": "2022-03-01",
                        "journal": "clinical trials journal",
                    },
                ],
            },
            "paracetamol": {
                "code": "n02be01",
                "pubmed": [
                    {
                        "publication_id": 2,
                        "title": "paracetamol usage",
                        "date_mention": "2022-02-01",
                        "journal": "pharmaceutical journal",
                    }
                ],
                "clinical_trials": [
                    {
                        "publication_id": 4,
                        "title": "paracetamol study",
                        "date_mention": "2022-04-01",
                        "journal": "medical research",
                    }
                ],
                "journal": [
                    {"date_mention": "2022-02-01", "journal": "pharmaceutical journal"},
                    {"date_mention": "2022-04-01", "journal": "medical research"},
                ],
            },
        }

    @patch("src.utils.utils.pd.read_csv")
    @patch("src.main.json_to_df")
    @patch("src.main.write_dict_to_json")
    def test_start_pipeline(
        self, mock_write_dict_to_json, mock_json_to_df, mock_read_csv
    ):
        # Mock the CSV and JSON reading
        mock_read_csv.side_effect = [
            self.drugs_df,
            self.pubmed_df,
            self.clinical_trials_df,
        ]
        mock_json_to_df.return_value = self.pubmed_json_df

        # Call the start_pipeline function
        start_pipeline()

        # Verify that the write_dict_to_json was called with the expected dictionary
        mock_write_dict_to_json.assert_called_once_with(
            self.expected_mentions_dict, "src/result/drug_mentions_graph.json"
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""{"drug A": {"journal": [{"journal": "Journal A"}, {"journal": "Journal B"}]},
                     "drug B": {"journal": [{"journal": "Journal B"}]}}""",
    )
    def test_print_max_journal_distinct_drugs(self, mock_file):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            print_max_journal_distinct_drugs("src/result/drug_mentions_graph.json")
            self.assertIn("Journal B", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
