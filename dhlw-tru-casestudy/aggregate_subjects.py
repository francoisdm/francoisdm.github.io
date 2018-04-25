import re
import pandas as pd
import argparse

categories = {}
sorted_categories = {}
already_used = {}
categories_used = {}

# Creates a Python regex from the words/expressions
def create_python_regex(exp):
	final_list = []
	str = "(^|\s|-|$)("

	exp = exp.strip()

	l = exp.split(" ")
	for w in l:
		w = w.replace('"', '') # take out quotation marks
		w = w.replace("*", "([a-zA-Z]*)")
		w = w.replace("(", "")
		w = w.replace(")", "")
		if w == "OR":
			str += ")(^|\s|-|$)|(^|\s|-|$)("
		elif w == "AND":
			str += ")(^|\s|-|$)"
			final_list.append(str)
			str = "(^|\s|-|$)("
		else:
			if str[len(str)-1] != "(":
				str += " "
			str += w
	str += ")(^|\s|-|$)"
	final_list.append(str)

	return final_list

# Reads in the words/expressions for subcategories
def read_csv():
	filename = 'wordphrase.csv'
	print("Reading in {}".format(filename))
	cols = ['category','exp','exclude','num']
	df = pd.read_csv(filename, skiprows = 1, names = cols, delimiter=",")

	curr_cat = ""
	for i,r in df.iterrows():
		cat = r[0]
		if not pd.isnull(cat):
			curr_cat = cat
			categories[cat] = []
		exp = create_python_regex(r[1])
		exclude = ""
		if not pd.isnull(r[2]):
			exclude = create_python_regex(r[2])
		
		categories[curr_cat].append([exp, exclude])

def read_subject_csv(dhlw):
	filename = 'data/tru_subject_counts_after_ignore.csv'
	if dhlw:
		filename = 'data/dhlw_subject_counts_after_ignore.csv'
	print("Reading in {}".format(filename))
	cols = ['count','subject']
	df = pd.read_csv(filename, skiprows = 1, names=cols, delimiter=";")

	for k,v in categories.items():
		if k not in sorted_categories:
			sorted_categories[k] = []

			for v_t in v:
				include = v_t[0]
				exclude = v_t[1]
				for i,r in df.iterrows():
					cont = True
					s = r['subject']
					for i in include:
						regex = re.compile(i)
						if not regex.search(s):
							cont = False
							break
					if cont:
						for e in exclude:
							regex = re.compile(e)
							if regex.search(s):
								cont = False
								break
					if cont and s not in already_used:
						sorted_categories[k].append([s,r['count']])
						already_used[s] = 1

def write_data(dhlw):
	# Counts of how many categories were used and subjects/counts included
	total_categories_used = 0
	total_subjects_included = 0
	total_counts_included = 0

	filename = "data/tru_aggregated_subjects.csv"
	if dhlw:
		filename = "data/dhlw_aggregated_subjects.csv"

	new_df = pd.DataFrame(columns=['category','subject','count'])
	for k,v in sorted_categories.items():
		total_categories_used += 1
		for s in v:
			new_df = new_df.append(pd.DataFrame({'category':k,'subject':s[0],'count':s[1]}, index=[0]), ignore_index=True);
			total_counts_included += s[1]
			total_subjects_included += 1

	new_df.to_csv(filename, sep='|')

	print("Total number of subcategories used: " + str(total_categories_used))
	print("Total number of subjects used: " + str(total_subjects_included))
	print("Total number of counts used: " + str(total_counts_included))

def main():
	# Checks if the flag --dhlw is set; if so, changes to DHLW
	parser = argparse.ArgumentParser("Count subjects")
	parser.add_argument('--dhlw', dest='dhlw', action='store_true', default=False)
	results = parser.parse_args()

	read_csv()
	read_subject_csv(results.dhlw)
	write_data(results.dhlw)

if __name__ == '__main__':
	main()