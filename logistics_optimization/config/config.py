from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Data paths
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

# Model parameters
MODEL_CONFIG = {
    "random_seed": 42,
    "test_size": 0.2,
    "validation_size": 0.1,
    
    # Predictive model parameters
    "prediction": {
        "batch_size": 64,
        "epochs": 100,
        "learning_rate": 0.001,
        "early_stopping_patience": 10,
    },
    
    # Feature engineering parameters
    "features": {
        "time_window": "7D",  # 7 days
        "weather_features": ["temperature", "precipitation", "wind_speed"],
        "traffic_features": ["congestion_level", "incident_count"],
    },
}

# Optimization parameters
OPTIMIZATION_CONFIG = {
    "solver": "CBC",  # Default solver for PuLP
    "time_limit": 300,  # 5 minutes
    "gap_tolerance": 0.01,
    
    # Route optimization parameters
    "route_optimization": {
        "max_distance": 500,  # km
        "max_duration": 12,   # hours
        "vehicle_capacity": 1000,  # kg
    },
    
    # Inventory optimization parameters
    "inventory_optimization": {
        "holding_cost_rate": 0.15,  # 15% per year
        "stockout_cost_multiplier": 2.0,
        "service_level": 0.95,
    },
}

# API configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", 8000)),
    "workers": int(os.getenv("API_WORKERS", 4)),
}

# Database configuration
DB_CONFIG = {
    "url": os.getenv("DATABASE_URL", "sqlite:///logistics.db"),
    "pool_size": int(os.getenv("DB_POOL_SIZE", 5)),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 10)),
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
} 