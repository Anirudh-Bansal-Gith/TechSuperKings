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

    try {
        const formData = packData(title, description, files, voice);
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

function packData(title, description, files = [], voice = null) {
    const formData = new FormData();

    let complaint_text = "";

    if (title) {
        complaint_text += `{title: ${title}}`;
    }

    if (description) {
        complaint_text += `{description: ${description}}`;
    }

    formData.append("complaint_text", complaint_text);

    files.forEach((file) => {
        formData.append("files", file);
    });

    if (voice) {
        if (voice.size === 0) {
            throw new Error("Voice recording is empty. Please record again.");
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

    console.log("Uploading files:");

    for (const [key, value] of formData.entries()) {
        if (value instanceof File) {
            console.log(
                key,
                value.name,
                value.size,
                value.type
            );
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

        // Handle irrelevant complaints.
        if (body.saved === false) {
            showResult(body);

            // Do not reset the form.
            return body;
        }

        // Handle successfully saved complaints.
        showResult(body);
        showMessage("Complaint submitted successfully.", "success");

        form.reset();

        // Clear the recorded voice note.
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

    // Irrelevant complaint
    if (body.saved === false) {
        heading.textContent = "Complaint not submitted";
        responseBox.append(heading);

        const message = document.createElement("p");
        message.textContent = body.message || "Your complaint could not be submitted.";

        responseBox.append(message);
        return;
    }

    // Relevant complaint
    heading.textContent = "Complaint submitted";
    responseBox.append(heading);

    const rows = [
        ["Complaint ID", body.complaint_id],
        ["Summary", body.query_description],
        ["Department", body.department],
        ["Priority score", body.importance_score],
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

