
import os
import tempfile

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut

from graph import graph
from database import SessionLocal
from persistence import save_complaint


geolocator = Nominatim(user_agent="complaint_management_system")


def get_location(latitude, longitude):
    if latitude is None or longitude is None:
        print("Coordinates missing")
        return None

    try:
        result = geolocator.reverse(
            (latitude, longitude),
            exactly_one=True,
            timeout=10
        )

        if result:
            print("Geocoded address:", result.address)
            return result.address

        print("No address found for these coordinates")
        return None

    except Exception as e:
        print("Reverse geocoding failed:", repr(e))
        return None


def process_complaint(
    complaint_text,
    uploaded_files=None,
    user_details=None,
):
    uploaded_files = uploaded_files or []
    user_details = user_details or {}

    attachments = []
    temp_paths = []

    try:
        # Extract coordinates from the address field
        address = user_details.get("address")

        latitude = None
        longitude = None

        if address:
            try:
                latitude, longitude = map(
                    float,
                    address.split(",")
                )
            except (ValueError, AttributeError):
                print("Invalid coordinate format:", address)

        # Preserve coordinates and generate human-readable address
        user_details["latitude"] = latitude
        user_details["longitude"] = longitude

        user_details["location"] = get_location(
            latitude,
            longitude
        )

        for file in uploaded_files:
            if file is None:
                continue

            mime_type = file.content_type

            if not mime_type:
                raise ValueError(
                    f"MIME type missing for file: {file.filename}"
                )

            file.file.seek(0)

            # Videos: store on disk instead of loading into RAM
            if mime_type.startswith("video/"):
                suffix = os.path.splitext(file.filename or "")[1]

                fd, temp_path = tempfile.mkstemp(suffix=suffix)
                os.close(fd)

                temp_paths.append(temp_path)

                with open(temp_path, "wb") as temp_file:
                    while True:
                        chunk = file.file.read(1024 * 1024)

                        if not chunk:
                            break

                        temp_file.write(chunk)

                if os.path.getsize(temp_path) == 0:
                    raise ValueError(
                        f"Empty file uploaded: {file.filename}"
                    )

                attachments.append({
                    "path": temp_path,
                    "mime_type": mime_type,
                    "filename": file.filename,
                })

            # Images and audio: continue using bytes
            else:
                file_data = file.file.read()

                if not file_data:
                    raise ValueError(
                        f"Empty file uploaded: {file.filename}"
                    )

                attachments.append({
                    "data": file_data,
                    "mime_type": mime_type,
                    "filename": file.filename,
                })

            # Keep original upload ready for B2 persistence
            file.file.seek(0)

        result = graph.invoke({
            "complaint_text": complaint_text or "",
            "attachments": attachments,
        })

        llm_output = result["structured_output"]

        if llm_output.importance_score > 0:
            # Ensure original files are ready for B2 upload
            for file in uploaded_files:
                if file is not None:
                    file.file.seek(0)

            db = SessionLocal()

            try:
                return save_complaint(
                    db,
                    llm_output,
                    [
                        file
                        for file in uploaded_files
                        if file is not None
                    ],
                    user_details,
                )
            finally:
                db.close()

        return {
            "message": "Your complaint appears to be invalid or irrelevant.",
            "saved": False,
        }

    finally:
        # Delete temporary video files regardless of success or failure
        for path in temp_paths:
            try:
                os.remove(path)
            except OSError:
                pass
