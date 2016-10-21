// constraints
// CREATE CONTSRAINT ON (p:Page) ASSERT p.title IS UNIQUE;
// CREATE CONTSRAINT ON (c:Category) ASSERT c.name IS UNIQUE;

// categories and relationships with articles 
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///article_categories.csv" AS row
//WITH row LIMIT 100
MATCH (p:Page {title:row.article_title})
//WHERE exists(row.category_name)
MERGE (c:Category {name:row.category_name})
MERGE (p)-[:IN_CATEGORY]->(c);

// category relationships (broader)
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///category_relations_broader.csv" AS row
//WITH row LIMIT 100
MATCH (c1:Category {name:row.category1}),(c2:Category {name:row.category2})
MERGE (c1)-[:BROADER]->(c2);

// category relationships (related)
USING PERIODIC COMMIT 10000
LOAD CSV WITH HEADERS FROM "file:///category_relations_related.csv" AS row
//WITH row LIMIT 100
MATCH (c1:Category {name:row.category1}),(c2:Category {name:row.category2})
MERGE (c1)-[:RELATED]->(c2);
