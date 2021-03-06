package sw705e16.shortestPath;

import org.neo4j.graphalgo.CostAccumulator;
import org.neo4j.graphalgo.CostEvaluator;
import org.neo4j.graphalgo.impl.shortestpath.Dijkstra;
import org.neo4j.graphdb.*;
import org.neo4j.graphdb.Label;
import org.neo4j.logging.Log;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;

import com.google.common.collect.*;


import java.util.*;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class WeightedShortestPath
{
    public static RelationshipType redirectType = RelationshipType.withName("redirect");
    public static RelationshipType clickStreamType = RelationshipType.withName("LinksTo");

    public class Output {
        public Path path;

        public Output(Path p) {
            path = p;
        }
    }

    public class aPath implements Path {

        private List<Node> _nodes;
        private List<Relationship> _rels;
        Dijkstra<Weight> dik;

        public aPath(Dijkstra<Weight> d) {
            _nodes = d.getPathAsNodes();
            _rels = d.getPathAsRelationships();
            dik = d;
        }

        @Override
        public Node startNode() {
            return _nodes.get(0);
        }

        @Override
        public Node endNode() {
            return _nodes.get(_nodes.size() - 1);
        }

        @Override
        public Relationship lastRelationship() {
            return _rels.get(_rels.size() - 1);
        }

        @Override
        public Iterable<Relationship> relationships() {
            return _rels;
        }

        @Override
        public Iterable<Relationship> reverseRelationships() {
            List<Relationship> shallowCopy = _rels.subList(0, _rels.size());
            Collections.reverse(shallowCopy);
            return shallowCopy;
        }

        @Override
        public Iterable<Node> nodes() {
            return _nodes;
        }

        @Override
        public Iterable<Node> reverseNodes() {
            List<Node> shallowCopy = _nodes.subList(0, _nodes.size());
            Collections.reverse(shallowCopy);
            return shallowCopy;
        }

        @Override
        public int length() {
            return _nodes.size();
        }

        @Override
        public String toString() {
            return "test";
        }

        @Override
        public Iterator<PropertyContainer> iterator() {
            return dik.getPath().iterator();
        }
    }

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

    private static Node pageA = null;
    private static Node pageB = null;

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

            Double value = 1.0;
            double pst = value.doubleValue();
            //pst above 1 means more people have used this link than people have visited the source node.
            pst = (pst > 1.0)? 1.0 : pst;
            boolean valid = !(Objects.equals((String) r.getStartNode().getProperty("title"), (String) pageA.getProperty("title")) &&
                    Objects.equals((String) r.getEndNode().getProperty("title"), (String) pageB.getProperty("title")));

            return new Weight(pst, valid);
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


    public Dijkstra<Weight> getDijkstra(
            @Name("fromStr") String fromStr,
            @Name("toStr") String toStr,
            @Name("number") Long max)
    {
        Label pageLabel = Label.label("Page");
        pageA = db.findNode(pageLabel, "title", fromStr);
        pageB = db.findNode(pageLabel, "title", toStr);

        Comparator<Weight> com = new WeightComparator();

        Weight maxW = new Weight(max, true);

        Dijkstra<Weight> d = new Dijkstra(new Weight(0.0, true), pageA, pageB, new CostEval(), new CostAccum(), com, Direction.OUTGOING, redirectType, clickStreamType);
        d.limitMaxCostToTraverse(maxW);

        return d;
    }

    public static <E> Collection<E> makeCollection(Iterable<E> iter) {
        Collection<E> list = new ArrayList<E>();
        for (E item : iter) {
            list.add(item);
        }
        return list;
    }

    @Procedure("weightedShortestPath")
    public Stream<Output> weightedShortestPath(
            @Name("fromStr") String fromStr,
            @Name("toStr") String toStr,
            @Name("number") Long max)
    {

        Dijkstra<Weight> d = getDijkstra(fromStr, toStr, max);


        Output res = new Output(new aPath(d));
        return Stream.of(res);

    }

    @Procedure("weightedShortestPathCost")
    public Stream<SearchHit> weightedShortestPathCost(
            @Name("fromStr") String fromStr,
            @Name("toStr") String toStr,
            @Name("number") Long max)
    {
        Dijkstra<Weight> d = getDijkstra(fromStr, toStr, max);

        Weight cost = d.getCost();
        if (cost == null) return Stream.of(new SearchHit(0.0));
        SearchHit res = cost.valid? new SearchHit(cost.pst) : new SearchHit(0.0);

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
