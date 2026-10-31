
(() => {
  const MAX_SECONDS = 300; // auto-stop at 5 minutes
  const $ = (id) => document.getElementById(id);
  const el = {
    start: $('startBtn'), pause: $('pauseBtn'), stop: $('stopBtn'), del: $('deleteBtn'),
    status: $('statusText'), timer: $('timer'), dot: $('pulseDot'),
    audio: $('audioPlayback'), error: $('errorText'),
  };

  let recorder = null, stream = null, chunks = [], tick = null, seconds = 0, blobUrl = null;
  window.voiceNote = { blob: null };

  const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  const setTimer = () => { el.timer.textContent = fmt(seconds); el.timer.dateTime = `PT${seconds}S`; };
  const setState = (text, dotClass = '') => { el.status.textContent = text; el.dot.className = `pulse-dot ${dotClass}`.trim(); };
  const showError = (msg) => { el.error.textContent = msg; el.error.hidden = !msg; };

  const startTimer = () => { tick = setInterval(() => { seconds++; setTimer(); if (seconds >= MAX_SECONDS) stop(); }, 1000); };
  const stopTimer = () => { clearInterval(tick); tick = null; };
  const releaseMic = () => { stream?.getTracks().forEach((t) => t.stop()); stream = null; };

  async function start() {
    showError('');
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      return showError('Voice recording is not supported here. Use https or localhost in a modern browser.');
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      return showError(err.name === 'NotAllowedError'
        ? 'Microphone access was blocked. Allow it in your browser settings and try again.'
        : 'No microphone found.');
    }

    chunks = []; seconds = 0; setTimer();
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
    recorder.onstop = onStopped;
    recorder.start();

    el.start.disabled = true; el.stop.disabled = false;
    el.pause.hidden = false; el.pause.disabled = false; el.pause.textContent = 'Pause';
    el.del.hidden = true; el.audio.hidden = true;
    setState('Recording…', 'recording');
    startTimer();
  }

  function togglePause() {
    if (recorder.state === 'recording') {
      recorder.pause(); stopTimer(); el.pause.textContent = 'Resume'; setState('Paused', 'paused');
    } else if (recorder.state === 'paused') {
      recorder.resume(); startTimer(); el.pause.textContent = 'Pause'; setState('Recording…', 'recording');
    }
  }

  function stop() {
    if (recorder && recorder.state !== 'inactive') recorder.stop();
  }

  function onStopped() {
    stopTimer(); releaseMic();
    const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
    window.voiceNote.blob = blob;
    if (blobUrl) URL.revokeObjectURL(blobUrl);
    blobUrl = URL.createObjectURL(blob);
    el.audio.src = blobUrl; el.audio.hidden = false;

    el.stop.disabled = true; el.pause.hidden = true; el.del.hidden = false; el.start.hidden = true;
    setState(`Recorded (${fmt(seconds)})`);
    el.del.focus();
  }

  function retake() {
    if (blobUrl) URL.revokeObjectURL(blobUrl);
    blobUrl = null; window.voiceNote.blob = null; chunks = []; seconds = 0; setTimer();
    el.audio.removeAttribute('src'); el.audio.hidden = true;
    el.del.hidden = true; el.start.hidden = false; el.start.disabled = false;
    setState('Ready to record');
    el.start.focus();
  }

  el.start.addEventListener('click', start);
  el.pause.addEventListener('click', togglePause);
  el.stop.addEventListener('click', stop);
  el.del.addEventListener('click', retake);
  window.addEventListener('pagehide', () => { stop(); releaseMic(); });
})();