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
    clean_text = ''.join(clean_text.split())

    # Clean dates
    date = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?|(?:[\d]{1}|[\d]{2}))(?: |. |, |/|\\|:|;|.|,)(?:[\d]{1}|[\d]{2})(?: |. |, |/|\\|:|;|.|,)(?:1\d{3}|2\d{3})"  #does the same as 1,2,3,8 and 9
    clean_text = re.sub(date, ' <DATE> ', clean_text)

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
        info = str(liste[j]).lower()
        if info not in dictionary:
            dictionary[info] = int(ID)
            ID += 1
    return int(ID)


def simpleEntityToCSV(filename, dictionary):
    file = open(filename, "w+", encoding="utf-8")
    for item in dictionary.items():
        if item[1] != '':
            file.write("%s,%s\n" % (str(item[1]), str(item[0])))
    file.close


def clearFile(filename):
    file = open(filename, "w+", encoding="utf-8")
    file.write("")
    file.close()


def isNaN(string):
    return string != string


# ------------------------------------------#
# reading data in
chunk_size = 10000
cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
        15]  # to skp index, source and meta_description column
df_chunk = pd.read_csv(
    filename,
    encoding='utf-8',
    skip_blank_lines=True,
    error_bad_lines=False,
    chunksize=chunk_size,
    verbose=True,
    na_filter=True,
    usecols=cols)  # dtype=datatypes skiprows = list(range(1,100000))

# clear files that are used for appending
clearFile(outputPath + "tags_relation.csv")
clearFile(outputPath + "writtenBy_relation.csv")
clearFile(outputPath + "article_entity1.csv")
clearFile(outputPath + "article_entity2.csv")

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

randomHighID = 20000000
chunk_no = 0

for chunk in df_chunk:

    authorList = []
    meta_keywordList = []
    domainList = []
    typeList = []

    for index, row in chunk.iterrows():

        authors = row['authors']
        if (not isNaN(authors)):
            authors = authors.split(", ")
            for a in authors:
                authorList.append(a)

        keywords = row['meta_keywords']
        if (not isNaN(keywords)):
            keywords = keywords[2:-2]
            if keywords != '':
                split_keywords = re.split("(?:\'|\"), (?:\'|\")", keywords)
                for word in split_keywords:
                    if word != '':
                        meta_keywordList.append(word[:128 - 1].replace(
                            '\"', '\"\"'))

        domains = row['domain']
        if (not isNaN(domains)):
            domainList.append(domains[:64 - 1])

        types = row['type']
        if (not isNaN(types)):
            typeList.append(types[:64 - 1])

    author_ID = putinDic(author, authorList, author_ID)

    keyword_ID = putinDic(keyword, meta_keywordList, keyword_ID)

    domain_ID = putinDic(domain, domainList, domain_ID)

    type_ID = putinDic(typ, typeList, type_ID)

    # ======================================================================
    #  This is where we need to append instead of write to file.
    # ======================================================================

    # we need to make two new cols to get the correct ID of type and domain
    # will impact running time
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

        types = row['type']
        if ((not isNaN(types)) and (len(types) <= 64)):
            type_id = typ[types]
        else:
            type_id = 0

        scraped_at = row['scraped_at'] if (isNaN(
            row['scraped_at'])) else datetime.datetime(1000, 1, 1)
        inserted_at = row['inserted_at'] if (isNaN(
            row['inserted_at'])) else datetime.datetime(1000, 1, 1)
        updated_at = row['updated_at'] if (isNaN(
            row['updated_at'])) else datetime.datetime(1000, 1, 1)

        res = "{}^{}^{}^{}^{}^{}^{}^{}^{}\n".format(article_ID, title, content,
                                                    summary, meta_description,
                                                    type_id, scraped_at,
                                                    inserted_at, updated_at)
        if chunk_no < 50:
            article_entity1 = open(outputPath + "article_entity1.csv",
                                   "a+",
                                   encoding="utf-8")
            article_entity1.write(res)
            article_entity1.close()
        else:
            article_entity2 = open(outputPath + "article_entity2.csv",
                                   "a+",
                                   encoding="utf-8")
            article_entity2.write(res)
            article_entity2.close()

        thisDomain = row['domain']
        url = row['url']
        if ((not isNaN(url)) and (not isNaN(thisDomain)) and (len(url) <= 1024)
                and (len(thisDomain) <= 1024)):
            res = "{}^{}^{}\n".format(article_ID, url, domain[thisDomain])

        if article_ID == 0:
            webpage_relation = open(outputPath + 'webpage_relation.csv',
                                    "w+",
                                    encoding='utf-8')
            webpage_relation.write(res)
            webpage_relation.close()
        else:
            webpage_relation = open(outputPath + 'webpage_relation.csv',
                                    "a+",
                                    encoding='utf-8')
            webpage_relation.write(res)
            webpage_relation.close()

        # Pandas becomes difficult when working with undefined sizes so
        # we use file method for authors and k

        tagsFile = open(outputPath + "tags_relation.csv",
                        "a+",
                        encoding="utf-8")

        keywords = row['meta_keywords']
        if (not isNaN(keywords)):
            keywords = keywords[2:-2]
            if keywords != '':
                split_keywords = re.split("(?:\'|\"), (?:\'|\")", keywords)
                for word in split_keywords:
                    if word != '':
                        tagsFile.write("{}^{}\n".format(
                            article_ID,
                            keyword[word[:128 - 1].replace('\"',
                                                           '\"\"').lower()]))

        tagsFile.close()

        writtenByFile = open(outputPath + "writtenBy_relation.csv",
                             "a+",
                             encoding="utf-8")

        authors = row['authors']
        if (not isNaN(authors)):
            authors = authors.split(", ")
            for a in authors:
                writtenByFile.write("{}^{}\n".format(article_ID,
                                                     author[a.lower()]))

        writtenByFile.close()

        article_ID += 1

    # ======================================================================
    # ends here
    # ======================================================================

    chunk_no += 1
    print("\n ============================")
    print(' |finished cleaning chunk {}|'.format(chunk_no, ))
    print(" ===============================\n")

# use create csv files for simple entities, ids created with dicts
simpleEntityToCSV(outputPath + "author_entity.csv", author)
simpleEntityToCSV(outputPath + "keyword_entity.csv", keyword)
simpleEntityToCSV(outputPath + "domain_entity.csv", domain)
simpleEntityToCSV(outputPath + "type_entity.csv", typ)
print('DONE!')
