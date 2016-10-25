package sw705e16.randomWalk;

import org.javatuples.Pair;
import org.neo4j.graphdb.*;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class RandomWalk
{
    @Context
    public GraphDatabaseService db;

    public static Stream<Long> lastNodes = null;

    public static Label pageLabel = Label.label("Page");

    public class Record{
        public String walk = "";
        public Record(String w) {
            walk = w;
        }
    }

    public class PairComp implements Comparator<Pair<Node, Double>> {

        @Override
        public int compare(Pair<Node, Double> o1, Pair<Node, Double> o2) {
            if (o1.getValue1() < o2.getValue1()) return -1;
            if (o1.getValue1() > o2.getValue1()) return 1;
            return 0;
        }

        @Override
        public boolean equals(Object obj) {
            return false;
        }
    }

    /**
     * Retrieves titles of predecessors and successors for an article
     * @param title The title of the article to find the predecessors and successors of.
     * @return Titles of predecessors and titles of successors.
     */
    @Procedure("randomWalk")
    public Stream<Record> randomWalk(@Name("title") String title,
                                     @Name("p") Double p,
                                     @Name("q") Double q,
                                     @Name("l") Long l,
                                     @Name("r") Long r,
                                     @Name("z") Double z,
                                     @Name("label") String label,
                                     @Name("weight") String weight) {

        RelationshipType clickStreamType = RelationshipType.withName(label);
        Node thisNode = db.findNode(pageLabel, "title", title);
        ArrayList<Node> walk = new ArrayList<Node>();
        walk.add(thisNode);
        boolean unWeighted = (weight.equals("None"));

        Comparator<Pair<Node, Double>> comp = new PairComp();

        int walkLength = 1;

        while(walkLength < l) {
            Node cur = walk.get(walkLength-1);
            Iterable<Relationship> rels = cur.getRelationships(Direction.OUTGOING, clickStreamType);
            Stream<Relationship> cur_nbrs = StreamSupport.stream(rels.spliterator(), false);
            if (walkLength == 1) {
                Stream<Pair<Node, Double>> ww = cur_nbrs.map((rel) -> new Pair<>(rel.getEndNode(), unWeighted? 1.0 : ((Double)rel.getProperty(weight)/z)/q ));
                lastNodes = ww.map((par) -> par.getValue0().getId());
                Optional<Pair<Node, Double>> max = ww.max(comp);
                if (!max.isPresent()) break;
                walk.add(max.get().getValue0());
            }
            else {
                Node prev = walk.get(walkLength-2);
                Long prevId = prev.getId();

                Stream<Pair<Node, Double>> ww = cur_nbrs.map((rel) -> new Pair<>(rel.getEndNode(), unWeighted? 1.0 : ((Double)rel.getProperty(weight)/z) ));
                Optional<Pair<Node, Double>> max = ww.map((par) ->
                {
                    Long thisId = par.getValue0().getId();
                    Predicate<Long> pred = (Long last) -> last.equals(thisId);
                    Double value = (Objects.equals(prevId, thisId))? (1.0/p) : (lastNodes.filter(pred).count() == 1)? 1.0 : (1.0/q);
                    value *= par.getValue1();
                    return new Pair<Node, Double>(par.getValue0(), value);
                } ).max(comp);

                lastNodes = ww.map(n -> n.getValue0().getId());

                if (!max.isPresent()) break;
                walk.add(max.get().getValue0());
            }

        }

        String retString = "";

        for(Node n : walk) {
            retString += (" " + (String)n.getProperty("title"));
        }

        return Stream.of(retString).map(Record::new);
    }

}
