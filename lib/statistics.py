import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns


# Question: What is purpose of metadata excel?
class Statistics:
    """
    Provides sets to derive and store stats for a
    pandas DataFrame type object

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame for stats calculation and plots

    """

    def __init__(self, df):
        if isinstance(df, pd.DataFrame):
            self.df = df
        else:
            logging.error("DataFrame constructor called"
                          "with incompatible data type! "
                          "Expecting Pandas DataFrame object")
            raise ValueError('DataFrame constructor called '
                             'with incompatible data and dtype!')

    @property
    def describe(self):
        """
        Generate descriptive statistics that summarize the central tendency,
        dispersion and shape of a dataset's distribution, excluding
        ``NaN`` values.

        Parameters
        ----------
        self.df : pd.DataFrame

        Returns
        -------
        statistics : pd.DataFrame
            Summary statistics of the DataFrame provided.

        Notes
        -----
        For numeric data, the result's index will include ``count``,
        ``mean``, ``std``, ``min``, ``mode``, ``max`` as well as
        lower, ``50`` and upper percentiles. By default the lower
        percentile is ``25`` and the upper percentile is ``75``.
        The ``50`` percentile is the same as the median.
        """
        mode = self.df.mode(numeric_only=True).dropna()
        mode.index = ['mode']
        describe = self.df.describe(include=[np.number])
        describe = describe.append(mode)
        return describe

    @property
    def corr(self):
        """
        Compute pairwise correlation of columns, excluding NA/null values.

        Parameters
        ----------
        self.df : pd.DataFrame type object

        Returns
        -------
        corr : pd.DataFrame
        """
        return self.df.corr().dropna(
            axis='columns', how='all').dropna(
            axis='rows', how='all')

    def corr_pair_plot(self, file_path):
        """
        Plot pairwise relationships in a dataset.

        Parameters
        ----------
        file_path : str
            File path to save pair plot figure
        """
        logging.debug("Generating pair plot for DataFrame")
        sns.set(font_scale=3.0)
        sns.set(rc={'figure.figsize': (60, 60)})
        logging.debug("Saving pair plot figure at %(file_path)s")
        sns.pairplot(self.corr, height=2).savefig(file_path)

    def corr_heatmap(self, file_path):
        """
        Plot and save rectangular data as a color-encoded matrix.

        Parameters
        ----------
        file_path : str
            File path to save heatmap
        """
        logging.debug("Generating Heatmap for DataFrame")
        sns.set(font_scale=3.0)
        fig, ax = plt.subplots(figsize=(35, 35))
        sns.heatmap(self.corr, xticklabels=self.corr.columns,
                    yticklabels=self.corr.columns, annot=True,
                    annot_kws={"size": 30, "weight": "bold"},
                    linewidths=1.0, ax=ax, cmap="Blues")
        logging.debug("Saving heatmap figure at %(file_path)s")
        fig.savefig(file_path)
        plt.close()
