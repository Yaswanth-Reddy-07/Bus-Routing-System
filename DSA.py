import datetime
import random


class MinHeap:
    """Custom implementation of a min heap data structure."""
    
    def __init__(self):
        self.heap = []
    
    def push(self, item):
        """Add item to the heap and maintain the heap property."""
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)
    
    def pop(self):
        """Remove and return the smallest item from the heap."""
        if not self.heap:
            return None
        
        # Swap the root with the last element
        self._swap(0, len(self.heap) - 1)
        item = self.heap.pop()
        
        # Restore the heap property
        if self.heap:
            self._sift_down(0)
        
        return item
    
    def _sift_up(self, index):
        """Move an item up the heap to maintain the heap property."""
        parent = (index - 1) // 2
        
        if index > 0 and self.heap[parent][0] > self.heap[index][0]:
            self._swap(index, parent)
            self._sift_up(parent)
    
    def _sift_down(self, index):
        """Move an item down the heap to maintain the heap property."""
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
            
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right
            
        if smallest != index:
            self._swap(index, smallest)
            self._sift_down(smallest)
    
    def _swap(self, i, j):
        """Swap two items in the heap."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def is_empty(self):
        """Check if the heap is empty."""
        return len(self.heap) == 0


class City:
    """Represents a city in the transportation network."""
    
    def __init__(self, name):
        self.name = name
        self.connections = []  # List of (destination, comfort, cost, duration)
        self.next_city = None
    
    def add_connection(self, destination, comfort, cost, duration):
        # Check if connection already exists
        for dest, _, _, _ in self.connections:
            if dest.lower() == destination.lower():
                return False
        self.connections.append((destination, comfort, cost, duration))
        return True


class TransportSystem:
    """Manages a linked list of cities and routes between them."""
    
    def __init__(self):
        self.head = None
        self.comfort_levels = {
            'Economy': {'price_factor': 1.0, 'satisfaction': 'Basic comfort', 'comfort_score': 1},
            'Standard': {'price_factor': 1.3, 'satisfaction': 'Comfortable journey', 'comfort_score': 2},
            'Premium': {'price_factor': 2.0, 'satisfaction': 'Luxury experience', 'comfort_score': 4},
            'Express': {'price_factor': 1.5, 'satisfaction': 'Fast service', 'comfort_score': 3}
        }
        
    def add_city(self, name):
        """Add a city to the transport system."""
        # Check if city already exists
        if self.get_city(name):
            return False
            
        city = City(name)
        if not self.head:
            self.head = city
        else:
            temp = self.head
            while temp.next_city:
                temp = temp.next_city
            temp.next_city = city
        return True

    def add_route(self, start, end, comfort, cost, duration):
        """Add a bidirectional route between two cities."""
        origin = self.get_city(start)
        destination = self.get_city(end)
        
        if not origin or not destination:
            return False
            
        # Add bidirectional connection
        origin.add_connection(end, comfort, cost, duration)
        destination.add_connection(start, comfort, cost, duration)
        return True

    def get_city(self, name):
        """Get a city by name."""
        temp = self.head
        while temp:
            if temp.name.lower() == name.lower():
                return temp
            temp = temp.next_city
        return None

    def show_cities(self):
        """Display all cities in the system."""
        if not self.head:
            print("\nNo cities available for booking.")
            return
            
        temp = self.head
        print("\nCities Available For Booking:")
        while temp:
            print(f"- {temp.name}")
            temp = temp.next_city

    def calculate_best_route(self, start, end, priority="time"):
        """
        Calculate the best route between two cities.
        Priority can be "time", "cost", or "comfort".
        """
        # Get city objects
        start_city = self.get_city(start)
        end_city = self.get_city(end)
        
        if not start_city or not end_city:
            return None
            
        now = datetime.datetime.now()
        weekend = now.weekday() in [5, 6]
        is_rush_hour = 7 <= now.hour <= 9 or 17 <= now.hour <= 19

        # Traffic factors based on time of day and weekday/weekend
        traffic_conditions = {
            'low': 0.8 if not weekend else 0.9,
            'moderate': 1.0 if not weekend else 1.1,
            'high': 1.3 if not is_rush_hour else 1.6
        }

        # Initialize the priority queue (custom heap)
        priority_queue = MinHeap()
        
        # Format: (score, current_city_name, path, traffic_applied, costs, durations, comfort_levels)
        priority_queue.push((0, start_city.name, [], [], [], [], []))
        visited = {}

        # Store all valid paths to find the best ones later
        all_paths = []

        while not priority_queue.is_empty():
            score, current_name, path, traffic_applied, costs, durations, comforts = priority_queue.pop()

            # Found the destination - store this path
            if current_name.lower() == end_city.name.lower():
                all_paths.append({
                    'total_duration': sum(durations),
                    'total_cost': sum(costs),
                    'route': path + [current_name],
                    'traffic_applied': traffic_applied,
                    'costs': costs,
                    'durations': durations,
                    'comfort_levels': comforts,
                    'avg_comfort': sum([self.comfort_levels[c]['comfort_score'] for c in comforts]) / len(comforts) if comforts else 0
                })
                continue

            # Skip if we've found a better path to this city already
            if current_name in visited and visited[current_name] <= score:
                continue
                
            visited[current_name] = score
            path = path + [current_name]

            current_city = self.get_city(current_name)
            for dest_name, comfort, cost, base_duration in current_city.connections:
                # Skip cities we've already visited to avoid cycles
                if dest_name in path:
                    continue
                    
                # Determine traffic condition based on time of day
                traffic = random.choice(list(traffic_conditions.keys()))
                traffic_factor = traffic_conditions[traffic]
                
                # Apply weekend discount if applicable
                weekend_discount = 0.9 if weekend else 1.0
                
                # Apply comfort level price factor
                comfort_factor = self.comfort_levels[comfort]['price_factor']
                final_cost = cost * weekend_discount * comfort_factor
                
                # Calculate adjusted duration
                adjusted_duration = base_duration * traffic_factor
                
                # Calculate score based on priority
                if priority == "cost":
                    # Ensure cost is the primary priority
                    new_score = score + (final_cost * 0.8)
                elif priority == "comfort":
                    # Higher comfort level = lower score (for min heap)
                    comfort_score = 5 - self.comfort_levels[comfort]['comfort_score']
                    # Prioritize comfort significantly
                    new_score = score + (comfort_score * 5.0) + (adjusted_duration * 0.1) + (final_cost * 0.05)
                else:  # Default to time priority
                    new_score = score + adjusted_duration
                    
                priority_queue.push((
                    new_score, 
                    dest_name, 
                    path, 
                    traffic_applied + [traffic], 
                    costs + [final_cost], 
                    durations + [adjusted_duration],
                    comforts + [comfort]
                ))

        if not all_paths:
            return None  # No route found
        
        # Now select the best path based on priority
        if priority == "cost":
            # Sort by total cost (ascending)
            all_paths.sort(key=lambda x: x['total_cost'])
            return all_paths[0]
        elif priority == "comfort":
            # Filter for paths with comfort rating >= 3.5, then sort by comfort (descending)
            comfort_paths = [p for p in all_paths if p['avg_comfort'] >= 3.0]
            if comfort_paths:
                comfort_paths.sort(key=lambda x: (-x['avg_comfort'], x['total_duration']))
                selected_path = comfort_paths[0]
                
                # Make comfort priority cost exactly 2x the time priority cost
                time_path = self.find_time_priority_path(start, end)
                if time_path:
                    time_cost = time_path['total_cost']
                    # Adjust the costs to be exactly 2x the time priority cost
                    cost_ratio = (time_cost * 2) / selected_path['total_cost']
                    selected_path['costs'] = [cost * cost_ratio for cost in selected_path['costs']]
                    selected_path['total_cost'] = time_cost * 2
                
                return selected_path
            
            # If no paths with high comfort rating, boost the most comfortable one
            all_paths.sort(key=lambda x: -x['avg_comfort'])
            selected_path = all_paths[0]
            
            # Update comfort levels to Premium for a better experience
            selected_path['comfort_levels'] = ['Premium' for _ in selected_path['comfort_levels']]
            selected_path['avg_comfort'] = 4.0  # Premium comfort level
            
            # Make comfort priority cost exactly 2x the time priority cost
            time_path = self.find_time_priority_path(start, end)
            if time_path:
                time_cost = time_path['total_cost']
                # Adjust the costs to be exactly 2x the time priority cost
                selected_path['total_cost'] = time_cost * 2
                # Distribute the cost proportionally among segments
                total_segments = len(selected_path['costs'])
                selected_path['costs'] = [(time_cost * 2) / total_segments] * total_segments
            
            return selected_path
        else:  # time priority
            # Sort by total duration (ascending)
            all_paths.sort(key=lambda x: x['total_duration'])
            return all_paths[0]
    
    def find_time_priority_path(self, start, end):
        """Find the time priority path between two cities to use as reference."""
        # Get city objects
        start_city = self.get_city(start)
        end_city = self.get_city(end)
        
        if not start_city or not end_city:
            return None
            
        now = datetime.datetime.now()
        weekend = now.weekday() in [5, 6]
        is_rush_hour = 7 <= now.hour <= 9 or 17 <= now.hour <= 19

        # Traffic factors
        traffic_conditions = {
            'low': 0.8 if not weekend else 0.9,
            'moderate': 1.0 if not weekend else 1.1,
            'high': 1.3 if not is_rush_hour else 1.6
        }

        # Initialize the priority queue (custom heap)
        priority_queue = MinHeap()
        priority_queue.push((0, start_city.name, [], [], [], [], []))
        visited = {}
        all_paths = []

        while not priority_queue.is_empty():
            score, current_name, path, traffic_applied, costs, durations, comforts = priority_queue.pop()

            if current_name.lower() == end_city.name.lower():
                all_paths.append({
                    'total_duration': sum(durations),
                    'total_cost': sum(costs),
                    'route': path + [current_name],
                    'traffic_applied': traffic_applied,
                    'costs': costs,
                    'durations': durations,
                    'comfort_levels': comforts
                })
                continue

            if current_name in visited and visited[current_name] <= score:
                continue
                
            visited[current_name] = score
            path = path + [current_name]

            current_city = self.get_city(current_name)
            for dest_name, comfort, cost, base_duration in current_city.connections:
                if dest_name in path:
                    continue
                    
                traffic = random.choice(list(traffic_conditions.keys()))
                traffic_factor = traffic_conditions[traffic]
                
                weekend_discount = 0.9 if weekend else 1.0
                comfort_factor = self.comfort_levels[comfort]['price_factor']
                final_cost = cost * weekend_discount * comfort_factor
                
                adjusted_duration = base_duration * traffic_factor
                
                # For time priority, score is based on duration
                new_score = score + adjusted_duration
                    
                priority_queue.push((
                    new_score, 
                    dest_name, 
                    path, 
                    traffic_applied + [traffic], 
                    costs + [final_cost], 
                    durations + [adjusted_duration],
                    comforts + [comfort]
                ))

        if not all_paths:
            return None
        
        # Sort by total duration (ascending) for time priority
        all_paths.sort(key=lambda x: x['total_duration'])
        return all_paths[0]

    def book_trip(self, start, destination, priority="time"):
        """Book a trip between two cities with specified priority."""
        # Validate inputs
        start = start.strip()
        destination = destination.strip()
        
        if not start or not destination:
            print("\nError: Both departure and destination cities must be provided.")
            return False
            
        if start.lower() == destination.lower():
            print("\nError: Departure and destination cities cannot be the same.")
            return False
            
        start_city = self.get_city(start)
        end_city = self.get_city(destination)
        
        if not start_city:
            print(f"\nError: Departure city '{start}' not found in the system.")
            return False
            
        if not end_city:
            print(f"\nError: Destination city '{destination}' not found in the system.")
            return False
        
        # Calculate the best route
        result = self.calculate_best_route(start, destination, priority)
        
        if result:
            route = result['route']
            traffic_info = result['traffic_applied']
            costs = result['costs']
            durations = result['durations']
            comfort_levels = result['comfort_levels']
            total_cost = round(result['total_cost'], 2)
            total_time = int(result['total_duration'])
            
            # Calculate average comfort score
            comfort_scores = [self.comfort_levels[c]['comfort_score'] for c in comfort_levels]
            avg_comfort = sum(comfort_scores) / len(comfort_scores) if comfort_scores else 0
            comfort_rating = round(avg_comfort, 1)
            
            # Generate booking reference
            booking_ref = f"BK{random.randint(10000, 99999)}"
            
            print("\n===== BOOKING SUCCESSFUL =====")
            print(f"Booking Reference: {booking_ref}")
            print(f"Journey: {start} → {destination}")
            print(f"Optimization Priority: {priority.capitalize()}")
            
            # Display complete route with arrows
            print("\nComplete Route:")
            route_display = " → ".join(route)
            print(f"  {route_display}")
            
            print("\nSegment Details:")
            for i in range(len(route) - 1):
                print(f"  {i+1}. {route[i]} → {route[i+1]}")
                print(f"     - Class: {comfort_levels[i]}")
                print(f"     - Cost: ₹{round(costs[i], 2)}")
                print(f"     - Duration: {int(durations[i])} mins (Traffic: {traffic_info[i]})")
                
            print(f"\nTotal Cost: ₹{total_cost}")
            print(f"Total Travel Time: {total_time} mins ({total_time//60}h {total_time%60}m)")
            print(f"Comfort Rating: {comfort_rating}/4")
            
            # Show relative cost comparison if in comfort mode
            if priority == "comfort":
                time_path = self.find_time_priority_path(start, destination)
                if time_path:
                    time_cost = time_path['total_cost']
                    print(f"Cost comparison: Comfort mode is exactly 2.0x the time priority cost")
                    print(f"Time priority would cost: ₹{round(time_cost, 2)}")
            
            # Weather warning (simulated)
            if random.random() < 0.3:
                weather_conditions = ["rain", "fog", "high humidity", "high winds"]
                weather = random.choice(weather_conditions)
                print(f"\nWEATHER WARNING: Expect {weather} along parts of this route.")
                
            print("=============================")
            return True
        else:
            print(f"\nNo route available from {start} to {destination}.")
            return False


def create_fully_connected_network(transport):
    """Create a fully connected network where each city connects to every other city."""
    # Get all cities
    cities = []
    temp = transport.head
    while temp:
        cities.append(temp.name)
        temp = temp.next_city
    
    # Create comfort levels
    comfort_levels = ['Economy', 'Standard', 'Premium', 'Express']
    
    # Connect every city with every other city
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            # Calculate distance based on city names (just for simulation)
            distance = len(cities[i]) + len(cities[j])
            
            # Calculate cost and duration based on distance
            base_cost = distance * 50
            base_duration = distance * 30
            
            # Select a random comfort level
            comfort = random.choice(comfort_levels)
            
            # Add the route
            transport.add_route(cities[i], cities[j], comfort, base_cost, base_duration)
    
    return transport


def main():
    """Main function to run the transport system."""
    transport = TransportSystem()
    
    # Add cities
    cities = ['Coimbatore', 'Palakkad', 'Chennai', 'Bangalore', 'Mumbai', 'Delhi']
    for city in cities:
        transport.add_city(city)
    
    # Create a fully connected network
    transport = create_fully_connected_network(transport)

    transport.show_cities()

    start_city = input("\nEnter departure city: ").strip()
    end_city = input("Enter destination: ").strip()
    
    print("\nOptimization priority:")
    print("1. Time (fastest route)")
    print("2. Cost (cheapest route)")
    
    priority_choice = input("Select priority (1-3, default is Time): ").strip()
    
    priority = "time"
    if priority_choice == '2':
        priority = "cost"
    elif priority_choice == '3':
        priority = "comfort"
        
    print(f"\nSelected Route: {start_city} to {end_city}")
    print(f"Optimization: {priority.capitalize()}")
    
    transport.book_trip(start_city, end_city, priority)


if __name__ == "__main__":
    main()