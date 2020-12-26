import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pylab as pl
from sklearn.ensemble import RandomForestClassifier
import pickle

df = pd.read_csv('dataset/indian_food.csv')
df = df.drop(df[df.flavor_profile == '-1'].index)
df = df.drop(df[df.prep_time == -1].index)
df = df.drop(df[df.cook_time == -1].index)
df = df.drop(df[df.region == '-1'].index)
df = df.dropna()

cdf = df[['diet', 'prep_time', 'cook_time', 'flavor_profile', 'course', 'region', 'name']]
cdf = pd.get_dummies(cdf, columns=['diet', 'flavor_profile', 'course'])

msk = np.random.rand(len(df)) < 0.8
train = cdf[msk]
test = cdf[~msk]

model = RandomForestClassifier()

X = train.drop(['region', 'name'], axis=1)
y = train[['region', 'name']]

model.fit(X, y)

example = {
    'prep_time': [17],
    'cook_time': [70],
    'diet_non vegetarian': [1],
    'diet_vegetarian': [0],
    'flavor_profile_bitter': [0],
    'flavor_profile_sour': [0],
    'flavor_profile_spicy': [1],
    'flavor_profile_sweet': [0],
    'course_dessert': [0],
    'course_main course': [0],
    'course_snack': [1],
    'course_starter': [0]
}
example_df = pd.DataFrame(example)
result = model.predict(example_df)
print(result)

filename = 'indian_kitchen.sav'
pickle.dump(model, open(filename, 'wb'))
