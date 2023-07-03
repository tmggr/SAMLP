""""####################################################################################################################
Author: Alexander Shevtsov ICS-FORTH
E-mail: shevtsov@ics.forth.gr
-----------------------------------
Implementation of data loading utility. It allows to load data from data path and manage to :
    - split them into train/validation (visible) and test (hold-out) portions
    - in case of repetitions script keeps original data split in order to keep testing set un-seen by model
    - also stability of test set and train/validation allow to multiple executions over different algorithms
      and keep their performances equal
####################################################################################################################"""

import pandas as pd
import numpy as np
from os import path
import utilities.mongoConfig as cnf
from sklearn.model_selection import train_test_split



class DataLoading:

    def __init__(self, data_path, test_size=0.2, verbose=False, shuffle=True):
        """Define all type of features filenames (output files from feature extraction methods)"""

        if not data_path.endswith('/'):
            data_path += '/'
        
        self.single_file = f'{data_path}{cnf.InputFileName}'

        self.visible_postfix = "_visible.csv"
        self.hidden_postfix = "_hold_out.csv"

        self.test_size = test_size
        self.verbose = verbose
        self.shuffle = shuffle

        self.main()

    """Check if data is already aligned or required pre-processing
        Return values: 0 (Don't require) 
                       1 (Required for all files)
    """
    def require_processing(self):
        to_check = [self.single_file.replace(".csv", self.visible_postfix), self.single_file.replace(".csv", self.hidden_postfix)]
        if False in [path.isfile(file) for file in to_check]:
            if self.verbose: print("-" * 5 + ': Required pre-processing')
            return True

        if self.verbose: print("-" * 5 + ': Pre-processing is not required')
        return False

    def prepare(self):
        if self.verbose: print("Data Loading: Prepare function")

        """Read CSV file and balance the classes"""
        df = pd.read_csv(self.single_file, header=0, sep='\t')

        """Split the data into train/val and testing sets"""
        visible_df, test_df = self.split(df)

        """Store the Train/Test and Hold-out data portions in separate CSV files"""
        self.store_df(visible_df, test_df)


    """
        Split Dataframe into two portions with *_visible.csv (train/val) and *_hidden.csv (test) postfix.
        This procedure is performed for each feature categories since 
        different model type require different category of features.
    """
    def split(self, data):


        if self.verbose: print('Data Loading: Split')

        """ Stratified split dataset into two portions
            Visible (Train/Validation) and Test portion as a hold-out
        """
        X_visible, X_test, _, _ = train_test_split(data, data["target"],
                                                   test_size=self.test_size,
                                                   shuffle=self.shuffle,
                                                   stratify=data["target"])
        return X_visible, X_test


    def store_df(self, X_visible, X_test):
        """Store dataframes in separate files for each feature category as visible and hidden portion"""
        X_visible.to_csv(self.single_file.replace(".csv", self.visible_postfix),
                        sep="\t", index=False)
        X_test.to_csv(self.single_file.replace(".csv", self.hidden_postfix),
                        sep="\t", index=False)


    def _load_csv_file(self, filename):
        X = pd.read_csv(filename, sep="\t", header=0)
        Y = X["target"].copy()
        X.drop(["target", "user_id"], axis=1, inplace=True)
        X.replace([np.inf, -np.inf], 0, inplace=True)
        return X, Y

    def load_dataset(self, splited=True):

        if self.verbose:
            print(f'Data Loading: read csv')
        if splited:
            """Loading visible and hidden dataframes"""
            X_train, Y_train = self._load_csv_file(self.single_file.replace(".csv", self.visible_postfix))
            X_test, Y_test = self._load_csv_file(self.single_file.replace(".csv", self.hidden_postfix))
            Y_train = Y_train.astype(int)
            Y_test = Y_test.astype(int)

            if self.verbose:
                print('Data Loading: Loaded dataset with:' +
                      f'\n\tVisible portion, class 0:{sum(Y_train == 0)} and 1:{sum(Y_train == 1)}' +
                      f'\n\t Hold-out portiona, class 0:{sum(Y_test == 0)} and 1:{sum(Y_test == 1)}')
            return X_train, Y_train, X_test, Y_test
        else:
            X, Y = self._load_csv_file(self.single_file)
            Y = Y.astype(int)
            if self.verbose:
                print('Data Loading: Loaded dataset with:' +
                      f'\n\tWith class 0:{sum(Y == 0)} and 1:{sum(Y == 1)}')
            return X, Y


    def main(self):
        if self.verbose:
            print("Data Loading: initialization")

        if self.require_processing():

            self.prepare()
            if self.verbose:
                print("\tComplete")





