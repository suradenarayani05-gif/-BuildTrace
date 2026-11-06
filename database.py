
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("buildtrace.db")

# Create a table for drone components
conn.execute("""
CREATE TABLE IF NOT EXISTS drone_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id TEXT NOT NULL UNIQUE,
    component TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    supplier TEXT NOT NULL,
    batch_number TEXT NOT NULL
)
""")


# Create assembly inspection table
conn.execute("""
CREATE TABLE IF NOT EXISTS assembly_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drone_id TEXT NOT NULL,
    checkpoint TEXT NOT NULL,
    inspection_status TEXT NOT NULL
        CHECK(inspection_status IN ('Pass', 'Fail', 'Pending')),
    inspector_name TEXT NOT NULL,
    inspection_date TEXT NOT NULL,
    remarks TEXT
)
""")

# Create drone parts traceability table
conn.execute("""
CREATE TABLE IF NOT EXISTS drone_traceability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drone_id TEXT NOT NULL,
    part_id TEXT NOT NULL,
    assigned_quantity INTEGER NOT NULL
        CHECK(assigned_quantity > 0),
    assignment_date TEXT NOT NULL,
    remarks TEXT,
    FOREIGN KEY (part_id)
        REFERENCES drone_parts(part_id)
)
""")


# Save changes
conn.commit()

# Close the database connection
conn.close()

print("BuildTrace database created successfully!")
