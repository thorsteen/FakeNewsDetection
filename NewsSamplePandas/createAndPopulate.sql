DROP TABLE Written_by;
DROP TABLE Tags;
DROP TABLE Webpage;
DROP TABLE Article CASCADE;
DROP TABLE Typ;
DROP TABLE Domain;
DROP TABLE Author;
DROP TABLE Keyword;

CREATE TABLE Keyword (
  keyword_id serial,
  keyword varchar(128),
  PRIMARY KEY (keyword_id)
);

CREATE TABLE Author (
  author_id serial,
  author_name varchar(64),
  PRIMARY KEY (author_id)
);

CREATE TABLE Domain (
  domain_id serial,
  domain_url varchar(1024),
  PRIMARY KEY (domain_id)
);

CREATE TABLE Typ (
  type_id serial,
  type_name varchar(64),
  PRIMARY KEY (type_id)
);

CREATE TABLE Article (
  article_id integer,
  title varchar (512),
  content text,
  summary text,
  meta_description text,
  type_id integer REFERENCES Typ(type_id),
  inserted_at timestamp,
  updated_at timestamp,
  scraped_at timestamp,
  PRIMARY KEY (article_id)
);

CREATE TABLE Webpage (
  url varchar(1024),
  article_id integer REFERENCES Article(article_id),
  domain_id integer REFERENCES Domain(domain_id)
);

CREATE TABLE Tags (
  article_id integer REFERENCES Article(article_id),
  keyword_id integer REFERENCES Keyword(keyword_id)
);

CREATE TABLE Written_by (
  article_id integer REFERENCES Article(article_id),
  author_id integer REFERENCES Author(author_id)
);

SET CLIENT_ENCODING TO 'utf8';

\copy keyword       from 'keyword_entity.csv'       delimiter','csv;
\copy author        from 'author_entity.csv'        delimiter','csv;
\copy typ           from 'type_entity.csv'          delimiter','csv;
\copy domain        from 'domain_entity.csv'        delimiter','csv;
\copy article       from 'article_entity.csv'       delimiter'^'csv;
\copy tags          from 'tags_relation.csv'        delimiter','csv;
\copy written_by    from 'writtenBy_relation.csv'   delimiter','csv;
\copy webpage       from 'webpage_relation.csv'     delimiter','csv;
