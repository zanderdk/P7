// constraints
// CREATE CONTSRAINT ON (p:Page) ASSERT p.title IS UNIQUE;
// CREATE CONTSRAINT ON (c:Category) ASSERT c.name IS UNIQUE;

USING PERIODIC COMMIT 10000

LOAD CSV WITH HEADERS FROM "file:///article_categories.csv" AS row
With row LIMIT 100

MATCH (p:Page {title:row.article_title})
MERGE (c:Category {name:row.category_name})
MERGE (p)-[r:IN_CATEGORY]->(c);
