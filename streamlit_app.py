
import requests
import streamlit as st

environment = st.sidebar.selectbox(
    "Backend environment",
    ["Local", "Production"]
)

API_URLS = {
    "Local": "http://localhost:8000",
    "Production": "https://techsuperkings.onrender.com"
}

API_URL = API_URLS[environment]
st.set_page_config(
    page_title="CivicDesk | Admin",
    page_icon="🏛️",
    layout="wide",
)

st.title("🏛️ CivicDesk — Admin Dashboard")
st.caption("Complaint Management System")


# ---------- API functions ----------

@st.cache_data(ttl=5)
def fetch_complaints():
    response = requests.get(
        f"{API_URL}/complaints",
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def fetch_complaint(complaint_id):
    response = requests.get(
        f"{API_URL}/complaints/{complaint_id}",
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def show_error(error):
    st.error(f"Request failed: {error}")


# ---------- Sidebar ----------

with st.sidebar:
    st.header("Admin Panel")

    if st.button("🔄 Refresh complaints", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption("CivicDesk Prototype")


# ---------- Main dashboard ----------

try:
    complaints = fetch_complaints()

    total = len(complaints)
    pending = sum(c.get("status") == "Pending" for c in complaints)
    in_progress = sum(c.get("status") == "In Progress" for c in complaints)
    resolved = sum(c.get("status") == "Resolved" for c in complaints)
    rejected = sum(c.get("status") == "Rejected" for c in complaints)

    # ---------- Statistics ----------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total", total)
    col2.metric("Pending", pending)
    col3.metric("In Progress", in_progress)
    col4.metric("Resolved", resolved)
    col5.metric("Rejected", rejected)

    st.divider()
    st.subheader("All Complaints")

    # ---------- Search and filters ----------

    search = st.text_input(
        "Search complaints",
        placeholder="Search by ID, name, department, location or description...",
    )

    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Pending", "In Progress", "Resolved", "Rejected"],
    )

    filtered = complaints

    if status_filter != "All":
        filtered = [
            c for c in filtered
            if c.get("status") == status_filter
        ]

    if search:
        query = search.lower()

        filtered = [
            c for c in filtered
            if query in str(c.get("id", "")).lower()
            or query in str(c.get("user_name", "")).lower()
            or query in str(c.get("department", "")).lower()
            or query in str(c.get("query_description", "")).lower()
            or query in str(c.get("location", "")).lower()
            or query in str(c.get("latitude", "")).lower()
            or query in str(c.get("longitude", "")).lower()
        ]

    # ---------- Complaint table ----------

    if not filtered:
        st.info("No complaints found.")

    else:
        table_data = [
            {
                "ID": c.get("id"),
                "Citizen": c.get("user_name"),
                "Department": c.get("department"),
                "Importance": c.get("importance_score"),
                "Status": c.get("status"),
                "Location": c.get("location") or "Not available",
                "Description": c.get("query_description"),
            }
            for c in filtered
        ]

        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Location": st.column_config.TextColumn(
                    "Location",
                    width="large",
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    width="large",
                ),
            },
        )

        st.divider()
        st.subheader("Manage Complaint")

        complaint_ids = [c["id"] for c in filtered]

        selected_id = st.selectbox(
            "Select complaint ID",
            complaint_ids,
        )

        complaint = fetch_complaint(selected_id)

        st.markdown(f"## Complaint #{selected_id}")

        # ---------- Location ----------

        st.subheader("📍 Complaint Location")

        location = complaint.get("location")
        latitude = complaint.get("latitude")
        longitude = complaint.get("longitude")

        if location:
            st.success(location)
        else:
            st.warning("Place/address is not available.")

        loc_col1, loc_col2 = st.columns(2)

        loc_col1.metric(
            "Latitude",
            latitude if latitude is not None else "Not available",
        )

        loc_col2.metric(
            "Longitude",
            longitude if longitude is not None else "Not available",
        )

        if latitude is not None and longitude is not None:
            map_url = (
                f"https://www.google.com/maps?q={latitude},{longitude}"
            )
            st.link_button(
                "📍 Open in Google Maps",
                map_url,
            )

        st.divider()

        # ---------- Dedicated status update ----------

        st.subheader("🔄 Update Complaint Status")

        status_options = [
            "Pending",
            "In Progress",
            "Resolved",
            "Rejected",
        ]

        current_status = complaint.get("status") or "Pending"

        if current_status not in status_options:
            status_options.append(current_status)

        selected_status = st.selectbox(
            "Current status",
            status_options,
            index=status_options.index(current_status),
            key=f"status_{selected_id}",
        )

        if st.button(
            "Update Status",
            type="primary",
            use_container_width=True,
        ):
            try:
                response = requests.patch(
                    f"{API_URL}/complaints/{selected_id}",
                    json={"status": selected_status},
                    timeout=20,
                )

                response.raise_for_status()

                st.success("Complaint status updated!")
                st.cache_data.clear()
                st.rerun()

            except requests.RequestException as e:
                show_error(e)

        st.divider()

        # ---------- Edit complaint details ----------

        with st.expander("✏️ Edit Complaint Details"):

            with st.form("edit_complaint"):

                name = st.text_input(
                    "Citizen name",
                    value=complaint.get("user_name") or "",
                )

                email = st.text_input(
                    "Email",
                    value=complaint.get("email_id") or "",
                )

                phone = st.text_input(
                    "Phone",
                    value=complaint.get("phone_number") or "",
                )

                department = st.text_input(
                    "Department",
                    value=complaint.get("department") or "",
                )

                description = st.text_area(
                    "Complaint description",
                    value=complaint.get("query_description") or "",
                )

                importance = st.number_input(
                    "Importance score",
                    value=int(complaint.get("importance_score") or 0),
                    step=1,
                )

                location_input = st.text_input(
                    "Location / Place",
                    value=location or "",
                )

                latitude_input = st.text_input(
                    "Latitude",
                    value=(
                        str(latitude)
                        if latitude is not None
                        else ""
                    ),
                )

                longitude_input = st.text_input(
                    "Longitude",
                    value=(
                        str(longitude)
                        if longitude is not None
                        else ""
                    ),
                )

                submitted = st.form_submit_button(
                    "Save Complaint Changes",
                    use_container_width=True,
                )

                if submitted:
                    try:
                        payload = {
                            "user_name": name,
                            "email_id": email or None,
                            "phone_number": phone or None,
                            "department": department,
                            "query_description": description,
                            "importance_score": int(importance),
                            "location": location_input or None,
                            "latitude": (
                                float(latitude_input)
                                if latitude_input.strip()
                                else None
                            ),
                            "longitude": (
                                float(longitude_input)
                                if longitude_input.strip()
                                else None
                            ),
                        }

                        response = requests.patch(
                            f"{API_URL}/complaints/{selected_id}",
                            json=payload,
                            timeout=20,
                        )

                        response.raise_for_status()

                        st.success("Complaint updated successfully!")
                        st.cache_data.clear()
                        st.rerun()

                    except (requests.RequestException, ValueError) as e:
                        show_error(e)

        st.divider()

        # ---------- Attachments ----------

        st.subheader("📎 Attachments")

        attachments = complaint.get("attachments", [])

        if attachments:
            for attachment in attachments:
                st.write(
                    f"**{attachment['storage_key']}**"
                    f" — {attachment['mime_type']}"
                    f" — {attachment['file_size']} bytes"
                )
        else:
            st.info("No attachments.")

        st.divider()

        # ---------- Admin remarks ----------

        st.subheader("📝 Admin Remarks")

        remarks = complaint.get("remarks", [])

        if remarks:
            for remark in remarks:
                st.info(
                    f"{remark['remark']}\n\n"
                    f"Added: {remark.get('created_at') or 'Unknown'}"
                )
        else:
            st.caption("No remarks added yet.")

        with st.form("add_remark", clear_on_submit=True):

            new_remark = st.text_area(
                "Write a new remark",
                placeholder="Enter inspection updates or administrative notes...",
            )

            add_button = st.form_submit_button(
                "Add Remark",
                use_container_width=True,
            )

            if add_button:
                if not new_remark.strip():
                    st.warning("Please enter a remark.")

                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/complaints/{selected_id}/remarks",
                            json={"remark": new_remark},
                            timeout=20,
                        )

                        response.raise_for_status()

                        st.success("Remark added!")
                        st.rerun()

                    except requests.RequestException as e:
                        show_error(e)


except requests.RequestException as e:
    st.error(
        "Cannot connect to FastAPI. Start your backend first."
    )
    st.code("uvicorn api:app --reload")
    st.caption(str(e))
