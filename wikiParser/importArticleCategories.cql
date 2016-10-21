// constraints
// CREATE CONTSRAINT ON (c:Category) ASSERT c.name IS UNIQUE;

USING PERIODIC COMMIT

LOAD CSV WITH HEADERS FROM "article_categories.csv" AS row
With row LIMIT 100

MATCH (p:Page {title:row.article_title})
MERGE (c:Category {name:row.category_title})
MERGE (p)-[r:IN_CATEGORY]->(c)
