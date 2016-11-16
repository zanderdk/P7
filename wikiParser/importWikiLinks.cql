USING PERIODIC COMMIT 10000
LOAD CSV FROM "file:///page_links.csv" AS row FIELDTERMINATOR ' '
//WITH row LIMIT 1
MATCH (from:Page {title:row[0]}),(to:Page {title:row[1]})
//no links from redirects
WHERE not exists(from.redirect)
MERGE (from)-[:linkTo]->(to);
