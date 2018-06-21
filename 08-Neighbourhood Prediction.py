#!/usr/bin/python
# -*- coding: latin-1 -*-

# For reproducibility
import random
import numpy as np
r_state = 42
random.seed(r_state)
np.random.seed(r_state)

import os
import re
import pandas as pd
import seaborn as sns

import sklearn
print('Your scikit-learn version is {}.'.format(sklearn.__version__))
print('Please check it is at least 0.18.0.')

from sklearn.preprocessing import scale
from sklearn import linear_model
from sklearn import tree
from sklearn import preprocessing
from sklearn import feature_selection
from sklearn import model_selection
from sklearn import metrics
from sklearn import ensemble

from sklearn.externals.six import StringIO
#from sklearn.model_selection import GridSearchCV
#from sklearn.feature_selection import SelectKBest
#from sklearn.feature_selection import f_regression

from timeit import default_timer as timer
import datetime

analytical = os.path.join('data','analytical')
output     = os.path.join(os.path.expanduser('~'),'Documents','Dropbox','ESRC Gentrification','data','analytical')

def load_status_scores(dtype):
    status = pd.read_csv(os.path.join(analytical,dtype+'-Scores.csv.gz'), index_col=0)  # SES scores

    # Scores
    status.drop(['RANK_01','RANK_11'], axis=1, inplace=True)
    status.rename(columns={
        'SES_01':'SES 2001',
        'SES_11':'SES 2011',
        'SES_ASC':'SES Ascent 2001-2011',
        'SES_PR_01':'SES 2001 Percentile', # 99 = High-status
        'SES_PR_11':'SES 2011 Percentile', # 99 = High-status
        'SES_PR_ASC':'SES Percentile Ascent 2001-2011'
    }, inplace=True)
    return status

def load_predictors(dtype):

    return status

def classifier_report(clf, y_true, y_hat):

    txt = ''

    # If the task is regression evaluate using regression metrics,
    # otherwise evaluate using classification metrics
    txt += "R2:        {0:8.5f}".format(metrics.r2_score(y_true, y_hat)) + "\n" #  R2 - Coefficient of determination
    txt += "MSE:       {0:8.5f}".format(metrics.mean_squared_error(y_true, y_hat)) + "\n"  #  Mean squared error regression loss
    txt += "MAE:       {0:8.5f}".format(metrics.mean_absolute_error(y_true, y_hat)) + "\n"  #  Mean absolute error regression loss
    txt += "Expl. Var: {0:8.5f}".format(metrics.explained_variance_score(y_true, y_hat)) + "\n"  # Explained variance regression score function
    txt += "\n"

    #print(metrics.accuracy_score(y_true, y_pred))  #  Accuracy Score
    #print(metrics.classification_report(y_true, y_pred, target_names=["Unascended","Ascended"]))  #  Classification Report
    #print(metrics.confusion_matrix(y_true, y_pred))  #  Confusion Matrix
    #print()
    return txt


# Can override to_use here
to_use = 'Untransformed'

SES = load_status_scores(to_use)  # SES scores in 2011

#  Read the transformed data
d01_trs2 = pd.read_csv(os.path.join(analytical,to_use+'-2001-Data-Transformed_and_Scaled.csv.gz'), index_col=0)
d11_trs2 = pd.read_csv(os.path.join(analytical,to_use+'-2011-Data-Transformed_and_Scaled.csv.gz'), index_col=0)

# Data about variables used later in process
vardb = pd.read_csv(os.path.join('data','variables.csv'), index_col=False)
vardb.drop('Description', axis=1, inplace=True)

X_full = d01_trs2

X_train, X_test, y_train, y_test = model_selection.train_test_split(
    d01_trs2, SES['SES Ascent 2001-2011'], test_size=0.2, random_state=r_state)

# Use a grid over parameters of interest -- search grid
# partly extracted from testing with notebook 7 and party
# from playing with grid ranges here (since results produced
# by manipulating one parameter separately from the others
# don't always replicate well as the single tuned parameter
# for the ensemble as a whole). In other words, just because
# max_depth==10 was the best result from manipulating _only_
# tree depth doesn't mean that it will be the best when you
# start manipulating all the main hyperparameters together.
param_grid = {
    "n_estimators"      : [int(x) for x in np.arange(start=160, stop=211, step=20)] + [int(x) for x in np.arange(start=1300, stop=1501, step=100)],
    "max_depth"         : [int(x) for x in np.arange(start=10, stop=141, step=90)]+[None],
    "min_samples_leaf"  : [1,2,4],
    "max_features"      : [0.7, 0.85, 'auto'], # For regression normally n_features (i.e. auto)
}

print("Estimators: " + str(param_grid['n_estimators']))
print("Depth: " + str(param_grid['max_depth']))
print("Minimum Samples Leaf: " + str(param_grid['min_samples_leaf']))
print("Maximum Features: " + str(param_grid['max_features']))
print("Number of permutations: " + str(len(param_grid['n_estimators']) * len(param_grid['max_depth']) * len(param_grid['max_features']) * len(param_grid['min_samples_leaf'])))

clf = ensemble.ExtraTreesRegressor(n_jobs=-1, random_state=r_state) # Can be 'mae' or 'mse' -- should presumably match scoring below
start = timer()
# There is some disagreement about whether cross-validation or bootstrapping
# is needed for ExtraTrees (or even RandomForests) regressors:
# https://stats.stackexchange.com/questions/279163/cross-validation-in-extratreesregressor
scoring = {'mae':'neg_mean_absolute_error', 'mse':'neg_mean_squared_error'} #, 'r2':'r2'}
#cv = model_selection.GridSearchCV(estimator=clf, param_grid=param_grid, cv=4, n_jobs=10, verbose=0, scoring='neg_mean_absolute_error')
cv = model_selection.GridSearchCV(estimator=clf, param_grid=param_grid, cv=4, n_jobs=6, verbose=1, scoring='neg_mean_squared_error')
#cv = model_selection.GridSearchCV(estimator=clf, param_grid=param_grid, cv=4, n_jobs=6, verbose=0, scoring='r2')
cv.fit(X_train, y_train)
duration = timer() - start
print("Execution complete in: {0:15.1f}s".format(duration) + " (" + str(datetime.timedelta(seconds=duration)) + ")")
print("Best score: " + str(cv.best_score_))
print("Done.")

log = open(os.path.join(output,to_use+'-Fit.txt'),'a')
print("########################", file=log)
print("Params: ", file=log)
print(param_grid, file=log)
print("Best Cross-Validation score: " + str(cv.best_score_), file=log)

best_clf = cv.best_estimator_ # Extract the best estimator from the GridSearch
best_clf.fit(X_train, y_train)
y_pred  = best_clf.predict(X_test)

print("Best parameters from Cross-Validation: " + str(cv.best_params_), file=log)
print("Best parameters from Cross-Validation: " + str(cv.best_params_))
print("", file=log)

print("Cross-check against full spec of model: ", file=log)
print(best_clf.get_params, file=log)
print(best_clf.get_params)
print("", file=log)

print("Tuned Extra Trees result:", file=log)
print(classifier_report(best_clf, y_test, y_pred), file=log)
print(classifier_report(best_clf, y_test, y_pred))
print("", file=log)

# Create a data frame of feature importance so that we
# can inspect later...
fi = pd.DataFrame.from_dict({'feature':X_test.columns.values, 'importance':best_clf.feature_importances_})
fi.sort_values(by='importance', ascending=False, inplace=True)
fi.to_csv(os.path.join(analytical,to_use+'-Feature Importance.csv.gz'), compression='gzip', index=False)

print("Feature Importances (5 Biggest):", file=log)
print(fi.head(5), file=log)
print(fi.head(5))

log.close()

exit()
