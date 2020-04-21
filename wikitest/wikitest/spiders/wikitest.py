import scrapy
import re
# Import the CrawlerProcess: for running the spider
#from scrapy.crawler import CrawlerProcess
class testSpider(scrapy.Spider):
    name = "wikitest"
    def start_requests(self):
        start_urls = [
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=S",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=A",
        ]

        #yield all the article links from the start urls
        for url in start_urls:
            yield scrapy.Request( url = url, callback = self.parse )
        
        
    #We want to follow the next page from the start urls until  we are finished entirely (at letter O)
    #Will find all links in the start url that correspond to category
    #Might also find some categories that should not be processed --- Fixed no longer applicable
    def parse(self, response):    
        links = response.xpath('/html/body/div[3]/div[3]/div[4]/div[2]/div[2]/div/div/div/ul/li/a/@href').extract() 

        WantedArticles =  r"/wiki/[A-D,S-Z]"
        
        for link in links:
            if link and (re.match(WantedArticles , link) != None):
                yield response.follow(url = link, callback = self.parse2)


        forbiddenNP =  r"https:\/\/en\.wikinews\.org\/w\/index\.php\?title=Category:Politics_and_conflicts&pagefrom=E"
        
        nextpageurl1 = response.xpath("//*[@id='mw-pages']/a[contains(.,'next page')]/@href").get()
        nextpageurl = response.urljoin(nextpageurl1)
        
        if nextpageurl and (re.match(forbiddenNP , nextpageurl ) == None):
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
        

#dictionary to store data
#test_dict = dict()

#run spider
#process = CrawlerProcess()
#process.crawl(testSpider)
#process.start()

# Print a preview of courses
#var = test_dict.keys()
#print(var)