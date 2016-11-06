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

    public Relationship backRelasion(Node prev, Node cur, String weight) {
        return new Relationship() {
            @Override
            public long getId() {
                return 0;
            }

            @Override
            public void delete() {

            }

            @Override
            public Node getStartNode() {
                return cur;
            }

            @Override
            public Node getEndNode() {
                return prev;
            }

            @Override
            public Node getOtherNode(Node node) {
                return (node.getId() == cur.getId())? prev : (node.getId() == prev.getId())? cur : null;
            }

            @Override
            public Node[] getNodes() {
                return new Node[0];
            }

            @Override
            public RelationshipType getType() {
                return null;
            }

            @Override
            public boolean isType(RelationshipType relationshipType) {
                return false;
            }

            @Override
            public GraphDatabaseService getGraphDatabase() {
                return null;
            }

            @Override
            public boolean hasProperty(String s) {
                return false;
            }

            @Override
            public Object getProperty(String s) {
                return (Objects.equals(s, weight))? 0.0 : null;
            }

            @Override
            public Object getProperty(String s, Object o) {
                return null;
            }

            @Override
            public void setProperty(String s, Object o) {

            }

            @Override
            public Object removeProperty(String s) {
                return null;
            }

            @Override
            public Iterable<String> getPropertyKeys() {
                return null;
            }

            @Override
            public Map<String, Object> getProperties(String... strings) {
                return null;
            }

            @Override
            public Map<String, Object> getAllProperties() {
                return null;
            }
        };
    }

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
     * @param title The title of the article to find the predecessors and successors of.
     * @return Titles of predecessors and titles of successors.
     */
    @Procedure("randomWalk")
    public Stream<Record> randomWalk(@Name("title") String title,
                                     @Name("p") Double p,
                                     @Name("q") Double q,
                                     @Name("l") Long l,
                                     @Name("z") Double z,
                                     @Name("nodeLabel") String nodeLabel,
                                     @Name("field") String field,
                                     @Name("label") String label,
                                     @Name("weight") String weight,
                                     @Name("directed") Boolean directed,
                                     @Name("hack") Boolean hack) {
        Label pageLabel = Label.label(nodeLabel);
        RelationshipType clickStreamType = RelationshipType.withName(label);
        Node thisNode;
        if (field.equals("id"))
            thisNode = db.getNodeById(Long.parseLong(title));
        else
            thisNode = db.findNode(pageLabel, field, title);
        ArrayList<Node> walk = new ArrayList<Node>();
        walk.add(thisNode);
        boolean unWeighted = (weight.equals("None"));
        int walkLength = 1;

        while(walkLength < l) {
            Node cur = walk.get(walkLength-1);
            Direction d = (directed)? Direction.OUTGOING : Direction.BOTH;
            Iterable<Relationship> rels = cur.getRelationships(d, clickStreamType);
            ArrayList<Relationship> cur_nbrs =  Lists.newArrayList(rels);

            ArrayList<Node> aliasList = new ArrayList<>();
            ArrayList<Double> propList = new ArrayList<>();
            if (walkLength == 1) {

                for(Relationship rel: cur_nbrs) {
                    // ignore this relationship, to simulate test data we will not walk through
                    if (rel.getProperty("testData") != null) {
                        continue;
                    }
                    Node end = rel.getOtherNode(cur);
                    if(end.getId() == cur.getId())
                        continue;
                    Double w = (unWeighted)? 1.0 : (Double)rel.getProperty(weight);
                    w = (w/z)/q;
                    aliasList.add(end);
                    propList.add(w);

                    lastNodes.add(end.getId());
                }

            }
            else {
                Node prev = walk.get(walkLength-2);
                Long prevId = prev.getId();
                if(directed && hack)
                    cur_nbrs.add(backRelasion(prev, cur, weight));
                ArrayList<Long> newLast = new ArrayList<>();
                for(Relationship rel: cur_nbrs) {
                    // ignore this relationship, to simulate test data we will not walk through
                    if (rel.getProperty("testData") != null) {
                        continue;
                    }
                    Node end = rel.getOtherNode(cur);
                    Long endId = end.getId();
                    if(endId == cur.getId())
                        continue;
                    Double w = (Objects.equals(endId, prevId))? 1.0/p : lastNodes.contains(endId)? 1.0 : 1.0/q;
                    w = w* ((unWeighted)? 1.0 : (Double)rel.getProperty(weight));
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

        String retString = "";

        for(Node n : walk) {
            retString += (" " + n.getProperty(field));
        }

        return Stream.of(retString).map(Record::new);
    }

}
