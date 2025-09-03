# FIDC API

## Overview
The FIDC API is a RESTful service designed for processing FIDC operations. It supports asynchronous processing using Celery, integrates with external price APIs, and provides functionality for operation calculations, job monitoring, and batch exports.

## Features
- **REST API**: Provides endpoints for processing operations, checking job status, and exporting data.
- **Asynchronous Processing**: Utilizes Celery for handling long-running tasks.
- **External Price Integration**: Fetches asset prices from external sources.
- **Operation Calculations**: Calculates operation values based on type (BUY/SELL).
- **Job Monitoring**: Tracks the status of processing jobs.
- **Batch Export Functionality**: Exports operation data to a specified bucket.

## Project Structure
```
├── app
│   ├── api
│   ├── models
│   ├── services
│   ├── tasks
│   └── utils
├── migrations
├── tests
├── celery_worker.py
├── run.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and updating the values as needed.

## Running the Application
To run the Flask application, execute:
```
python run.py
```

## Running Celery Worker
To start the Celery worker, run:
```
celery -A celery_worker worker --loglevel=info
```

## Testing
To run the tests, use:
```
pytest
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.
