
-----------------------------------------------------------------------------------------------------
					TASK 4
-----------------------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW
articles_per_domain_and_type
	(domain, typ, article_count)
	AS (SELECT domain_url, type_name, COUNT(*)
		FROM article NATURAL JOIN typ NATURAL JOIN webpage NATURAL JOIN domain
		WHERE domain_url IS NOT NULL AND type_name != '<null>'
		GROUP BY domain_url, type_name);


select * from articles_per_domain_and_type order by domain;

-----------------------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW
articles_per_author_and_type
	(author, typ, article_count)
	AS (SELECT author_name, type_name, COUNT(*)
		FROM article NATURAL JOIN typ NATURAL JOIN written_by NATURAL JOIN author
		WHERE author_name != '<null>' AND type_name != '<null>'
		GROUP BY author_name, type_name);

select * from articles_per_author_and_type order by author;

-----------------------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW
articles_per_keyword_and_type
	(keyword, typ, article_count)
	AS (SELECT keyword, type_name, COUNT(*)
		FROM article NATURAL JOIN typ NATURAL JOIN tags NATURAL JOIN keyword
		WHERE keyword != '<null>' AND type_name != '<null>'
		GROUP BY keyword, type_name);

select * from articles_per_keyword_and_type order by keyword;

-----------------------------------------------------------------------------------------------------
					TASK 3
-----------------------------------------------------------------------------------------------------


SELECT distinct domain_url 
FROM Domain NATURAL JOIN webpage NATURAL JOIN article NATURAL JOIN typ 
WHERE type_name = 'reliable';

π domain_url σ type_name = 'reliable' Domain ⨝ Webpage ⨝ Article ⨝ Typ

-----------------------------------------------------------------------------------------------------

WITH myTable AS (SELECT author_name, COUNT(author) AS value_occurrence 
FROM     author NATURAL JOIN written_by NATURAL JOIN article NATURAL JOIN typ
WHERE    type_name = 'fake'
GROUP BY author_name)
SELECT author_name 
FROM myTable
WHERE value_occurrence = (SELECT MAX(value_occurrence)
                            FROM myTable);

-----------------------------------------------------------------------------------------------------

WITH tags_s AS (SELECT * FROM tags WHERE article_id <= 1000), 
    arts_s AS (SELECT DISTINCT article_id FROM tags_s)

SELECT arts1.article_id, arts2.article_id

FROM arts_s arts1, arts_s arts2

WHERE arts1.article_id < arts2.article_id
AND 1 = ((SELECT COUNT(*)
                FROM (
    (
        SELECT tags_s.keyword_id
        FROM tags_s
        WHERE arts1.article_id = tags_s.article_id 
    ) INTERSECT (
        SELECT tags_s.keyword_id
        FROM tags_s
        WHERE arts2.article_id = tags_s.article_id 
        ) ) as foo
) / (SELECT COUNT(*)
    FROM(
    (
        SELECT tags_s.keyword_id
        FROM tags_s
        WHERE arts1.article_id = tags_s.article_id 
    ) UNION (
        SELECT tags_s.keyword_id
        FROM tags_s
        WHERE arts2.article_id = tags_s.article_id 
    )) as bar 
    ));
