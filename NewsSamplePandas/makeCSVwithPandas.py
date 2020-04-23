# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 10:30:54 2020

@author: tsl19

WARNING: RUNNING TIME IS VERY LONG ON MIO DATA SET
"""

import re
import pandas as pd
import time
#import csv
start_time = time.time()

#filename ='news_sample.csv' #works with this data
#filename ='../../../../../../data/clean-100k.csv' #this is where i have to store my files... :/
#filename = '../../Data/clean-100k.csv' #works with this data
#filename = '../../Data/1mio-raw.csv' #contains difficult empty rows and other problems

#following is csv file is without empty rows and made from 1mio-raw
filename = '../../Data/500k.csv'

#så man kan se mere print i terminal
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

def clean_text(content):

    # Set all words to be lowercased
    clean_text = content.lower()

    # Clean dates
    date = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?|(?:[\d]{1}|[\d]{2}))(?: |. |, |/|\\|:|;|.|,)(?:[\d]{1}|[\d]{2})(?: |. |, |/|\\|:|;|.|,)(?:1\d{3}|2\d{3})" #does the same as 1,2,3,8 and 9
    clean_text = re.sub(date, ' <DATE> ', clean_text)

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
        if item[1] != '':
            file.write("%s,%s\n" %(str(item[1]), str(item[0])))
    file.close

#------------------------------------------#
#might help to give datatypes beforehand to pd.read_csv
data = pd.read_csv(filename, encoding='utf-8', skip_blank_lines=True, verbose = True, na_filter=True)

#alternative way to load data. seem to give same result as pd.read_csv
"""
with open(filename, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader, None)
    rows = []
    for row in reader:
        rows.append({header: value for header, value in zip(headers, row)})
print(rows[0])

data = pd.DataFrame(rows)
"""
print('Read data')

#data.dropna(subset = ['id'], inplace = True)
#det virker tilsyndeladende heller ikke at slette rækker med tomme ids

#to avoid NaNs and other nulls we set these to string ''
data = data.where(pd.notnull(data), '')

clean_start_time = time.time()
#clean text
#we clean all at once which takes n^9 running time
#for i in data['content'].index:
#    data.loc[i,'content'] = clean_text(data.loc[i,'content'])
print('finished cleaning after {}s'.format(time.time()-clean_start_time))

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
        authors.append(name[:64-1]) #names must not be longer than 64 char

print('finished splitting authors and making authors list')

keywords = []
keywords.append('')
for words in data['meta_keywords']:
    #splitter = words[1]
    words = words[2:-2]
    if words != '':
        #split er ændret, da det split der var før lavede fejl ved dobbelt quotation 
        split_keywords = re.split("(?:\'|\"), (?:\'|\")", words)
        split_keywords = words.split(', ')
        for word in split_keywords:
            if word != '':
                keywords.append(word[:128-1].replace('\"', '\"\"')) #make sure that every keyword is no longer than 128 char

print('finished splitting keywords and making keywords list')


#make dicts with key string and id int from sorted list
putinDic(author, authors)

putinDic(keyword,keywords)

putinDic(domain,data['domain'])
domain.update({'NULL' : -1}) #add NULL entry in dict for misses

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
    domain_id.append(int(domain.get(i,-1)))
for j in data['type']:
    type_id.append(int(typ.get(j,-1)))


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
                                data['inserted_at'],
                                data['updated_at'],
                                data['scraped_at']],axis=1)
article_entity.to_csv('article_entity.csv', index = False, header = False, sep = "^")

domain_id_df = pd.DataFrame(domain_id, columns = ['domain_id'])

webpage_relation = pd.concat([data['url'],data['id'], domain_id_df], axis = 1)

webpage_relation.to_csv('webpage_relation.csv',index = False, header = False)
print('finished making article_entity webpage_relation csv files')

#Pandas becomes difficult when working with undefined sizes so
#we use file method for authors and keywords

tagsFile = open("tags_relation.csv", "w+", encoding="utf-8")
article_id = 0

for m in data['meta_keywords']:
    #split_keywords = re.split(r'[;,"\'\[\]]\s*', m)
    #splitter = m[1]
    m = m[2:-2]
    split_keywords = re.split("(?:\'|\"), (?:\'|\")", m)
    split_keywords = m.split(', ')
    for meta_keyword in split_keywords:
        meta_keyword = meta_keyword[:127].replace('\"', '\"\"')
        if meta_keyword != '':
            tagsFile.write("%s,%s\n" % (data.loc[article_id,"id"], keyword.get(meta_keyword.lower(),'')))
    article_id += 1

tagsFile.close()

print('finished making article_entity, webpage_relation csv files')


writtenByFile = open("writtenBy_relation.csv", "w+", encoding="utf-8")
article_id = 0

for k in data['authors']:
    split_authors = k.split(', ')
    for a in split_authors:
        writtenByFile.write("%s,%s\n" % (data.loc[article_id,"id"], author.get(a.lower(),'')))
    article_id += 1

writtenByFile.close()
print('finished making writtenBy_relation csv files')

print("--- Total running time %s seconds ---" % (time.time() - start_time))
