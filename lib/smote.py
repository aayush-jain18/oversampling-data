import logging

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC
# from sote import SOTENC


# TODO: Creating too many pandas objects/dataframes slows the performance
# FIXME: parametrize this input for y_kmeans
def custom_smote(df, cat_cols, random_state=1234):
    """
    Creates synthetic DataFrame for a Input DataFrame by splitting dataframe
    to minority and majority using train_test_split by a given percentage.
    Adds a boolean column to minority and majority assigning, where all
    column values for one dataset will be 0 and 1 for the other. Joins the
    two datasets back and feeds to SMOTE algorithm for synthetic data
    generation.

    Parameters
    ----------
    df : pd.DataFrame
    cat_cols : list
        List of categorical columns
    random_state : int

    Returns
    -------
    output : pd.DataFrame
    """
    df_dtypes = df.dtypes.astype('str').to_dict()
    logging.debug("shuffling the data just in case if the datafile "
                  "itself has majority and minority grouped together")
    df = df.sample(frac=1)
    df_dtypes.update({'__flag_value': 'int8'})

    minority = df.copy()
    majority = df.append([df, df], ignore_index=True)
    minority['__flag_value'] = 1
    majority['__flag_value'] = 0
    df_x = majority.append(minority, ignore_index=True)
    y = df_x.iloc[:, df_x.columns == '__flag_value'].squeeze()
    df_x = df
    y = np.zeros(len(df_x), dtype=int)

    logging.info("Performing Smote operation on the DataFrame")
    sm = SMOTENC(categorical_features=cat_cols,
                 random_state=random_state,
                 k_neighbors=6)
    output = sm.fit_sample(df_x, y)

    logging.info("Creating DataFrame from synthetic results, "
                 "and casting Input DataFrame column names and dtypes")
    output = pd.DataFrame(output[0],
                          columns=list(df_dtypes.keys()
                                       )).astype(df_dtypes)
    output = output[output['__flag_value'] != 0]
    output.drop('__flag_value', inplace=True, axis='columns')
    return output
