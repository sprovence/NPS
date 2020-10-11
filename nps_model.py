# -*- coding: utf-8 -*-
"""
Estimator module for predicting visitors from NPS datasets
"""

from sklearn import base

class GroupbyEstimator(base.BaseEstimator, base.RegressorMixin):
    
    def __init__(self, column, estimator_factory):
        # column is the value to group by; estimator_factory can be
        # called to produce estimators
        self.column = column
        self.estimator = estimator_factory()
        self.ests = {}   # dictionary of each individual fit
    
    def fit(self, X, y):
        # Create an estimator and fit it with the portion in each group
        groups = X[self.column].unique()
        for group in groups:
            indices = (X[X[self.column] == group]).index
            X_subset = X[X[self.column] == group]
            y_subset = y.iloc[indices]
            self.ests[group] = self.estimator
            self.ests[group].fit(X_subset, y_subset)
        return self

    def predict(self, X):
        preds = pd.Series(index=X.index.copy())
        # Separate X into groups by column
        groups = X[self.column].unique()
        for group in groups:
            indices = (X[X[self.column] == group]).index
            X_subset = X[X[self.column] == group]
            preds.iloc[indices] = self.ests[group].predict(X_subset)
        return preds.to_numpy()

