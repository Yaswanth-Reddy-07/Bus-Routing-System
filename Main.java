import java.text.DecimalFormat;
import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.util.*;

class TransportSystem {
    City head;
    Map<String, ComfortInfo> comfortLevels;

    public static void main(String[] args) {
        TransportSystem transport = new TransportSystem();
        Scanner scanner = new Scanner(System.in);

        String[] cities = {"Coimbatore", "Palakkad", "Chennai", "Bangalore", "Mumbai", "Delhi"};
        for (String city : cities) {
            transport.addCity(city);
        }

        NetworkHelper.createFullyConnectedNetwork(transport);

        transport.showCities();

        System.out.print("\nEnter departure city: ");
        String startCity = scanner.nextLine().trim();

        System.out.print("Enter destination: ");
        String endCity = scanner.nextLine().trim();

        System.out.println("\nOptimization priority:");
        System.out.println("1. Time (fastest route)");
        System.out.println("2. Cost (cheapest route)");
        System.out.println("3. Comfort (most comfortable route)");

        System.out.print("Select priority (1-3, default is Time): ");
        String priorityChoice = scanner.nextLine().trim();

        String priority = "time";
        if (priorityChoice.equals("2")) {
            priority = "cost";
        } else if (priorityChoice.equals("3")) {
            priority = "comfort";
        }

        System.out.println("\nSelected Route: " + startCity + " to " + endCity);
        System.out.println("Optimization: " + priority.substring(0, 1).toUpperCase() + priority.substring(1));

        transport.bookTrip(startCity, endCity, priority);

        scanner.close();
    }

    public TransportSystem() {
        this.head = null;
        this.comfortLevels = new HashMap<>();
        comfortLevels.put("Economy", new ComfortInfo(1.0, "Basic comfort"));
        comfortLevels.put("Standard", new ComfortInfo(1.3, "Comfortable journey"));
        comfortLevels.put("Premium", new ComfortInfo(1.8, "Luxury experience"));
        comfortLevels.put("Express", new ComfortInfo(1.5, "Fast service"));
    }

    public boolean addCity(String name) {
        if (getCity(name) != null) return false;
        City city = new City(name);
        if (head == null) head = city;
        else {
            City temp = head;
            while (temp.nextCity != null)
                temp = temp.nextCity;
            temp.nextCity = city;
        }
        return true;
    }

    public boolean addRoute(String start, String end, String comfort, double cost, double duration) {
        City origin = getCity(start);
        City destination = getCity(end);
        if (origin == null || destination == null) return false;
        origin.addConnection(end, comfort, cost, duration);
        destination.addConnection(start, comfort, cost, duration);
        return true;
    }

    public City getCity(String name) {
        City temp = head;
        while (temp != null) {
            if (temp.name.equalsIgnoreCase(name)) return temp;
            temp = temp.nextCity;
        }
        return null;
    }

    public void showCities() {
        if (head == null) {
            System.out.println("\nNo cities available for booking.");
            return;
        }
        City temp = head;
        System.out.println("\nCities Available For Booking:");
        while (temp != null) {
            System.out.println("- " + temp.name);
            temp = temp.nextCity;
        }
    }

    public boolean bookTrip(String start, String destination, String priority) {
        start = start.trim();
        destination = destination.trim();

        if (start.isEmpty() || destination.isEmpty()) {
            System.out.println("\nError: Both departure and destination cities must be provided.");
            return false;
        }

        if (start.equalsIgnoreCase(destination)) {
            System.out.println("\nError: Departure and destination cities cannot be the same.");
            return false;
        }

        City startCity = getCity(start);
        City endCity = getCity(destination);

        if (startCity == null || endCity == null) {
            System.out.println("\nError: One or both cities not found in the system.");
            return false;
        }

        RouteResult result = calculateBestRoute(start, destination, priority);

        if (result != null) {
            List<String> route = result.route;
            List<String> trafficInfo = result.trafficApplied;
            List<Double> costs = result.costs;
            List<Double> durations = result.durations;
            List<String> segmentComforts = result.comfortLevels;

            double totalCost = Math.round(result.totalCost * 100.0) / 100.0;
            int totalTime = (int) result.totalDuration;

            String bookingRef = "BK" + (new Random().nextInt(90000) + 10000);

            System.out.println("\n===== BOOKING SUCCESSFUL =====");
            System.out.println("Booking Reference: " + bookingRef);
            System.out.println("Journey: " + start + " → " + destination);
            System.out.println("Optimization Priority: " + priority.substring(0, 1).toUpperCase() + priority.substring(1));

            System.out.println("\nComplete Route:");
            for (int i = 0; i < route.size(); i++) {
                System.out.print(route.get(i));
                if (i < route.size() - 1) System.out.print(" → ");
            }

            System.out.println("\n\nSegment Details:");
            DecimalFormat df = new DecimalFormat("#.##");
            for (int i = 0; i < route.size() - 1; i++) {
                System.out.println("  " + (i + 1) + ". " + route.get(i) + " → " + route.get(i + 1));
                System.out.println("     - Class: " + segmentComforts.get(i));
                System.out.println("     - Cost: $" + df.format(costs.get(i)));
                System.out.println("     - Duration: " + (int) Math.round(durations.get(i)) + " mins (Traffic: " + trafficInfo.get(i) + ")");
            }

            System.out.println("\nTotal Cost: $" + df.format(totalCost));
            System.out.println("Total Travel Time: " + totalTime + " mins (" + (totalTime / 60) + "h " + (totalTime % 60) + "m)");

            if (new Random().nextDouble() < 0.3) {
                String[] weatherConditions = {"rain", "fog", "snow", "high winds"};
                String weather = weatherConditions[new Random().nextInt(weatherConditions.length)];
                System.out.println("\nWEATHER WARNING: Expect " + weather + " along parts of this route.");
            }

            System.out.println("=============================");
            return true;
        } else {
            System.out.println("\nNo route available from " + start + " to " + destination + ".");
            return false;
        }
    }

    public RouteResult calculateBestRoute(String start, String end, String priority) {
        City startCity = getCity(start);
        City endCity = getCity(end);

        if (startCity == null || endCity == null) return null;

        LocalDateTime now = LocalDateTime.now();
        boolean weekend = now.getDayOfWeek() == DayOfWeek.SATURDAY || now.getDayOfWeek() == DayOfWeek.SUNDAY;
        boolean isRushHour = (now.getHour() >= 7 && now.getHour() <= 9) || (now.getHour() >= 17 && now.getHour() <= 19);

        Map<String, Double> trafficConditions = Map.of(
            "low", weekend ? 1.0 : 0.8,
            "moderate", weekend ? 1.2 : 1.0,
            "high", isRushHour ? 1.6 : 1.3
        );

        MinHeap queue = new MinHeap();
        queue.push(new HeapNode(0, start, new ArrayList<>(), new ArrayList<>(), new ArrayList<>(), new ArrayList<>(), new ArrayList<>()));
        Map<String, Double> visited = new HashMap<>();

        String[] trafficTypes = {"low", "moderate", "high"};
        Random rand = new Random();

        while (!queue.isEmpty()) {
            HeapNode current = queue.pop();

            if (visited.containsKey(current.currentCity) && visited.get(current.currentCity) <= current.score) continue;
            visited.put(current.currentCity, current.score);

            List<String> newPath = new ArrayList<>(current.path);
            newPath.add(current.currentCity);

            if (current.currentCity.equalsIgnoreCase(end)) {
                double totalDuration = current.durations.stream().mapToDouble(Double::doubleValue).sum();
                double totalCost = current.costs.stream().mapToDouble(Double::doubleValue).sum();
                return new RouteResult(totalDuration, totalCost, newPath, current.trafficApplied, current.costs, current.durations, current.comfortLevels);
            }

            City cityObj = getCity(current.currentCity);
            for (Route route : cityObj.connections) {
                if (newPath.contains(route.destination)) continue;

                String traffic = trafficTypes[rand.nextInt(trafficTypes.length)];
                double trafficFactor = trafficConditions.get(traffic);
                double adjustedDuration = route.duration * trafficFactor;

                double weekendDiscount = weekend ? 0.9 : 1.0;
                double adjustedCost = route.cost * weekendDiscount;

                ComfortInfo comfortInfo = this.comfortLevels.get(route.comfort);
                double finalCost = adjustedCost * comfortInfo.priceFactor;

                double score = switch (priority) {
                    case "cost" -> current.score + finalCost;
                    case "comfort" -> current.score + switch (route.comfort) {
                        case "Economy" -> 3;
                        case "Standard" -> 2;
                        case "Premium" -> 0;
                        default -> 1;
                    };
                    default -> current.score + adjustedDuration;
                };

                List<String> newTraffic = new ArrayList<>(current.trafficApplied);
                newTraffic.add(traffic);

                List<Double> newCosts = new ArrayList<>(current.costs);
                newCosts.add(finalCost);

                List<Double> newDurations = new ArrayList<>(current.durations);
                newDurations.add(adjustedDuration);

                List<String> newComforts = new ArrayList<>(current.comfortLevels);
                newComforts.add(route.comfort);

                queue.push(new HeapNode(score, route.destination, newPath, newTraffic, newCosts, newDurations, newComforts));
            }
        }

        return null;
    }
}

class City {
    String name;
    List<Route> connections;
    City nextCity;

    public City(String name) {
        this.name = name;
        this.connections = new ArrayList<>();
    }

    public boolean addConnection(String destination, String comfort, double cost, double duration) {
        for (Route route : connections) {
            if (route.destination.equalsIgnoreCase(destination)) return false;
        }
        connections.add(new Route(destination, comfort, cost, duration));
        return true;
    }
}

class Route {
    String destination;
    String comfort;
    double cost;
    double duration;

    public Route(String destination, String comfort, double cost, double duration) {
        this.destination = destination;
        this.comfort = comfort;
        this.cost = cost;
        this.duration = duration;
    }
}

class ComfortInfo {
    double priceFactor;
    String satisfaction;

    public ComfortInfo(double priceFactor, String satisfaction) {
        this.priceFactor = priceFactor;
        this.satisfaction = satisfaction;
    }
}

class RouteResult {
    double totalDuration;
    double totalCost;
    List<String> route;
    List<String> trafficApplied;
    List<Double> costs;
    List<Double> durations;
    List<String> comfortLevels;

    public RouteResult(double totalDuration, double totalCost, List<String> route,
                       List<String> trafficApplied, List<Double> costs,
                       List<Double> durations, List<String> comfortLevels) {
        this.totalDuration = totalDuration;
        this.totalCost = totalCost;
        this.route = route;
        this.trafficApplied = trafficApplied;
        this.costs = costs;
        this.durations = durations;
        this.comfortLevels = comfortLevels;
    }
}

class HeapNode {
    double score;
    String currentCity;
    List<String> path;
    List<String> trafficApplied;
    List<Double> costs;
    List<Double> durations;
    List<String> comfortLevels;

    public HeapNode(double score, String currentCity, List<String> path, List<String> trafficApplied,
                    List<Double> costs, List<Double> durations, List<String> comfortLevels) {
        this.score = score;
        this.currentCity = currentCity;
        this.path = path;
        this.trafficApplied = trafficApplied;
        this.costs = costs;
        this.durations = durations;
        this.comfortLevels = comfortLevels;
    }
}

class MinHeap {
    private List<HeapNode> heap = new ArrayList<>();

    public void push(HeapNode node) {
        heap.add(node);
        siftUp(heap.size() - 1);
    }

    public HeapNode pop() {
        if (heap.isEmpty()) return null;
        swap(0, heap.size() - 1);
        HeapNode top = heap.remove(heap.size() - 1);
        siftDown(0);
        return top;
    }

    public boolean isEmpty() {
        return heap.isEmpty();
    }

    private void siftUp(int idx) {
        while (idx > 0) {
            int parent = (idx - 1) / 2;
            if (heap.get(idx).score >= heap.get(parent).score) break;
            swap(idx, parent);
            idx = parent;
        }
    }

    private void siftDown(int idx) {
        int left = 2 * idx + 1, right = 2 * idx + 2, smallest = idx;

        if (left < heap.size() && heap.get(left).score < heap.get(smallest).score)
            smallest = left;
        if (right < heap.size() && heap.get(right).score < heap.get(smallest).score)
            smallest = right;
        if (smallest != idx) {
            swap(idx, smallest);
            siftDown(smallest);
        }
    }

    private void swap(int i, int j) {
        HeapNode tmp = heap.get(i);
        heap.set(i, heap.get(j));
        heap.set(j, tmp);
    }
}

class Main {
    public static void createFullyConnectedNetwork(TransportSystem transport) {
        List<String> cities = new ArrayList<>();
        City temp = transport.head;
        while (temp != null) {
            cities.add(temp.name);
            temp = temp.nextCity;
        }

        String[] comfortLevels = {"Economy", "Standard", "Premium", "Express"};
        Random rand = new Random();

        for (int i = 0; i < cities.size(); i++) {
            for (int j = i + 1; j < cities.size(); j++) {
                int distance = cities.get(i).length() + cities.get(j).length();
                double baseCost = distance * 50;
                double baseDuration = distance * 30;
                String comfort = comfortLevels[rand.nextInt(comfortLevels.length)];
                transport.addRoute(cities.get(i), cities.get(j), comfort, baseCost, baseDuration);
            }
        }
    }
}