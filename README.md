# Geospatial File Measurement API

A backend API for uploading geospatial files and calculating measurements from their geometries.

The API accepts a ZIP archive containing a Shapefile (`.shp`) or KML (`.kml`), extracts and processes the geospatial data, handles coordinate reference systems (CRS), and calculates measurements based on geometry type.

## Features

- Upload ZIP archives containing supported geospatial files
- Support for Shapefile (`.shp`) and KML (`.kml`)
- Extract and read geospatial features using GeoPandas
- Detect:
  - Feature ID
  - Geometry type
  - Geometry
  - CRS
  - Feature properties
- Calculate:
  - Polygon / MultiPolygon → area in square meters
  - LineString / MultiLineString → length in meters
  - Point → no measurement
- Handle geographic CRS such as EPSG:4326
- Automatically transform geographic coordinates to a suitable projected CRS before measurement
- Gracefully handle unsupported and empty geometries
- Store uploaded file metadata in SQLite
- Interactive Swagger API documentation
- Automated tests using Pytest

---

## Tech Stack

| Technology  | Purpose                    |
| ----------- | -------------------------- |
| Python 3.12 | Backend language           |
| FastAPI     | REST API framework         |
| GeoPandas   | Geospatial data processing |
| Shapely     | Geometry operations        |
| PyProj      | CRS transformation         |
| Pyogrio     | Geospatial file I/O        |
| SQLAlchemy  | Database ORM               |
| SQLite      | Local metadata storage     |
| Pytest      | Automated testing          |

---

## Project Structure

```text
geospatial-measurement-api/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── files.py
│   │       └── measurements.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── file.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── file.py
│   │   └── measurement.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crs_service.py
│   │   ├── file_service.py
│   │   ├── geospatial_service.py
│   │   └── measurement_service.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_validation.py
│   │
│   ├── database.py
│   └── main.py
│
├── tests/
│   └── test_measurements.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

# Setup

## Prerequisites

- Python 3.12
- pip
- Git

## 1. Clone the repository

```bash
git clone https://github.com/NaveenKumar095/geospatial-measurement-api.git
cd geospatial-measurement-api
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 5. Run tests

```bash
python -m pytest -v
```

---

# API Endpoints

## 1. Health Check

### `GET /health`

Checks whether the API is running.

### Response

```json
{
  "status": "ok"
}
```

---

## 2. Upload Geospatial File

### `POST /api/files/`

Uploads a ZIP archive containing a supported geospatial file.

### Supported files

- `.shp`
- `.kml`

For a Shapefile, all required companion files should be included in the ZIP, such as:

```text
.shp
.shx
.dbf
.prj
```

### Example response

```json
{
  "id": 1,
  "filename": "example.zip",
  "file_path": "uploads\\example.zip",
  "status": "uploaded"
}
```

---

## 3. Get File Details

### `GET /api/files/{file_id}`

Returns metadata for an uploaded file.

### Example

```text
GET /api/files/1
```

### Response

```json
{
  "id": 1,
  "filename": "example.zip",
  "status": "uploaded",
  "created_at": "2026-10-07T05:58:59.935796"
}
```

---

## 4. Get Measurements

### `GET /api/files/{file_id}/measurements/`

Processes the uploaded geospatial file and returns measurements for its features.

### Example

```text
GET /api/files/1/measurements/
```

### Polygon response

```json
[
  {
    "feature_id": 0,
    "geometry_type": "Polygon",
    "properties": {
      "name": "Test Polygon"
    },
    "area_m2": 1201684.7167952394,
    "length_m": null,
    "warning": null
  }
]
```

### LineString response

```json
[
  {
    "feature_id": 0,
    "geometry_type": "LineString",
    "properties": {
      "name": "Test Line"
    },
    "area_m2": null,
    "length_m": 1550.4276666371866,
    "warning": null
  }
]
```

### Point response

```json
[
  {
    "feature_id": 0,
    "geometry_type": "Point",
    "properties": {
      "name": "Test Point"
    },
    "area_m2": null,
    "length_m": null,
    "warning": null
  }
]
```

---

# Processing Flow

```text
Client
  │
  │ POST /api/files/
  ▼
FastAPI Upload Endpoint
  │
  ▼
Validate ZIP
  │
  ├── Invalid → 400 Bad Request
  │
  ▼
Save ZIP
  │
  ▼
Store File Metadata in SQLite
  │
  ▼
GET /api/files/{id}/measurements/
  │
  ▼
Extract ZIP
  │
  ▼
Find .shp / .kml
  │
  ▼
Read with GeoPandas
  │
  ▼
Read CRS
  │
  ├── Geographic CRS
  │       │
  │       ▼
  │   Estimate suitable UTM CRS
  │       │
  │       ▼
  │   Transform geometry
  │
  ▼
Determine Geometry Type
  │
  ├── Polygon → Area
  ├── MultiPolygon → Area
  ├── LineString → Length
  ├── MultiLineString → Length
  ├── Point → No measurement
  └── Unsupported → Warning
  │
  ▼
Return JSON Response
```

---

# Architecture

The application follows a simple layered architecture.

## API Layer

Located in:

```text
app/api/routes/
```

Responsible for:

- HTTP endpoints
- Request handling
- Input validation
- HTTP error responses

## Service Layer

Located in:

```text
app/services/
```

Responsible for business logic.

### `file_service.py`

Handles saving uploaded files.

### `geospatial_service.py`

Handles:

- ZIP extraction
- Finding supported geospatial files
- Reading data with GeoPandas

### `crs_service.py`

Handles:

- CRS validation
- Geographic vs projected CRS detection
- CRS transformation

### `measurement_service.py`

Handles:

- Geometry detection
- Area calculation
- Length calculation
- Unsupported geometry handling

## Database Layer

Located in:

```text
app/database.py
app/models/
```

SQLite is used to store uploaded file metadata.

The database currently stores:

- File ID
- Original filename
- File path
- Processing status
- Creation timestamp

---

# CRS Handling

Correct CRS handling is important for accurate measurements.

Geographic coordinate systems such as:

```text
EPSG:4326
```

represent coordinates using longitude and latitude in degrees.

Calculating area or distance directly from geographic coordinates would produce values in degree-based units and would not provide meaningful square-meter or meter measurements.

Therefore, when the input CRS is geographic, the application:

```text
EPSG:4326
       ↓
Determine suitable projected CRS
       ↓
UTM CRS
       ↓
Transform geometry
       ↓
Calculate measurement
```

For example, the Bengaluru test dataset uses:

```text
Input CRS:
EPSG:4326

Measurement CRS:
EPSG:32643
```

`EPSG:32643` is a projected UTM CRS suitable for the test data location.

If the input data is already in a projected CRS, the application uses the existing CRS without unnecessary transformation.

If CRS information is missing, the application raises an error instead of silently assuming a CRS.

---

# Geometry Measurement Rules

| Geometry             | Measurement    |
| -------------------- | -------------- |
| Polygon              | Area in m²     |
| MultiPolygon         | Area in m²     |
| LineString           | Length in m    |
| MultiLineString      | Length in m    |
| Point                | No measurement |
| Unsupported geometry | Warning        |

For unsupported geometries, the API does not attempt to invent a measurement. Instead, it returns a warning.

---

# Error Handling

The API handles several invalid-input scenarios.

### File ID does not exist

Returns:

404 Not Found

### Non-ZIP upload

Returns:

```text
400 Bad Request
```

with:

```json
{
  "detail": "Only .zip files are supported"
}
```

### ZIP without supported geospatial file

Returns:

```text
400 Bad Request
```

with:

```json
{
  "detail": "ZIP must contain a .shp or .kml file"
}
```

### File ID does not exist

Returns:

```text
404 Not Found
```

### Missing CRS

Returns:

```text
400 Bad Request
```

instead of assuming an incorrect CRS.

### Empty geometry

Empty geometries are handled without attempting to estimate a UTM CRS from unavailable coordinates.

---

# Testing

The project includes automated tests covering the core measurement functionality.

Current test coverage includes:

- Polygon area calculation
- LineString length calculation
- Point handling
- Geographic CRS transformation
- Unsupported / empty geometry handling

Run:

```bash
python -m pytest -v
```

Expected result:

```text
5 passed
```

---

# Design Decisions

## FastAPI

FastAPI was selected because it provides:

- Simple REST API development
- Automatic request validation
- Automatic OpenAPI documentation
- Swagger UI
- Good support for asynchronous file handling
- Clear separation between routes and services

## GeoPandas

GeoPandas provides a high-level interface for reading and processing common geospatial formats while integrating well with Shapely and PyProj.

## SQLite

SQLite is used for the initial implementation because the assignment does not require a production database.

It keeps local development simple while still providing persistent metadata storage.

For a production deployment, PostgreSQL with PostGIS would be a stronger choice.

## Service Separation

File handling, CRS processing, geospatial reading, and measurement logic are separated into services.

This makes the code easier to:

- Test
- Maintain
- Extend
- Replace individual components

---

# Assumptions

- Uploaded files are provided as ZIP archives.
- ZIP archives contain either a Shapefile or KML.
- Shapefiles include the necessary companion files.
- CRS information is expected to be present.
- Measurements are returned in metric units:
  - Area → square meters
  - Length → meters
- Uploaded file metadata is stored in SQLite.
- Processing is currently synchronous.

---

# Limitations

The current implementation is intentionally focused on the assignment requirements.

Current limitations include:

- Uploaded files are stored on the local filesystem.
- Processing is synchronous.
- No authentication or authorization.
- No user-level file ownership.
- No background job queue.
- No cloud object storage.
- SQLite is intended for development/small-scale usage.
- KML support depends on the geospatial file-reading capabilities available through the installed GDAL/GeoPandas stack.

---

# Future Improvements

For a production-ready version, the following improvements could be added:

### Storage

Replace local filesystem storage with:

- Amazon S3
- Google Cloud Storage
- Azure Blob Storage

### Database

Replace SQLite with:

- PostgreSQL
- PostGIS

PostGIS would also allow more advanced spatial queries and indexing.

### Background Processing

Large geospatial files could be processed asynchronously using:

- Celery
- Redis
- Background workers

The upload endpoint could return immediately while processing happens in the background.

### Scalability

Potential improvements include:

- Horizontal API scaling
- Worker pools
- Object storage
- Job queues
- Processing status tracking

### Security

Add:

- Authentication
- Authorization
- File size limits
- ZIP bomb protection
- Path traversal protection
- Content validation
- Rate limiting

### Additional Geometries

Support additional geometry types and more advanced measurement operations.

---

# API Documentation

Once the application is running, interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

FastAPI also provides the OpenAPI specification at:

```text
http://127.0.0.1:8000/openapi.json
```

---

# Development

Start the development server:

```bash
uvicorn app.main:app --reload
```

Run the complete test suite:

```bash
python -m pytest -v
```

Check Git status:

```bash
git status
```

---

# License

This project was developed as part of a backend engineering assignment.
