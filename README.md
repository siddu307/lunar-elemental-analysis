# 🌙 Intelligent Analysis and Visualization of Lunar Elemental Composition Using Chandrayaan-2 Data

## Project Overview

This project analyzes Chandrayaan-2 lunar Al-Si raster data using data preprocessing and machine learning techniques.

It applies K-Means clustering to group similar pixel measurements and Isolation Forest to identify unusual observations. The results are stored in SQLite databases and explored through an interactive Streamlit dashboard.

## Objectives

- Process and clean Chandrayaan-2 raster data.
- Extract pixel coordinates and band measurements.
- Group similar pixel observations using K-Means.
- Detect unusual observations using Isolation Forest.
- Integrate pixel data and machine learning results.
- Visualize results through an interactive dashboard.

## Technology Stack

- Python
- Pandas
- FastAPI
- SQLite
- Streamlit
- Scikit-learn

## Machine Learning Algorithms

### 1. K-Means Clustering

K-Means is an unsupervised machine learning algorithm used to group similar pixel measurements into three clusters.

### 2. Isolation Forest

Isolation Forest is an anomaly detection algorithm used to identify unusual observations.

The anomaly flag values are:

- 0 – Normal observation
- 1 – Anomalous observation

## Dataset Information

The preprocessed dataset contains:

- 2,064,603 valid pixel records.
- Two measurement bands.
- Pixel row and column coordinates.
- No missing values in the cleaned dataset.

Machine learning was performed on a 100,000-record sample.

## Backend

FastAPI provides REST API endpoints for accessing pixel observations and machine learning results.

Available endpoints:

| Endpoint | Description |
|---|---|
| `/` | API status |
| `/metadata` | Dataset information |
| `/observations` | Retrieve pixel observations |
| `/observations/{observation_id}` | Retrieve an individual observation |
| `/ml-results` | Retrieve machine learning results |
| `/combined-results` | Retrieve integrated results |

## Dashboard Features

- Dataset summary cards.
- Cluster distribution chart.
- Cluster filtering.
- Anomaly filtering.
- Pixel row and column search.
- Combined pixel and ML results table.
- Filtered record count.
- CSV export.

## Project Structure

```text
lunar-analysis/
│
├── main.py
├── database.py
├── dashboard.py
├── import_pixels.py
├── check_csv.py
├── check_ml_matches.py
├── README.md
└── .gitignore
```

## Running the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd lunar-analysis
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows:

```powershell
.venv\Scripts\Activate
```

### 4. Install dependencies

```bash
pip install pandas fastapi uvicorn streamlit scikit-learn
```

### 5. Start the FastAPI backend

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the Streamlit dashboard

Open another terminal and run:

```bash
streamlit run dashboard.py
```

Dashboard:

```text
http://localhost:8501
```

**Note:** The original dataset and generated SQLite databases are not included in the Git repository. They must be provided locally before running the complete project.

## Important Scientific Note

Cluster labels and anomaly flags are computational machine learning outputs. They should not be interpreted as confirmed lunar geological classifications without further scientific validation.

## Project Status

Core preprocessing, machine learning integration, backend API development, dashboard development and API endpoint testing have been completed. Final documentation, repository setup and project presentation are in progress.

## Team Project

Developed as an academic project using Chandrayaan-2 lunar measurement data.