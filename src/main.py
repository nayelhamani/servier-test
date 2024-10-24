import json
import pandas as pd
from collections import defaultdict
from utils.utils import (
    lower_strip_df,
    format_date,
    delete_chars,
    json_to_df,
    consolidate_pubmed_df,
    consolidate_clinical_trials_df,
    write_dict_to_json,
    find_mentions_in_publications,
    merge_dicts,
)

RESOURCE_FOLDER = "resources"


def start_pipeline():
    """
    Starts the data processing pipeline.

    Loads DataFrames from CSV and JSON files, normalizes the data,
    generates a dictionary of drug mentions, and writes this dictionary
    to a JSON file.

    Returns:
        None
    """
    drugs_df, pubmed_df, clinical_trials_df = dfs_from_files()
    drugs_df, pubmed_df, clinical_trials_df = normalize_dfs(
        drugs_df, pubmed_df, clinical_trials_df
    )
    mentions_dict = generate_mentions_dict(drugs_df, pubmed_df, clinical_trials_df)
    write_dict_to_json(mentions_dict, "src/result/drug_mentions_graph.json")


def dfs_from_files():
    """
    Loads data from CSV and JSON files and combines them.

    Returns:
        tuple: A tuple containing three DataFrames:
            - drugs_df: DataFrame containing drug data.
            - pubmed_df: DataFrame containing PubMed data.
            - clinical_trials_df: DataFrame containing clinical trials data.
    """
    drugs_df = pd.read_csv(f"{RESOURCE_FOLDER}/drugs.csv")
    pubmed_df1 = pd.read_csv(f"{RESOURCE_FOLDER}/pubmed.csv")
    pubmed_df2 = json_to_df(f"{RESOURCE_FOLDER}/pubmed.json")
    clinical_trials_df = pd.read_csv(f"{RESOURCE_FOLDER}/clinical_trials.csv")
    pubmed_df = pd.concat([pubmed_df1, pubmed_df2]).reset_index(drop=True)
    return drugs_df, pubmed_df, clinical_trials_df


def normalize_dfs(drugs_df, pubmed_df, clinical_trials_df):
    """
    Normalizes the DataFrames by applying transformations to the columns.

    This includes lowercasing, formatting dates,
    and removing unwanted characters.

    Args:
        drugs_df (pd.DataFrame): DataFrame containing drug data.
        pubmed_df (pd.DataFrame): DataFrame containing PubMed data.
        clinical_trials_df (pd.DataFrame): DataFrame containing clinical trials data.

    Returns:
        tuple: A tuple containing the three normalized DataFrames.
    """
    drugs_df = lower_strip_df(drugs_df)
    pubmed_df = lower_strip_df(pubmed_df)
    clinical_trials_df = lower_strip_df(clinical_trials_df)

    pubmed_df = format_date(pubmed_df, "date")
    clinical_trials_df = format_date(clinical_trials_df, "date")

    pubmed_df["article_type"] = "pubmed"
    clinical_trials_df["article_type"] = "clinical_trials"
    clinical_trials_df = clinical_trials_df.rename(
        columns={"scientific_title": "title", "date": "date_mention"}
    )
    pubmed_df = pubmed_df.rename(columns={"date": "date_mention"})

    clinical_trials_df = delete_chars(clinical_trials_df)
    pubmed_df = delete_chars(pubmed_df)

    pubmed_df = consolidate_pubmed_df(pubmed_df)
    clinical_trials_df = consolidate_clinical_trials_df(clinical_trials_df)

    return drugs_df, pubmed_df, clinical_trials_df


def generate_mentions_dict(drugs_df, pubmed_df, clinical_trials_df):
    """
    Generates a dictionary of drug mentions from the DataFrames.

    This function searches for drug mentions in PubMed articles and
    clinical trials.

    Args:
        drugs_df (pd.DataFrame): DataFrame containing drug data.
        pubmed_df (pd.DataFrame): DataFrame containing PubMed data.
        clinical_trials_df (pd.DataFrame): DataFrame containing clinical trials data.

    Returns:
        dict: A dictionary containing drug mentions.
    """
    pubmed_mentions = find_mentions_in_publications(drugs_df, pubmed_df, "pubmed")
    clinical_trials_mentions = find_mentions_in_publications(
        drugs_df, clinical_trials_df, "clinical_trials"
    )
    return merge_dicts(pubmed_mentions, clinical_trials_mentions)


def print_max_journal_distinct_drugs(filepath):
    """
    Prints the journal that mentions the most distinct drugs.

    Args:
        filepath (str): The path to the JSON file containing drug mentions.

    Returns:
        None
    """
    with open(filepath, "r") as file:
        data = json.load(file)

    journal_counts = defaultdict(set)
    for drug, info in data.items():
        for entry in info["journal"]:
            journal_counts[entry["journal"]].add(drug)

    max_journal = max(journal_counts.items(), key=lambda x: len(x[1]))

    print(
        f"Le journal qui mentionne le plus de médicaments différents est : '{max_journal[0]}'."
    )


if __name__ == "__main__":
    start_pipeline()
    print_max_journal_distinct_drugs("src/result/drug_mentions_graph.json")
