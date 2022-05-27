import pandas as pd
from collections import Counter
from io import BytesIO, BufferedReader, TextIOWrapper


class Dataframe_reader:
    """
    Class for reading data from a dataframe.
    It is going to try several methods to read the dataframe.
    """

    def __init__(self, dataframe, extension):
        """Initialize the dataframe reader."""
        self.dataframe = dataframe
        self.extension = extension
        self.csv_wrapper = None

        ## Read the file.
        self.pick_route()

        ## Check if there are duplicated columns.
        duplicates = self.check_columns()
        if duplicates != []:
            raise Exception(f"The dataframe has duplicated columns: {duplicates}")

    def get_dataframe(self):
        """Return the dataframe."""
        return self.dataframe

    def read_xlsx(self):
        """Read an xlsx file."""
        self.dataframe = pd.read_excel(self.dataframe)

    def read_csv(self):
        """Read a csv file."""
        delimiter = self.detect_delimiter()
        self.csv_wrapper.seek(0)
        self.dataframe = pd.read_csv(self.csv_wrapper, sep=delimiter, low_memory=False)

    def csv_head(self, n):
        try:
            self.csv_wrapper = TextIOWrapper(
                BufferedReader(self.dataframe), encoding="utf-8"
            )
            head_lines = [next(self.csv_wrapper).rstrip() for x in range(n)]
        except StopIteration:
            with open(self.dataframe) as f:
                head_lines = f.read().splitlines()
        return head_lines

    def detect_delimiter(self, n: int = 20):
        sample_lines = self.csv_head(n)
        n_samples = int(len(sample_lines))
        common_delimiters = [",", ";", "\t", " ", "|", ":"]
        for d in common_delimiters:
            ref = sample_lines[0].count(d)
            if ref > 0:
                if all([ref == sample_lines[i].count(d) for i in range(1, n_samples)]):
                    return d
        return ","

    def read_pickle(self):
        """Read a pickle file."""
        self.dataframe = pd.read_pickle(self.dataframe)

    def read_parquet(self):
        """Read a parquet file."""
        self.dataframe = pd.read_parquet(self.dataframe)

    def check_columns(self):
        """
        Function to check if there are duplicated columns names in the dataframe.
        If True, return a list of the duplicate columns.
        """
        columns = self.dataframe.columns.tolist()
        if len(columns) != len(set(columns)):
            count = Counter(columns).most_common(1000)
            list_of_duplicates = [i[0] for i in count if i[1] > 1]
            return list_of_duplicates
        else:
            return []

    def pick_route(self):
        """Pick a route based on the extension."""
        if self.extension == "csv":
            self.read_csv()
        elif self.extension == "xlsx":
            self.read_xlsx()
        elif self.extension in ["pickle", "pkl"]:
            self.read_pickle()
        elif self.extension == "parquet":
            self.read_parquet()
        else:
            raise ValueError("The extension is not supported.")
