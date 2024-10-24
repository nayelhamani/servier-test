# Python Drug Mentions Pipeline

## Description

This Python project builds a pipeline that reads, normalizes, and consolidates data from several sources (e.g., clinical trials, PubMed publications) and generates a graph of drug mentions across these publications. The pipeline includes utility functions for data manipulation and formatting, as well as logic to extract mentions of drugs and generate a JSON file with the results.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Formatting and Linting](#formatting-and-linting)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)

## Installation

### Prerequisites

- Python 3.8+ installed on your system.
- `pip` (Python package manager) installed.

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/nayelhamani/servier-test.git
   cd servier-test
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Pipeline

1. Run the pipeline script:

   ```bash
   python src/main.py
   ```

   This will generate a `drug_mentions_graph.json` file in src/result with the results of the pipeline.

### Main Features

- **Start Pipeline:** The `start_pipeline()` function loads the CSV and JSON data, normalizes it, and writes the results to a JSON file.
- **Data Normalization:** Functions to format dates, remove unwanted characters, and standardize text.
- **Drug Mentions Extraction:** The pipeline identifies mentions of drugs in PubMed articles and clinical trials, and consolidates these mentions into a JSON file.

## Running Tests

Unit and integration tests are provided to ensure that the pipeline works as expected.

### Running Unit Tests

To run the tests, firstly install pytest :

```bash
pip install pytest
```
and then execute the following command:

```bash
python -m pytest
```

## Formatting and Linting

### Code Formatting

This project uses **Black** for code formatting. To format your code, run:

```bash
black .
```

### Code Linting

Linting is performed using **Flake8** to check for style issues. You can run the linter as follows:

```bash
flake8 .
```

## Project Structure

```bash
.
├── README.md                   # Project documentation
├── src/
│   ├── result/                 # Result folder
│   ├── utils/
│   ├────── utils.py            # Utility functions
│   └── main.py                 # Main script
├── requirements.txt            # Dependencies list
├── resources/                  # Input data files (drugs.csv, pubmed.csv, etc.)
└── tests/                      # Unit and integration tests
    ├── unit_tests/             # Unit tests folder
    └── integration_tests/      # Integration tests folder
```

## Technologies Used

- **Python**: Core programming language.
- **Pandas**: Data manipulation and analysis library.
- **JSON5**: To handle flexible JSON parsing.
- **Flake8**: Python linter.
- **Black**: Python code formatter.
- **Unittest**: Built-in Python testing framework.