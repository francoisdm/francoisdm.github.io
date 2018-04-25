import re
import pandas as pd
import argparse

regexes = []
not_ignored = {}

# Reads in condition and creates a Python regex from it
def create_python_regex(exp, condition):
	str = "(^|\s|-|$)("
	if condition == "exact":
		str = "^("

	exp = exp.strip()
	exp = exp.replace('"', '') # take out quotation marks
	if exp[len(exp)-1] == '*':
		exp = exp[:-1]
		exp = exp.replace("*", "([a-zA-Z]*)")
		exp += "([a-zA-Z]*))$"
		str += exp
	elif '*' in exp:
		exp = exp.replace("*", "([a-zA-Z]*)")
		str += exp
		if condition == "exact":
			str += ")$"
		else:
			str += ")(^|\s|-|$)"
	else:
		str += exp
		if condition == "exact":
			str += ")$"
		else:
			str += ")(^|\s|-|$)"
	return str

# Reads in the words/expressions to be ignored
def read_csv():
	filename = "wordphrase_ignore.csv"
	print("Reading in {}".format(filename))
	cols = ['exp', 'condition']
	df = pd.read_csv(filename, skiprows=1, names=cols, delimiter=",")

	for i,r in df.iterrows():
		exp = create_python_regex(r['exp'], r['condition'])
		regexes.append(exp)

# Reads in the list of subjects
def read_subject_csv(dhlw):
	filename = "data/tru_subject_counts.csv"
	if dhlw:
		filename = "data/dhlw_subject_counts.csv"
		
	print("Reading in {}".format(filename))
	cols = ['count', 'subject']
	df = pd.read_csv(filename, skiprows=1, names=cols, delimiter=";")

	total_subjects_before = 0
	total_counts_before = 0

	for i,r in df.iterrows():
		total_counts_before += r['count']
		total_subjects_before += 1

		subject = r['subject']

		found = False
		for reg in regexes:
			regex = re.compile(reg)
			if regex.search(subject):
				found = True
				break
		if not found:
			not_ignored[subject] = r['count']

	print("Total number of subjects before cleaning: "+str(total_subjects_before))
	print("Total number of counts before cleaning: "+str(total_counts_before))

# Writes the subject data to a CSV file after removing subjects that need to be ignored
def write_data(dhlw):
	filename = "data/tru_subject_counts_after_ignore.csv"
	if dhlw:
		filename = "data/dhlw_subject_counts_after_ignore.csv"

	total_subjects_after = 0
	total_counts_after = 0

	new_df = pd.DataFrame(columns=['subject', 'count'])
	for k,v in not_ignored.items():
		new_df = new_df.append(pd.DataFrame({'subject':k,'count':v}, index=[0]), ignore_index=True);
		total_counts_after += v
		total_subjects_after += 1

	new_df.to_csv(filename, sep=';')

	print("Total number of subjects after cleaning: "+str(total_subjects_after))
	print("Total number of counts after cleaning: "+str(total_counts_after))

def main():
	# Default is TRU; checks if the flag --dhlw is set; if so, changes to DHLW
	parser = argparse.ArgumentParser("Count subjects")
	parser.add_argument('--dhlw', dest='dhlw', action='store_true', default=False)
	results = parser.parse_args()

	read_csv()
	read_subject_csv(results.dhlw)
	write_data(results.dhlw)


if __name__ == '__main__':
	main()