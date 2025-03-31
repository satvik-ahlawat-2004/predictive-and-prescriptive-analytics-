import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictiveModel:
    """
    Implements predictive models for logistics optimization:
    1. Delay Prediction: Predicts delivery delays using random forest
    2. Demand Forecasting: Predicts future demand using gradient boosting
    """
    
    def __init__(self):
        """Initialize the predictive models."""
        self.delay_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.demand_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def preprocess_data(self, df):
        """Preprocess the input data."""
        try:
            # Convert date columns to numerical features
            df['ShipmentDate'] = pd.to_datetime(df['ShipmentDate'])
            df['DeliveryDate'] = pd.to_datetime(df['DeliveryDate'])
            
            # Extract features
            features = pd.DataFrame({
                'month': df['ShipmentDate'].dt.month,
                'day_of_week': df['ShipmentDate'].dt.dayofweek,
                'inventory_level': df['InventoryLevel'],
                'is_rainy': (df['WeatherCondition'] == 'Rain').astype(int),
                'is_foggy': (df['WeatherCondition'] == 'Foggy').astype(int),
                'is_truck': (df['TransportMode'] == 'Truck').astype(int),
                'is_ship': (df['TransportMode'] == 'Ship').astype(int),
                'is_train': (df['TransportMode'] == 'Train').astype(int)
            })
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            return pd.DataFrame(scaled_features, columns=features.columns)
        
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
    
    def train_delay_model(self, df):
        """Train the delay prediction model."""
        try:
            X = self.preprocess_data(df)
            
            # Calculate delays in hours
            df['DeliveryDate'] = pd.to_datetime(df['DeliveryDate'])
            df['ShipmentDate'] = pd.to_datetime(df['ShipmentDate'])
            y = (df['DeliveryDate'] - df['ShipmentDate']).dt.total_seconds() / 3600
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.delay_model.fit(X_train, y_train)
            self.is_fitted = True
            
            logger.info("Delay model trained successfully")
        except Exception as e:
            logger.error(f"Error training delay model: {str(e)}")
            raise
    
    def train_demand_model(self, df):
        """Train the demand prediction model."""
        try:
            X = self.preprocess_data(df)
            y = df['InventoryLevel']
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.demand_model.fit(X_train, y_train)
            self.is_fitted = True
            
            logger.info("Demand model trained successfully")
        except Exception as e:
            logger.error(f"Error training demand model: {str(e)}")
            raise
    
    def predict_delays(self, df):
        """Predict delivery delays."""
        try:
            if not self.is_fitted:
                raise ValueError("Model not trained. Please train the model first.")
            
            X = self.preprocess_data(df)
            delays = self.delay_model.predict(X)
            
            return delays.tolist()
        except Exception as e:
            logger.error(f"Error predicting delays: {str(e)}")
            raise
    
    def predict_demand(self, df):
        """Predict future demand."""
        try:
            if not self.is_fitted:
                raise ValueError("Model not trained. Please train the model first.")
            
            X = self.preprocess_data(df)
            demand = self.demand_model.predict(X)
            
            return demand.tolist()
        except Exception as e:
            logger.error(f"Error predicting demand: {str(e)}")
            raise
    
    def generate_insights(self, df):
        """Generate insights from the predictions."""
        try:
            delays = self.predict_delays(df)
            demand = self.predict_demand(df)
            
            insights = {
                'average_delay': np.mean(delays),
                'max_delay': np.max(delays),
                'average_demand': np.mean(demand),
                'peak_demand': np.max(demand),
                'delay_risk_level': 'High' if np.mean(delays) > 24 else 'Medium' if np.mean(delays) > 12 else 'Low',
                'demand_trend': 'Increasing' if np.polyfit(range(len(demand)), demand, 1)[0] > 0 else 'Decreasing'
            }
            
            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise 