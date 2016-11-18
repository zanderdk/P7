package sw705e16.randomWalk;

import com.google.common.collect.Collections2;
import com.google.common.collect.Lists;
import org.javatuples.Pair;
import org.neo4j.graphdb.*;
import org.neo4j.kernel.configuration.SystemPropertiesConfiguration;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

import java.util.*;
import java.util.function.Predicate;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class RandomWalk
{
    static RelationshipType redirectType = RelationshipType.withName("REDIRECTS_TO");


    @Context
    public GraphDatabaseService db;

    public static List<Long> lastNodes = new ArrayList<>();

    public class Record{
        public String walk = "";
        public Record(String w) {
            walk = w;
        }
    }

    /**
     * Retrieves titles of predecessors and successors for an article
     * @param pageTitle The title of the article to find the predecessors and successors of.
     * @return Titles of predecessors and titles of successors.
     */
    @Procedure("randomWalk")
    public Stream<Record> randomWalk(@Name("title") String pageTitle,
                                     @Name("p") Double p,
                                     @Name("q") Double q,
                                     @Name("l") Long l,
                                     @Name("z") Double z,
                                     @Name("directed") Boolean directed) {
        Label pageLabel = Label.label("Page");
        RelationshipType linksToType = RelationshipType.withName("LINKS_TO");


        Node startNode = db.findNode(pageLabel, "title", pageTitle);

        ArrayList<Node> walk = new ArrayList<Node>();
        walk.add(startNode);
        int walkLength = 1;

        while(walkLength < l) {
            // get last node in walk
            Node cur = walk.get(walkLength-1);


            Relationship redirectRel;
            // we want to follow redirects until we reach a Page
            do {
                // is cur a redirect page?
                redirectRel = cur.getSingleRelationship(redirectType, Direction.OUTGOING);
                // if rediretRel was not null, cur is a redirect, so follow that redirect to a page
                cur = (redirectRel != null)? redirectRel.getOtherNode(cur) : cur;
            } while (redirectRel == null);


            Direction d = (directed)? Direction.OUTGOING : Direction.BOTH;
            Iterable<Relationship> cur_nbrs = cur.getRelationships(d, linksToType);

            ArrayList<Node> aliasList = new ArrayList<>();
            ArrayList<Double> propList = new ArrayList<>();
            // if we are at the start node, we can only go out from start node
            if (walkLength == 1) {
                for(Relationship rel: cur_nbrs) {
                    Node end = rel.getOtherNode(cur);
                    // ignore self loops
                    if(end.getId() == cur.getId())
                        continue;
                    Double w = (1.0/z)/q;
                    aliasList.add(end);
                    propList.add(w);

                    lastNodes.add(end.getId());
                }
            }
            else {
                Node prev = walk.get(walkLength-2);
                Long prevId = prev.getId();
                ArrayList<Long> newLast = new ArrayList<>();
                for(Relationship rel: cur_nbrs) {
                    Node end = rel.getOtherNode(cur);
                    Long endId = end.getId();
                    // ignore self loops
                    if(endId == cur.getId())
                        continue;
                    Double w = (Objects.equals(endId, prevId))? 1.0/p : lastNodes.contains(endId)? 1.0 : 1.0/q;
                    aliasList.add(end);
                    propList.add(w);

                    newLast.add(endId);
                }
                lastNodes = newLast;
            }
            if(aliasList.isEmpty())
                break;
            AliasMethod m = new AliasMethod(propList);
            walk.add(aliasList.get(m.next()));
            walkLength++;
        }

        //walk.stream().collect()

        String retString = "";

        for(Node n : walk) {
            retString += (" " + n.getProperty("title"));
        }

        return Stream.of(retString).map(Record::new);
    }

}
