import logging

import pandas as pd
import openpyxl
import sqlalchemy

from constants import Constants


class UserMetadata:
    """
    class to get metadata from any database
    pass the connection string while creating object for the wrapper
    say for sqlite i.e. sqlite:///satyam.db

    Exposed Methods
    ---------------
        get_tables
        get_meta_for_table

    Parameters
    ----------
    conn : str
        SQLAlchemy connectable (engine/connection) or database string URI
        or DBAPI2 connection (fallback mode)
    """

    def __init__(self, conn):
        self.__engine = sqlalchemy.create_engine(conn)
        self.__metadata = sqlalchemy.MetaData()
        self.__metadata.reflect(bind=self.__engine)

    def get_tables(self):
        """
        Function for getting all the tables in the schema
            this list all the available functions
        """
        return self.__metadata.tables.keys()

    def get_meta_for_table(self, db_table):
        """
        Returns metadata for a given Table in Database

        Parameters
        ----------
        db_table : Table name from Database

        Returns
        -------
        y : pd.DataFrame
        """
        if db_table in self.__metadata.tables.keys():
            table_meta = ([{i: self.__filter_col_meta(j)
                          for i, j in
                            self.__metadata.tables[db_table].columns.items()}
                           ])
            df = pd.DataFrame.from_records(table_meta[0])
            return df
        else:
            raise Exception('Table Not Found')

    def __parse_cols(self, column_meta):
        """
        Formatting columns with class objects

        Parameters
        ----------
        column_meta :

        Returns
        -------
        column_meta
        """
        column_meta['type'] = column_meta.pop('type').__str__()
        list_fk = list(column_meta.pop('foreign_keys'))
        column_meta['constraints'] = list_fk
        return column_meta

    def __filter_col_meta(self, data):
        """
        For converting column object to keys
        and parsing the data and objects to JSON serializable
        format so that it can be dumped as JSON

        Parameters
        ----------
        data :

        Returns
        -------
        column_meta
        """
        column_meta = self.__parse_cols({i: j
                                         for i, j in
                                         data.__dict__.items()
                                         if i in
                                         Constants.METADATA_ALLOWED_KEYS})
        return column_meta


def db_metadata(engine, output_xlsx):
    """
    Gets metadata for all the tables in Database

    Parameters
    ----------
    engine : str
        SQLAlchemy connectable (engine/connection) or database string URI
        or DBAPI2 connection
    output_xlsx : str
        Output xlsx path to store table metadata
    """
    umd = UserMetadata(engine)
    tables = umd.get_tables()
    with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
        for table in tables:
            logging.debug(f'Adding sheet {table}')
            df = pd.DataFrame(umd.get_meta_for_table(table))
            df.to_excel(writer, sheet_name=table, na_rep='None')
