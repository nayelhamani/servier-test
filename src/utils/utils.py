import json5
import json
import pandas as pd
import unicodedata
from datetime import datetime


class TimestampEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for handling datetime objects.

    This encoder converts datetime objects to string format (YYYY-MM-DD).
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d")  # Convert to string
        return super().default(obj)


def json_to_df(filepath):
    """
    Loads data from a JSON5 file and converts it to a DataFrame.

    Args:
        filepath (str): The path to the JSON5 file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the JSON file.
    """
    with open(filepath) as f:
        data = json5.load(f)  # json5 handles trailing comma in json
    return pd.DataFrame(data)


def concat_dataframes(dataframes, reset_index=True):
    """
    Concatenates a list of DataFrames into a single DataFrame.

    Args:
        dataframes (list of pd.DataFrame): The list of DataFrames to concatenate.
        reset_index (bool): If True, resets the index of the concatenated DataFrame. Default is True.

    Returns:
        pd.DataFrame: The concatenated DataFrame.

    Raises:
        ValueError: If the input list of DataFrames is empty.
    """
    if not dataframes:
        raise ValueError("The list of DataFrames is empty.")

    concatenated_df = pd.concat(dataframes, ignore_index=reset_index)
    return concatenated_df


def delete_chars(df):
    """
    Cleans the DataFrame by removing specific unwanted characters and accents.

    Args:
        df (pd.Dataframe): A DataFrame to clean.

    Returns:
        pd.Dataframe: The cleaned DataFrame.
    """
    df = df.map(lambda s: s.replace("\\xc3\\xb1", "") if isinstance(s, str) else s)
    df = df.map(lambda s: s.replace("\\xc3\\x28", "") if isinstance(s, str) else s)
    df = df.map(lambda s: s.replace("\u2122", "") if isinstance(s, str) else s)
    df = df.map(lambda s: remove_accents(s) if isinstance(s, str) else s)
    return df


def remove_accents(text):
    """
    Removes accents from a given text string.

    Args:
        text (str): The text from which accents will be removed.

    Returns:
        str: The text without accents.
    """
    text_nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in text_nfd if unicodedata.category(c) != "Mn")


def lower_strip_df(df):
    """
    Converts all string values in a DataFrame to lowercase and strips whitespace.

    Args:
        df (pd.Dataframe): A DataFrame to normalize.

    Returns:
        pd.Dataframe: The normalized DataFrame.
    """
    return df.map(lambda s: s.lower().strip() if isinstance(s, str) else s)


def format_date(df, column):
    """
    Converts a specified column in the DataFrame to datetime format.

    Args:
        df (pd.DataFrame): The DataFrame containing the date column.
        column (str): The name of the column to format as datetime.

    Returns:
        pd.DataFrame: The DataFrame with the formatted date column.
    """
    df[column] = pd.to_datetime(df[column], format="mixed").astype(str)
    return df


def consolidate_clinical_trials_df(df):
    """
    Merges rows in the DataFrame that have a common title.

    Args:
        df (pd.DataFrame): The DataFrame containing clinical trials data.

    Returns:
        pd.DataFrame: A consolidated DataFrame with merged rows.
    """
    # Fusionner les lignes ayant un 'title' en commun
    df_grouped = df.groupby(
        ["title", "date_mention", "article_type"], as_index=False
    ).agg(
        {
            "id": "first",  # Combiner les IDs non vides
            "journal": "first",  # Combiner les journaux non vides
        }
    )

    # Réinitialiser l'index
    df_grouped.reset_index(drop=True, inplace=True)
    # Afficher le DataFrame nettoyé et fusionné
    return df_grouped


def consolidate_pubmed_df(df):
    """
    Cleans the PubMed DataFrame by removing rows with empty IDs.

    Args:
        df (pd.DataFrame): The DataFrame containing PubMed data.

    Returns:
        pd.DataFrame: A cleaned DataFrame with valid IDs.
    """
    df_clean = df[df["id"].str.strip() != ""]
    df_clean.loc[:, "id"] = df_clean["id"].astype("int")
    return df_clean


def write_dict_to_json(dict, filename):
    """
    Writes a dictionary to a JSON file using a custom JSON encoder.

    Args:
        dict (dict): The dictionary to write to the JSON file.
        filename (str): The name of the file to write to.

    Returns:
        None
    """
    dict_json = json.dumps(dict, cls=TimestampEncoder)
    with open(filename, "w") as f:
        f.write(dict_json)


def find_mentions_in_publications(drugs_df, pub_df, pub_type):
    """
    Finds mentions of drugs in publication DataFrames.

    Args:
        drugs_df (pd.DataFrame): DataFrame containing drug information.
        pub_df (pd.DataFrame): DataFrame containing publication data.
        pub_type (str): The type of publication (e.g., 'pubmed' or 'clinical_trials').

    Returns:
        dict: A dictionary containing drug mentions, with details from publications.
    """
    result_dict = {}
    for _, drug_row in drugs_df.iterrows():
        pub_mention = []
        journal_mention = []
        for _, pub_row in pub_df.iterrows():
            if drug_row["drug"] in pub_row["title"]:
                pub_mention.append(
                    {
                        "publication_id": pub_row["id"],
                        "title": pub_row["title"],
                        "date_mention": pub_row["date_mention"],
                        "journal": pub_row["journal"],
                    }
                )
                journal_mention.append(
                    {
                        "date_mention": pub_row["date_mention"],
                        "journal": pub_row["journal"],
                    }
                )
        result_dict[drug_row["drug"]] = {
            "code": drug_row["atccode"],
            pub_type: pub_mention,
            "journal": journal_mention,
        }
    return result_dict


def merge_dicts(dict1, dict2):
    """
    Merges two dictionaries, combining their entries.

    Args:
        dict1 (dict): The first dictionary to merge.
        dict2 (dict): The second dictionary to merge.

    Returns:
        dict: The merged dictionary with combined entries.
    """
    merged_dict = dict1.copy()

    for key, value in dict2.items():
        if "clinical_trials" in value:
            merged_dict[key]["clinical_trials"] = value["clinical_trials"]
        combined_journal = merged_dict[key]["journal"] + value["journal"]
        unique_journal = []
        seen = set()
        for entry in combined_journal:
            identifier = (entry["date_mention"], entry["journal"])
            if identifier not in seen:
                unique_journal.append(entry)
                seen.add(identifier)
        merged_dict[key]["journal"] = unique_journal
    return merged_dict
