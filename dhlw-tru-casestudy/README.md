# DHLW/TRU Case Study

This repository contains the code to scrape, process, and analyze data for an analysis of OST data for DHLW and TRU.

## Getting Started

### Prerequisites

You will need to install the relevant libraries used. First ensure that you have [pip](https://pip.pypa.io/en/stable/installing/) installed.

Then, run the following to ensure that you have all the relevant libraries installed:
```
pip install
```

All the code below was run using Python3 with the exception of `count_subjects.py`.

## Data Collection

### Scraping OSTI.gov

The data for this case study was collected by scraping data from [OSTI](https://osti.gov).

To scrape the TRU search results, simply run:
```
py -3 scrape_ost.py
```

To scrape the DHLW search results, run:
```
py -3 scrape_ost.py --dhlw
```

Keep in mind that the URLS for the two search results as well as the number of search result pages are statically defined in `scrape_ost.py` as the constants `tru_url`, `dhlw_url`, `tru_pages`, and `dhlw_pages`. Before running the code, please verify the URLs for the search results and change the number of pages of results as needed.

### Accessing the Data

After running the web scraping code above, the data should be accessible in the `data` folder through either `tru.csv` or `dhlw.csv`. Sometimes the URL calls will fail; these are also in the `data` folder under `pages_failed.txt` and `doc_urls_failed.txt`. You can either manually enter these in failed URLs into your browser after or run API calls on them later.

## Data Cleaning and Aggregation

### Initial Subject Cleaning and Getting Subject Counts

To count the number of subjects and do an initial cleaning of the subjects data (stripping of whitespace; singularizing; removing any numbers, dashes, or spaces from the beginning of the string; and turning them all to lowercase), run:
```
py -2 count_subjects.py [--dhlw]
```

We singularize the last word of the subject; to do this, we use `singularize` from `pattern.text.en`, which only works with Python2. This is why we run this command with Python2.

The resulting counts should be under `data/*_subject_counts.csv`. The data files with the cleaned subjects should be under `data/*_cleaned.csv`.

### Ignoring Subjects

Some subjects were ignored because they were too generic or ambiguous. A list of conditions for which subjects were to be ignored was read in, and subjects that satisfied these conditions were removed from the list. To do this, run:
```
py -3 ignore_subjects.py [--dhlw]
```

The resulting subjects that were not ignored and their counts should be under `data/*_subject_counts_after_ignore.csv`.

### Aggregating Subjects

To aggregate the subjects to their corresponding subcategories, run:
```
py -3 aggregate_subjects.py [--dhlw]
```

The resulting subject aggregations should be under `data/*_aggregated_subjects.csv`.

## Labeling of Data

To label the documents with their corresponding categories and subcategories, run:
```
py -3 label_data.py [--dhlw]
```

The resulting data file should be under `data/*_final.csv`.

Because we are using a modified version of the [Global Migrations plot](https://github.com/null2/globalmigration), we also generated JSON files containing the matrices with data link information, located under `*_data.json`.

## Creating the Visualization

To create the visualization, open the `plot/chart_*.html` files or the `plot/charts.html` and copy in the JSON object into the `data` variables. Open the HTML file in your browser.

## Credit
This plot was taken from [The Global Flow of People plot](http://www.global-migration.info/), which is done by Nikola Sander, Guy J. Abel, and Ramon Bauer. The source code is [here](https://github.com/null2/globalmigration), done by null2 GmbH. Their work is licensed under a [Creative Commons Attribution-NonCommercial 3.0 Unported License](http://creativecommons.org/licenses/by-nc/3.0/) and copyright (c) 2013 null2 GmbH Berlin.

Minor changes were made, including:
* Making links bidirectional
* Taking out the timeline
* Changing the region labels to be perpendicular

## License
This work is licensed under a [Creative Commons Attribution-NonCommercial 3.0 Unported License](http://creativecommons.org/licenses/by-nc/3.0/).
