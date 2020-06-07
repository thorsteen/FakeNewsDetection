import scrapy
import re
import datetime

scraped_at = datetime.datetime.now()
articleID = 1000000


class testSpider(scrapy.Spider):
    name = "wikitest"

    def start_requests(self):
        start_urls = [
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=S",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=A",
        ]

        # yield all the article links from the start urls
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # We want to follow the next page from the start urls until  we are finished entirely (at letter O)
    # Will find all links in the start url that correspond to category
    # Might also find some categories that should not be processed --- Fixed no longer applicable
    def parse(self, response):
        links = response.xpath(
            '/html/body/div[3]/div[3]/div[4]/div[2]/div[2]/div/div/div/ul/li/a/@href'
        ).extract()

        WantedArticles = r"/wiki/[A-D,S-Z]"

        for link in links:
            if link and (re.match(WantedArticles, link) != None):
                yield response.follow(url=link, callback=self.parse2)

        forbiddenNP = r"https:\/\/en\.wikinews\.org\/w\/index\.php\?title=Category:Politics_and_conflicts&pagefrom=E"

        nextpageurl1 = response.xpath(
            "//*[@id='mw-pages']/a[contains(.,'next page')]/@href").get()
        nextpageurl = response.urljoin(nextpageurl1)

        if nextpageurl and (re.match(forbiddenNP, nextpageurl) == None):
            yield scrapy.Request(
                nextpageurl,
                callback=self.parse)  # Return a call to the function "parse"

    # Will run over all individual articles and extract appropriate data
    def parse2(self, response):

        dateRe = r"(?:january|february|march|april|may|june|july|august|september|october|november|december)(?: )(?:[\d]{1}|[\d]{2})(?:, )(?:1\d{3}|2\d{3})"

        # return individual article
        url = response.url
        # title
        title = response.xpath('/html/body/div[3]/h1/text()').get()
        # source(s)  /html/body/div[3]/div[3]/div[4]/div/ul

        sources = []
        for li in response.xpath(
                """//a[contains(@class, 'external text')]/@href"""):
            temp = li.get().lower()
            sources.append(temp)

        # sources = response.xpath("""//span[contains(@class, 'sourceTemplate')]/descendant-or-self::text()""").extract()
        # text TODO: add dl as part of sibling to p
        text = response.xpath(
            """//div[contains(@class, 'mw-parser-output')]/p/descendant-or-self::text()[not( parent::strong )]"""
        ).extract()
        # keywords
        keywords = response.xpath(
            """//div[contains(@class, 'mw-normal-catlinks')]/ul/descendant-or-self::text()"""
        ).extract()
        # date

        date = ""
        finalKeywords = '[\"'

        for i in range(len(keywords)):
            keyword = keywords[i].lower()
            if re.fullmatch(dateRe, keyword) != None:
                date = keyword
            else:
                finalKeywords += (keyword + '\", \"')

        if len(finalKeywords) < 3:
            finalKeywords = ''
        else:
            finalKeywords = finalKeywords[:-3] + ']'

        finalsource = '[\"'

        for i in range(len(sources)):
            source = sources[i].lower()
            finalsource += (source + '\", \"')

        if len(finalsource) < 3:
            finalsource = ''
        else:
            finalsource = finalsource[:-3] + ']'

        finaltext = ''.join(text)

        global articleID
        articleID += 1

        #,id,domain,type,url,content,scraped_at,inserted_at,updated_at,title,authors,keywords,meta_keywords,meta_description,tags,summary

        yield {
            'id': articleID,
            'domain': 'wikinews.org',
            'type': 'reliable',
            'url': url,
            'content': finaltext,
            'scraped_at': scraped_at,
            'date': date,
            'title': title,
            'sources': finalsource,
            'keywords': finalKeywords,
        }
