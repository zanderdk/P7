package sw705e16.relationships;

import org.neo4j.graphdb.*;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

import java.util.ArrayList;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

public class Relationships
{
    public static RelationshipType clickStreamType = RelationshipType.withName("clickStream");

    @Context
    public GraphDatabaseService db;


    /**
     * Retrieves titles of predecessors and successors for an article
     * @param title The title of the article to find the predecessors and successors of.
     * @return Titles of predecessors and titles of successors.
     */
    @Procedure("getRelationships")
    public Stream<RelationshipWrapper> getRelationships(@Name("title") String title) {
        // Lookup title in db to find the corresponding node.
        Label pageLabel = Label.label("Page");
        Node thisNode = db.findNode(pageLabel, "title", title);

        // Get all successor relationships
        Iterable<Relationship> relationIterator = thisNode.getRelationships(clickStreamType, Direction.BOTH);

        Stream<Relationship> rels = StreamSupport.stream(relationIterator.spliterator(), false);

        return rels.map( r -> new RelationshipWrapper(r, thisNode) );
    }

    public class RelationshipWrapper {

        public Double clickRate = 0.0;
        public Long clicks = (long)0;
        public String direction = "Outgoing";
        public String otherNode = null;

        public RelationshipWrapper(Relationship r, Node startNode) {
            clickRate = (Double)r.getProperty("clickRate");
            clicks = (Long)r.getProperty("clicks");
            direction = (r.getStartNode().getId() == startNode.getId())? "Outgoing" : "Ingoing";
            otherNode = (String)r.getOtherNode(startNode).getProperty("title");

        }
    }
}
