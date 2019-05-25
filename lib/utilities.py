import logging
import pandas as pd


def save_to_excel(dataframes, images,
                       output_xlsx):
    """
    Writes Input source ``statistics``, ``correlation``,
    ``correlation heatmap`` and ``correlation pair plot``
    to a Excel output

    Parameters
    ----------
    dataframes : dict
        Heatmap Image file path
    images : dict
        Pair Plot Image file path
    output_xlsx : str
        Excel output location


    Examples
    --------
    >>> save_to_excel(output_xlsx=CONFIG['OUTPUT']['synth_summary_excel'],
                      dataframes={'Description': synth_stats.describe,
                                  'Correlation': synth_stats.corr, },
                      images={'Pair Plot': CONFIG['OUTPUT']['synth_corr_pair_plot'],
                              'Heatmap': CONFIG['OUTPUT']['synth_corr_heatmap'],
                              'Cluster': CONFIG['OUTPUT']['synth_cluster'], })
    """
    logging.info(f'Storing dataframes {dataframes} and images {images} '
                 f'at {output_xlsx}')
    with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
        for sheet, df in dataframes.items():
            logging.debug(f'Adding sheet {sheet}, content from {(str(df))} to '
                          f'{output_xlsx}')
            exec(f'df.to_excel(writer, sheet_name="{sheet}")')
        # FIXME: creating empty DataFrame in order to add empty sheets
        #  for images
        empty_df = pd.DataFrame()
        for sheet, image in images.items():
            logging.debug(f'Adding sheet {sheet}, Image {image} to '
                          f'{output_xlsx}')
            empty_df.to_excel(writer, sheet_name=sheet)
            writer.sheets[sheet].insert_image(0, 0, image)
