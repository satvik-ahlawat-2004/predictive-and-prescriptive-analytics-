import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import logging
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

from logistics_optimization.config.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    MODEL_CONFIG
)

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data processing for the logistics optimization system.
    This includes data loading, cleaning, and feature engineering.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_config = MODEL_CONFIG["features"]
    
    def load_shipment_data(self, start_date: Optional[str] = None, 
                          end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Load shipment data from the raw data directory.
        
        Args:
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            DataFrame containing shipment data
        """
        try:
            df = pd.read_csv(RAW_DATA_DIR / "shipments.csv", parse_dates=["timestamp"])
            
            if start_date:
                df = df[df["timestamp"] >= start_date]
            if end_date:
                df = df[df["timestamp"] <= end_date]
                
            logger.info(f"Loaded {len(df)} shipment records")
            return df
            
        except Exception as e:
            logger.error(f"Error loading shipment data: {str(e)}")
            raise
    
    def load_weather_data(self) -> pd.DataFrame:
        """Load and preprocess weather data."""
        try:
            weather_df = pd.read_csv(RAW_DATA_DIR / "weather.csv", parse_dates=["timestamp"])
            weather_features = self.feature_config["weather_features"]
            return weather_df[["timestamp", "location"] + weather_features]
            
        except Exception as e:
            logger.error(f"Error loading weather data: {str(e)}")
            raise
    
    def load_traffic_data(self) -> pd.DataFrame:
        """Load and preprocess traffic data."""
        try:
            traffic_df = pd.read_csv(RAW_DATA_DIR / "traffic.csv", parse_dates=["timestamp"])
            traffic_features = self.feature_config["traffic_features"]
            return traffic_df[["timestamp", "location"] + traffic_features]
            
        except Exception as e:
            logger.error(f"Error loading traffic data: {str(e)}")
            raise
    
    def merge_external_data(self, shipment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge weather and traffic data with shipment data.
        
        Args:
            shipment_df: DataFrame containing shipment data
            
        Returns:
            DataFrame with merged external data
        """
        try:
            # Load external data
            weather_df = self.load_weather_data()
            traffic_df = self.load_traffic_data()
            
            # Merge weather data
            df = pd.merge(
                shipment_df,
                weather_df,
                on=["timestamp", "location"],
                how="left"
            )
            
            # Merge traffic data
            df = pd.merge(
                df,
                traffic_df,
                on=["timestamp", "location"],
                how="left"
            )
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error merging external data: {str(e)}")
            raise
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for the predictive model.
        
        Args:
            df: Input DataFrame with raw features
            
        Returns:
            DataFrame with engineered features
        """
        try:
            # Time-based features
            df["hour"] = df["timestamp"].dt.hour
            df["day_of_week"] = df["timestamp"].dt.dayofweek
            df["month"] = df["timestamp"].dt.month
            df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
            
            # Calculate historical averages
            window = pd.Timedelta(self.feature_config["time_window"])
            
            # Rolling averages for delivery times
            df["avg_delivery_time"] = df.groupby("route_id")["delivery_time"].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            
            # Rolling averages for delays
            df["avg_delay"] = df.groupby("route_id")["delay"].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            
            # Distance-based features
            df["distance_km"] = self._calculate_distances(
                df["origin_lat"], 
                df["origin_lon"],
                df["destination_lat"],
                df["destination_lon"]
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Error engineering features: {str(e)}")
            raise
    
    def prepare_model_data(self, df: pd.DataFrame, 
                          target_col: str) -> tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for model training.
        
        Args:
            df: Input DataFrame
            target_col: Name of the target column
            
        Returns:
            Tuple of (X, y) arrays for model training
        """
        try:
            # Select features
            feature_cols = [
                # Time features
                "hour", "day_of_week", "month", "is_weekend",
                
                # Historical features
                "avg_delivery_time", "avg_delay",
                
                # Distance features
                "distance_km",
                
                # Weather features
                *self.feature_config["weather_features"],
                
                # Traffic features
                *self.feature_config["traffic_features"]
            ]
            
            X = df[feature_cols].copy()
            y = df[target_col].copy()
            
            # Scale features
            X = self.scaler.fit_transform(X)
            
            return X, y
            
        except Exception as e:
            logger.error(f"Error preparing model data: {str(e)}")
            raise
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        # Forward fill for time series data
        df = df.fillna(method="ffill")
        
        # Fill remaining missing values with medians
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        return df
    
    def _calculate_distances(self, lat1: pd.Series, lon1: pd.Series,
                           lat2: pd.Series, lon2: pd.Series) -> pd.Series:
        """Calculate distances between coordinates using Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lon1_rad = np.radians(lon1)
        lat2_rad = np.radians(lat2)
        lon2_rad = np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c 