const CONFIG = {
    api_url: "http://localhost:8000/complaints", //temporary
    max_file_MB: 25,
    max_files: 10,
    timeout_ms: 60000,
}

const form = document.getElementById("complaintForm")
const submitBtn = form.querySelector('button[type="submit"]')
const responseBox = document.getElementById("response")


let msg = document.getElementById("formMessage")
if (!msg) {
    msg = document.createElement("p")
    msg.id = "formMessage"
    msg.setAttribute("role", "status")
    msg.setAttribute("aria-live", "polite")
    msg.hidden = true
    submitBtn.before(msg)
}

form.addEventListener("submit", async (e) => {

    e.preventDefault()
    showMessage("")
    responseBox.replaceChildren()

    const title = form.complaintTitle.value.trim()
    const description = form.complaintDescription.value.trim()
    const files = Array.from(form.file.files)
    const voice = window.voiceNote?.blob || null

    const problem = validate({ title, description, voice }, files)

    if (problem) {
        showMessage(problem, "error")
        return
    }

    await submit_complaint(packData(title, description, files, voice))
})

function showMessage(text, type = "info") {
    msg.textContent = text
    msg.hidden = !text
    msg.style.color =
        type === "error" ? "var(--danger, #dc2626)" :
        type === "success" ? "#15803d" : "inherit"
    msg.style.fontWeight = "500"
}

function setLoading(on) {
    submitBtn.disabled = on
    submitBtn.textContent = on ? "Submitting…" : "Submit Complaint"
}

function packData(title, description, files = [], voice = null) {

    const formData = new FormData()
    let complaint_text = ""

    if (title) complaint_text += `{title: ${title}}`
    if (description) complaint_text += `{description: ${description}}`

    formData.append("complaint_text", complaint_text)

    files.forEach((file) => formData.append("files", file))

    if (voice) formData.append("files", voice, "voice-note.webm")

    return formData
}

async function submit_complaint(formData) {

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), CONFIG.timeout_ms)
    setLoading(true)

    try {
        const res = await fetch(CONFIG.api_url, {
            method: "POST",
            body: formData, // no Content-Type header: the browser adds the boundary
            signal: controller.signal,
        })

        const body = await res.json().catch(() => ({}))

        if (!res.ok) {
            // FastAPI errors: { detail: "..." } or { detail: [ { msg: "..." } ] }
            const detail = Array.isArray(body.detail)
                ? body.detail.map((d) => d.msg).join(", ")
                : body.detail
            throw new Error(detail || `Request failed (${res.status}). Please try again.`)
        }

        showResult(body)
        form.reset()
        document.getElementById("deleteBtn")?.click() // clears the recorded voice note

        return body

    } catch (err) {
        const text =
            err.name === "AbortError" ? "The request timed out. Please try again." :
            err instanceof TypeError ? "Network error. Check your connection and try again." :
            err.message
        showMessage(text, "error")

    } finally {
        clearTimeout(timer)
        setLoading(false)
    }
}

// backend returns: { query_description, department, importance_score }
function showResult({ query_description, department, importance_score }) {
    responseBox.replaceChildren() // clear any previous result

    const heading = document.createElement("h3")
    heading.textContent = "Complaint submitted"
    responseBox.append(heading)

    const rows = [
        ["Summary", query_description],
        ["Department", department],
        ["Priority score", importance_score],
    ]

    // textContent/append (not innerHTML) so backend text is never parsed as HTML
    for (const [label, value] of rows) {
        const p = document.createElement("p")
        const strong = document.createElement("strong")
        strong.textContent = `${label}: `
        p.append(strong, String(value))
        responseBox.append(p)
    }
}

function validate(data, files) {

    if (!data.title && !data.description && !data.voice && files.length === 0) {
        return "Please add a title, description, voice note, or file."
    }

    if (files.length > CONFIG.max_files) {
        return `Maximum ${CONFIG.max_files} files can be uploaded.`
    }

    for (const file of files) {
        if (file.size > CONFIG.max_file_MB * 1024 * 1024) {
            return `"${file.name}" is larger than ${CONFIG.max_file_MB} MB.`
        }
    }

    return null
}