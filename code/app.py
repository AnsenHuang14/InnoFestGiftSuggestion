# Dependencies
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import spacy
import ast
from amazonImageCrawler import *
from numpy import dot
from numpy.linalg import norm


 # flask run --port=5000 --host=0.0.0.0

# Your API definition
app = Flask(__name__)
nlp = spacy.load("en_core_web_lg")
print("Model loaded")

def preprocessAllKeywords():
    keywordsTable = dict()
    for category in ["All_Beauty","Sports_and_Outdoors","Home_and_Kitchen","Electronics","Clothing_Shoes_and_Jewelry"]:
        path = category+"_WithKeyWords"
        path = "../data/parsedData/{}.csv".format(path)
        data = pd.read_csv(path) 
        subTable = dict()
        for idx in data.index:
            productKeywords = data.loc[idx,"keywords"]
            for k in ast.literal_eval(productKeywords):
                if k not in subTable:
                    subTable[k] = nlp(k)[0]
        keywordsTable[category] = subTable
    return keywordsTable

keywordsTable = preprocessAllKeywords()
print("keywordsTable constructed")


def preprocessUserKeywords(inputKeywords):
    inputTokens = nlp(inputKeywords.lower())
    return inputTokens

def calculateSimilarity(category, inputTokens, productKeywords):
    productKeywords = ast.literal_eval(productKeywords)
    highestScore, mostSimilarWord = [0]*len(inputTokens), [""]*len(inputTokens)
    for product_k in productKeywords:
        product_t = keywordsTable[category][product_k]
        for idx,input_t in enumerate(inputTokens):
            if product_t.has_vector:
                score = dot(product_t.vector, input_t.vector)/(norm(product_t.vector)*norm(product_t.vector))
                # score = product_t.similarity(input_t)
                if score>highestScore[idx]:
                    highestScore[idx] = score
                    mostSimilarWord[idx]= product_t.text+"/"+input_t.text
    return np.mean(highestScore), mostSimilarWord


def searchItemByKeywords(inputKeywords, category, n):
    path = category+"_WithKeyWords"
    path = "../data/parsedData/{}.csv".format(path)
    data = pd.read_csv(path) 
    for idx in data.index:
        productKeywords = data.loc[idx,"keywords"]
        score, words = calculateSimilarity(category, inputKeywords, productKeywords)
        data.loc[idx,"score"] = score

    data = data.sort_values(by=['score'], ascending=False).reset_index(drop=True)
    output_data = []
    numberOfProduct = 0
    for idx in data.index:
        productURL = "https://www.amazon.com/dp/"+data.loc[idx,"asin"]
        imagesUrl =  data.loc[idx,"image"]
        if str(imagesUrl) == "nan": continue
        d = {"title":data.loc[idx,"title"], "imagesUrl":imagesUrl, "url":productURL, "nReviews":data.loc[idx,"nReviews"], "rating":data.loc[idx,"rating"]}
        output_data.append(d)
        numberOfProduct += 1
        if numberOfProduct >= n: break
    return output_data


@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.json
    print("Input: ",input_data)
    inputKeywords = " ".join(input_data["keywords"])
    category = input_data["category"]
    numberOfItems = input_data["n"]
    inputKeywords = preprocessUserKeywords(inputKeywords)
    output_data = searchItemByKeywords(inputKeywords, category, n=numberOfItems)
    return jsonify(output_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=port, debug=False)

