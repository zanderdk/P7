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
import java.util.Objects;
import java.util.stream.Stream;

public class WeightedShortestPath
{
    public static RelationshipType redirectType = RelationshipType.withName("redirect");
    public static RelationshipType clickStreamType = RelationshipType.withName("clickStream");

    public class Weight {
        public double pst = 0.0;
        public boolean valid = true;

        public Weight add(Weight w) {
            return new Weight(pst + w.pst, w.valid && valid);
        }

        public Weight(double c, boolean v) {
            pst = c;
            valid = v;
        }
    }

    private static Node from = null;
    private static Node to = null;

    public class CostAccum implements CostAccumulator<Weight> {
        @Override
        public Weight addCosts(Weight a, Weight b) {
            return a.add(b);
        }
    }

    public class CostEval implements CostEvaluator<Weight> {

        @Override
        public Weight getCost(Relationship r, Direction d) {
            if(r.isType(redirectType)){
                return new Weight(0.0, true);
            }

            Double value = (Double)r.getProperty("clickRate");
            double pst = value.doubleValue();
            //pst above 1 means more people have used this link than people have visited the source node.
            pst = (pst > 1.0)? 1.0 : pst;
            boolean valid = !(Objects.equals((String) r.getStartNode().getProperty("title"), (String) from.getProperty("title")) &&
                    Objects.equals((String) r.getEndNode().getProperty("title"), (String) to.getProperty("title")));

            System.out.println(valid);
            return new Weight(-1.0 * Math.log10(pst), valid);
        }
    }

    public class WeightComparator implements Comparator<Weight>{

        @Override
        public int compare(Weight o1, Weight o2) {
            if(!o1.valid && !o2.valid) return 0;
            else if (!o1.valid) return 1;
            else if (!o2.valid) return -1;
            else {
                return (int)Math.signum(o1.pst -o2.pst);
            }
        }
    }


    @Context
    public GraphDatabaseService db;

    @Context
    public Log log;

    @Procedure("weightedShortestPath")
    @PerformsWrites
    public Stream<SearchHit> shortestPath(
            @Name("fromStr") String fromStr,
            @Name("toStr") String toStr,
            @Name("number") Long max)
    {
        Label pageLabel = Label.label("Page");
        from = db.findNode(pageLabel, "title", fromStr);
        to = db.findNode(pageLabel, "title", toStr);

        Comparator<Weight> com = new WeightComparator();

        Dijkstra<Weight> d = new Dijkstra(new Weight(0.0, true), from, to, new CostEval(), new CostAccum(), com, Direction.OUTGOING, redirectType, clickStreamType);
        d.limitMaxNodesToTraverse(max);

        Weight cost = d.getCost();
        SearchHit res = cost.valid? new SearchHit(Math.pow(10, -1.0 *cost.pst)) : new SearchHit(null);

        return Stream.of(res);

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
