package sw705e16.keywordExtraction;

import com.google.common.collect.Sets;
import org.apache.commons.collections15.SetUtils;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;
import org.sweble.wikitext.engine.PageId;
import org.sweble.wikitext.engine.PageTitle;
import org.sweble.wikitext.engine.WtEngineImpl;
import org.sweble.wikitext.engine.config.WikiConfig;
import org.sweble.wikitext.engine.nodes.EngProcessedPage;
import org.sweble.wikitext.engine.utils.DefaultConfigEnWp;
import sw705e16.keywordExtraction.tools.RakeExtractor;
import sw705e16.keywordExtraction.tools.TextConverter;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

public class KeywordExtractor {
    @Context
    public GraphDatabaseService db;

    private static WikiConfig wikiConfig = DefaultConfigEnWp.generate();
    private static WtEngineImpl engine = new WtEngineImpl(wikiConfig);
    private static TextConverter textConverter = new TextConverter(wikiConfig, 10000);

    private static String wikiToText(String wikitext, String title) throws Exception {
        // Retrieve a page
        PageTitle pageTitle = PageTitle.make(wikiConfig, title);
        PageId pageId = new PageId(pageTitle, -1);

        // Compile the retrieved page
        EngProcessedPage cp = engine.postprocess(pageId, wikitext, null);

        return (String) textConverter.go(cp.getPage());
    }

    public List<String> keywords(Node node, int limit) throws Exception {
        String title = (String) node.getProperty("title");
        String wikitext = (String) node.getProperty("text");

        String plainText = wikiToText(wikitext, title);

        List<String> keywords = RakeExtractor.INSTANCE.extract(plainText);

        return keywords.size() > limit ? keywords.subList(0, limit) : keywords;
    }

    @Procedure("keywordSimilarity")
    public Stream<SearchHit> keywordSimilarity(@Name("node1") Node node1, @Name("node2") Node node2, @Name("limit") Long limit) throws Exception {
        Set<String> keywords1 = new HashSet<>(keywords(node1, limit.intValue()));
        Set<String> keywords2 = new HashSet<>(keywords(node2, limit.intValue()));

        double intersectionLength = Sets.intersection(keywords1, keywords2).size();

        double unionLength = Sets.union(keywords1, keywords2).size();

        return Stream.of(new SearchHit(intersectionLength/unionLength));
    }

    public static class SearchHit {
        public double similarity;

        public SearchHit(double similarity) {
            this.similarity = similarity;
        }
    }

}
