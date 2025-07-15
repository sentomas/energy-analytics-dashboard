# ⚡ Energy Consumption Analytics Dashboard

A comprehensive Streamlit-based web application for analyzing and monitoring energy consumption patterns, costs, and forecasting future usage.

## Features

- **📊 Interactive Dashboard**: Real-time energy consumption monitoring with key metrics
- **📤 Data Management**: Upload CSV/Excel files or manual data entry
- **📈 Advanced Analytics**: Consumption patterns, cost analysis, and efficiency metrics
- **🔮 Forecasting**: Predict future energy consumption using machine learning
- **🧮 Energy Calculator**: Calculate costs for single/multiple appliances
- **📄 Report Generation**: Generate comprehensive energy reports

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/energy-analytics-dashboard.git
cd energy-analytics-dashboard
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
energy-analytics-dashboard/
├── app.py                 # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── data_generator.py  # Sample data generation
│   ├── analytics.py       # Energy analytics functions
│   ├── forecasting.py     # Forecasting models
│   ├── calculator.py      # Energy cost calculator
│   └── reports.py         # Report generation
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Usage

### Dashboard
- View real-time energy consumption metrics
- Analyze daily, weekly, and monthly trends
- Monitor consumption by category and location

### Data Input
- Upload CSV/Excel files with energy data
- Manual data entry for individual records
- Database connection capabilities

### Analytics
- Consumption pattern analysis
- Cost breakdown and analysis
- Efficiency metrics calculation
- Peak usage identification

### Forecasting
- Linear and polynomial regression models
- Moving average predictions
- Configurable forecast periods

### Calculator
- Single appliance cost calculation
- Multiple appliance analysis
- Monthly bill estimation
- Energy savings recommendations

### Reports
- Summary reports with key metrics
- Detailed analysis reports
- Custom report builder
- Export functionality

## Data Format

The application expects data with the following columns:
- `timestamp`: Date and time of measurement
- `consumption_kwh`: Energy consumption in kWh
- `rate_per_kwh`: Energy rate per kWh
- `cost`: Total cost
- `category`: Energy category (Lighting, HVAC, Equipment, Other)
- `device`: Device/equipment name
- `location`: Location of consumption
- `notes`: Additional notes

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.
```

```text:.gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Streamlit
.streamlit/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data files
*.csv
*.xlsx
*.json
data/

# Logs
*.log
```

## 6. Now push everything to GitHub

```bash
git add .
```

```bash
git commit -m "Add README, requirements, and gitignore"
```

```bash
git push origin main
```

## 7. Optional: Create a GitHub Actions workflow for deployment

```yaml:.github/workflows/streamlit-app.yml
name: Streamlit App

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test import
      run: |
        python -c "import streamlit; print('Streamlit installed successfully')"
```

## 8. Final steps

```bash
mkdir .github
mkdir .github/workflows
```

Then add the workflow file and push:

```bash
git add .
```

```bash
git commit -m "Add GitHub Actions workflow"
```

```bash
git push origin main
```

## Summary of commands to run:

```bash
cd "C:\Petrus\02_Innovation Garrage\09_DT\digital_twin"
git init
git add .
git commit -m "Initial commit: Energy Consumption Analytics Dashboard"
git remote add origin https://github.com/YOUR_USERNAME/energy-analytics-dashboard.git
git branch -M main
git push -u origin main