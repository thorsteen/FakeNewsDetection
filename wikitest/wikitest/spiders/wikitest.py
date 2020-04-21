import scrapy
import re
# Import the CrawlerProcess: for running the spider
#from scrapy.crawler import CrawlerProcess
class testSpider(scrapy.Spider):
    name = "wikitest"
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


        #yield all the article links from the start urls
        for url in start_urls:
            yield scrapy.Request( url = url, callback = self.parse )
        
        
    #We want to follow the next page from the start urls until  we are finished entirely (at letter O)
    #Will find all links in the start url that correspond to category
    #Might also find some categories that should not be processed --- Fixed no longer applicable
    def parse(self, response):    
        links = response.xpath('/html/body/div[3]/div[3]/div[4]/div[2]/div[2]/div/div/div/ul/li/a/@href').extract() 
        #links = response.css('div.mw-category-group ul li').xpath('a/@href').extract()
        for link in links:
            if link:
                yield response.follow(url = link, callback = self.parse2)

        #TODO: add a regex pattern that matches anything after the O
        forbiddenNP =  r"https:\/\/en\.wikinews\.org\/w\/index\.php\?title=Category:Politics_and_conflicts&pagefrom=O"
        #forbiddenNP =  'https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&pagefrom=Obama+signs+healthcare+bill+for+9%2F11+emergency+workers&amp;subcatfrom=N&amp;filefrom=N#mw-pages'
        #forbiddenNP = 'Politics_and_conflicts&pagefrom=O'
        #This has to be get() instead of extract so that forbiddenNP in nextpageurl can be compared as strings
        nextpageurl1 = response.xpath("//*[@id='mw-pages']/a[contains(.,'next page')]/@href").get()
        nextpageurl = response.urljoin(nextpageurl1)
        print(nextpageurl + '\n')

        #Obama signs $787 billion stimulus package #Last on the N page
        #Obama signs healthcare bill for 9/11 emergency workers #first on the O page
        #Gets the links to title "Obama's first State of the Union speech focuses on economy, jobs" and no further
        #SO no Obama's Inaugural Celebration "We are One" attracts 400,000
        '''if (re.match(forbiddenNP , nextpageurl ) != None):
            #nextpage = response.urljoin(nextpageurl)
            #print("Did not find url: {}".format(nextpage)) # Write a debug statement
            yield scrapy.Request(nextpageurl, callback=self.parse_no_follow)'''
        if nextpageurl and (re.match(forbiddenNP , nextpageurl ) == None):
            # If we've found a pattern which matches
            #nextpage = response.urljoin(nextpageurl)
            #print("Found url: {}".format(nextpage)) # Write a debug statement
            yield scrapy.Request(nextpageurl, callback=self.parse) # Return a call to the function "parse"

    #Will run over all individual articles and extract appropriate data
    def parse2(self, response):
        #return individual article 
        # title
        title = response.xpath('/html/body/div[3]/h1/text()').get()
        #source(s)
        source = response.xpath('/html/body/div[3]/div[3]/div[4]/div/ul/li/span/descendant-or-self::text()').extract()
        #date
        date = response.xpath('/html/body/div[3]/div[3]/div[4]/div/p[1]/strong/text()').get()
        #text TODO: add dl as part of sibling to p
        text = response.xpath("""//div[contains(@class, 'mw-parser-output')]/p/descendant-or-self::text()[not( parent::strong )]""").extract()

        finaltext = ''.join(text)

        finalsource = ''.join(source)

        yield {
            'title': title,
            'source' : finalsource,
            'date' : date,
            'text' : finaltext,
        }
        '''
        #zip them
        row_data=zip(title,source,date,text)        
        
        #create a dictionary to store the scraped info
        scraped_info = {
            #key:value
            'title': title,
            'source' : source,
            'date' : date,
            'text' : text,
        }
        yield scraped_info'''
        '''
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
                    }'''
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

# Print a preview of courses
#var = test_dict.keys()
#print(var)