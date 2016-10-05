package dk.aau.cs.wikitext;

import org.sweble.wikitext.engine.PageId;
import org.sweble.wikitext.engine.PageTitle;
import org.sweble.wikitext.engine.WtEngineImpl;
import org.sweble.wikitext.engine.config.WikiConfig;
import org.sweble.wikitext.engine.nodes.EngProcessedPage;
import org.sweble.wikitext.engine.utils.DefaultConfigEnWp;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.stream.Collectors;

public class App {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) {
            System.err.println("Usage: java -jar wikitext-parser.jar \"Artile Title\" < article.wikitext");
            return;
        }

        String title = args[0];

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));

        String wikitext = String.join("\n", br.lines().collect(Collectors.toList()));

        String text = run(wikitext, title);
        System.out.println(text);
    }

    static String run(String wikitext, String title) throws Exception {
        // Set-up a simple wiki configuration
        WikiConfig config = DefaultConfigEnWp.generate();

        final int wrapCol = 80;

        // Instantiate a compiler for wiki pages
        WtEngineImpl engine = new WtEngineImpl(config);

        // Retrieve a page
        PageTitle pageTitle = PageTitle.make(config, title);

        PageId pageId = new PageId(pageTitle, -1);

        // Compile the retrieved page
        EngProcessedPage cp = engine.postprocess(pageId, wikitext, null);

        TextConverter p = new TextConverter(config, wrapCol);
        return (String) p.go(cp.getPage());
    }

}
