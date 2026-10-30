
import sqlite3

main_connection = sqlite3.connect("lunar_analysis.db")
ml_connection = sqlite3.connect("lunar_ml_integration.db")

main_coordinates = set(
    main_connection.execute(
        "SELECT pixel_y, pixel_x FROM observations"
    ).fetchall()
)

ml_coordinates = ml_connection.execute(
    "SELECT pixel_row, pixel_column FROM ml_results"
).fetchall()

matches = sum(
    (row, column) in main_coordinates
    for row, column in ml_coordinates
)

print("Full pixel records:", len(main_coordinates))
print("ML sample records:", len(ml_coordinates))
print("Matching coordinate pairs:", matches)
print("Unmatched ML records:", len(ml_coordinates) - matches)

main_connection.close()
ml_connection.close()
