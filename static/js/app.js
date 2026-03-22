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
        return;
    }

    const cleanText = text
        .replace(/[↑↓→]/g, '')
        .replace(/\s+/g, ' ')
        .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'en-US';
    utterance.rate = 0.85;
    utterance.pitch = 1;

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

        // Hide previous feedback
        const feedback = card.querySelector('.feedback-panel');
        if (feedback) feedback.classList.add('hidden');

        let seconds = 0;
        const timerEl = card.querySelector('.recording-time');
        recordingTimers[exerciseIndex] = setInterval(() => {
            seconds++;
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            if (timerEl) timerEl.textContent = `${m}:${s.toString().padStart(2, '0')}`;
        }, 1000);

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

        showLiveTranscript(exerciseIndex, fullTranscript.trim());
    };

    recognition.onend = () => {
        if (fullTranscript.trim()) {
            generateFeedback(exerciseIndex, fullTranscript.trim());
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

// ========== Live Transcript Display ==========

function showLiveTranscript(exerciseIndex, text) {
    const resultDiv = document.getElementById(`result-${exerciseIndex}`);
    if (resultDiv) {
        resultDiv.classList.remove('hidden');
        resultDiv.querySelector('.result-text').textContent = text;
    }
}

// ========== Feedback Engine ==========

function normalizeText(text) {
    return text
        .toLowerCase()
        .replace(/[↑↓→]/g, '')
        .replace(/[^\w\s']/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

function getWords(text) {
    return normalizeText(text).split(' ').filter(w => w.length > 0);
}

function longestCommonSubsequence(a, b) {
    const m = a.length, n = b.length;
    const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (a[i - 1] === b[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
            } else {
                dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
    }

    // Backtrack to find which words matched
    const matched = new Set();
    let i = m, j = n;
    while (i > 0 && j > 0) {
        if (a[i - 1] === b[j - 1]) {
            matched.add(i - 1);
            i--; j--;
        } else if (dp[i - 1][j] > dp[i][j - 1]) {
            i--;
        } else {
            j--;
        }
    }

    return { length: dp[m][n], matchedIndices: matched };
}

function analyzePronunciation(expected, spoken) {
    const expectedWords = getWords(expected);
    const spokenWords = getWords(spoken);

    if (expectedWords.length === 0) {
        return {
            score: spokenWords.length > 0 ? 100 : 0,
            grade: 'great',
            expectedWords: [],
            spokenWords: spokenWords,
            matchedIndices: new Set(),
            missedWords: [],
            extraWords: [],
            feedback: "Great job recording! Keep practicing.",
            tips: []
        };
    }

    const lcs = longestCommonSubsequence(expectedWords, spokenWords);
    const matchCount = lcs.length;
    const score = Math.round((matchCount / expectedWords.length) * 100);

    const missedWords = expectedWords.filter((w, i) => !lcs.matchedIndices.has(i));
    const spokenSet = new Set(spokenWords);
    const extraWords = spokenWords.filter(w => !new Set(expectedWords).has(w));

    // Build word-by-word markup for expected text
    const wordResults = expectedWords.map((word, i) => ({
        word: word,
        matched: lcs.matchedIndices.has(i)
    }));

    let grade, feedback, tips = [];

    if (score >= 90) {
        grade = 'excellent';
        feedback = "Excellent! Your pronunciation is very clear and accurate.";
        tips.push("Try increasing your speaking speed slightly for a more natural flow.");
        if (missedWords.length > 0) {
            tips.push(`Minor: practice the word${missedWords.length > 1 ? 's' : ''} "${missedWords.slice(0, 3).join('", "')}" a few more times.`);
        }
    } else if (score >= 75) {
        grade = 'great';
        feedback = "Great job! Most words came through clearly.";
        if (missedWords.length > 0) {
            tips.push(`Focus on these words: "${missedWords.slice(0, 5).join('", "')}" — listen to the model and repeat.`);
        }
        tips.push("Try speaking a bit more slowly and enunciate each syllable.");
    } else if (score >= 50) {
        grade = 'good';
        feedback = "Good effort! You're getting there — keep practicing.";
        if (missedWords.length > 0) {
            tips.push(`These words need practice: "${missedWords.slice(0, 5).join('", "')}".`);
        }
        tips.push("Listen to the model pronunciation first, then record yourself.");
        tips.push("Try breaking the sentence into smaller chunks and practice each part.");
    } else if (score >= 25) {
        grade = 'developing';
        feedback = "Keep going! Pronunciation takes time and repetition.";
        tips.push("Start by listening to the model 2-3 times before speaking.");
        tips.push("Practice just 3-4 words at a time, then combine them.");
        tips.push("Slow down — accuracy matters more than speed at this stage.");
    } else {
        grade = 'starting';
        feedback = spokenWords.length === 0
            ? "We didn't catch any words. Make sure your microphone is close and speak clearly."
            : "Let's try again! Listen to the model first, then speak slowly and clearly.";
        tips.push("Move closer to your microphone and reduce background noise.");
        tips.push("Press 'Listen' first to hear the correct pronunciation.");
        tips.push("Try saying just the first few words, then gradually add more.");
    }

    return {
        score,
        grade,
        expectedWords,
        spokenWords,
        wordResults,
        matchedIndices: lcs.matchedIndices,
        missedWords,
        extraWords: [...new Set(extraWords)],
        feedback,
        tips
    };
}

function generateFeedback(exerciseIndex, spokenText) {
    const feedbackPanel = document.getElementById(`feedback-${exerciseIndex}`);
    if (!feedbackPanel) return;

    // Get the expected prompt text
    const card = feedbackPanel.closest('.exercise-card') || feedbackPanel.closest('.pb-card');
    const promptEl = card?.querySelector('.exercise-prompt p') || card?.querySelector('.pb-example p');
    let expectedText = card?.dataset?.expectedText || '';

    if (!expectedText && promptEl) {
        expectedText = promptEl.textContent.replace(/^"|"$/g, '').trim();
    }

    const analysis = analyzePronunciation(expectedText, spokenText);

    // Score ring color
    let scoreColor;
    if (analysis.score >= 90) scoreColor = '#10b981';
    else if (analysis.score >= 75) scoreColor = '#3b82f6';
    else if (analysis.score >= 50) scoreColor = '#f59e0b';
    else scoreColor = '#ef4444';

    const circumference = 2 * Math.PI * 36;
    const dashOffset = circumference - (analysis.score / 100) * circumference;

    // Build word highlight HTML
    let wordHighlightHTML = '';
    if (analysis.wordResults) {
        wordHighlightHTML = analysis.wordResults.map(wr =>
            `<span class="fw ${wr.matched ? 'fw-match' : 'fw-miss'}">${wr.word}</span>`
        ).join(' ');
    }

    // Build tips HTML
    const tipsHTML = analysis.tips.map(tip =>
        `<div class="fb-tip">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span>${tip}</span>
        </div>`
    ).join('');

    // Grade label
    const gradeLabels = {
        excellent: 'Excellent',
        great: 'Great',
        good: 'Good Progress',
        developing: 'Keep Practicing',
        starting: 'Try Again'
    };

    feedbackPanel.innerHTML = `
        <div class="fb-header">
            <div class="fb-score-ring">
                <svg viewBox="0 0 80 80">
                    <circle cx="40" cy="40" r="36" fill="none" stroke="#e5e7eb" stroke-width="5"/>
                    <circle cx="40" cy="40" r="36" fill="none" stroke="${scoreColor}" stroke-width="5"
                        stroke-dasharray="${circumference}" stroke-dashoffset="${dashOffset}"
                        stroke-linecap="round" transform="rotate(-90 40 40)"
                        style="transition: stroke-dashoffset 0.8s ease;"/>
                </svg>
                <div class="fb-score-num">
                    <span class="fb-score-val">${analysis.score}</span>
                    <span class="fb-score-pct">%</span>
                </div>
            </div>
            <div class="fb-summary">
                <span class="fb-grade fb-grade-${analysis.grade}">${gradeLabels[analysis.grade]}</span>
                <p class="fb-message">${analysis.feedback}</p>
                <div class="fb-stats">
                    <span class="fb-stat"><strong>${analysis.expectedWords.length - analysis.missedWords.length}</strong> / ${analysis.expectedWords.length} words matched</span>
                </div>
            </div>
        </div>

        ${wordHighlightHTML ? `
        <div class="fb-section">
            <div class="fb-section-title">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Word-by-Word Results
            </div>
            <div class="fb-words">${wordHighlightHTML}</div>
            <div class="fb-legend">
                <span class="fb-legend-item"><span class="fw fw-match">matched</span> = recognized</span>
                <span class="fb-legend-item"><span class="fw fw-miss">missed</span> = not detected</span>
            </div>
        </div>
        ` : ''}

        <div class="fb-section">
            <div class="fb-section-title">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                What We Heard
            </div>
            <p class="fb-transcript">"${spokenText}"</p>
        </div>

        ${analysis.tips.length > 0 ? `
        <div class="fb-section">
            <div class="fb-section-title">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="16" x2="12" y2="12"/>
                    <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                How to Improve
            </div>
            <div class="fb-tips">${tipsHTML}</div>
        </div>
        ` : ''}

        <button class="btn btn-retry" onclick="this.closest('.feedback-panel').classList.add('hidden')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
            </svg>
            Try Again
        </button>
    `;

    feedbackPanel.classList.remove('hidden');
    feedbackPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
