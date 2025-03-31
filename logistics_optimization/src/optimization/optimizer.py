from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
import pulp
import logging
from scipy import stats

from logistics_optimization.config.config import OPTIMIZATION_CONFIG

logger = logging.getLogger(__name__)

class LogisticsOptimizer:
    """
    Implements optimization algorithms for logistics operations:
    1. Route Optimization: Finds optimal delivery routes
    2. Inventory Optimization: Determines optimal inventory levels
    """
    
    def __init__(self):
        self.config = OPTIMIZATION_CONFIG
        self.route_config = self.config["route_optimization"]
        self.inventory_config = self.config["inventory_optimization"]
    
    def optimize_routes(self, 
                       locations: List[Dict],
                       distances: np.ndarray,
                       demands: np.ndarray,
                       num_vehicles: int) -> Dict:
        """
        Solve the Vehicle Routing Problem (VRP) to optimize delivery routes.
        
        Args:
            locations: List of location dictionaries with coordinates
            distances: Matrix of distances between locations
            demands: Array of demands for each location
            num_vehicles: Number of available vehicles
            
        Returns:
            Dictionary containing optimized routes and metrics
        """
        try:
            # Create optimization problem
            prob = pulp.LpProblem("VRP", pulp.LpMinimize)
            
            n_locations = len(locations)
            
            # Decision variables
            x = pulp.LpVariable.dicts("route",
                ((i, j, k) for i in range(n_locations) 
                           for j in range(n_locations) 
                           for k in range(num_vehicles)),
                cat="Binary")
            
            # Objective function: minimize total distance
            prob += pulp.lpSum(distances[i][j] * x[i,j,k]
                             for i in range(n_locations)
                             for j in range(n_locations)
                             for k in range(num_vehicles))
            
            # Constraints
            
            # Each location must be visited exactly once
            for j in range(1, n_locations):
                prob += pulp.lpSum(x[i,j,k] 
                                 for i in range(n_locations) if i != j
                                 for k in range(num_vehicles)) == 1
            
            # Each vehicle must start and end at the depot
            for k in range(num_vehicles):
                # Start at depot
                prob += pulp.lpSum(x[0,j,k] for j in range(1, n_locations)) <= 1
                # End at depot
                prob += pulp.lpSum(x[i,0,k] for i in range(1, n_locations)) <= 1
            
            # Flow conservation
            for k in range(num_vehicles):
                for j in range(n_locations):
                    prob += (pulp.lpSum(x[i,j,k] for i in range(n_locations) if i != j) ==
                            pulp.lpSum(x[j,i,k] for i in range(n_locations) if i != j))
            
            # Capacity constraints
            for k in range(num_vehicles):
                prob += (pulp.lpSum(demands[j] * x[i,j,k]
                                  for i in range(n_locations)
                                  for j in range(1, n_locations))
                        <= self.route_config["vehicle_capacity"])
            
            # Distance constraints
            for k in range(num_vehicles):
                prob += (pulp.lpSum(distances[i][j] * x[i,j,k]
                                  for i in range(n_locations)
                                  for j in range(n_locations))
                        <= self.route_config["max_distance"])
            
            # Solve the problem
            prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=self.config["time_limit"]))
            
            # Extract solution
            routes = []
            total_distance = 0
            
            for k in range(num_vehicles):
                route = []
                current = 0  # Start at depot
                
                while True:
                    route.append(current)
                    next_stop = None
                    
                    for j in range(n_locations):
                        if j != current and x[current,j,k].value() == 1:
                            next_stop = j
                            total_distance += distances[current][j]
                            break
                    
                    if next_stop is None or next_stop == 0:
                        break
                        
                    current = next_stop
                
                if len(route) > 2:  # Only include non-empty routes
                    routes.append(route)
            
            return {
                "routes": routes,
                "total_distance": total_distance,
                "status": pulp.LpStatus[prob.status],
                "objective_value": pulp.value(prob.objective)
            }
            
        except Exception as e:
            logger.error(f"Error in route optimization: {str(e)}")
            raise
    
    def optimize_inventory(self,
                         historical_demand: np.ndarray,
                         lead_time: int,
                         holding_cost: float,
                         stockout_cost: float) -> Dict:
        """
        Determine optimal inventory levels using newsvendor model.
        
        Args:
            historical_demand: Array of historical demand values
            lead_time: Lead time for replenishment
            holding_cost: Cost of holding one unit of inventory
            stockout_cost: Cost of stockout per unit
            
        Returns:
            Dictionary containing optimal inventory levels and metrics
        """
        try:
            # Calculate demand distribution parameters
            demand_mean = np.mean(historical_demand)
            demand_std = np.std(historical_demand)
            
            # Calculate critical ratio
            critical_ratio = stockout_cost / (holding_cost + stockout_cost)
            
            # Calculate optimal order quantity using normal distribution
            z_score = stats.norm.ppf(critical_ratio)
            safety_stock = z_score * demand_std * np.sqrt(lead_time)
            
            # Calculate reorder point
            reorder_point = demand_mean * lead_time + safety_stock
            
            # Calculate economic order quantity (EOQ)
            order_cost = stockout_cost * 10  # Assuming order cost is 10x stockout cost
            annual_demand = demand_mean * 365
            eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)
            
            # Calculate expected costs
            expected_holding_cost = holding_cost * safety_stock
            expected_stockout_cost = (stockout_cost * demand_std * 
                                    stats.norm.pdf(z_score))
            total_cost = expected_holding_cost + expected_stockout_cost
            
            return {
                "reorder_point": reorder_point,
                "safety_stock": safety_stock,
                "economic_order_quantity": eoq,
                "expected_total_cost": total_cost,
                "service_level": critical_ratio,
                "metrics": {
                    "demand_mean": demand_mean,
                    "demand_std": demand_std,
                    "expected_holding_cost": expected_holding_cost,
                    "expected_stockout_cost": expected_stockout_cost
                }
            }
            
        except Exception as e:
            logger.error(f"Error in inventory optimization: {str(e)}")
            raise
    
    def optimize_delivery_schedule(self,
                                 tasks: List[Dict],
                                 resources: List[Dict],
                                 time_windows: List[Tuple[int, int]]) -> Dict:
        """
        Optimize delivery schedule using constraint programming.
        
        Args:
            tasks: List of delivery tasks with durations and priorities
            resources: List of available resources (vehicles, drivers)
            time_windows: List of allowed time windows for deliveries
            
        Returns:
            Dictionary containing optimized schedule and metrics
        """
        try:
            # Create optimization problem
            prob = pulp.LpProblem("Scheduling", pulp.LpMinimize)
            
            n_tasks = len(tasks)
            n_resources = len(resources)
            n_time_slots = max(tw[1] for tw in time_windows)
            
            # Decision variables
            x = pulp.LpVariable.dicts("schedule",
                ((i, j, t) for i in range(n_tasks)
                           for j in range(n_resources)
                           for t in range(n_time_slots)),
                cat="Binary")
            
            # Objective: minimize weighted completion time
            prob += pulp.lpSum(tasks[i]["priority"] * t * x[i,j,t]
                             for i in range(n_tasks)
                             for j in range(n_resources)
                             for t in range(n_time_slots))
            
            # Constraints
            
            # Each task must be assigned exactly once
            for i in range(n_tasks):
                prob += pulp.lpSum(x[i,j,t]
                                 for j in range(n_resources)
                                 for t in range(n_time_slots)) == 1
            
            # Resource capacity constraints
            for j in range(n_resources):
                for t in range(n_time_slots):
                    prob += pulp.lpSum(x[i,j,t] for i in range(n_tasks)) <= 1
            
            # Time window constraints
            for i in range(n_tasks):
                for tw in time_windows:
                    start, end = tw
                    prob += pulp.lpSum(x[i,j,t]
                                     for j in range(n_resources)
                                     for t in range(start, end)) <= 1
            
            # Solve the problem
            prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=self.config["time_limit"]))
            
            # Extract solution
            schedule = []
            total_weighted_time = 0
            
            for i in range(n_tasks):
                for j in range(n_resources):
                    for t in range(n_time_slots):
                        if x[i,j,t].value() == 1:
                            schedule.append({
                                "task_id": tasks[i]["id"],
                                "resource_id": resources[j]["id"],
                                "start_time": t,
                                "duration": tasks[i]["duration"]
                            })
                            total_weighted_time += tasks[i]["priority"] * t
            
            return {
                "schedule": schedule,
                "total_weighted_time": total_weighted_time,
                "status": pulp.LpStatus[prob.status],
                "objective_value": pulp.value(prob.objective)
            }
            
        except Exception as e:
            logger.error(f"Error in schedule optimization: {str(e)}")
            raise 