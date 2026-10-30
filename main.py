
from fastapi import FastAPI, Query, HTTPException
from database import get_connection, get_ml_connection, initialize_database

app = FastAPI(
    title="Lunar Elemental Analysis API",
    description="API for exploring Chandrayaan-2 Al-Si data and machine learning results.",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def home():
    return {
        "message": "Lunar Elemental Analysis API is running",
        "project": "Chandrayaan-2 Al-Si Analysis",
        "status": "success"
    }


@app.get("/metadata")
def get_metadata():
    connection = get_connection()

    try:
        observation_count = connection.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]
    finally:
        connection.close()

    return {
        "project": "Chandrayaan-2 Al-Si Analysis",
        "database": "SQLite",
        "observation_count": observation_count,
        "data_status": "empty" if observation_count == 0 else "available"
    }


@app.get("/observations")
def get_observations(
    limit: int = Query(default=20, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM observations
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        ).fetchall()

        total = connection.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "observations": [dict(row) for row in rows]
        }
    finally:
        connection.close()


@app.get("/observations/{observation_id}")
def get_observation(observation_id: int):
    connection = get_connection()

    try:
        row = connection.execute(
            "SELECT * FROM observations WHERE id = ?",
            (observation_id,)
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Observation not found"
        )

    return dict(row)

@app.get("/ml-results")
def get_ml_results(limit: int = 20, offset: int = 0):
    if limit < 1 or limit > 1000:
        return {"error": "Limit must be between 1 and 1000"}

    if offset < 0:
        return {"error": "Offset cannot be negative"}

    connection = get_ml_connection()

    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM ml_results"
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT observation_id, pixel_row, pixel_column,
                   cluster_label, isolation_forest_score,
                   isolation_forest_flag
            FROM ml_results
            ORDER BY pixel_row, pixel_column
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        ).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [dict(row) for row in rows]
        }

    finally:
        connection.close()


@app.get("/combined-results")
def get_combined_results(
    limit: int = Query(default=20, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    observations_connection = get_connection()
    ml_connection = get_ml_connection()

    try:
        total = ml_connection.execute(
            "SELECT COUNT(*) FROM ml_results"
        ).fetchone()[0]

        rows = observations_connection.execute(
            """
            ATTACH DATABASE ? AS ml_db
            """,
            (str(__import__("pathlib").Path(__file__).resolve().parent / "lunar_ml_integration.db"),)
        )

        results = observations_connection.execute(
            """
            SELECT
                o.pixel_y AS pixel_row,
                o.pixel_x AS pixel_column,
                o.band_1,
                o.band_2,
                m.cluster_label,
                m.isolation_forest_score,
                m.isolation_forest_flag
            FROM observations AS o
            INNER JOIN ml_db.ml_results AS m
                ON o.pixel_y = m.pixel_row
                AND o.pixel_x = m.pixel_column
            ORDER BY o.pixel_y, o.pixel_x
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        ).fetchall()

        return {
            "total_ml_records": total,
            "limit": limit,
            "offset": offset,
            "results": [dict(row) for row in results]
        }

    finally:
        try:
            observations_connection.execute("DETACH DATABASE ml_db")
        except Exception:
            pass
        observations_connection.close()
        ml_connection.close()
