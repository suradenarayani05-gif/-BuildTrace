
import streamlit as st
import pandas as pd


import sqlite3

# Connect to BuildTrace database
def save_part(part_id, component, quantity, supplier, batch):
    with sqlite3.connect("buildtrace.db") as conn:
        conn.execute(
            """
            INSERT INTO drone_parts
            (part_id, component, quantity, supplier, batch_number)
            VALUES (?, ?, ?, ?, ?)
            """,
            (part_id, component, quantity, supplier, batch)
        )
        conn.commit()


def load_parts():
    with sqlite3.connect("buildtrace.db") as conn:
        return pd.read_sql_query(
            """
            SELECT
                part_id AS "Part ID",
                component AS "Component",
                quantity AS "Quantity",
                supplier AS "Supplier",
                batch_number AS "Batch Number"
            FROM drone_parts
            ORDER BY id
            """,
            conn
        )


# Save drone assembly inspection records
def save_inspection(
    drone_id,
    checkpoint,
    inspection_status,
    inspector_name,
    inspection_date,
    remarks
):
    with sqlite3.connect("buildtrace.db") as conn:
        conn.execute(
            """
            INSERT INTO assembly_inspections
            (
                drone_id,
                checkpoint,
                inspection_status,
                inspector_name,
                inspection_date,
                remarks
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                drone_id,
                checkpoint,
                inspection_status,
                inspector_name,
                str(inspection_date),
                remarks
            )
        )
        conn.commit()



# Load saved drone assembly inspections
def load_inspections():
    with sqlite3.connect("buildtrace.db") as conn:
        return pd.read_sql_query(
            """
            SELECT
                drone_id AS "Drone ID",
                checkpoint AS "Checkpoint",
                inspection_status AS "Status",
                inspector_name AS "Inspector",
                inspection_date AS "Date",
                remarks AS "Remarks"
            FROM assembly_inspections
            ORDER BY id DESC
            """,
            conn
        )





# Save drone parts assignment to SQLite
def save_assignment(
    drone_id,
    part_id,
    assigned_quantity,
    assignment_date,
    remarks
):
    with sqlite3.connect("buildtrace.db") as conn:

        # Enable foreign key checking
        conn.execute("PRAGMA foreign_keys = ON")

        conn.execute(
            """
            INSERT INTO drone_traceability
            (
                drone_id,
                part_id,
                assigned_quantity,
                assignment_date,
                remarks
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                drone_id,
                part_id,
                int(assigned_quantity),
                str(assignment_date),
                remarks
            )
        )

        conn.commit()


# Load saved drone parts assignments
def load_assignments():
    with sqlite3.connect("buildtrace.db") as conn:
        return pd.read_sql_query(
            """
            SELECT
                t.drone_id AS "Drone ID",
                t.part_id AS "Part ID",
                p.component AS "Component",
                t.assigned_quantity AS "Assigned Quantity",
                p.supplier AS "Supplier",
                p.batch_number AS "Batch Number",
                t.assignment_date AS "Assignment Date",
                t.remarks AS "Remarks"
            FROM drone_traceability AS t
            LEFT JOIN drone_parts AS p
                ON t.part_id = p.part_id
            ORDER BY t.id DESC
            """,
            conn
        )



# Check available quantity of a registered part
def check_available_quantity(part_id):

    with sqlite3.connect("buildtrace.db") as conn:

        registered = conn.execute(
            """
            SELECT quantity
            FROM drone_parts
            WHERE part_id = ?
            """,
            (part_id,)
        ).fetchone()

        if registered is None:
            return 0

        assigned = conn.execute(
            """
            SELECT COALESCE(SUM(assigned_quantity), 0)
            FROM drone_traceability
            WHERE part_id = ?
            """,
            (part_id,)
        ).fetchone()

        registered_quantity = int(registered[0])
        assigned_quantity = int(assigned[0])

        available_quantity = (
            registered_quantity - assigned_quantity
        )

        return available_quantity



# Load inventory quantity summary
def load_inventory_summary():

    with sqlite3.connect("buildtrace.db") as conn:

        return pd.read_sql_query(
            """
            SELECT
                p.part_id AS "Part ID",
                p.component AS "Component",
                p.quantity AS "Registered Quantity",

                COALESCE(
                    SUM(t.assigned_quantity), 0
                ) AS "Assigned Quantity",

                p.quantity - COALESCE(
                    SUM(t.assigned_quantity), 0
                ) AS "Available Quantity"

            FROM drone_parts AS p

            LEFT JOIN drone_traceability AS t
                ON p.part_id = t.part_id

            GROUP BY
                p.part_id,
                p.component,
                p.quantity

            ORDER BY p.part_id
            """,
            conn
        )



# Generate drone inspection status summary
def load_drone_quality_summary():

    inspections = load_inspections()

    if inspections.empty:
        return pd.DataFrame(
            columns=[
                "Drone ID",
                "Pass",
                "Fail",
                "Pending",
                "Overall Status"
            ]
        )

    summary = pd.crosstab(
        inspections["Drone ID"],
        inspections["Status"]
    )

    for status in ["Pass", "Fail", "Pending"]:
        if status not in summary.columns:
            summary[status] = 0

    summary = summary.reset_index()

    def overall_status(row):
        if row["Fail"] > 0:
            return "Fail"
        elif row["Pending"] > 0:
            return "Pending"
        else:
            return "Pass"

    summary["Overall Status"] = summary.apply(
        overall_status,
        axis=1
    )

    return summary[
        [
            "Drone ID",
            "Pass",
            "Fail",
            "Pending",
            "Overall Status"
        ]
    ]






st.set_page_config(
    page_title="BuildTrace",
    page_icon="🛠️",
    layout="wide"
)

st.title("BuildTrace")
st.subheader("Drone Assembly QA and Parts Traceability System")

st.write("Welcome to the BuildTrace Project Dashboard!")

st.info("Project Status: Development Started")

st.header("Main Modules")

st.write("1. Drone Parts and BOM Management")
st.write("2. Assembly Quality Checkpoints")
st.write("3. Bench-Test Certification")
st.write("4. Defect Tracking and Reports")

st.success("BuildTrace application is running successfully!")


# Drone Parts Management Module

st.divider()
st.header("📦 Drone Parts Management")

st.write("Saved Drone Components - Bill of Materials")

# Load parts from SQLite database
df = load_parts()

# Display saved components
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# Display summary
st.subheader("📊 Parts Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric("Component Types", len(df))

with col2:
    st.metric(
        "Total Components",
        int(df["Quantity"].sum())
    )



# Drone Parts Registration Form

st.divider()
st.header("➕ Register New Drone Part")

with st.form("add_part_form"):
    part_id = st.text_input("Part ID", placeholder="P007")
    component = st.text_input(
        "Component Name",
        placeholder="GPS Module"
    )
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=1
    )
    supplier = st.text_input(
        "Supplier Name",
        placeholder="Supplier G"
    )
    batch = st.text_input(
        "Batch Number",
        placeholder="B007"
    )

    submitted = st.form_submit_button("Add Part")

if submitted:
    if not all([
        part_id.strip(),
        component.strip(),
        supplier.strip(),
        batch.strip()
    ]):
        st.error("Please fill in all fields.")
    else:
        new_part = {
            "Part ID": part_id.strip(),
            "Component": component.strip(),
            "Quantity": quantity,
            "Supplier": supplier.strip(),
            "Batch Number": batch.strip()
        }

        try:
            save_part(
                part_id.strip(),
                component.strip(),
                int(quantity),
                supplier.strip(),
                batch.strip()
            )
            st.success("Part saved permanently in database!")
        except sqlite3.IntegrityError:
            st.error("This Part ID already exists.")


        st.success("New drone part registered!")
        st.write("Registered Part Details:")
        st.dataframe(
            pd.DataFrame([new_part]),
            hide_index=True
        )



# Drone Assembly Quality Inspection Module

st.divider()
st.header("🔧 Drone Assembly Quality Inspection")

st.write("Record drone assembly inspection details.")

with st.form("assembly_inspection_form"):

    drone_id = st.text_input(
        "Drone ID",
        placeholder="DRONE001"
    )

    checkpoint = st.selectbox(
        "Inspection Checkpoint",
        [
            "Frame Condition",
            "Motor Mounting Inspection",
            "Propeller Condition",
            "Wiring Inspection",
            "Battery Mounting Inspection",
            "Flight Controller Mounting"
        ]
    )

    inspection_status = st.selectbox(
        "Inspection Status",
        ["Pending", "Pass", "Fail"]
    )

    inspector_name = st.text_input(
        "Inspector Name"
    )

    inspection_date = st.date_input(
        "Inspection Date"
    )

    remarks = st.text_area(
        "Inspection Remarks"
    )

    inspection_submitted = st.form_submit_button(
        "Submit Inspection"
    )



# Save inspection when the form is submitted
if inspection_submitted:

    if not drone_id.strip() or not inspector_name.strip():
        st.error("Please enter Drone ID and Inspector Name.")

    else:
        try:
            save_inspection(
                drone_id.strip(),
                checkpoint,
                inspection_status,
                inspector_name.strip(),
                inspection_date,
                remarks.strip()
            )

            st.success(
                "Inspection record saved permanently in database!"
            )

            st.subheader("Saved Inspection Details")

            st.write("Drone ID:", drone_id)
            st.write("Checkpoint:", checkpoint)
            st.write("Status:", inspection_status)
            st.write("Inspector:", inspector_name)
            st.write("Date:", inspection_date)
            st.write("Remarks:", remarks)

        except sqlite3.Error as error:
            st.error(f"Database error: {error}")



# Display saved assembly inspection records

st.divider()
st.header("📋 Assembly Inspection Records")

st.write("Previously saved drone assembly inspections")

inspection_df = load_inspections()

if inspection_df.empty:
    st.info("No inspection records found.")
else:
    st.dataframe(
        inspection_df,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        f"Total Inspection Records: {len(inspection_df)}"
    )



# Quality Inspection Summary

st.divider()
st.header("📊 Quality Inspection Summary")

total_inspections = len(inspection_df)

passed_inspections = len(
    inspection_df[inspection_df["Status"] == "Pass"]
)

failed_inspections = len(
    inspection_df[inspection_df["Status"] == "Fail"]
)

pending_inspections = len(
    inspection_df[inspection_df["Status"] == "Pending"]
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Inspections", total_inspections)

with col2:
    st.metric("Passed", passed_inspections)

with col3:
    st.metric("Failed", failed_inspections)

with col4:
    st.metric("Pending", pending_inspections)


# Quality Inspection Status Chart

st.divider()
st.header("📈 Quality Inspection Status Chart")

status_chart_data = pd.DataFrame({
    "Inspection Status": ["Pass", "Fail", "Pending"],
    "Number of Inspections": [
        passed_inspections,
        failed_inspections,
        pending_inspections
    ]
})

st.bar_chart(
    status_chart_data,
    x="Inspection Status",
    y="Number of Inspections"
)



# Drone Inspection Search Module

st.divider()
st.header("🔍 Search Drone Inspection Records")

st.write("Search inspection records using a Drone ID.")

search_drone_id = st.text_input(
    "Enter Drone ID",
    placeholder="Example: DRONE001"
)

if search_drone_id.strip():

    filtered_inspections = inspection_df[
        inspection_df["Drone ID"].str.contains(
            search_drone_id.strip(),
            case=False,
            na=False,
            regex=False
        )
    ]

    if filtered_inspections.empty:
        st.warning("No inspection records found for this Drone ID.")

    else:
        st.success(
            f"Found {len(filtered_inspections)} inspection record(s)."
        )

        st.dataframe(
            filtered_inspections,
            use_container_width=True,
            hide_index=True
        )

else:
    st.info("Enter a Drone ID above to search inspection records.")



# Inspection Status Filter Module

st.divider()
st.header("🔎 Filter Inspections by Status")

st.write("View inspection records based on their status.")

selected_status = st.selectbox(
    "Select Inspection Status",
    ["All", "Pass", "Fail", "Pending"]
)

if selected_status == "All":
    status_filtered_df = inspection_df.copy()

else:
    status_filtered_df = inspection_df[
        inspection_df["Status"] == selected_status
    ]

if status_filtered_df.empty:
    st.info("No inspection records found for this status.")

else:
    st.success(
        f"Found {len(status_filtered_df)} inspection record(s)."
    )

    st.dataframe(
        status_filtered_df,
        use_container_width=True,
        hide_index=True
    )



# Export Inspection Records to CSV

st.divider()
st.header("📥 Export Inspection Records")

st.write("Download saved inspection records as a CSV file.")

csv_data = inspection_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Inspection Records (CSV)",
    data=csv_data,
    file_name="BuildTrace_Inspection_Records.csv",
    mime="text/csv",
    disabled=inspection_df.empty
)



# Drone Parts Assignment Module

st.divider()
st.header("🔗 Drone Parts Assignment")

st.write("Assign registered drone components to a drone assembly.")

# Load registered parts
available_parts = load_parts()

if available_parts.empty:
    st.warning("Please register a drone part first.")

else:
    # Create part selection options
    part_options = {
        f"{row['Part ID']} - {row['Component']}": row["Part ID"]
        for _, row in available_parts.iterrows()
    }

    with st.form("drone_parts_assignment_form"):

        assignment_drone_id = st.text_input(
            "Drone ID",
            placeholder="Example: DRONE001"
        )

        selected_part = st.selectbox(
            "Select Registered Part",
            list(part_options.keys())
        )

        assigned_quantity = st.number_input(
            "Assigned Quantity",
            min_value=1,
            value=1,
            step=1
        )

        assignment_date = st.date_input(
            "Assignment Date"
        )

        assignment_remarks = st.text_area(
            "Remarks"
        )

        assignment_submitted = st.form_submit_button(
            "Assign Part to Drone"
        )

   
    # Save assignment when the form is submitted
    if assignment_submitted:

        if not assignment_drone_id.strip():
            st.error("Please enter a Drone ID.")

        else:
            selected_part_id = part_options[selected_part]

            try:
                
                available_quantity = check_available_quantity(
                    selected_part_id
                )

                if assigned_quantity > available_quantity:
                    st.error(
                        f"Insufficient inventory! Only "
                        f"{available_quantity} unit(s) available."
                    )
                    st.stop()

                save_assignment(
                    assignment_drone_id.strip(),
                    selected_part_id,
                    assigned_quantity,
                    assignment_date,
                    assignment_remarks.strip()
                )

                st.success(
                    "Drone part assignment saved permanently!"
                )

                st.subheader("Saved Assignment Details")

                st.write("Drone ID:", assignment_drone_id)
                st.write("Part ID:", selected_part_id)
                st.write("Quantity:", assigned_quantity)
                st.write("Date:", assignment_date)
                st.write("Remarks:", assignment_remarks)

            except sqlite3.Error as error:
                st.error(f"Database error: {error}")


# Drone Parts Traceability Table

st.divider()
st.header("📦 Drone Parts Traceability Records")

st.write("View all drone component assignments.")

# Load saved assignments from SQLite
traceability_df = load_assignments()

if traceability_df.empty:
    st.info("No drone parts assignments found.")

else:
    st.dataframe(
        traceability_df,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        f"Total Part Assignments: {len(traceability_df)}"
    )



# Search Drone Parts Traceability Records

st.divider()
st.header("🔍 Search Drone Parts by Drone ID")

st.write("Find components assigned to a specific drone.")

search_trace_drone = st.text_input(
    "Enter Drone ID to Search",
    placeholder="Example: DRONE001",
    key="traceability_search"
)

if search_trace_drone.strip():

    matching_parts = traceability_df[
        traceability_df["Drone ID"].str.strip().str.upper()
        == search_trace_drone.strip().upper()
    ]

    if matching_parts.empty:
        st.warning("No assigned components found for this Drone ID.")

    else:
        st.success(
            f"Found {len(matching_parts)} component assignment(s)."
        )

        st.dataframe(
            matching_parts,
            use_container_width=True,
            hide_index=True
        )


        # Drone Traceability Summary
        st.subheader("Drone Traceability Summary")

        total_assignments = len(matching_parts)
        unique_components = matching_parts["Part ID"].nunique()
        total_quantity = matching_parts["Assigned Quantity"].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Assignments", total_assignments)

        with col2:
            st.metric("Unique Parts", unique_components)

        with col3:
            st.metric("Total Assigned Quantity", int(total_quantity))



        # Export Drone Traceability Records

        st.subheader("Export Drone Traceability Report")

        csv_data = matching_parts.to_csv(index=False)

        st.download_button(
            label="Download Drone Traceability CSV",
            data=csv_data,
            file_name=f"{search_trace_drone.strip().upper()}_traceability.csv",
            mime="text/csv",
            key="download_drone_traceability"
        )



else:
    st.info("Enter a Drone ID above to view assigned components.")




# Inventory Availability Dashboard

st.divider()
st.header("📦 Inventory Availability Dashboard")

st.write(
    "Monitor registered, assigned, and available drone components."
)

# Load inventory summary from SQLite
inventory_df = load_inventory_summary()

if inventory_df.empty:
    st.info("No registered drone parts found.")

else:
    st.dataframe(
        inventory_df,
        use_container_width=True,
        hide_index=True
    )



# Low Stock Alert System

st.divider()
st.header("Low Stock Alerts")

st.write("Components with 5 or fewer units available.")

if inventory_df.empty:
    st.info("No inventory records available.")

else:
    low_stock_df = inventory_df[
        inventory_df["Available Quantity"] <= 5
    ].copy()

    if low_stock_df.empty:
        st.success("All registered components have sufficient stock.")

    else:
        low_stock_df["Stock Status"] = low_stock_df[
            "Available Quantity"
        ].apply(
            lambda quantity: (
                "Out of Stock" if quantity <= 0
                else "Low Stock"
            )
        )

        st.warning(
            f"{len(low_stock_df)} component(s) need attention!"
        )

        st.dataframe(
            low_stock_df,
            use_container_width=True,
            hide_index=True
        )



# Inventory Status Summary Cards

st.divider()
st.header("Inventory Status Summary")

if inventory_df.empty:
    st.info("No inventory records available.")

else:
    total_parts = len(inventory_df)

    sufficient_parts = len(
        inventory_df[
            inventory_df["Available Quantity"] > 5
        ]
    )

    low_stock_parts = len(
        inventory_df[
            (inventory_df["Available Quantity"] > 0)
            & (inventory_df["Available Quantity"] <= 5)
        ]
    )

    out_of_stock_parts = len(
        inventory_df[
            inventory_df["Available Quantity"] <= 0
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Registered Parts", total_parts)

    with col2:
        st.metric("Sufficient Stock", sufficient_parts)

    with col3:
        st.metric("Low Stock", low_stock_parts)

    with col4:
        st.metric("Out of Stock", out_of_stock_parts)



# Inventory CSV Export

st.divider()
st.header("Download Inventory Report")

st.write(
    "Export registered, assigned, and available "
    "component quantities."
)

if inventory_df.empty:
    st.info("No inventory data available to export.")

else:
    inventory_csv = inventory_df.to_csv(index=False)

    st.download_button(
        label="Download Inventory CSV",
        data=inventory_csv,
        file_name="BuildTrace_Inventory_Report.csv",
        mime="text/csv",
        key="download_inventory_report"
    )



# Drone Quality Status Summary Dashboard

st.divider()
st.header("Drone Quality Status Summary")

st.write(
    "View inspection results and overall recorded "
    "quality status for each drone."
)

# Load inspection summary from SQLite
quality_summary_df = load_drone_quality_summary()

if quality_summary_df.empty:
    st.info("No drone inspection records found.")

else:
    st.dataframe(
        quality_summary_df,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        f"Total Drones Inspected: {len(quality_summary_df)}"
    )



    # Drone Quality Status Summary Cards

    passed_drones = len(
        quality_summary_df[
            quality_summary_df["Overall Status"] == "Pass"
        ]
    )

    failed_drones = len(
        quality_summary_df[
            quality_summary_df["Overall Status"] == "Fail"
        ]
    )

    pending_drones = len(
        quality_summary_df[
            quality_summary_df["Overall Status"] == "Pending"
        ]
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Passed Drones", passed_drones)

    with col2:
        st.metric("Failed Drones", failed_drones)

    with col3:
        st.metric("Pending Drones", pending_drones)
