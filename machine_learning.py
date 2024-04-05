import pickle

import joblib
import pandas as pd
import mysql.connector
import csv

from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

con = mysql.connector.connect(host='localhost', user='root',password='aak20f031', database='dbms_project')
df = pd.read_sql_query('''SELECT * FROM products''', con=con)


print(df)

X = df.iloc[:, [False,False,False,False,True,True,True,False,False,True,True,True,False,False,True]]
Y = df.iloc[:, [False,False,False,False,False,False,False,True,False,False,False,False,False,False,False]]



num_columns = X.select_dtypes(exclude=['object']).columns


cat_columns = X[["Category","Brand"]].columns


minmaxscaler = Pipeline([['scale', MinMaxScaler()]])
scale_columntransformer = ColumnTransformer([('scale', minmaxscaler, num_columns)])
scaled_columns = scale_columntransformer.fit(X)
joblib.dump(scaled_columns,'minmaxscaler')
scaled_data = pd.DataFrame(scaled_columns.transform(df))
print(scaled_data)

encoding_pipeline = Pipeline([('onehot', OneHotEncoder())])
preprocess_pipeline = ColumnTransformer([('categorical', encoding_pipeline, cat_columns)])
clean = preprocess_pipeline.fit(X)

joblib.dump(clean,'onehotencoder')
encoded_data = pd.DataFrame(clean.transform(X).todense())
clean_data = pd.concat([scaled_data, encoded_data], axis=1 , ignore_index = True)
x = clean_data


print(x.columns)

train_X_smot, test_X, train_Y_smot, test_y = train_test_split(x, Y, test_size = 0.3, random_state = 21)

from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors = 21)
knn.fit(train_X_smot,train_Y_smot)
y_pred = knn.predict(test_X)
print(classification_report(test_y,y_pred))

y_pred_train = knn.predict(train_X_smot)
print(classification_report(train_Y_smot,y_pred_train))


#KNN HyperParametre

leaf_size = list(range(1,20))
n_neighbors = list(range(1,20))
p=[1,2]
hyperparameters = dict(leaf_size=leaf_size, n_neighbors=n_neighbors, p=p)
knn_2 = KNeighborsClassifier()
clf = GridSearchCV(knn_2, hyperparameters, cv=3,verbose=3,n_jobs=-1)
best_model = clf.fit(train_X_smot,train_Y_smot)
y_pred = best_model.predict(test_X)
print(classification_report(test_y,y_pred))

print(test_X)

pickle.dump(best_model,open('bestknn.pkl','wb'))