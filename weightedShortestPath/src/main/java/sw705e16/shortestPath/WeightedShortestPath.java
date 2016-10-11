package sw705e16.shortestPath;

import org.neo4j.graphalgo.CostAccumulator;
import org.neo4j.graphalgo.CostEvaluator;
import org.neo4j.graphalgo.impl.shortestpath.Dijkstra;
import org.neo4j.graphdb.*;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.PerformsWrites;
import org.neo4j.procedure.Procedure;

import java.util.Comparator;
import java.util.stream.Stream;

public class WeightedShortestPath
{
    public static RelationshipType redirectType = RelationshipType.withName("redirect");
    public static RelationshipType clickStreamType = RelationshipType.withName("clickStream");

    public class CostAccum implements CostAccumulator<Double> {
        @Override
        public Double addCosts(Double a, Double b) {
            return a + b;
        }
    }

    public class CostEval implements CostEvaluator<Double> {

        @Override
        public Double getCost(Relationship r, Direction d) {
            if(r.isType(redirectType)){
                return 0.0;
            }


            Double value = (Double)r.getProperty("clickRate");
            double pst = value.doubleValue();
            pst = (pst > 1.0)? 0.0 : 1.0 - pst;
            return new Double(pst);
        }
    }


    @Context
    public GraphDatabaseService db;

    @Context
    public Log log;

    @Procedure("weightedShortestPath")
    @PerformsWrites
    public Stream<SearchHit> shortestPath( @Name("fromStr") String fromStr, @Name("toStr") String toStr )
    {
        Label pageLabel = Label.label("Page");
        Node from = db.findNode(pageLabel, "title", fromStr);
        Node to = db.findNode(pageLabel, "title", toStr);

        Comparator<Double> com = Comparator.naturalOrder();

        Dijkstra<Double> d = new Dijkstra<Double>(0.0, from, to, new CostEval(), new CostAccum(), com, Direction.OUTGOING, redirectType, clickStreamType);

        return Stream.of(new SearchHit(d.getCost()));

    }


    public static class SearchHit
    {
        public Double Cost;

        public SearchHit( Double cost )
        {
            this.Cost = cost;
        }
    }


}
