import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import json

# These are set parameters
tru_url = "https://www.osti.gov/search/semantic:%22TRU%20waste%22%20OR%20%22transuranic%20waste%22%20OR%20WIPP%20OR%20%22Waste%20Isolation%20Pilot%20Plant%22/product-type:Journal%20Article,%20Technical%20Report/page:"
dhlw_url = "https://www.osti.gov/search/semantic:%22DHLW%22%20OR%20%22defense%20HLW%22%20OR%20%22defense%20high%20level%20waste%22%20OR%20%22defense%20high-level%20waste%22/product-type:Journal%20Article,%20Technical%20Report/page:"
tru_pages = 947
dhlw_pages = 117

# Lists used to contain failed URLs
pages_failed = []
doc_urls_failed = []

# Scrapes the page corresponding to the document
def scrape_doc(df, doc_html):
	title = ""
	doi = ""
	subjects = []

	doi_html = doc_html.find('a', class_='misc doi-link')
	if doi_html is not None:
		doi = doi_html.get_text().strip()

	title_html = doc_html.find('h2', class_='title')
	if title_html is not None:
		title = title_html.get_text().strip()
		ahref_html = title_html.find('a', href=True)
		if ahref_html is not None:
			doc_url = 'https://www.osti.gov'+(ahref_html)['href']
			try:
				doc_page = requests.get(doc_url)
				doc_soup = BeautifulSoup(doc_page.content, 'html.parser')
				for sub_html in doc_soup.find_all('span', class_='subject'):
					subjects.append(sub_html.get_text().strip())
			except requests.exceptions.RequestException:
				print("Failed doc")
				doc_urls_failed.append(doc_url)

	df = df.append(pd.DataFrame({'title':title, 'doi':doi, 'subjects':','.join(subjects)}, index=[0]), ignore_index=True)

# Scrapes the search result page i
def scrape_page(df, base_url, i):
	print("Scraping page"+str(i))
	url = base_url + str(i)

	try:
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')

		for doc_html in soup.find_all('div', class_='article item document'):
			t0 = time.time()
			scrape_doc(df, doc_html)

			response_delay = time.time() - t0
			time.sleep(response_delay)
			

	except requests.exceptions.RequestException:
		print("Failed page")
		pages_failed.append(i)

def main():
	# Default search is TRU
	base_url = tru_url
	csv_filename = "data/tru.csv"
	page_range = tru_pages

	# Checks if the flag --dhlw is set; if so, changes search to DHLW
	parser = argparse.ArgumentParser("Web scrape OSTI.gov")
	parser.add_argument('--dhlw', dest='dhlw', action='store_true', default=False)
	results = parser.parse_args()
	if (results.dhlw):
		base_url = dhlw_url
		csv_filename = "data/dhlw.csv"
		page_range = dhlw_pages

	df = pd.DataFrame(columns=['title', 'doi', 'subjects'])
	
	# Scrapes all the pages for the corresponding search
	for i in range(1, page_range+1):
		scrape_page(df, base_url, i)

	# Writes the data to the corresponding filename
	df.to_csv(csv_filename, sep=';')

	# Search result pages that failed and URLs for documents that failed
	with open("data/pages_failed.txt", "w") as outfile:
		json.dump(pages_failed, outfile)
	with open("data/doc_urls_failed.txt", "w") as outfile:
		json.dump(doc_urls_failed, outfile)


if __name__ == '__main__':
	main()