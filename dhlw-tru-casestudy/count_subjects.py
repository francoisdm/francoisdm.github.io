import os
import pandas as pd
from collections import defaultdict
import argparse
from pattern.text.en import singularize

# Dictionary used to store subject counts
subject_counts = defaultdict(lambda:0)

# Reads in the data
def read_data(filename):	
	print("Reading in {}".format(filename))
	df = pd.read_csv(filename, skiprows = 1, names = ['doi', 'subjects', 'title'], delimiter="|")

	return df

def sort(df, dhlw):
	# Used to store our cleaned subject data
	cleaned_data = pd.DataFrame(columns=['doi', 'subjects', 'title'])
	cleaned_data_filename = 'data/tru_cleaned.csv'
	if dhlw:
		cleaned_data_filename = 'data/dhlw_cleaned.csv'

	blank_subjects = 0 # number that OSTI listed as blank...
	removed_subjects = 0 # number of subjects that were all digits, dots, *, -, and whitespaces
	#p = nltk.PorterStemmer()

	for i,r in df.iterrows():
		subjects_str = r['subjects']
		if not pd.isnull(subjects_str):
			subjects = subjects_str.split(";")

			cleaned_subjects = []
			for s in subjects:
				cleaned_s = s.lower().strip() # first cleans by removing whitespace and then putting it all to lowercase
				cleaned_s = cleaned_s.lstrip('0123456789.-* ') # removes all digits, dots, dashes, and spaces from the start

				if cleaned_s != "":
					# converts the last word in the subject to be singular
					cleaned_s_words = cleaned_s.split(" ")
					cleaned_s_words[len(cleaned_s_words)-1] = singularize(cleaned_s_words[len(cleaned_s_words)-1])
					cleaned_s = " ".join(cleaned_s_words)

					subject_counts[cleaned_s] += 1
					cleaned_subjects.append(cleaned_s)
				else:
					if s == "":
						blank_subjects += 1
					else:
						removed_subjects += 1

			subjects_str = ';'.join(cleaned_subjects)
		else:
			subjects_str = ""

		cleaned_data = cleaned_data.append(pd.DataFrame({'title':r['title'], 'doi':r['doi'], 'subjects':subjects_str}, index=[0]), ignore_index=True)

	cleaned_data.to_csv(cleaned_data_filename, sep='|')

	print("Blank subjects: " + str(blank_subjects))
	print("Removed subjects: " + str(removed_subjects))

# Write the output subject counts to a new file
def write_files(dhlw):
	filename = "data/tru_subject_counts.csv"
	if dhlw:
		filename = "data/dhlw_subject_counts.csv"

	df = pd.DataFrame(columns=['subject','count'])

	for k, v in sorted(subject_counts.items(), key=lambda kv: kv[1], reverse=True):
		df = df.append(pd.DataFrame({'subject':k,'count':v}, index=[0]), ignore_index=True);

	df.to_csv(filename, sep=';')

def main():
	# Default is TRU
	filename = "data/tru.csv"

	# Checks if the flag --dhlw is set; if so, changes to DHLW
	parser = argparse.ArgumentParser("Count subjects")
	parser.add_argument('--dhlw', dest='dhlw', action='store_true', default=False)
	results = parser.parse_args()
	if (results.dhlw):
		filename = "data/dhlw.csv"

	df = read_data(filename)
	sort(df, results.dhlw)
	write_files(results.dhlw)
	

if __name__ == '__main__':
	main()