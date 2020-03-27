# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 10:30:54 2020

@author: tsl19

WARNING: RUNNING TIME IS VERY LONG
"""

import re
import pandas as pd
import time
start_time = time.time()

filename ='news_sample.csv'
#filename = '../../Data/clean-100k.csv'
#filename = '../../Data/1mio-raw.csv'

#så man kan se mere print i terminal
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

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
print('Read data')

#to avoid NaNs and other nulls we set these to string '<null>'
data = data.where(pd.notnull(data), '<null>')

#clean text
for i in data['content'].index:
    data.loc[i,'content'] = clean_text(data.loc[i,'content'])
#we clean all at once which takes time
print('Finished cleaning')

#define dicts
author  = dict()
domain  = dict() 
typ     = dict()
keyword = dict()   


#we fill authors into author dictionary, sort to make sure they get the same id every time the code is run
authors = []
for i in data['authors']:
    split_authors = i.split(", ")
    for name in split_authors:
        authors.append(name[:64]) #names must not be longer than 64 char
        
print('finished splitting authors and making authors list')

keywords = []
for words in data['meta_keywords']:
    split_keywords = re.split(r'[;,"\'\[\]]\s*', words)
    for word in split_keywords:
        keywords.append(word[:128]) #make sure that every keyword is no longer than 128 char

print('finished splitting keywords and making keywords list')


#make dicts with key string and id int from sorted list
putinDic(author, authors)

putinDic(keyword,keywords)

putinDic(domain,data['domain'])

putinDic(typ,data['type'])
print('finished making dictionaries')


#use create csv files for simple entities, ids created with dicts
simpleEntityToCSV("author_entity.csv", author)
simpleEntityToCSV("keyword_entity.csv", keyword)
simpleEntityToCSV("domain_entity.csv", domain)
simpleEntityToCSV("type_entity.csv", typ)
print('finished author_entity, keyword_entity, domain_entity, type_entity csv files')


#we need to make two new cols to get the correct ID of type and domain
#will impact running time
domain_id = []
type_id = []
for i in data['domain']: 
    domain_id.append(domain.get(i),)
for j in data['type']:
    type_id.append(typ.get(j))
    

#using first column as article id
#is wrong due to false in
#data.iloc[:,0].is_unique
#true in
#data['id'].is_unique
#which we use later on
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
print('finished making article_entity webpage_relation csv files')

#Pandas becomes difficult when working with undefined sizes so
#we use file method for authors and keywords

tagsFile = open("tags_relation.csv", "w+", encoding="utf-8")
article_id = 0

for m in data['meta_keywords']:
    split_keywords = re.split(r'[;,"\'\[\]]\s*', m)
    for meta_keyword in split_keywords:
        tagsFile.write("%s,%s\n" % (data.loc[article_id,"id"], keyword.get(meta_keyword.lower())))
    article_id += 1

tagsFile.close()

print('finished making article_entity, webpage_relation csv files')


writtenByFile = open("writtenBy_relation.csv", "w+", encoding="utf-8")
article_id = 0

for k in data['authors']:
    split_authors = k.split(', ')  
    for a in authors:
        writtenByFile.write("%s,%s\n" % (data.loc[article_id,"id"], author.get(a.lower(),)))
    article_id += 1
    
writtenByFile.close()
print('finished making writtenBy_relation csv files')

print("--- Total running time %s seconds ---" % (time.time() - start_time))