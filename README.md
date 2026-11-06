# BuildTrace
## Drone Assembly Quality Assurance and Parts Traceability System

### 1. Project Overview

BuildTrace is a Python-based application developed to support drone assembly quality inspection, component inventory management, and parts traceability.

The application helps users register drone components, record assembly inspections, assign components to specific drones, monitor inventory availability, and generate reports.

BuildTrace is designed as a prototype for organizing and demonstrating drone assembly quality assurance workflows.

### 2. Project Objectives

- Maintain digital records of drone components and suppliers.
- Record assembly inspection results.
- Track components assigned to individual drones.
- Prevent assignments that exceed available inventory.
- Monitor low-stock and out-of-stock components.
- Display inspection status summaries.
- Export inventory, inspection, and traceability records.

### 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application programming |
| Streamlit | Interactive web dashboard |
| SQLite | Local database storage |
| Pandas | Data processing and reporting |
| CSV | Exporting reports |

### 4. Main Modules

**Drone Parts Registration:** Stores component details, registered quantities, suppliers, and batch information.

**Assembly Quality Inspection:** Records inspection checkpoints, inspection statuses (Pass, Fail, Pending), inspectors, dates, and remarks.

**Drone Parts Assignment:** Associates registered components with Drone IDs and validates available quantities before saving assignments.

**Drone Parts Traceability:** Displays assigned components for a selected Drone ID, including supplier and batch information.

**Inventory Dashboard:** Displays registered, assigned, and available quantities, along with low-stock and out-of-stock alerts.

**Drone Quality Status Summary:** Summarizes recorded inspection results for each Drone ID and calculates an overall recorded status.

**CSV Reporting:** Supports downloading inspection, inventory, and traceability data.

### 5. Project Files

- `app.py` — Streamlit application and dashboard.
- `database.py` — Database initialization.
- `buildtrace.db` — SQLite database containing saved records.
- `README.md` — Project documentation.

### 6. How to Run the Project

1. Open Command Prompt in the BuildTrace project folder.
2. Activate the Python virtual environment.
3. Run the Streamlit application using:

   `python -m streamlit run app.py`

4. Open `http://localhost:8501` in a web browser.

Required Python packages include Streamlit and Pandas.

### 7. Testing

The prototype has been manually tested for:

- Component registration and database persistence.
- Parts assignment and inventory validation.
- Drone ID traceability search and CSV export.
- Inspection record creation and persistence.
- Inspection search, filtering, and CSV export.
- Inventory summary calculations and CSV export.

### 8. Limitations

BuildTrace is an educational prototype. Its inspection summaries reflect recorded checkpoints only. They do not establish that all required checks have been completed or that a drone is safe or approved for flight.

The application uses a local SQLite database and does not currently provide multi-user access controls or a production deployment environment.

### 9. Conclusion

BuildTrace demonstrates how Python, Streamlit, and SQLite can support digital recordkeeping for drone assembly quality assurance, component inventory monitoring, and parts traceability.