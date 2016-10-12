package sw705e16.keywordExtraction;

import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Label;
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

import java.util.List;
import java.util.stream.Stream;

public class KeywordExtractor {
    @Context
    public GraphDatabaseService db;

    private static WikiConfig wikiConfig = DefaultConfigEnWp.generate();
    private static WtEngineImpl engine = new WtEngineImpl(wikiConfig);
    private static final int wrapCol = 80;
    private static TextConverter textConverter = new TextConverter(wikiConfig, wrapCol);

    private static String wikiToText(String wikitext, String title) throws Exception {
        // Retrieve a page
        PageTitle pageTitle = PageTitle.make(wikiConfig, title);
        PageId pageId = new PageId(pageTitle, -1);

        // Compile the retrieved page
        EngProcessedPage cp = engine.postprocess(pageId, wikitext, null);

        return (String) textConverter.go(cp.getPage());
    }

    @Procedure("keywords")
    public Stream<SearchHit> keywords(@Name("title") String title) throws Exception {
        Label pageLabel = Label.label("Page");
        Node node = db.findNode(pageLabel, "title", title);

        String wikitext = (String) node.getProperty("text");

        String plainText = wikiToText(wikitext, title);

        List<String> keywords = RakeExtractor.INSTANCE.extract(plainText);

        return Stream.of(new SearchHit(keywords));
    }

    public static class SearchHit {
        public List<String> keywords;

        public SearchHit(List<String> keywords) {
            this.keywords = keywords;
        }
    }

}
