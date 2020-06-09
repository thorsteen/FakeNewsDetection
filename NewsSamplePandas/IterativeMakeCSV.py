# -*- coding: utf-8 -*-

import re
import pandas as pd
import datetime
from cleantext import clean

inputPath = '../../../../../../data/input/'
# inputPath = '../../Data/'

outputPath = '../../../../../../data/fakeOutput/'
# outputPath = '../../Data/'

# filename ='news_sample.csv' #works with this data
filename = '1mio-raw.csv'
# filename = '../../Data/clean-100k.csv' #works with this data
# filename = '../../Data/1mio-raw.csv'  # does not work yet

# following is csv file is without empty rows and made from 1mio-raw
# filename = '../../Data/500k.csv'

filename = inputPath + filename


def clean_text(content):

    # Set all words to be lowercased
    clean_text = content.lower()
    clean_text = ' '.join(clean_text.split())

    clean(clean_text,
          fix_unicode=True,
          to_ascii=True,
          no_line_breaks=True,
          no_urls=True,
          no_emails=True,
          no_phone_numbers=False,
          no_numbers=True,
          no_digits=False,
          no_currency_symbols=False,
          no_punct=False,
          replace_with_url="<URL>",
          replace_with_email="<EMAIL>",
          replace_with_phone_number="<PHONE>",
          replace_with_number="<NUMBER>",
          replace_with_digit="0",
          replace_with_currency_symbol="<CUR>",
          lang="en")

    # Remove ^ since we use them as delimiter
    clean_text = clean_text.replace('^', '')

    # Remove "
    clean_text = clean_text.replace('"', '')

    # Remove { since we use them as delimiter
    clean_text = clean_text.replace('{', '')
    clean_text = clean_text.replace('}', '')

    return clean_text


def putinDic(dictionary, liste, ID):
    liste = list(set(liste))
    liste.sort()
    for j in range(len(liste)):
        info = str(liste[j])
        if info not in dictionary:
            dictionary[info] = int(ID)
            ID += 1
    return int(ID)


def simpleEntityToCSV(filename, dictionary):
    file = open(filename, "w+", encoding="utf-8")
    for item in dictionary.items():
        file.write("%s^%s\n" % (str(item[1]), str(item[0])))
    file.close


def prepFile(filename):
    return open(filename, "w+", encoding="utf-8")


def isNaN(string):
    return string != string


# ------------------------------------------#
# reading data in
chunk_size = 10000
csvfile = open(filename, 'r', encoding='utf-8', newline='')
df_chunk = pd.read_csv(
    csvfile,
    chunksize=chunk_size)  # dtype=datatypes skiprows = list(range(1,100000))

# clear files that are used for appending
tagsRelationFile = prepFile(outputPath + "tags_relation.csv")
writtenByFile = prepFile(outputPath + "writtenBy_relation.csv")
webpageRelationFile = prepFile(outputPath + "webpage_relation.csv")
articleEntity1File = prepFile(outputPath + "article_entity1.csv")
articleEntity2File = prepFile(outputPath + "article_entity2.csv")

# define dicts
author = dict()
domain = dict()
typ = dict()
keyword = dict()

# Define IDS
author_ID = 0
domain_ID = 0
type_ID = 0
keyword_ID = 0
article_ID = 0

chunk_no = 0

for chunk in df_chunk:

    print("chunk loaded")

    authorList = []
    meta_keywordList = []
    domainList = []
    typeList = []

    for index, row in chunk.iterrows():

        authors = row['authors']
        if (not isNaN(authors)):
            authors = authors.split(", ")
            for a in authors:
                if (len(a) <= 64):
                    authorList.append(a)

        keywords = row['meta_keywords']
        if (not isNaN(keywords)):
            keywords = keywords[2:-2]
            split_keywords = re.split("(?:\'|\"), (?:\'|\")", keywords)
            for word in split_keywords:
                if (len(word) <= 128):
                    meta_keywordList.append(word.replace("\'", ""))

        thisDomain = row['domain']
        if (not isNaN(thisDomain)):
            if (len(thisDomain) <= 1024):
                domainList.append(thisDomain)

        thisType = row['type']
        if (not isNaN(thisType)):
            if (len(thisType) <= 64):
                typeList.append(thisType)

    author_ID = putinDic(author, authorList, author_ID)

    keyword_ID = putinDic(keyword, meta_keywordList, keyword_ID)

    domain_ID = putinDic(domain, domainList, domain_ID)

    type_ID = putinDic(typ, typeList, type_ID)

    print("set up dictionaries")

    for index, row in chunk.iterrows():

        title = row['title']
        if (title and (not isNaN(title)) and (len(title) <= 512)):
            title = clean_text(title)
        else:
            title = "NULL"

        content = row['content']
        if (not isNaN(content)):
            content = clean_text(content)
        else:
            content = "NULL"

        summary = row['summary']
        if (summary and (not isNaN(summary))):
            summary = clean_text(summary)
        else:
            summary = "NULL"

        meta_description = row['meta_description']
        if (meta_description and (not isNaN(meta_description))):
            meta_description = clean_text(meta_description)
        else:
            meta_description = "NULL"

        thisType = row['type']
        if (not isNaN(thisType) and (len(thisType) <= 64)):
            type_id = typ[thisType]
        else:
            type_id = 0

        scraped_at = row['scraped_at'] if (
            not isNaN(row['scraped_at'])) else datetime.datetime(1000, 1, 1)

        inserted_at = row['inserted_at'] if (
            not isNaN(row['inserted_at'])) else datetime.datetime(1000, 1, 1)

        updated_at = row['updated_at'] if (
            not isNaN(row['updated_at'])) else datetime.datetime(1000, 1, 1)

        res = ("%s^%s^%s^%s^%s^%s^%s^%s^%s\n" %
               (article_ID, title, content, summary, meta_description, type_id,
                scraped_at, inserted_at, updated_at))

        if chunk_no < 50:
            articleEntity1File.write(res)
        else:
            articleEntity2File.write(res)

        thisDomain = row['domain']
        url = row['url']

        if ((not isNaN(url)) and (not isNaN(thisDomain)) and (len(url) <= 1024)
                and (len(thisDomain) <= 1024)):
            webpageRelationFile.write("%s^%s^%s\n" %
                                      (article_ID, url, domain[thisDomain]))

        keywords = row['meta_keywords']
        if (not isNaN(keywords)):
            keywords = keywords[2:-2]
            split_keywords = re.split("(?:\'|\"), (?:\'|\")", keywords)
            for word in split_keywords:
                if (len(word) <= 128):
                    tagsRelationFile.write(
                        "%s,%s\n" %
                        (article_ID, keyword[word.replace("\'", "")]))

        authors = row['authors']
        if (not isNaN(authors)):
            authors = authors.split(", ")
            for a in authors:
                if (len(a) <= 64):
                    writtenByFile.write("%s,%s\n" % (article_ID, author[a]))

        article_ID += 1

    # ======================================================================
    # ends here
    # ======================================================================

    chunk_no += 1
    print("\n ============================")
    print(' |finished cleaning chunk {}|'.format(chunk_no, ))
    print(" ===============================\n")

tagsRelationFile.close()
writtenByFile.close()
webpageRelationFile.close()
articleEntity1File.close()
articleEntity2File.close()

# use create csv files for simple entities, ids created with dicts
simpleEntityToCSV(outputPath + "author_entity.csv", author)
simpleEntityToCSV(outputPath + "keyword_entity.csv", keyword)
simpleEntityToCSV(outputPath + "domain_entity.csv", domain)
simpleEntityToCSV(outputPath + "type_entity.csv", typ)
print('DONE!')
