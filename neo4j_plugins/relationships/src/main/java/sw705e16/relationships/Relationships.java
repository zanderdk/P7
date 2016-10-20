package sw705e16.relationships;

import com.google.common.collect.Lists;
import org.neo4j.graphdb.*;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;
import org.neo4j.unsafe.impl.batchimport.cache.idmapping.string.Radix;

import javax.management.relation.Relation;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class Relationships
{
    public static RelationshipType clickStreamType = RelationshipType.withName("clickStream");

    @Context
    public GraphDatabaseService db;

    public static class resultclass {
        public static String title;
        public static Double clickRate;

        resultclass(String Title, Double ClickRate){
            title = Title;
            clickRate = ClickRate;
        }

    }

    public static class RelationshipsList {
        public static List<Object> successorsList;
        public static List<Object> predecessorsList;

        public RelationshipsList(List<Object> successors, List<Object> predecessors) {
            successorsList = successors;
            predecessorsList = predecessors;
        }
    }

    /**
     * Retrieves titles of predecessors and successors for an article
     * @param title The title of the article to find the predecessors and successors of.
     * @return Titles of predecessors and titles of successors.
     */
    @Procedure("getRelationships")
    public Stream<Relationship> getRelationships(@Name("title") String title) {
        // Lookup title in db to find the corresponding node.
        Label pageLabel = Label.label("Page");
        Node thisNode = db.findNode(pageLabel, "title", title);

        // Get all successor relationships
        Iterable<Relationship> relationIterator = thisNode.getRelationships(clickStreamType, Direction.BOTH);

        List<Object> successorList = new ArrayList<>();
        List<Object> predecessorList = new ArrayList<>();

        for (Relationship r : relationIterator) {
            Double clickRate = (Double) r.getProperty("clickRate");
            if(r.getStartNode().getId() == thisNode.getId()){
                successorList.add((Object)new resultclass((String)r.getEndNode().getProperty("title"), clickRate));
            } else {
                predecessorList.add((Object)new resultclass((String)r.getStartNode().getProperty("title"), clickRate));
            }
        }

        List<Relationship> res = new ArrayList<>();

        for (Relationship r : relationIterator){
            res.add(r);
        }

        return StreamSupport.stream(relationIterator.spliterator(), false);
    }
}
