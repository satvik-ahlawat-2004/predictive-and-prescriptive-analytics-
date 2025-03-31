# Logistics Optimization System

A comprehensive Python-based solution that leverages predictive and prescriptive analytics to optimize logistics operations. This system analyzes historical data to forecast potential disruptions and provides actionable recommendations for logistics optimization.

## Features

- **Predictive Analytics**
  - Shipment delay prediction
  - Demand forecasting
  - Weather impact analysis
  - Traffic pattern prediction

- **Prescriptive Analytics**
  - Route optimization
  - Inventory level optimization
  - Delivery schedule optimization
  - Resource allocation

- **Data Pipeline**
  - Automated data ingestion
  - Data preprocessing and cleaning
  - Feature engineering
  - Model training and updating

- **Visualization & Reporting**
  - Interactive dashboards
  - Real-time alerts
  - Performance metrics
  - Custom report generation

## Project Structure

```
logistics_optimization/
├── config/                 # Configuration files
├── data/                   # Data storage
│   ├── raw/               # Raw data
│   ├── processed/         # Processed data
│   └── external/          # External data sources
├── models/                # Trained models
├── notebooks/             # Jupyter notebooks
├── src/                   # Source code
│   ├── data/             # Data processing scripts
│   ├── features/         # Feature engineering
│   ├── models/           # Model training and prediction
│   ├── optimization/     # Optimization algorithms
│   ├── visualization/    # Visualization and reporting
│   └── api/             # API endpoints
├── tests/                # Unit tests
└── logs/                 # Application logs
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd logistics-optimization
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Configure the environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Run the data pipeline:
```bash
python src/data/run_pipeline.py
```

3. Start the API server:
```bash
uvicorn src.api.main:app --reload
```

4. Access the dashboard:
```bash
python src/visualization/run_dashboard.py
```

## Configuration

The system can be configured through:
- Environment variables (.env file)
- Configuration files in the config/ directory
- Command-line arguments for specific scripts

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
black .
```

4. Run linter:
```bash
flake8
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Logistics Optimization Dashboard

A modern dashboard for logistics data analysis, providing predictive and prescriptive analytics including route optimization, inventory management, and delivery performance tracking.

## Features

- **Data Upload:** Upload logistics data in CSV format
- **Visual Insights:** Interactive visualizations of key logistics metrics
- **Predictive Analytics:** Forecasts for delays and demand
- **Prescriptive Suggestions:** Route optimization and operational recommendations
- **Report Generation:** Create and download comprehensive PDF reports

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the dashboard:
   ```
   python app.py
   ```

3. Access the dashboard at:
   ```
   http://127.0.0.1:8065
   ```

## Deployment Options

### Deploy on Render.com

1. Sign up for a [Render account](https://render.com/)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure the service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:server`
   - Environment Variables:
     - Key: `PYTHON_VERSION`, Value: `3.9.x`

### Deploy on Heroku

1. Sign up for a [Heroku account](https://heroku.com/)
2. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Login to Heroku:
   ```
   heroku login
   ```
4. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```
5. Deploy to Heroku:
   ```
   git push heroku main
   ```

### Deploy on PythonAnywhere

1. Sign up for a [PythonAnywhere account](https://www.pythonanywhere.com/)
2. Create a new web app with Flask
3. Set up a virtual environment and install requirements
4. Modify the WSGI file to point to your app.py file

## Project Structure

- `app.py` - Main deployment entry point
- `logistics_optimization/src/visualization/simple_dashboard.py` - Dashboard implementation
- `logistics_optimization/src/api/main.py` - API for data processing (not required for deployment) 