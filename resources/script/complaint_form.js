
const CONFIG = {
    api_url: "http://localhost:8000/complaints",
    max_file_MB: 25,
    max_files: 10,
    timeout_ms: 60000,
};

const form = document.getElementById("complaintForm");
const submitBtn = form.querySelector('button[type="submit"]');
const responseBox = document.getElementById("response");

let msg = document.getElementById("formMessage");

if (!msg) {
    msg = document.createElement("p");
    msg.id = "formMessage";
    msg.setAttribute("role", "status");
    msg.setAttribute("aria-live", "polite");
    msg.hidden = true;
    submitBtn.before(msg);
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    showMessage("");
    responseBox.replaceChildren();

    const title = form.complaintTitle.value.trim();
    const description = form.complaintDescription.value.trim();
    const files = Array.from(form.file.files || []);
    const voice = window.voiceNote?.blob || null;

    // Contact information
    const name = form.elements.namedItem("name").value.trim();
    const phone = form.elements.namedItem("phone").value.trim();

    // Location information
    const latitude = form.elements.namedItem("latitude").value;
    const longitude = form.elements.namedItem("longitude").value;
    const address = form.elements.namedItem("address").value.trim();

    console.log("Voice note at submission:", voice);

    if (voice) {
        console.log("Voice size:", voice.size);
        console.log("Voice type:", voice.type);
    }

    const problem = validate(
        { title, description, voice },
        files
    );

    if (problem) {
        showMessage(problem, "error");
        return;
    }

    if (!address && !(latitude && longitude)) {
        showMessage(
            "Please provide an address or use your current location.",
            "error"
        );
        return;
    }

    try {
        const formData = packData(
            title,
            description,
            files,
            voice,
            name,
            phone,
            latitude,
            longitude,
            address
        );

        await submit_complaint(formData);

    } catch (err) {
        showMessage(err.message, "error");
    }
});


function showMessage(text, type = "info") {
    msg.textContent = text;
    msg.hidden = !text;

    msg.style.color =
        type === "error" ? "var(--danger, #dc2626)" :
        type === "success" ? "#15803d" : "inherit";

    msg.style.fontWeight = "500";
}


function setLoading(on) {
    submitBtn.disabled = on;
    submitBtn.textContent = on
        ? "Submitting…"
        : "Submit Complaint";
}


function packData(
    title,
    description,
    files = [],
    voice = null,
    name,
    phone,
    latitude,
    longitude,
    address
) {
    const formData = new FormData();

    // These names match the UserInfo Pydantic schema.
    const userDetails = {
        name: name,
        phone: phone || null,
        address: address || (
            latitude && longitude
                ? `${latitude}, ${longitude}`
                : null
        )
    };

    formData.append(
        "user_details",
        JSON.stringify(userDetails)
    );

    // Complaint text is sent separately.
    let complaint_text = "";

    if (title) {
        complaint_text += `{title: ${title}}`;
    }

    if (description) {
        complaint_text += `{description: ${description}}`;
    }

    formData.append("complaint_text", complaint_text);

    // Attach uploaded files.
    files.forEach((file) => {
        formData.append("files", file);
    });

    // Attach voice recording.
    if (voice) {
        if (voice.size === 0) {
            throw new Error(
                "Voice recording is empty. Please record again."
            );
        }

        const extension = voice.type.includes("mp4")
            ? "mp4"
            : "webm";

        formData.append(
            "files",
            voice,
            `voice-note.${extension}`
        );
    }

    console.log("Uploading form data:");

    for (const [key, value] of formData.entries()) {
        if (value instanceof File) {
            console.log(
                key,
                value.name,
                value.size,
                value.type
            );
        } else {
            console.log(key, value);
        }
    }

    return formData;
}


async function submit_complaint(formData) {
    const controller = new AbortController();

    const timer = setTimeout(
        () => controller.abort(),
        CONFIG.timeout_ms
    );

    setLoading(true);

    try {
        const res = await fetch(CONFIG.api_url, {
            method: "POST",
            body: formData,
            signal: controller.signal,
        });

        const body = await res.json().catch(() => ({}));

        if (!res.ok) {
            const detail = Array.isArray(body.detail)
                ? body.detail.map((d) => d.msg).join(", ")
                : body.detail;

            throw new Error(
                detail || `Request failed (${res.status}). Please try again.`
            );
        }

        showResult(body);

        showMessage(
            "Complaint submitted successfully.",
            "success"
        );

        form.reset();

        // Clear recorded voice note.
        document.getElementById("deleteBtn")?.click();

        return body;

    } catch (err) {
        const errorText =
            err.name === "AbortError"
                ? "The request timed out. Please try again."
                : err instanceof TypeError
                    ? "Network error. Check your connection and try again."
                    : err.message;

        showMessage(errorText, "error");

    } finally {
        clearTimeout(timer);
        setLoading(false);
    }
}


function showResult({
    query_description,
    department,
    importance_score
}) {
    responseBox.replaceChildren();

    const heading = document.createElement("h3");
    heading.textContent = "Complaint submitted";

    responseBox.append(heading);

    const rows = [
        ["Summary", query_description],
        ["Department", department],
        ["Priority score", importance_score],
    ];

    for (const [label, value] of rows) {
        const p = document.createElement("p");
        const strong = document.createElement("strong");

        strong.textContent = `${label}: `;

        p.append(
            strong,
            String(value ?? "")
        );

        responseBox.append(p);
    }
}


function validate(data, files) {
    if (
        !data.title &&
        !data.description &&
        !data.voice &&
        files.length === 0
    ) {
        return "Please add a title, description, voice note, or file.";
    }

    if (files.length + (data.voice ? 1 : 0) > CONFIG.max_files) {
        return `Maximum ${CONFIG.max_files} files can be uploaded.`;
    }

    for (const file of files) {
        if (file.size > CONFIG.max_file_MB * 1024 * 1024) {
            return `"${file.name}" is larger than ${CONFIG.max_file_MB} MB.`;
        }
    }

    if (
        data.voice &&
        data.voice.size > CONFIG.max_file_MB * 1024 * 1024
    ) {
        return `Voice recording is larger than ${CONFIG.max_file_MB} MB.`;
    }

    return null;
}


// Location handling
(function () {
    const locationBtn = document.getElementById("getLocation");
    const locationStatus = document.getElementById("status");
    const latInput = document.getElementById("latitude");
    const lngInput = document.getElementById("longitude");
    const addressInput = document.getElementById("address");
    const locationError = document.getElementById("error");

    function setStatus(message, isError = false) {
        locationStatus.textContent = message;
        locationStatus.style.color = isError ? "red" : "green";
    }

    function clearCoordinates() {
        latInput.value = "";
        lngInput.value = "";
    }

    function handleLocationError(err) {
        clearCoordinates();

        switch (err.code) {
            case err.PERMISSION_DENIED:
                setStatus(
                    "Location permission denied. Please type your address below.",
                    true
                );
                break;

            case err.POSITION_UNAVAILABLE:
                setStatus(
                    "Location unavailable. Please type your address below.",
                    true
                );
                break;

            case err.TIMEOUT:
                setStatus(
                    "Location request timed out. Please try again or type your address.",
                    true
                );
                break;

            default:
                setStatus(
                    "Could not get location. Please type your address below.",
                    true
                );
        }

        addressInput.focus();
    }

    function getLocation() {
        if (!("geolocation" in navigator)) {
            setStatus(
                "Your browser does not support location. Please type your address.",
                true
            );
            addressInput.focus();
            return;
        }

        locationError.textContent = "";
        locationBtn.disabled = true;
        setStatus("Getting your location...");
        locationStatus.style.color = "";

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const {
                    latitude,
                    longitude,
                    accuracy
                } = position.coords;

                latInput.value = latitude.toFixed(6);
                lngInput.value = longitude.toFixed(6);

                setStatus(
                    `Location captured ✔ (accuracy: about ${Math.round(accuracy)} m)`
                );

                locationBtn.disabled = false;
                locationBtn.textContent = "📍 Update my location";
            },

            (err) => {
                handleLocationError(err);
                locationBtn.disabled = false;
            },

            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    locationBtn.addEventListener("click", getLocation);
})();

