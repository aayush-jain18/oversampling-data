"""
main.py
====================================
The core module of Synthetic Data Generation
"""
import logging
import os
from datetime import datetime

import oyaml as yaml
import pandas as pd
import click
from sqlalchemy import create_engine

from smote import custom_smote
from metadata import db_metadata
from statistics import Statistics
from constants import Constants
from clustering import kmeans_cluster
from utilities import save_to_excel


def load_objects_file(file):
    """
    Read yaml file into a Dictionary.

    Parameters
    ----------
    file : yaml file to load

    Returns
    -------
    dict
    """
    with open(file, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            raise


def get_cat_codes_df(df):
    """
    Returns DataFrame containing only categorical columns
    converted into numeric code, used for clustering

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    df_cat_codes : pd.DataFrame
    """
    df_cat_codes = pd.DataFrame()
    for column, dtype in df.dtypes.to_dict().items():
        if str(dtype) == 'category':
            df_cat_codes[column] = df[column].cat.codes
        elif str(dtype).startswith('int'):
            df_cat_codes[column] = df[column]
    return df_cat_codes


def read_sql(sql, con):
    """
    Read SQL query or database table into a DataFrame.

    Parameters
    ----------
    sql : string or SQLAlchemy Selectable (select or text object)
        SQL query to be executed or a table name.
    con : SQLAlchemy connectable (engine/connection) or database string URI
        or DBAPI2 connection (fallback mode)

    Returns
    -------
    y : pd.DataFrame
    """
    try:
        y = pd.read_sql(sql, con).astype(config['SMOTE']['index_cat_col'])
        logging.warning(f"Dropping columns {config['INPUT']['drop_cols']} "
                        f"from DataFrame")
        # TODO: do not drop any columns, use this as parameterized
        #  convert them to numerical bin
        y.drop(config['INPUT']['drop_cols'], axis='columns', inplace=True)
        return y
    except Exception as exception:
        logging.error('%(exception)s')
        raise exception


@click.command()
@click.option('-c', '--cfg',
              required=True,
              type=click.Path(exists=True),
              default=os.path.abspath(os.path.join(os.getcwd(),
                                                   'tests',
                                                   'config.yaml')),
              help='yaml type Config file containing list of parameters for '
                   'Synthetic data generation')
def main(cfg):
    global config
    config = load_objects_file(cfg)
    logging.basicConfig(format=Constants.LOG_FORMAT,
                        filemode='w',
                        filename=os.path.abspath(
                            config['OUTPUT']['log_file']),
                        level=logging.INFO)
    logging.info(f'Start Time: {START}')
    logging.info(f'Present Working Directory: {os.getcwd()}')

    engine = create_engine(config['INPUT']['engine'])
    logging.info("Generating DataFrame from sql, executing query "
                 f"{config['INPUT']['sql']}; "
                 f"on db {config['INPUT']['engine']}")
    df = read_sql(config['INPUT']['sql'], engine)
    df_cat_codes = get_cat_codes_df(df)

    # TODO: Enable this only if input source is db, move it to module
    # Get Database metadata in Excel
    db_metadata(config['INPUT']['engine'],
                config['OUTPUT']['db_metadata'])
    logging.info(f"DB metadata excel output: "
                 f"{os.path.abspath(config['OUTPUT']['db_metadata'])}")

    # pre synthetic data generation, generate clusters
    kmeans_cluster(df_cat_codes,
                   config['CLUSTER']['X'],
                   (config['OUTPUT']['cluster']))

    # Get categorical columns index loc
    cat_cols = [df.columns.get_loc(c)
                for c, dtype in df.dtypes.to_dict().items()
                if str(dtype) == 'category']

    # Call smote algorithm for synthetic data generation
    synth_df = custom_smote(df, cat_cols)

    # TODO: write the synthetic output to desired data structure type
    synth_df.to_excel(os.path.join(config['OUTPUT']['output_path'],
                                   'synth_results.xlsx'))

    # post synthetic data generation
    synth_df_cat_codes = get_cat_codes_df(synth_df)
    kmeans_cluster(synth_df_cat_codes,
                   config['CLUSTER']['X'],
                   (config['OUTPUT']['synth_cluster']))

    # TEMP:
    # getting statistics model and generating reports for input source
    stats = Statistics(df)
    logging.info(f"Statistics summary of input DataFrame:\n"
                 f"{stats.describe.to_string()}")
    stats.corr_heatmap(config['OUTPUT']['corr_heatmap'])
    logging.info("Correlation heatmap output: "
                 f"{os.path.abspath(config['OUTPUT']['corr_heatmap'])}")
    stats.corr_pair_plot(config['OUTPUT']['corr_pair_plot'])
    logging.info("Correlation pair plot output: "
                 f"{os.path.abspath(config['OUTPUT']['corr_pair_plot'])}")

    save_to_excel(output_xlsx=config['OUTPUT']['summary_excel'],
                  dataframes={'Description': stats.describe,
                              'Correlation': stats.corr,},
                  images={'Pair Plot': config['OUTPUT']['corr_pair_plot'],
                          'Heatmap': config['OUTPUT']['corr_heatmap'],
                          'Cluster': config['OUTPUT']['cluster'], })
    logging.info("Statistics summary excel output: "
                 f"{os.path.abspath(config['OUTPUT']['summary_excel'])}")

    # TEMP:
    # getting statistics model and generating reports for input source
    synth_stats = Statistics(synth_df)
    logging.info("Statistics summary of Synthetic generated DataFrame:\n"
                 f"{synth_stats.describe.to_string()}")
    synth_stats.corr_heatmap(config['OUTPUT']['synth_corr_heatmap'])
    logging.info("Correlation heatmap output: "
                 f"{os.path.abspath(config['OUTPUT']['synth_corr_heatmap'])}")
    synth_stats.corr_pair_plot(config['OUTPUT']['synth_corr_pair_plot'])
    logging.info("Correlation heatmap output: "
                 f"{os.path.abspath(config['OUTPUT']['synth_corr_pair_plot'])}")

    save_to_excel(output_xlsx=config['OUTPUT']['synth_summary_excel'],
                  dataframes={'Description': synth_stats.describe,
                              'Correlation': synth_stats.corr, },
                  images={'Pair Plot': config['OUTPUT']['synth_corr_pair_plot'],
                          'Heatmap': config['OUTPUT']['synth_corr_heatmap'],
                          'Cluster': config['OUTPUT']['synth_cluster'], })
    logging.info("Statistics summary excel output: "
                 f"{os.path.abspath(config['OUTPUT']['synth_summary_excel'])}")

    logging.info(f"Total Time Taken: {datetime.now() - START}")


if __name__ == '__main__':
    START = datetime.now()
    main()

