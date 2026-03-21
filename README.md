# VoiceUp — Communication Skills Coaching App

A 21-day voice coaching web app designed for non-native English speakers to improve their American English pronunciation, fluency, and professional communication skills.

## Features

- **21 structured daily lessons** covering pronunciation, rhythm, fluency, professional communication, and public speaking
- **Text-to-Speech** — listen to native pronunciation for every exercise
- **Voice Recording** — record yourself and play back to compare
- **Speech Recognition** — see what the browser hears when you speak (pronunciation feedback)
- **Progress Tracking** — mark lessons complete and track your journey
- **Certificate** — earn a completion certificate after finishing all 21 days
- **Mobile-friendly** — responsive design works on any device

## Setup

1. **Install Python 3.8+** if you don't already have it

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open your browser** and go to: [http://localhost:5000](http://localhost:5000)

## Curriculum

| Day | Topic | Category |
|-----|-------|----------|
| 1 | Self-Assessment & American English Basics | Foundation |
| 2 | Master the Power of First Impressions | Social |
| 3 | Vowel Sounds That Americans Actually Use | Pronunciation |
| 4 | Consonant Clarity & The American R and L | Pronunciation |
| 5 | Word Stress — The Secret Rhythm of English | Rhythm |
| 6 | Sentence Stress & Natural Flow | Rhythm |
| 7 | Connected Speech — Sound Like a Native | Fluency |
| 8 | Intonation — The Music of Your Message | Fluency |
| 9 | Speak Without Fear — Confidence Building | Mindset |
| 10 | Professional Communication at Work | Professional |
| 11 | Small Talk & Social Conversations | Social |
| 12 | Say 'No' & Set Boundaries Politely | Professional |
| 13 | Crafting a Powerful Speech | Advanced |
| 14 | Phone & Video Call Mastery | Professional |
| 15 | Handle Conflicts Like a Pro | Advanced |
| 16 | Persuade & Influence with Words | Advanced |
| 17 | Storytelling That Captivates | Advanced |
| 18 | Active Listening & Powerful Responses | Social |
| 19 | Interview & High-Stakes Speaking | Professional |
| 20 | Presentation Skills & Public Speaking | Advanced |
| 21 | Final Assessment & Your Communication Certificate | Milestone |

## Browser Requirements

For the best experience, use **Google Chrome** or **Microsoft Edge** (Chromium-based) as they have the best support for:
- Web Speech API (text-to-speech and speech recognition)
- MediaRecorder API (voice recording)

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript (no frameworks — lightweight and fast)
- **Speech:** Web Speech API (browser-native, no API keys needed)
- **Storage:** JSON file for progress tracking
