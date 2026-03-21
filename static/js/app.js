// ==========================================
// VoiceUp — Speech Practice Engine
// Uses Web Speech API for TTS & recognition
// ==========================================

let mediaRecorder = null;
let audioChunks = [];
let recordings = {};
let recordingTimers = {};
let recognition = null;

// ========== Text-to-Speech ==========

function speakText(button, text) {
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        button.classList.remove('speaking');
        button.querySelector('span, .btn-text')?.remove();
        return;
    }

    // Clean up the text: remove arrows, special chars
    const cleanText = text
        .replace(/[↑↓→]/g, '')
        .replace(/\s+/g, ' ')
        .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'en-US';
    utterance.rate = 0.85;
    utterance.pitch = 1;

    // Prefer a natural US English voice
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v =>
        v.lang === 'en-US' && (v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('Google'))
    ) || voices.find(v => v.lang === 'en-US');
    if (preferred) utterance.voice = preferred;

    button.classList.add('speaking');
    const originalHTML = button.innerHTML;

    utterance.onend = () => {
        button.classList.remove('speaking');
        button.innerHTML = originalHTML;
    };

    utterance.onerror = () => {
        button.classList.remove('speaking');
        button.innerHTML = originalHTML;
    };

    window.speechSynthesis.speak(utterance);
}

// Load voices (they load async in some browsers)
if (window.speechSynthesis) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}

// ========== Audio Recording ==========

async function toggleRecording(button, exerciseIndex) {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        stopRecording(button, exerciseIndex);
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            recordings[exerciseIndex] = URL.createObjectURL(audioBlob);

            stream.getTracks().forEach(t => t.stop());

            const card = button.closest('.exercise-card') || button.closest('.pb-card');
            const playBtn = card.querySelector('.btn-play-recording');
            if (playBtn) playBtn.classList.remove('hidden');
        };

        mediaRecorder.start();

        button.classList.add('recording');
        const label = button.querySelector('.record-label');
        label._original = label._original || label.textContent;
        label.textContent = 'Stop';

        const card = button.closest('.exercise-card') || button.closest('.pb-card');
        const visualizer = document.getElementById(`visualizer-${exerciseIndex}`) || card.querySelector('.visualizer');
        if (visualizer) visualizer.classList.remove('hidden');

        // Start timer
        let seconds = 0;
        const timerEl = card.querySelector('.recording-time');
        recordingTimers[exerciseIndex] = setInterval(() => {
            seconds++;
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            if (timerEl) timerEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
        }, 1000);

        // Start speech recognition alongside recording
        startRecognition(exerciseIndex);

    } catch (err) {
        alert('Microphone access is required for recording exercises. Please allow microphone access and try again.');
        console.error('Microphone error:', err);
    }
}

function stopRecording(button, exerciseIndex) {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }

    button.classList.remove('recording');
    const label = button.querySelector('.record-label');
    label.textContent = label._original || 'Record';

    const card = button.closest('.exercise-card') || button.closest('.pb-card');
    const visualizer = document.getElementById(`visualizer-${exerciseIndex}`) || card.querySelector('.visualizer');
    if (visualizer) visualizer.classList.add('hidden');

    if (recordingTimers[exerciseIndex]) {
        clearInterval(recordingTimers[exerciseIndex]);
        delete recordingTimers[exerciseIndex];
    }

    stopRecognition();
}

// ========== Play Recording ==========

function playRecording(exerciseIndex) {
    const url = recordings[exerciseIndex];
    if (!url) return;

    const audio = new Audio(url);
    audio.play();
}

// ========== Speech Recognition ==========

function startRecognition(exerciseIndex) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = true;
    recognition.maxAlternatives = 1;

    let fullTranscript = '';

    recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                fullTranscript += event.results[i][0].transcript + ' ';
            }
        }

        const resultDiv = document.getElementById(`result-${exerciseIndex}`);
        if (resultDiv) {
            resultDiv.classList.remove('hidden');
            resultDiv.querySelector('.result-text').textContent = fullTranscript.trim();
        }
    };

    recognition.onerror = (event) => {
        if (event.error !== 'no-speech' && event.error !== 'aborted') {
            console.log('Speech recognition note:', event.error);
        }
    };

    try {
        recognition.start();
    } catch (e) {
        // Recognition might already be running
    }
}

function stopRecognition() {
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) {
            // Ignore
        }
        recognition = null;
    }
}

// ========== Progress Management ==========

function toggleComplete(day, complete) {
    const url = complete ? '/api/progress/complete' : '/api/progress/uncomplete';
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day: day })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    })
    .catch(err => console.error('Progress update failed:', err));
}

// ========== User Dropdown ==========

document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('user-dropdown');
    if (!dropdown) return;
    const avatar = e.target.closest('.user-avatar');
    if (!avatar && !e.target.closest('.user-dropdown')) {
        dropdown.classList.remove('show');
    }
});
