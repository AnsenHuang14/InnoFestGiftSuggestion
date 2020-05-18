# Dependencies
from flask import Flask, request, jsonify
from sklearn.externals import joblib
import traceback
import pandas as pd
import numpy as np
import spacy
import ast
from collections import Counter
from string import punctuation


# Your API definition
app = Flask(__name__)
nlp = spacy.load("en_core_web_lg")
print("Model loaded")

def calculateSimilarity(inputKeywords, productKeywords):
    productKeywords = " ".join(ast.literal_eval(productKeywords))
    productTokens = nlp(productKeywords)
    inputTokens = nlp(inputKeywords.lower())
    highestScore, mostSimilarWord = [0]*len(inputTokens), [""]*len(inputTokens)

    for product_t in productTokens:
        for idx,input_t in enumerate(inputTokens):
            if product_t.has_vector:
                score = product_t.similarity(input_t)
                if score>highestScore[idx]:
                    highestScore[idx] = score
                    mostSimilarWord[idx]= product_t.text+"/"+input_t.text
    return np.mean(highestScore), mostSimilarWord


def searchItemByKeywords(inputKeywords, category="ALL_Beauty", n=5):
    category = category+"WithKeyWords"
    path = "../data/parsedData/{}.csv".format(category)
    data = pd.read_csv(path) 
    for idx in data.index:
        productKeywords = data.loc[idx,"keywords"]
        score, words = calculateSimilarity(inputKeywords, productKeywords)
        data.loc[idx,"score"] = score

    data = data.sort_values(by=['score'], ascending=False).reset_index(drop=True)[0:n]
    output_data = []
    for idx in data.index:
        productURL = "https://www.amazon.com/dp/"+data.loc[idx,"asin"]
        d = {"title":data.loc[idx,"title"], "imagesUrl":data.loc[idx,"image"], "url":productURL, "nReviews":data.loc[idx,"nReviews"], "rating":data.loc[idx,"rating"]}
        output_data.append(d)
    return output_data

@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.json
    inputKeywords = " ".join(input_data["keywords"])
    category = input_data["category"]
    numberOfItems = input_data["n"]

    output_data = searchItemByKeywords(inputKeywords, category, n=numberOfItems)
    return jsonify(output_data)

if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 8080 # If you don't provide any port the port will be set to 12345


    app.run(port=port, debug=True)

