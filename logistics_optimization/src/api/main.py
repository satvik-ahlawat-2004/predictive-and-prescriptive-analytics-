from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime, timedelta
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Logistics Optimization API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Data validation function (simplified for demo)
def validate_data(df: pd.DataFrame) -> tuple[bool, str]:
    """Basic validation for the input data."""
    # For demo purposes, we'll just check if there are rows
    if len(df) == 0:
        return False, "Dataset is empty"
    return True, "Data validation successful"

# Root route for health check
@app.get("/")
async def read_root():
    """API health check endpoint."""
    return {"message": "Logistics Optimization API is running", "status": "healthy"}

@app.post("/upload-data/")
async def upload_data(file: UploadFile = File(...)):
    """Upload logistics data file."""
    try:
        # For demo, we'll just acknowledge receipt
        return {
            "message": "File uploaded successfully",
            "rows_processed": 100,
            "validation": "Data validation successful"
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {"message": f"Error processing file: {str(e)}"}

@app.post("/predict/")
async def predict_logistics(data: dict = None):
    """Generate sample prediction data."""
    try:
        # Generate random predictions for demo
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        values = [round(random.uniform(10, 30), 1) for _ in range(7)]
        demand = [random.randint(300, 700) for _ in range(7)]
        
        return {
            "message": "Predictions generated successfully",
            "predictions": {
                "delay_forecast": {
                    "dates": dates,
                    "values": values,
                    "trend": random.choice(["Increasing", "Decreasing", "Stable"])
                },
                "demand_forecast": {
                    "dates": dates,
                    "values": demand,
                    "trend": random.choice(["Increasing", "Decreasing", "Stable"])
                }
            }
        }
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return {"message": f"Error generating predictions: {str(e)}"}

@app.post("/optimize-routes/")
async def optimize_routes(data: dict = None):
    """Generate sample route optimization data."""
    try:
        # Generate sample warehouses
        warehouses = [
            {"id": 1, "name": "Chicago Warehouse", "lat": 41.8781, "lon": -87.6298},
            {"id": 2, "name": "Atlanta Warehouse", "lat": 33.7490, "lon": -84.3880},
            {"id": 3, "name": "Dallas Warehouse", "lat": 32.7767, "lon": -96.7970}
        ]
        
        # Generate delivery points
        deliveries = []
        for i in range(10):
            warehouse = random.choice(warehouses)
            deliveries.append({
                "id": i + 1,
                "name": f"Delivery Point {i + 1}",
                "lat": warehouse["lat"] + random.uniform(-1, 1),
                "lon": warehouse["lon"] + random.uniform(-1, 1)
            })
        
        # Sample routes
        routes = []
        for i, warehouse in enumerate(warehouses):
            routes.append({
                "warehouse": i,
                "deliveries": [j for j in range(len(deliveries)) if random.random() > 0.7]
            })
        
        return {
            "message": "Routes optimized successfully",
            "optimizations": {
                "optimized_routes": {
                    "warehouses": warehouses,
                    "deliveries": deliveries,
                    "routes": routes
                },
                "inventory_optimization": {
                    "products": [
                        {"name": "Product A", "current_levels": [120, 80, 150], "optimized_levels": [100, 70, 130]},
                        {"name": "Product B", "current_levels": [90, 110, 70], "optimized_levels": [80, 90, 60]},
                        {"name": "Product C", "current_levels": [60, 130, 100], "optimized_levels": [50, 110, 90]}
                    ]
                },
                "route_recommendations": [
                    "Consolidate deliveries to reduce total distance by 15%",
                    "Reschedule deliveries to reduce transit times by 12%",
                    "Optimize warehouse allocation to reduce average delivery distance by 8%"
                ],
                "inventory_recommendations": [
                    "Reduce safety stock of Product A at Atlanta Warehouse by 20%",
                    "Increase inventory levels of Product C at Chicago Warehouse to meet growing demand",
                    "Implement just-in-time delivery for Product B to minimize storage costs"
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error optimizing routes: {str(e)}")
        return {"message": f"Error optimizing routes: {str(e)}"}

@app.post("/insights/")
async def generate_insights(data: dict = None):
    """Generate sample insights data."""
    try:
        return {
            "message": "Insights generated successfully",
            "insights": {
                "delivery_performance": {
                    "average_delay": round(random.uniform(10, 20), 1),
                    "on_time_rate": random.randint(75, 95),
                    "delay_trend": random.choice(["Increasing", "Decreasing", "Stable"])
                },
                "inventory_performance": {
                    "average_inventory_level": random.randint(400, 600),
                    "inventory_trend": random.choice(["Increasing", "Decreasing", "Stable"]),
                    "stockout_rate": round(random.uniform(1, 5), 1)
                },
                "cost_analysis": {
                    "total_logistics_cost": random.randint(10000, 20000),
                    "cost_efficiency": random.randint(75, 95),
                    "potential_savings": random.randint(8000, 15000)
                }
            }
        }
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return {"message": f"Error generating insights: {str(e)}"}

# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8075) 