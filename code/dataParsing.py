import os
import json
import gzip
import pandas as pd
import numpy as np
from urllib.request import urlopen
from IPython.display import Image as IPImage
from IPython.core.display import HTML 
import math
import sys

def loadMetaData(path):
	data = []
	with gzip.open(path) as f:
		for i,l in enumerate(f):
			if i%1000==0:
				print("======{}======".format(i))
				print("Number of valid review data:{}".format(len(data)))	
			if i%100 == 0:
				d = json.loads(l.strip())
				new_d = dict()
				valid = True
				for k in ['asin', 'overall']:
					if k in d:
						new_d[k] = d[k]
					else:
						valid = False
						break
				if valid:
					data.append(new_d)
			
	return pd.DataFrame.from_dict(data)

def loadProductData(path):
	data = []
	with gzip.open(path) as f:
		for i,l in enumerate(f):
			if i%1000==0:
				print("======{}======".format(i))
				print("Number of valid product data:{}".format(len(data)))	
			if i%10 == 0:
				d = json.loads(l.strip())
				new_d = dict()
				valid = True
				for k in ['title', 'description', 'brand', 'asin', 'image']:
					if k in d:
						if k=="title" and 'getTime' in d[k]: 
							valid = False
							break
						if k=="description" and d[k]=="":
							valid = False
							break
						new_d[k] = d[k]
					else:
						valid = False
						break
				if valid:
					data.append(new_d)
		
	return pd.DataFrame.from_dict(data)

def getAverageRating(asin, review_df):
	indices = review_df.asin==asin
	return np.sum(indices), review_df[indices].overall.mean()



if __name__ == '__main__':
# category = ["All_Beauty","Sports_and_Outdoors","Home_and_Kitchen","Electronics","Clothing_Shoes_and_Jewelry"][4]
	category = str(sys.argv[1])
	df = loadProductData(path='../data/meta_{}.json.gz'.format(category))
	df = df.fillna('')
	review_df = loadMetaData(path='../data/{}.json.gz'.format(category))

	print("Total number of products: {}".format(len(df)))
	print("Total number of reviews: {}".format(len(review_df)))
	drop_asin = []
	for idx,productId in enumerate(df.asin):
		if idx % 1000 == 0:
			print("Finished: {:.2f} in {} of products".format(idx/len(df),len(df)))
		nReviews, averageRating = getAverageRating(asin=productId, review_df=review_df)
		if nReviews!=0:
			df.loc[idx,"rating"] = averageRating
			df.loc[idx,"nReviews"] = nReviews
		else:
			drop_asin.append(productId)
	df = df[ [ idx not in drop_asin for idx in df.asin] ]
	df.to_csv("../data/parsedData/{}.csv".format(category),index=False)
	print("Finish:{}".format(len(df)))

