package sw705e16.keywordExtraction;

import org.apache.commons.io.IOUtils;
import org.junit.Rule;
import org.junit.Test;
import org.neo4j.driver.v1.*;
import org.neo4j.harness.junit.Neo4jRule;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

public class KeywordExtractorTest {
    @Rule
    public Neo4jRule neo4j = new Neo4jRule().withProcedure(KeywordExtractor.class);

    @Test
    public void shouldExtractKeywords() throws Throwable {
        String waterwiki = IOUtils.toString(getClass().getResourceAsStream("/water.wikitext")).replace("'", "\\'");

        // In a try-block, to make sure we close the driver and session after the test
        try (Driver driver = GraphDatabase.driver(neo4j.boltURI(),
                Config.build().withEncryptionLevel(Config.EncryptionLevel.NONE).toConfig());
             Session session = driver.session()) {

            session.run("CREATE (p:Page {title:'Water', text:'" + waterwiki + "'}) RETURN id(p)");

            StatementResult result = session.run("MATCH (p:Page) WHERE p.title = 'Water' CALL keywordSimilarity(p, p) yield similarity as x return x");


            System.out.println(result.list(x -> x.get("x")));


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