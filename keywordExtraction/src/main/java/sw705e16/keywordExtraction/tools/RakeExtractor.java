// heavily based on: https://github.com/sujitpal/hia-examples/blob/master/java/cascading-newsclip/src/main/java/com/mycompany/newsclip/RakeExtractor.java

package sw705e16.keywordExtraction.tools;

import org.apache.commons.collections15.Bag;
import org.apache.commons.collections15.bag.HashBag;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.NumberUtils;
import org.apache.commons.lang.StringUtils;
//import org.slf4j.Logger;
//import org.slf4j.LoggerFactory;

import java.io.File;
import java.text.BreakIterator;
import java.util.*;
import java.util.regex.Pattern;

/**
 * Java implementation of the RAKE algorithm, based on a
 * Python/NLTK version I did previously.
 */
public class RakeExtractor {
    private static final int MAX_NUM_WORDS = 4;
    private static final int MIN_KEYWORD_FREQUENCY = 3;
    private static final String STOPWORD_INDICATOR = "__";
    private static final Pattern containsLetter = Pattern.compile("[a-zA-Z]");
   // private static final Logger LOGGER = LoggerFactory.getLogger(RakeExtractor.class);

    public static final RakeExtractor INSTANCE = new RakeExtractor();
    protected Set<String> stopwords;

    private RakeExtractor() {
        stopwords = new HashSet<String>();
        try {
            String stopText = FileUtils.readFileToString(
                    new File("src/main/resources/stopwords.txt"));
            for (String word : stopText.split("\n")) {
                stopwords.add(word);
            }
        } catch (Exception e) {
           // LOGGER.error(e.getMessage(), e);
        }
    }

    public List<String> extract(String text) {
        List<String> sentences = parseSentences(text);
        List<List<String>> phrases = generateCandidatePhrases(sentences);
        Map<String, Float> wordScores = calculateWordScores(phrases);
        final Map<String, Float> phraseScores = calculatePhraseScores(
                phrases, wordScores);
        List<String> ophrases = new ArrayList<String>();
        ophrases.addAll(phraseScores.keySet());
        Collections.sort(ophrases, new Comparator<String>() {
            @Override
            public int compare(String phrase1, String phrase2) {
                return phraseScores.get(phrase2).compareTo(
                        phraseScores.get(phrase1));
            }
        });
        int numPhrases = ophrases.size();
        return ophrases.subList(0, numPhrases / 3);
    }

    protected List<String> parseSentences(String text) {
        List<String> sentences = new ArrayList<String>();
        if (StringUtils.isNotEmpty(text)) {
            BreakIterator sit = BreakIterator.getSentenceInstance();
            sit.setText(text);
            int index = 0;
            while (sit.next() != BreakIterator.DONE) {
                // break on newlines as well to improve keywords for wikitext
                for(String s : text.substring(index, sit.current()).split("\n+")) {
                    sentences.add(s);
                }
                index = sit.current();
            }
        }
        return sentences;
    }

    protected List<List<String>> generateCandidatePhrases(
            List<String> sentences) {
        List<List<String>> phrases = new ArrayList<List<String>>();
        for (String sentence : sentences) {
            List<String> owords = new ArrayList<String>();
            List<String> words = parseWords(
                    StringUtils.lowerCase(sentence));
            for (String word : words) {
                if (stopwords.contains(word)) {
                    owords.add(STOPWORD_INDICATOR);
                } else {
                    owords.add(word);
                }
            }
            List<String> phrase = new ArrayList<String>();
            for (String word : owords) {
                if (STOPWORD_INDICATOR.equals(word) ||
                        word.matches("\\p{Punct}")) {
                    if (phrase.size() > 0 && phrase.size() <= MAX_NUM_WORDS)
                        phrases.add(phrase);
                    phrase = new ArrayList<String>();
                } else {
                    if(containsLetter.matcher(word).find())
                        phrase.add(word);
                }
            }
        }

        return phrases;
    }

    protected List<String> parseWords(String sentence) {
        List<String> words = new ArrayList<String>();
        BreakIterator wit = BreakIterator.getWordInstance();
        wit.setText(sentence);
        int index = 0;
        while (wit.next() != BreakIterator.DONE) {
            String word = sentence.substring(index, wit.current());
            if (StringUtils.isNotBlank(word)) {
                words.add(word);
            }
            index = wit.current();
        }
        return words;
    }

    @SuppressWarnings("deprecation")
    protected Map<String, Float> calculateWordScores(
            List<List<String>> phrases) {
        Bag<String> wordFreq = new HashBag<String>();
        Bag<String> wordDegree = new HashBag<String>();
        for (List<String> phrase : phrases) {
            int degree = -1;
            for (String word : phrase) {
                if (NumberUtils.isNumber(word)) continue;
                else degree++;
            }
            for (String word : phrase) {
                wordFreq.add(word);
                wordDegree.add(word, degree); // other words
            }
        }
        for (String word : wordFreq.uniqueSet()) {
            wordDegree.add(word, wordFreq.getCount(word)); // itself
        }
        Map<String, Float> wordScores = new HashMap<String, Float>();
        for (String word : wordFreq.uniqueSet()) {
            float score = (float) wordDegree.getCount(word) /
                    (float) wordFreq.getCount(word);
            wordScores.put(word, score);
        }
        return wordScores;
    }

    protected Map<String, Float> calculatePhraseScores(
            List<List<String>> phrases,
            Map<String, Float> wordScores) {
        Map<String, Float> phraseScores = new HashMap<String, Float>();
        Map<String, Integer> phraseFreq = new HashMap<String, Integer>();
        for (List<String> phrase : phrases) {
            float phraseScore = 0.0F;
            for (String word : phrase) {
                if (wordScores.containsKey(word)) {
                    phraseScore += wordScores.get(word);
                }
            }

            String phraseString = StringUtils.join(phrase, " ");

            phraseFreq.putIfAbsent(phraseString, 0);
            phraseFreq.compute(phraseString, (k, v) -> v + 1);

            if(phraseFreq.get(phraseString) > MIN_KEYWORD_FREQUENCY)
                phraseScores.put(phraseString, phraseScore);

        }
        return phraseScores;
    }
}