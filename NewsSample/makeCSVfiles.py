import csv
import datetime
import urllib.request
import urllib.error
import nltk
from cleantext import clean
import re
import numpy as np

def clean_text(content):

    # Set all words to be lowercased
    clean_text = content.lower()
    
    # Clean dates 
    date1 = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) (?:[\d]{1, 2}), (?:1\d{3}|2\d{3})(?=\D|$)" # feb(ruary) 10, 2010
    date2 = r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec?). (?:[\d]{1, 2}), (?:1\d{3}|2\d{3})(?=\D|$)" # Feb. 10, 2010
    date3 = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) (?:[\d]{1,2}) (?:1\d{3}|2\d{3})(?=\D|$)" # June 12 2016
    date4 = r"\b(?:[\d]{1, 2}) (?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) (?:1\d{3}|2\d{3})(?=\D|$)" # 31 Dec 2017
    date5 = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) (?:1\d{3}|2\d{3})(?=\D|$)"  # July 2015
    date6 = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) (?:[\d]{1,2})(?=\D|$)"  # June 27
    date7 = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) of (?:1\d{3}|2\d{3})(?=\D|$)" #Aug(ust) of 2014
    date8 = r"[\d]{1,2}/[\d]{1,2}/[\d]{4}" # 20/20/2020
    date9 = r"[\d]{1,2}-[\d]{1,2}-[\d]{4}" # 20-20-2020
    date_patterns = [date1, date2, date3, date4, date5, date6, date7, date8, date9]
    
    for pattern in date_patterns:
        clean_text = re.sub(pattern, ' <DATE> ', clean_text)
    
    # Clean email
    email1 = r'([\w0-9._-]+@[\w0-9._-]+\.[\w0-9_-]+)'
    clean_text = re.sub(email1, ' <EMAIL> ', clean_text)
    
    # Clean URLs 
    url1 = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    clean_text = re.sub(url1, ' <URL> ', clean_text)
    
    # Clean numbers
    num1 = r'[0-9]+'
    clean_text = re.sub(num1, ' <NUM> ', clean_text)
    
    # Clean multiple white spaces, tabs, and newlines
    space1 = r"\s+"
    clean_text = re.sub(space1, ' ', clean_text)
    
    return clean_text

def putinDic(dictionary, liste):
    liste = list(set(liste))
    liste.sort()
    ID = 0
    for j in range(len(liste)):
        info = str(liste[j]).lower()
        dictionary[info] = ID
        ID += 1

def simpleEntityToCSV(filename, dictionary):
    file = open(filename,"w+")
    for item in dictionary.items():
        file.write("%s,%s\n" %(str(item[1]), str(item[0])))
    file.close
     
with open('news_sample.csv', newline='', encoding='utf8') as csvfile:

    #opens file and reads header into head
    file = csv.reader(csvfile)
    head = file.__next__()
    
    #Finds indexes of columns 
    for i in range(len(head)):
        if   str(head[i]) == "id":                  idIdx = i               #identification given to each article
        elif str(head[i]) == "domain":              domainIdx = i           #simple form of the url
        elif str(head[i]) == "type":                typeIdx = i             #how reliable the source is
        elif str(head[i]) == "url":                 urlIdx = i              #link to article itself
        elif str(head[i]) == "content":             contentIdx = i          #all the juice of the article
        elif str(head[i]) == "scraped_at":          scraped_atIdx = i       #date of 
        elif str(head[i]) == "inserted_at":         inserted_atIdx = i
        elif str(head[i]) == "updated_at":          updated_atIdx = i
        elif str(head[i]) == "title":               titleIdx = i
        elif str(head[i]) == "authors":             authorIdx = i           #who made this source
        elif str(head[i]) == "keywords":            keywordsIdx = i         #always empty
        elif str(head[i]) == "meta_keywords":       meta_keywordsIdx = i    #real keywords
        elif str(head[i]) == "meta_description":    meta_descriptionIdx = i
        elif str(head[i]) == "tags":                tagsIdx = i
        elif str(head[i]) == "summary":             summaryIdx = i

    #converts csv.reader type to 2d array
    data = np.array(list(csv.reader(csvfile)))

    #This initializes the dictionary
    author  = dict()
    domain  = dict() 
    typ     = dict()
    keyword = dict()   
    article = dict()

    #Creates csv files for relations and article entity.
    writtenByFile   = open("writtenBy_relation.csv", "w+", encoding="utf-8")
    tagsFile        = open("tags_relation.csv", "w+", encoding="utf-8")
    webpageFile     = open("webpage_relation.csv", "w+", encoding="utf-8")
    articleFile     = open("article_entity.csv", "w+", encoding="utf-8")
    
    #fills authors into author dictionary, sort to make sure they get the same id every time the code is run
    authorList = data[:,authorIdx]
    temp = []
    for i in authorList:
        something = i.split(", ")
        for j in something:
            temp.append(j)
    putinDic(author, temp)
    
    #fills metaKeywords into author dictionary, sort to make sure they get the same id every time the code is run
    tempKeywords = data[:,meta_keywordsIdx]
    keywords = []
    for words in tempKeywords:
        temp = re.split(r'[;,"\'\[\]]\s*', words)
        for word in temp:
            keywords.append(word)
    putinDic(keyword,keywords)

    #fills domains into author dictionary, sort to make sure they get the same id every time the code is run
    putinDic(domain,data[:,domainIdx])

    #fills types into author dictionary, sort to make sure they get the same id every time the code is run
    putinDic(typ,data[:,typeIdx])

    #example of how to extract and print data from dictionaries, to be used for riding into .csv files
    simpleEntityToCSV("author_entity.csv", author)
    simpleEntityToCSV("keyword_entity.csv", keyword)
    simpleEntityToCSV("domain_entity.csv", domain)
    simpleEntityToCSV("type_entity.csv", typ)

    domainID = typeID = authorID = keywordID = 0 

    for row in data:
        articleID           = row[0] 
        title               = row[titleIdx].lower()
        content             = clean_text(row[contentIdx])
        summary             = row[summaryIdx].lower()
        meta_description    = row[meta_descriptionIdx].lower()
        type_id             = typ[row[typeIdx].lower()]
        scrappedAt          = row[scraped_atIdx]
        insertedAt          = row[inserted_atIdx]
        updatedAt           = row[updated_atIdx]
        thisDomain          = row[domainIdx]
        thisType            = row[typeIdx]
        authors             = row[authorIdx]
        mkeywords           = row[meta_keywordsIdx]

        articleFile.write("%s^\"%s\"^\"%s\"^\"%s\"^\"%s\"^%s^%s^%s^%s\n"%
            (articleID, title, content, summary, meta_description, type_id, scrappedAt, insertedAt, updatedAt))

        url = row[urlIdx].lower()
        webpageFile.write("\"%s,%s,%s\n" % (url, articleID, domain[row[domainIdx].lower()]))

        authors = authors.split(', ')
        for a in authors:
            writtenByFile.write("%s,%s\n" % (articleID, author[a.lower()]))

        mkeywords = re.split(r'[;,"\'\[\]]\s*', mkeywords)
        for k in mkeywords:
            tagsFile.write("%s,%s\n" % (articleID, keyword[k.lower()]))

#commando i post gress: https://www.postgresql.org/docs/9.2/sql-copy.html 

