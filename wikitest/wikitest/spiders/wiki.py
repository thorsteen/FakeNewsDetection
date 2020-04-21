import scrapy
import re
# Import the CrawlerProcess: for running the spider
from scrapy.crawler import CrawlerProcess
class testSpider(scrapy.Spider):
    name = "wiki"
    def start_requests(self):
        start_urls = [
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=D",
            '''"https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=E",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=F",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=G",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=H",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=I",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=J",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=K",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=L",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=M",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=N",'''
        ]
        for url in start_urls:
            yield scrapy.Request( url = url, callback = self.parse )

    #Will find all links in the start url that correspond to category
    #Might also find some categories that should not be processed
    #maybe use some regex to filter them
    def parse(self, response):
        links = response.css('div.mw-category-group ul li').xpath('a/@href').extract()
        for link in links:
            if link:
                yield response.follow(url = link, callback = self.parse2)

    #Will run over all individual articles and extract appropriate data
    def parse2(self, response):
        #return individual article 
        # title
        title = response.xpath('/html/body/div[3]/h1/text()').get()
        #source(s)
        source = response.xpath('/html/body/div[3]/div[3]/div[4]/div/ul/li/span/text()').getall()
        #date
        date = response.xpath('/html/body/div[3]/div[3]/div[4]/div/p[1]/strong/text()').get()
        #text
        text = response.xpath('/html/body/div[3]/div[3]/div[4]/div/p/text()').getall()
        #put the date and text in the zip
    
        if title:
            yield {
                        'title': title,
                    }
        if source:
            yield {
                        'source': source,
                    }
        if date:
            yield {
                        'date': date,
                    }
        if text:
            yield {
                        'text': text,
                    }
        #for crs_title, crs_descr, text in zip( title, source , text ):
            #put date text and source in right side of equal sign
            #title as key
        #test_dict[title] = [source , date , text]

#dictionary to store data
#test_dict = dict()

#run spider
#process = CrawlerProcess()
#process.crawl(testSpider)
#process.start()
#print(test_dict.keys())

# Print a preview of courses
#var = test_dict.keys()
#print(var)