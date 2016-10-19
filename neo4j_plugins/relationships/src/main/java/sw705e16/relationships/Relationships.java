package sw705e16.relationships;

import com.google.common.collect.Lists;
import org.neo4j.graphdb.*;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;
import org.neo4j.unsafe.impl.batchimport.cache.idmapping.string.Radix;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Relationships
{
    public static RelationshipType clickStreamType = RelationshipType.withName("clickStream");

    @Context
    public GraphDatabaseService db;

    public class RelationshipsList {
        public List<String> successorsList;
        public List<String> predecessorsList;

        public RelationshipsList(List<String> successors, List<String> predecessors) {
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
    public Stream<RelationshipsList> getRelationships(@Name("title") String title) {
        // Lookup title in db to find the corresponding node.
        Label pageLabel = Label.label("Page");
        Node thisNode = db.findNode(pageLabel, "title", title);

        // Get all successor relationships
        Iterable<Relationship> successorIt = thisNode.getRelationships(clickStreamType, Direction.OUTGOING);
        List<String> successorList = new ArrayList<>();
        for (Relationship x : successorIt) {
            successorList.add((String)x.getEndNode().getProperty("title"));
        }

        //List<String> successorList = Lists.newArrayList(successorIt).stream().map(
        //        x -> (String)x.getEndNode().getProperty("title")).collect(Collectors.toList());

        // Get all predecessor relationships
        Iterable<Relationship> predecessorIt = thisNode.getRelationships(clickStreamType, Direction.INCOMING);
        List<String> predecessorList = new ArrayList<>();
        for (Relationship x : successorIt) {
            predecessorList.add((String)x.getEndNode().getProperty("title"));
        }
        //List<String> predecessorList = Lists.newArrayList(predecessorIt).stream().map(
        //        x -> (String)x.getStartNode().getProperty("title")).collect(Collectors.toList());

        return Stream.of(new RelationshipsList(predecessorList, successorList));
    }

}
