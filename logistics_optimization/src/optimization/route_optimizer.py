import numpy as np
from pulp import *
import logging
from typing import List, Dict, Any
from itertools import combinations

logger = logging.getLogger(__name__)

class RouteOptimizer:
    def __init__(self):
        """Initialize the route optimizer."""
        self.solver = None
        self.last_solution = None
    
    def calculate_distances(self, locations: List[Dict]) -> np.ndarray:
        """
        Calculate distances between all locations using Euclidean distance.
        
        Args:
            locations: List of dictionaries containing location coordinates
            
        Returns:
            Distance matrix
        """
        n = len(locations)
        distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(
                    (locations[i]['x'] - locations[j]['x'])**2 +
                    (locations[i]['y'] - locations[j]['y'])**2
                )
                distances[i][j] = dist
                distances[j][i] = dist
        
        return distances
    
    def optimize(self, locations: List[Dict], constraints: Dict[str, Any] = None) -> List[Dict]:
        """
        Optimize delivery routes using Vehicle Routing Problem (VRP) formulation.
        
        Args:
            locations: List of dictionaries containing location information
            constraints: Optional constraints for the optimization
            
        Returns:
            List of optimized routes
        """
        try:
            if not locations:
                raise ValueError("No locations provided")
            
            # Set default constraints if none provided
            if constraints is None:
                constraints = {
                    "max_vehicles": 3,
                    "max_distance": 1000,
                    "vehicle_capacity": 100
                }
            
            # Calculate distances
            distances = self.calculate_distances(locations)
            n_locations = len(locations)
            
            # Create optimization problem
            prob = LpProblem("Vehicle_Routing_Problem", LpMinimize)
            
            # Decision variables
            x = LpVariable.dicts("route",
                               ((i, j) for i in range(n_locations) for j in range(n_locations)),
                               cat='Binary')
            
            # Objective function: minimize total distance
            prob += lpSum(distances[i][j] * x[i, j]
                        for i in range(n_locations)
                        for j in range(n_locations))
            
            # Constraints
            
            # Each location must be visited exactly once
            for j in range(1, n_locations):
                prob += lpSum(x[i, j] for i in range(n_locations) if i != j) == 1
            
            # Each location must be left exactly once
            for i in range(1, n_locations):
                prob += lpSum(x[i, j] for j in range(n_locations) if i != j) == 1
            
            # Flow conservation
            for k in range(1, n_locations):
                prob += lpSum(x[i, k] for i in range(n_locations) if i != k) == \
                       lpSum(x[k, j] for j in range(n_locations) if j != k)
            
            # Solve the problem
            prob.solve()
            
            if LpStatus[prob.status] != 'Optimal':
                raise Exception("Could not find optimal solution")
            
            # Extract solution
            routes = self._extract_routes(x, n_locations)
            self.last_solution = routes
            
            return routes
        
        except Exception as e:
            logger.error(f"Error in route optimization: {str(e)}")
            return []
    
    def _extract_routes(self, x, n_locations: int) -> List[Dict]:
        """Extract routes from the optimization solution."""
        routes = []
        unvisited = set(range(1, n_locations))
        current_route = []
        
        while unvisited:
            if not current_route:
                current = 0  # Start from depot
                current_route = [current]
            
            # Find next location
            next_loc = None
            for j in range(n_locations):
                if j in unvisited and value(x[current, j]) > 0.5:
                    next_loc = j
                    break
            
            if next_loc is None:
                # End current route
                if len(current_route) > 1:
                    routes.append({
                        "route": current_route,
                        "distance": self._calculate_route_distance(current_route)
                    })
                current_route = []
            else:
                current_route.append(next_loc)
                unvisited.remove(next_loc)
                current = next_loc
        
        # Add last route if not empty
        if len(current_route) > 1:
            routes.append({
                "route": current_route,
                "distance": self._calculate_route_distance(current_route)
            })
        
        return routes
    
    def _calculate_route_distance(self, route: List[int]) -> float:
        """Calculate the total distance of a route."""
        if not hasattr(self, 'distances'):
            return 0.0
        
        total_distance = 0.0
        for i in range(len(route) - 1):
            total_distance += self.distances[route[i]][route[i + 1]]
        return total_distance
    
    def calculate_total_distance(self, routes: List[Dict]) -> float:
        """Calculate total distance across all routes."""
        return sum(route["distance"] for route in routes)
    
    def calculate_cost(self, routes: List[Dict], cost_per_km: float = 1.0) -> float:
        """Calculate total cost of the routes."""
        total_distance = self.calculate_total_distance(routes)
        return total_distance * cost_per_km 