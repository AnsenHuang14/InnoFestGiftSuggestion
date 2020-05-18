import pandas as pd
import numpy as np
import spacy
import ast
from collections import Counter
from string import punctuation

nlp = spacy.load("en_core_web_lg")

category = ["ALL_Beauty","Sports_and_Outdoors","Home_and_Kitchen","Electronics","Clothing_Shoes_and_Jewelry"][4]
path = "../data/parsedData/{}.csv".format(category)
data = pd.read_csv(path) 

def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN'] # 1
    doc = nlp(text.lower())
    for token in doc:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            result.append(token.text)
    result = str(list(set(result)))
    return result


# filter out items by number of reviews and ratings
nReviewsThreshold = data.quantile(.9)["nReviews"]
data = data[data.nReviews > nReviewsThreshold]
data = data.sort_values(by=['rating'], ascending=False).reset_index(drop=True)[0:100]
print("Number of rows after filtering: {}".format(len(data)))
print(data.head())
print("==="*30)

# convert keywords
for idx in data.index:
	row = data.iloc[idx]
	text = " ".join([row.title]+ast.literal_eval(row.description))
	keywords = get_hotwords(text)
	data.loc[idx,"keywords"] = keywords

data.to_csv("../data/parsedData/{}WithKeyWords.csv".format(category),index=False)
print("Finish:{}".format(len(data)))