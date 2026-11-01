
import requests
import streamlit as st

API_URL = "http://localhost:8000/track"

st.set_page_config(
    page_title="Track Complaint",
    page_icon="📍",
    layout="centered",
)

st.title("📍 Track Your Complaint")
st.write("Check the latest status of your submitted complaint.")

with st.form("tracking_form"):
    complaint_id = st.number_input(
        "Complaint ID",
        min_value=1,
        step=1,
    )

    phone_number = st.text_input(
        "Registered phone number",
        placeholder="Enter the phone number used during submission",
    )

    submitted = st.form_submit_button(
        "Track Complaint",
        use_container_width=True,
    )

if submitted:
    if not phone_number.strip():
        st.warning("Please enter your registered phone number.")

    else:
        try:
            response = requests.get(
                f"{API_URL}/{int(complaint_id)}",
                params={"phone_number": phone_number.strip()},
                timeout=20,
            )

            if response.status_code == 404:
                st.error(
                    "Complaint not found. Check your ID and phone number."
                )
            else:
                response.raise_for_status()
                data = response.json()

                st.success("Complaint found!")

                st.subheader(
                    f"Complaint #{data['complaint_id']}"
                )

                status = data["status"]

                if status == "Resolved":
                    st.success(f"Status: {status}")
                elif status == "Rejected":
                    st.error(f"Status: {status}")
                elif status == "In Progress":
                    st.info(f"Status: {status}")
                else:
                    st.warning(f"Status: {status}")

                st.write("**Department:**", data["department"])
                st.write("**Description:**", data["description"])
                st.write(
                    "**Location:**",
                    data.get("location") or "Not available",
                )

        except requests.RequestException as e:
            st.error(f"Unable to contact the server: {e}")
