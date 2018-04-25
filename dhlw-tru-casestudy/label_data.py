import os
import pandas as pd
from collections import defaultdict
import argparse
import json

# Dictionary used to hold category with their subcategories
cat_dict = defaultdict(lambda: [])
# Category ordering
cat_order = []
# Dictionary used to hold which category each subcategory belongs to
categories = {}
# Dictionary used to hold which subcategory each subject belongs to
subjects = {}
# Used to store pairwise counts
sub_matrix = defaultdict(lambda:defaultdict(lambda: 0.0))
parent_matrix = defaultdict(lambda:defaultdict(lambda: 0.0))

# Reads in the data
def read_data(filename):	
	print("Reading in {}".format(filename))
	df = pd.read_csv(filename, skiprows = 1, names = ['doi', 'subjects', 'title'], delimiter="|")

	return df

# Parses categories into dictionary for easier access
def read_subcategories():
	filename = "categories.csv"
	print("Reading in {}".format(filename))
	df = pd.read_csv(filename, skiprows=1, names=['parent_cat', 'sub_cat'], delimiter=";")
	
	parent_cat = ""
	for i,r in df.iterrows():
		if not pd.isnull(r['parent_cat']):
			parent_cat = r['parent_cat'].strip()
			cat_order.append(parent_cat)
		if not pd.isnull(r['sub_cat']):
			categories[r['sub_cat'].strip()] = parent_cat
			cat_dict[parent_cat].append(r['sub_cat'])


# Parses aggregated subjects into dictionary for easier access
def read_aggregated_subjects(dhlw):
	filename = 'data/tru_aggregated_subjects.csv'
	if dhlw:
		filename = 'data/dhlw_aggregated_subjects.csv'

	print("Reading in {}".format(filename))
	df = pd.read_csv(filename, skiprows=1, names=['category','count','subject'], delimiter="|")
	
	for i,r in df.iterrows():
		subjects[r['subject']] = r['category']

# Writes out our finalized data with categories and subcategories
def categorize(df, dhlw):
	# Used to store our cleaned subject data
	categorized_data = pd.DataFrame(columns=['doi', 'title', 'parent_categories', 'subcategories'])
	# categorized_data_filename = 'data/tru_final.csv'
	categorized_data_filename = 'data/test_final.csv'
	if dhlw:
		categorized_data_filename = 'data/dhlw_final.csv'

	for i, r in df.iterrows():
		subjects_str = r['subjects']
		parent_cat = {}
		sub_cat = {}
		if not pd.isnull(subjects_str):
			ss = subjects_str.split(";")
			for s in ss:
				if s in subjects:
					curr = subjects[s]
					sub_cat[curr] = 1 # stores the subcategory
					parent_cat[categories[curr]] = 1 # stores the parent category of the subcategory

		else:
			subjects_str = ""

		categorized_data = categorized_data.append(pd.DataFrame({'title':r['title'], 'doi':r['doi'], 'parent_categories':','.join(parent_cat.keys()), 'subcategories':','.join(sub_cat.keys())}, index=[0]), ignore_index=True)

	categorized_data.to_csv(categorized_data_filename, sep='|')
	return categorized_data

# Generates the data matrix for visualization counts
def generate_matrix(categorized_data, dhlw):
	no_subcategory = 0 # number of documents that have no subjects
	one_subcategory = 0 # number of documents that have one subject
	two_more_subcategories = 0 # number of documents that have 2+ subjects

	for i, r in categorized_data.iterrows():
		# has no subcategories
		subcats = r['subcategories']
		if pd.isnull(subcats) or subcats == '':
			no_subcategory += 1
			continue

		sub_cat = subcats.split(",")
		if len(sub_cat) == 1: # has one subcategory, so makes the link to itself
			one_subcategory += 1
			curr = sub_cat[0]
			curr_parent = categories[curr]
			sub_matrix[curr][curr] += 1
			parent_matrix[curr_parent][curr_parent] += 1
		else: # has more than 1 subcategory, so half link for each direction
			two_more_subcategories += 1
			categories_done = defaultdict(lambda: defaultdict(lambda: 0))
			for m in range(len(sub_cat)):
				curr = sub_cat[m]
				curr_parent = categories[curr]
				for n in range(len(sub_cat)):
					curr2 = sub_cat[n]
					curr_parent2 = categories[curr2]
					# if link doesn't already exist, adds the link
					if (m!= n and categories_done[curr][curr2] == 0):
						# marks it as done
						categories_done[curr][curr2] = 1
						categories_done[curr2][curr] = 1
						# adds a half link in each direction
						sub_matrix[curr][curr2] += 1
						sub_matrix[curr2][curr] += 1
						parent_matrix[curr_parent][curr_parent2] += 1
						parent_matrix[curr_parent2][curr_parent] += 1

	print("Total number of documents: "+str(categorized_data.shape[0]))
	print("Number of documents that have no subjects: "+str(no_subcategory))
	print("Number of documents that have one subject: "+str(one_subcategory))
	print("Number of documents that have 2+ subjects: "+str(two_more_subcategories))

	# For global migration d3 visualization
	names = []
	regions = []
	matrix = []

	# Creates list of categories with subcategories and their corresponding indices
	index = 0
	for cat in cat_order:
		names.append(cat)
		regions.append(index)
		index += 1
		for s in cat_dict[cat]:
			names.append(s)
			index += 1

	region_index = -1

	# Create actual data matrix with counts
	for i in range(len(names)):
		mat = []
		m = names[i]

		for j in range(len(names)):
			n = names[j]

			# if m is a parent category
			if m in cat_dict:
				# if n is also a parent category, make the links; otherwise, make it 0
				if n in cat_dict:
					mat.append(parent_matrix[m][n])
					parent_matrix[n][m] = 0
				# otherwise, put a 0
				else:
					mat.append(0.0)
			# if m is a subcategory
			else:
				# if n is a parent category, need to add up all links with the subcategories in that parent category
				if n in cat_dict:
					count = 0
					for p in cat_dict[n]:
						if sub_matrix[m][p] == 0:
							count += sub_matrix[p][m]
						else:
							count += sub_matrix[m][p]
					mat.append(count)
				else:
					mat.append(sub_matrix[m][n])
					if m != n:
						sub_matrix[n][m] = 0

		matrix.append(mat)

	year_matrix = {"2005":matrix}

	data_filename = 'data/tru_data.json'
	if dhlw:
		data_filename = 'data/dhlw_data.json'

	data = {"names":names,"regions":regions,"matrix":year_matrix}
	with open(data_filename,'w') as outfile:
		json.dump(data, outfile)

		

def main():
	# Default is TRU
	filename = "data/tru_cleaned.csv"

	# Checks if the flag --dhlw is set; if so, changes to DHLW
	parser = argparse.ArgumentParser("Label data")
	parser.add_argument('--dhlw', dest='dhlw', action='store_true', default=False)
	results = parser.parse_args()
	if (results.dhlw):
		filename = "data/dhlw_cleaned.csv"

	df = read_data(filename)
	read_aggregated_subjects(results.dhlw)
	read_subcategories()
	categorized_data = categorize(df, results.dhlw)
	generate_matrix(categorized_data, results.dhlw)
	

if __name__ == '__main__':
	main()