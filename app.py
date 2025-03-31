# Deployable version of the dashboard
import os
import sys

# Add the project root to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the dashboard app
from logistics_optimization.src.visualization.simple_dashboard import app

# This is used by Gunicorn
server = app.server

# For local testing
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8065))
    app.run_server(debug=False, host='0.0.0.0', port=port) 