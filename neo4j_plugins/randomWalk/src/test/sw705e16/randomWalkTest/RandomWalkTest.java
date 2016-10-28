package sw705e16.randomWalkTest;

import org.apache.commons.io.IOUtils;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.neo4j.driver.v1.*;
import org.neo4j.harness.junit.Neo4jRule;
import sw705e16.randomWalk.RandomWalk;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

public class RandomWalkTest {
    @Rule
    public Neo4jRule neo4j = new Neo4jRule().withProcedure(RandomWalk.class);

    @Test
    public void shouldRandomWalk() throws Throwable {
        String waterwiki = "dfgfdgfh";

        // In a try-block, to make sure we close the driver and session after the test
        try (Driver driver = GraphDatabase.driver(neo4j.boltURI(),
                Config.build().withEncryptionLevel(Config.EncryptionLevel.NONE).toConfig());
             Session session = driver.session()) {

            session.run("CREATE (p:Page {title:'Jesus', text:'" + waterwiki + "'}) RETURN id(p)");
            session.run("CREATE (p:Page {title:'Gabriel', text:'" + waterwiki + "'}) RETURN id(p)");
            session.run("CREATE (p:Page {title:'test', text:'" + waterwiki + "'}) RETURN id(p)");
            session.run("MATCH (a:Page), (b:Page) where a.title = 'Jesus' and b.title = 'Gabriel' CREATE (a)-[:clickStream {click: 200, clickRate: 0.5}]->(b)");
            session.run("MATCH (a:Page), (b:Page) where a.title = 'Gabriel' and b.title = 'test' CREATE (a)-[:clickStream {click: 200, clickRate: 0.5}]->(b)");

            //StatementResult result = session.run("MATCH (p:Page) WHERE p.title = 'Water' CALL keywordSimilarity(p, p) yield similarity as x return x");

            StatementResult result = session.run("CALL randomWalk(\"0\", 1000, 0.1, 5, 1, \"Page\", \"id\", \"clickStream\", \"None\", False)");


            System.out.println(result.next().get("walk"));


//            List<String> expected = Arrays.asList("safe drinking water", "new york", "water management", "pure water",
//                    "boiling point", "safe water", "water intake", "drinking water", "water vapor", "physical properties",
//                    "human consumption", "hydrogen atoms", "liquid water", "billion people", "sea water", "potable water",
//                    "including", "drinking", "pressure", "surface", "cooling", "world", "liquid", "freshwater", "heat",
//                    "temperature", "chemical", "billion", "hydrogen", "industry", "water", "fire", "moon", "sea", "runoff",
//                    "gas", "steam", "pollution", "body", "life", "food", "people");
//
//            //System.out.println(result.list(x -> x.get("x")));
//
//            assertThat(result.list(x -> x.get("x").asString()), is(expected));
        }
    }

}
