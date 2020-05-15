@ECHO OFF
ECHO resetting .csv file
break>wiki.csv
ECHO scraping
scrapy crawl wikitest -L WARNING
ECHO DONE
