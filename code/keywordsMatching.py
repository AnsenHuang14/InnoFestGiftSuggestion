import spacy
import pandas as pd
import numpy as np
import ast
from collections import Counter
from string import punctuation

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
	output_url = []
	for idx in data.index:
		productURL = "https://www.amazon.com/dp/"+data.loc[idx,"asin"]
		output_url.append(productURL)
	return output_url
# inputKeywords = "men eyes fat beautiful"
# searchItemByKeywords(inputKeywords)