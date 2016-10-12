package sw705e16.keywordExtraction;

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
        // In a try-block, to make sure we close the driver and session after the test
        try (Driver driver = GraphDatabase.driver(neo4j.boltURI(),
                Config.build().withEncryptionLevel(Config.EncryptionLevel.NONE).toConfig());
             Session session = driver.session()) {

            session.run("CREATE (p:Page {title:'Water', text:'" + waterwiki + "'}) RETURN id(p)");

            StatementResult result = session.run("MATCH (p:Page)\nCALL keywords(p) yield keyword as x return x");


            List<String> expected = Arrays.asList(
                    "standard ambient temperature", "colorless chemical substance", "water strictly refers",
                    "chemical formula", "earth's streams", "living organisms", "liquid state", "hydrogen atoms",
                    "main constituent", "atmospheric humidity");

            //System.out.println(result.list(x -> x.get("x")));

            assertThat(result.list(x -> x.get("x").asString()), is(expected));
        }
    }

    public static String waterwiki = "{{about|general aspects of water|a detailed discussion of its physical and chemical properties|Properties of water|other uses}}\n" +
            "{{pp-move-indef}}\n" +
            "{{Use dmy dates|date=May 2016}}\n" +
            "[[File:Iceberg with hole near Sandersons Hope 2007-07-28 2.jpg|thumb|Water in three states: liquid, solid ([[ice]]), and gas (invisible [[water vapor]] in the air). [[Cloud]]s are accumulations of water droplets, [[condensation|condensed]] from vapor-saturated air.]]\n" +
            "[[File:Water Video.webm|thumb|Video demonstrating states of water present in domestic life.]]\n" +
            "\\'\\'\\'Water\\'\\'\\' is a transparent and nearly colorless chemical substance that is the main constituent of Earth\\'s [[stream]]s, [[lake]]s, and [[ocean]]s, and the [[fluid]]s of most living [[organism]]s.  Its [[chemical formula]] is \\'\\'\\'H<sub>2</sub>O\\'\\'\\', " +
            "meaning that its [[molecule]] contains one [[oxygen]] and two [[hydrogen]] [[atom]]s, that are connected by [[covalent bond]]s. Water strictly refers to the [[liquid]] state of that substance, that prevails at [[standard ambient temperature and pressure]]; " +
            "but it often refers also to its [[solid]] state ([[ice]]) or its [[gas]]eous state ([[steam]] or [[water vapor]]). It also occurs in nature as [[snow]], [[glacier]]s, [[ice pack]]s and [[iceberg]]s, [[cloud]]s, [[fog]], [[dew]], [[aquifer]]s, and atmospheric [[humidity]].\n";
}