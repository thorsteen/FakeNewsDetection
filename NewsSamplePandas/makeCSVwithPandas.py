# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 10:30:54 2020

@author: tsl19
"""

import re
import pandas as pd

#filename ='news_sample.csv'
filename = 'clean-100k.csv'


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
    file = open(filename,"w+",encoding="utf-8")
    for item in dictionary.items():
        file.write("%s,%s\n" %(str(item[1]), str(item[0])))
    file.close

#------------------------------------------#
data = pd.read_csv(filename)
#to avoid problems later on
#data = data.drop([0])

data = data.where(pd.notnull(data), '<null>')


#using first column as article id
#is wrong due to false in
#data.iloc[:,0].is_unique
"""
columns = list(data.columns)
columns[0] = 'article_id' 
data.columns = columns
"""

#clean text
for i in data['content']:
    i = clean_text(i)

author  = dict()
domain  = dict() 
typ     = dict()
keyword = dict()   
article = dict()


#we fill authors into author dictionary, sort to make sure they get the same id every time the code is run
temp = []
new = []
         
for i in data['authors']:
    split_authors = i.split(", ")
    for j in split_authors:
        temp.append(j)
putinDic(author, temp)

#we fill metaKeywords into author dictionary, sort to make sure they get the same id every time the code is run
tempKeywords = data['meta_keywords']
keywords = []
for words in tempKeywords:
    temp = re.split(r'[;,"\'\[\]]\s*', words)
    for word in temp:
        keywords.append(word)
putinDic(keyword,keywords)

#fills domains into author dictionary, sort to make sure they get the same id every time the code is run
putinDic(domain,data['domain'])

#fills types into author dictionary, sort to make sure they get the same id every time the code is run
putinDic(typ,data['type'])

#making dict to dataframe directly 
#wrong order
"""
#keys becomes index
author_entity = pd.DataFrame.from_dict(author, orient='index')
keyword_entity = pd.DataFrame.from_dict(keyword, orient='index')
domain_entity = pd.DataFrame.from_dict(domain, orient='index')
type_entity = pd.DataFrame.from_dict(typ, orient='index')

#makes csv with pandas, writing indexes because they are dict keys
author_entity.to_csv('author_entity.csv', index = True, header = False)
keyword_entity.to_csv('keyword_entity.csv', index = True, header = False)
domain_entity.to_csv('domain_entity.csv', index = True,header = False)
type_entity.to_csv('type_entity.csv', index = True,header = False)
"""

#use file.io method instead
simpleEntityToCSV("author_entity.csv", author)
simpleEntityToCSV("keyword_entity.csv", keyword)
simpleEntityToCSV("domain_entity.csv", domain)
simpleEntityToCSV("type_entity.csv", typ)


#we need to make two new cols to get correct ID of type and domain as well as right meta keywords and author
domain_id = []
type_id = []
for i in data['domain']: 
    domain_id.append(domain.setdefault(i),)
for j in data['type']:
    type_id.append(typ.setdefault(j))


#index is the same as article_id
#we do not need indexes and header when making csv

article_entity = pd.concat([data['id'],
                                data['title'].str.lower(),
                                data['content'],
                                data['summary'].str.lower(),
                                data['meta_description'].str.lower(),
                                pd.DataFrame(type_id,columns=['type_id']),
                                data['scraped_at'],
                                data['inserted_at'],
                                data['updated_at']],axis=1)
article_entity.to_csv('article_entity.csv', index = False, header = False, sep = "^")

webpage_relation = pd.concat([data['url'],data['id'],pd.DataFrame(domain_id, columns = ['domain_id'] )], axis = 1)
webpage_relation.to_csv('webpage_relation.csv',index = False, header = False)


#Pandas becomes difficult when working with undefined sizes so
#we use file.io method for authors and keywords

tagsFile = open("tags_relation.csv", "w+", encoding="utf-8")
article_id = 0

for m in data['meta_keywords']:
    mkeywords = re.split(r'[;,"\'\[\]]\s*', m)
    for meta_keyword in mkeywords:
        tagsFile.write("%s,%s\n" % (data.loc[article_id,"id"], keyword.setdefault(meta_keyword.lower())))
    article_id += 1

tagsFile.close()

writtenByFile = open("writtenBy_relation.csv", "w+", encoding="utf-8")
article_id = 0

for k in data['authors']:
    authors = k.split(', ')  
    for a in authors:
        print(a)
        writtenByFile.write("%s,%s\n" % (data.loc[article_id,"id"], author.setdefault(a.lower(),)))
    article_id += 1
    
writtenByFile.close()