# re-train random forest on new dataset with visual features by resnet


import pandas as pd
import pickle
import statistics
import sklearn.metrics as skm
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from joblib import dump, load
from sklearn.model_selection import PredefinedSplit
from sklearn.feature_selection import SelectPercentile, f_classif


pd.set_option("display.max.columns", None)

#load manual features & resnet features dataset
#df_feat = pd.read_pickle(r'E:\Babette\MasterThesis\Feature_extractor\ResNet_finetuned\manual_resnet_finetuned_features_dataset.pkl')
df_feat = pd.read_pickle(r'manual_resnet_finetuned_features_dataset.pkl')
df_feat.columns


df_train = df_feat[df_feat['set']=='train']
df_test = df_feat[df_feat['set']=='test']
df_train= df_train.drop(['set',], axis=1)
df_test= df_test.drop(['set',], axis=1)


#load GS labels
#df = pd.read_pickle(r'E:\Babette\MasterThesis\gs_125_warc_files_comb.pkl')
df = pd.read_pickle(r'gs_125_warc_files_comb.pkl')
#df = df[filter]


label=[]
label_id= []

for index, row in df.iterrows():
    if row['id'] in df_train['id']:
        label_id.append(row['id'])
        if row['label']== 'genuine':
            label.append(1)
        else:
            label.append(0)

len(label)
len(label_id)
len(df_train)
#test set
label_test=[]
label_test_id= []

for index, row in df.iterrows():
    if row['id'] in df_test['id']:
        label_test_id.append(row['id'])
        if row['label']== 'genuine':
            label_test.append(1)
        else:
            label_test.append(0)

len(label_test)
len(label_test_id)
len(df_train)

#df_train, df_test, label, label_test = train_test_split( df_train, label, test_size=0.20, random_state=42)


#simple mean imputation
for x in df_test.iloc[:,1:27].columns:
        df_test[x].fillna(df_test[x].mean() , inplace = True)

for x in df_train.iloc[:,1:27].columns:
        df_train[x].fillna(df_train[x].mean() , inplace = True)


# define test val split:
#v_ids= np.load(r'E:\Babette\MasterThesis\Classifier_Dresden\all_val_ids.npy')
v_ids= np.load(r'all_val_ids.npy')

split=[]
#va=[]
for index, row in df_train.iterrows():
    if row['id'] in v_ids:
        split.append(0)
#        va.append(False)
    else: 
        split.append(-1)
#        va.append(True)


ps = PredefinedSplit(split)

df_test= df_test.drop(['id',], axis=1)
df_train= df_train.drop(['id',], axis=1)

n_classes=2
target_names= ['Layout', 'Genuine']


#--------------------------------------------------------------------------------------------------------------------------------------#
# train random forest classifier with grid search param optimization ###################################################################
#--------------------------------------------------------------------------------------------------------------------------------------#

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 9)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]


random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
               
print(random_grid)

rf= RandomForestClassifier()
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = ps, verbose=2, random_state=42, n_jobs = -1)
rf_random.fit(df_train, label)

print('Best parameter setting found:')
print(rf_random.best_params_)
best_grid = rf_random.best_estimator_


y_pred = best_grid.predict(df_test)

# Results of default RF model Prediction
print('Evaluation on test set:')
print('Acurracy' + str(accuracy_score(label_test, y_pred)))
print(classification_report(label_test, y_pred, target_names=target_names))
print(classification_report(label_test, y_pred, target_names=target_names, digits=4))
print(confusion_matrix(label_test, y_pred, labels=range(n_classes)))

dump(best_grid, r'heuristic_resnet_finetuned_rf.joblib', protocol=4) 



importances = best_grid.feature_importances_
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(10):
    print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))
    

#----------------------------------------------------------------------------------------------------------------------#
#Only visual features
#----------------------------------------------------------------------------------------------------------------------#
print('only visual features')
#only use visual features
df_train_vis=df_train.iloc[:,26:2074]
df_test_vis=df_test.iloc[:,26:2074]

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]


random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
               
print(random_grid)

rf= RandomForestClassifier()
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = ps, verbose=2, random_state=42, n_jobs = -1)
rf_random.fit(df_train_vis, label)

print('Best parameter setting found:')
print(rf_random.best_params_)
best_grid_vis = rf_random.best_estimator_
#{'n_estimators': 522, 'min_samples_split': 5, 'min_samples_leaf': 1, 'max_features': 'sqrt', 'max_depth': 60, 'bootstrap': False}

y_pred = best_grid_vis.predict(df_test_vis)

# Results of  RF model Prediction
print('Evaluation on test set:')
print('Acurracy' + str(accuracy_score(label_test, y_pred)))
print(classification_report(label_test, y_pred, target_names=target_names))
print(classification_report(label_test, y_pred, target_names=target_names, digits=4))
print(confusion_matrix(label_test, y_pred, labels=range(n_classes)))


#save model
#dump(best_grid, r'E:\Babette\MasterThesis\Feature_extractor\ResNet_imagenet\rf_classifier\resnet_finetuned_rf.joblib') 
#model= best_grid( r'E:\Babette\MasterThesis\Feature_extractor\ResNet_imagenet\rf_classifier\resnet_finetuned_rf.joblib') 

dump(best_grid_vis, r'resnet_finetuned_rf.joblib', protocol=4) 

importances = best_grid_vis.feature_importances_
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(0,11):
    print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

#Save wrongly predicted ids

false=[]
for i in range(len(y_pred)):
    if y_pred[i]!= label_test[i]:
        false.append(label_test_id[i])
len(false)

#np.save(r'E:\Babette\MasterThesis\Feature_extractor\ResNet_imagenet\rf_classifier\resnet_false_id.npy', false)


print('Script finished successfully')



#----------------------------------------------------------------------------------------------------------------------------------------------
#feature selection
#---------------------------------------------------------------------------------------------------------------------------------------------
print('Feature selection cfs')
# from skfeature.function.statistical_based import CFS
# sel= CFS.cfs(df_train.to_numpy(), label)
# len(sel) 
# 18
# sel
#array([  15,   10,   12, 1009,   21,    5,  451,   24,  654,   14, 1284, 6,  593,   16,  714, 1100,    8,  364])

sel= [15, 10, 12, 1009, 21,  5,  451,   24,  654,   14, 1284, 6,  593,   16,  714, 1100,    8,  364]
df_test_sel = df_test.iloc[:, sel]
df_train_sel = df_train.iloc[:, sel]

cols=df_test.columns[[15, 10, 12, 1009, 21,  5,  451,   24,  654,   14, 1284, 6,  593,   16,  714, 1100,    8,  364]]
df_train[cols].columns
print(df_train_sel.columns)
print(df_test_sel.columns)
print(df_train.columns)
print(df_test.columns)
df_test_sel.columns
df_train_sel.shape


# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]


random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
               
print(random_grid)

rf= RandomForestClassifier()

rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = ps, verbose=2, random_state=42, n_jobs = -1)
rf_random.fit(df_train_sel, label)

print('Best parameter setting found:')
print(rf_random.best_params_)
best_grid_sel = rf_random.best_estimator_
#{'n_estimators': 2000, 'min_samples_split': 2, 'min_samples_leaf': 2, 'max_features': 'auto', 'max_depth': 90, 'bootstrap': True}


y_pred = best_grid_sel.predict(df_test_sel)

# Results of  RF model Prediction
print('Evaluation on test set:')
print('Acurracy' + str(accuracy_score(label_test, y_pred)))
print(classification_report(label_test, y_pred, target_names=target_names))
print(classification_report(label_test, y_pred, target_names=target_names, digits=4))
print(confusion_matrix(label_test, y_pred, labels=range(n_classes)))


#save model
#dump(best_grid, r'E:\Babette\MasterThesis\Feature_extractor\ResNet_finetuned\rf_classifier\resnet_sel_rf.joblib') 
#model= best_grid( r'E:\Babette\MasterThesis\Feature_extractor\ResNet_finetuned\rf_classifier\resnet_sel_rf.joblib') 
dump(best_grid_sel, r'resnet_finetuned_rf_sel.joblib', protocol=4) 

importances = best_grid_sel.feature_importances_
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(0,11):
    print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))





# Feature selection
print('Feat sel with percentile')
s = SelectPercentile(f_classif, percentile=10)
s.fit(df_train, label)
df_train_sel = df_train.iloc[:, s.get_support()]
df_test_sel = df_test.iloc[:, s.get_support()]



# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]


random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
               
print(random_grid)

rf= RandomForestClassifier()

rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = ps, verbose=2, random_state=42, n_jobs = -1)
rf_random.fit(df_train_sel, label)

print('Best parameter setting found:')
print(rf_random.best_params_)
best_grid_sel = rf_random.best_estimator_
#{'n_estimators': 2000, 'min_samples_split': 2, 'min_samples_leaf': 2, 'max_features': 'auto', 'max_depth': 90, 'bootstrap': True}


y_pred = best_grid_sel.predict(df_test_sel)

# Results of  RF model Prediction
print('Evaluation on test set:')
print('Acurracy' + str(accuracy_score(label_test, y_pred)))
print(classification_report(label_test, y_pred, target_names=target_names))
print(classification_report(label_test, y_pred, target_names=target_names, digits=4))
print(confusion_matrix(label_test, y_pred, labels=range(n_classes)))


#save model
#dump(best_grid, r'E:\Babette\MasterThesis\Feature_extractor\ResNet_finetuned\rf_classifier\resnet_finetuned_rf_sel_perc.joblib') 
#model= load( r'E:\Babette\MasterThesis\Feature_extractor\ResNet_finetuned\rf_classifier\resnet_finetuned_rf_sel_perc.joblib') 
dump(best_grid_sel, r'resnet_finetuned_rf_sel_perc.joblib', protocol=4) 

importances = best_grid_sel.feature_importances_
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(0,11):
    print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))
