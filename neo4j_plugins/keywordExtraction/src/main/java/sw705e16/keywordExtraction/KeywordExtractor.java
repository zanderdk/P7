package sw705e16.keywordExtraction;

import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import com.google.common.collect.Sets;
import org.apache.commons.io.IOUtils;
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

import java.io.IOException;
import java.util.Arrays;
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

    private static Set<String> stopwordsSet = null;

    public KeywordExtractor() {
        try {
            String stopText = IOUtils.toString(getClass().getResourceAsStream("/stopwords.txt"));
            String[] stopwords = stopText.split("\n");
            stopwordsSet = new HashSet<>(Arrays.asList(stopwords));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static LoadingCache<Node, List<String>> keywordsCache = CacheBuilder.newBuilder()
            .maximumSize(1000)
            .build(
                    new CacheLoader<Node, List<String>>() {
                        public List<String> load(Node node) throws Exception {
                            String title = (String) node.getProperty("title");
                            String wikitext = (String) node.getProperty("text");

                            String plainText = wikiToText(wikitext, title);

                            List<String> keywords = RakeExtractor.INSTANCE.extract(plainText);

                            return keywords;
                        }
                    });

    private static String wikiToText(String wikitext, String title) throws Exception {
        // Retrieve a page
        PageTitle pageTitle = PageTitle.make(wikiConfig, title);
        PageId pageId = new PageId(pageTitle, -1);

        // Compile the retrieved page
        EngProcessedPage cp = engine.postprocess(pageId, wikitext, null);

        return (String) textConverter.go(cp.getPage());
    }

    private static List<String> limitList(List<String> list, int limit) {
        return list.size() > limit ? list.subList(0, limit) : list;
    }

    private List<String> extractKeywords(Node node) throws Exception {
        return keywordsCache.get(node);
    }

    @Procedure("keywords")
    public Stream<Keywords> keywords(@Name("node") Node node) throws Exception {
        return extractKeywords(node).stream().map(Keywords::new);
    }

    @Procedure("text")
    public Stream<PlainText> plaintext(@Name("node") Node node) throws Exception {
        String title = (String) node.getProperty("title");
        String wikitext = (String) node.getProperty("text");

        String plainText = wikiToText(wikitext, title);

        return Stream.of(new PlainText(plainText));
    }

    @Procedure("words")
    public Stream<Words> words(@Name("node") Node node) throws Exception {
        String title = (String) node.getProperty("title");
        String wikitext = (String) node.getProperty("text");

        String plainText = wikiToText(wikitext, title);

        // split punctuation, whitespace and digits
        String[] words = plainText.toLowerCase().split("[\\p{Punct}\\s\\d]+");

        Set<String> wordsSet = new HashSet<>(Arrays.asList(words));

        return Sets.difference(wordsSet, stopwordsSet).stream().map(Words::new);
    }

    /* Deprecated */
    @Procedure("keywordSimilarity")
    public Stream<Similarity> keywordSimilarity(@Name("node1") Node node1, @Name("node2") Node node2, @Name("limit") Long limit) throws Exception {
        Set<String> keywords1 = new HashSet<>(limitList(extractKeywords(node1), limit.intValue()));
        Set<String> keywords2 = new HashSet<>(limitList(extractKeywords(node2), limit.intValue()));

        double intersectionLength = Sets.intersection(keywords1, keywords2).size();
        double unionLength = Sets.union(keywords1, keywords2).size();

        if (unionLength == 0) return Stream.of(new Similarity(0));

        return Stream.of(new Similarity(intersectionLength / unionLength));
    }

    public static class PlainText {
        public String text;

        public PlainText(String text) {
            this.text = text;
        }
    }

    public static class Words {
        public String words;

        public Words(String words) {
            this.words = words;
        }
    }

    public static class Keywords {
        public String keyword;

        public Keywords(String keyword) {
            this.keyword = keyword;
        }
    }

    public static class Similarity {
        public double similarity;

        public Similarity(double similarity) {
            this.similarity = similarity;
        }
    }

}
