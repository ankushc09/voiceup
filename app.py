from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
import json
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "voiceup-local-dev-key-change-in-prod")

DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(__file__))
USERS_FILE = os.path.join(DATA_DIR, "users.json")

CURRICULUM = [
    {
        "day": 1,
        "title": "Self-Assessment & American English Basics",
        "duration": "5 min",
        "category": "foundation",
        "description": "Record your baseline voice, learn the key differences between American English and other accents, and identify your personal improvement areas.",
        "objectives": [
            "Record a 30-second self-introduction",
            "Identify your accent patterns",
            "Understand the American English sound system",
            "Set personal goals for the course",
        ],
        "exercises": [
            {
                "type": "record",
                "prompt": "Hi, my name is ___ and I'm from ___. I work as a ___ and I'm excited to improve my English communication skills.",
                "tip": "Speak naturally — don't try to change anything yet. This is your baseline!",
            },
            {
                "type": "repeat",
                "prompt": "The weather today is absolutely beautiful.",
                "focus": "Notice how you naturally say each word",
            },
            {
                "type": "repeat",
                "prompt": "I'd like to schedule a meeting for next Thursday.",
                "focus": "Pay attention to the 'th' sound and word connections",
            },
        ],
        "tips": [
            "American English uses a lot of reduced sounds — 'gonna' instead of 'going to'",
            "The 'r' sound is pronounced more strongly than in British English",
            "Intonation rises and falls more dramatically in American English",
        ],
    },
    {
        "day": 2,
        "title": "Master the Power of First Impressions",
        "duration": "5 min",
        "category": "social",
        "description": "Learn how to make a strong first impression with clear pronunciation, confident tone, and engaging body language cues in your voice.",
        "objectives": [
            "Perfect your self-introduction",
            "Use confident intonation patterns",
            "Master the firm handshake of speech — the greeting",
            "Practice elevator pitches",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "Hi, I'm really glad to meet you! I've heard great things about your team.",
                "focus": "Emphasize 'really glad' and 'great things' with a rising tone",
            },
            {
                "type": "repeat",
                "prompt": "My name is Alex, and I specialize in data analytics. How about you?",
                "focus": "Keep your voice warm and end with genuine curiosity",
            },
            {
                "type": "record",
                "prompt": "Practice your 30-second elevator pitch — who are you, what do you do, and what makes you passionate about it?",
                "tip": "Smile while speaking — it changes your voice tone!",
            },
        ],
        "tips": [
            "People form opinions in the first 7 seconds — make them count",
            "A warm, steady voice signals confidence",
            "Mirror the energy level of the person you're meeting",
        ],
    },
    {
        "day": 3,
        "title": "Vowel Sounds That Americans Actually Use",
        "duration": "5 min",
        "category": "pronunciation",
        "description": "Master the most commonly confused American English vowel sounds with targeted practice and real-world examples.",
        "objectives": [
            "Distinguish between short and long vowels",
            "Master the 'schwa' — the most common American sound",
            "Practice minimal pairs (ship/sheep, bit/beat)",
            "Build muscle memory for correct mouth positions",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "The sheep on the ship seem to slip and sleep.",
                "focus": "Distinguish between 'ee' (sheep/sleep) and 'ih' (ship/slip)",
            },
            {
                "type": "repeat",
                "prompt": "I can't believe the cat sat on my hat in the car.",
                "focus": "Practice the open 'æ' in cat/sat/hat vs the 'ar' in car",
            },
            {
                "type": "repeat",
                "prompt": "About a dozen people arrived at the apartment around eleven.",
                "focus": "The 'uh' schwa sound: about, a, apartment, around, eleven",
            },
        ],
        "tips": [
            "The schwa (ə) is the most common sound in American English — it sounds like 'uh'",
            "Many vowel errors come from applying your native language's vowel system",
            "Record yourself and compare with native speakers — use YouTube for reference",
        ],
    },
    {
        "day": 4,
        "title": "Consonant Clarity & The American R and L",
        "duration": "5 min",
        "category": "pronunciation",
        "description": "Tackle the trickiest consonant sounds for non-native speakers, especially the American R, L, TH, and V/W distinctions.",
        "objectives": [
            "Master the American 'R' sound",
            "Distinguish R and L clearly",
            "Perfect the 'TH' sounds (voiced and voiceless)",
            "Practice V vs W and B vs V distinctions",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "The red robin ran right around the river road.",
                "focus": "Curl your tongue slightly back for the American R — don't roll it",
            },
            {
                "type": "repeat",
                "prompt": "I really like the light blue color of the lake at night.",
                "focus": "R = tongue curls back, L = tongue touches behind upper teeth",
            },
            {
                "type": "repeat",
                "prompt": "I think that this thing is worth three thousand dollars though.",
                "focus": "Place tongue between teeth for 'th' — voice it for 'this/that', whisper for 'think/three'",
            },
        ],
        "tips": [
            "For the American R, imagine you're gently growling — your tongue never touches the roof",
            "Practice TH by exaggerating — stick your tongue out between your teeth",
            "V requires biting your lower lip; W requires rounding your lips like a kiss",
        ],
    },
    {
        "day": 5,
        "title": "Word Stress — The Secret Rhythm of English",
        "duration": "5 min",
        "category": "rhythm",
        "description": "Learn why word stress is the #1 key to being understood in American English. Wrong stress = confused listener, even if every sound is perfect.",
        "objectives": [
            "Understand stressed vs unstressed syllables",
            "Learn common word stress patterns",
            "Practice stress shifts that change meaning",
            "Apply stress patterns to multi-syllable words",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "I need to PRESENT the PRESENT to the PRESident.",
                "focus": "pre-SENT (verb) vs PRES-ent (noun) — stress changes meaning!",
            },
            {
                "type": "repeat",
                "prompt": "The photograph was taken by a professional photographer for a photography magazine.",
                "focus": "PHO-to-graph, pho-TOG-ra-pher, pho-TOG-ra-phy — stress moves!",
            },
            {
                "type": "repeat",
                "prompt": "Can you reCORD this RECORD? I need to exPORT this EXport.",
                "focus": "Verbs stress the second syllable, nouns stress the first",
            },
        ],
        "tips": [
            "Stressed syllables are LOUDER, LONGER, and HIGHER in pitch",
            "Wrong word stress confuses listeners more than wrong sounds",
            "When in doubt, most 2-syllable nouns stress the FIRST syllable",
        ],
    },
    {
        "day": 6,
        "title": "Sentence Stress & Natural Flow",
        "duration": "5 min",
        "category": "rhythm",
        "description": "Master the music of American English sentences. Learn which words to emphasize and which to reduce for natural-sounding speech.",
        "objectives": [
            "Identify content words vs function words",
            "Practice reducing unstressed words",
            "Use emphasis to convey meaning",
            "Sound more natural and less robotic",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "I WANT to GO to the STORE to BUY some BREAD.",
                "focus": "Stress content words (want, go, store, buy, bread) — reduce 'to, the, some'",
            },
            {
                "type": "repeat",
                "prompt": "She SAID she was GOING to CALL him BACK toMORrow.",
                "focus": "Function words (she, was, to, him) become quick and quiet",
            },
            {
                "type": "repeat",
                "prompt": "I didn't say HE stole the money. I didn't SAY he stole the money. I didn't say he STOLE the money.",
                "focus": "Moving emphasis completely changes the meaning!",
            },
        ],
        "tips": [
            "American English is stress-timed — stressed syllables come at regular intervals",
            "Reducing function words is what makes you sound fluent, not fast speaking",
            "Listen to podcasts and notice which words speakers emphasize",
        ],
    },
    {
        "day": 7,
        "title": "Connected Speech — Sound Like a Native",
        "duration": "5 min",
        "category": "fluency",
        "description": "Learn how Americans blend, link, and reduce words in natural conversation. This is the biggest gap between textbook English and real speech.",
        "objectives": [
            "Master linking between words",
            "Learn common reductions (gonna, wanna, gotta)",
            "Practice elision (dropping sounds)",
            "Understand assimilation (sounds changing near each other)",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "What are you going to do? → Whaddaya gonna do?",
                "focus": "Practice both forms — formal and natural connected speech",
            },
            {
                "type": "repeat",
                "prompt": "I have got to get out of here → I gotta get outta here",
                "focus": "Words blend together: 'got to' → 'gotta', 'out of' → 'outta'",
            },
            {
                "type": "repeat",
                "prompt": "Could you hand me that? I want to take a look at it.",
                "focus": "Link: 'hand_me', 'look_at_it' — words flow into each other",
            },
        ],
        "tips": [
            "Native speakers rarely pronounce every word fully — and neither should you",
            "Linking is when the end of one word flows into the start of the next",
            "Practice with TV shows — pause and repeat casual dialogue",
        ],
    },
    {
        "day": 8,
        "title": "Intonation — The Music of Your Message",
        "duration": "5 min",
        "category": "fluency",
        "description": "Master the rise and fall patterns of American English intonation to convey the right emotion, attitude, and meaning.",
        "objectives": [
            "Learn rising vs falling intonation patterns",
            "Use intonation to show interest and engagement",
            "Practice question intonation patterns",
            "Express emotions through pitch changes",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "You got the job! ↑ You got the job? ↑↑ You got the job. ↓",
                "focus": "Same words, different intonation = different meaning",
            },
            {
                "type": "repeat",
                "prompt": "I love Italian food, ↑ especially pasta, ↑ pizza, ↑ and tiramisu. ↓",
                "focus": "List intonation: rise on each item, fall on the last one",
            },
            {
                "type": "repeat",
                "prompt": "Really? That's amazing! I had no idea you could do that!",
                "focus": "Express genuine surprise — let your pitch jump up on 'Really' and 'amazing'",
            },
        ],
        "tips": [
            "Flat intonation can sound bored or unfriendly in American English",
            "Yes/no questions rise at the end; WH-questions fall",
            "Americans use more pitch variation than many other languages",
        ],
    },
    {
        "day": 9,
        "title": "Speak Without Fear — Confidence Building",
        "duration": "5 min",
        "category": "mindset",
        "description": "Overcome speaking anxiety and build unshakeable confidence. Learn techniques used by professional speakers to manage nervousness.",
        "objectives": [
            "Identify and reframe speaking fears",
            "Practice power posing and breathing techniques",
            "Use the 'fake it till you make it' voice",
            "Build a confidence anchor phrase",
        ],
        "exercises": [
            {
                "type": "record",
                "prompt": "Stand tall, take a deep breath, and say with full confidence: 'I have something valuable to share, and people want to hear what I have to say.'",
                "tip": "Record this 3 times — each time louder and more confident",
            },
            {
                "type": "repeat",
                "prompt": "I'm not perfect, and that's perfectly fine. My accent is part of my story, and my ideas are what matter.",
                "focus": "Speak slowly and deliberately — confidence is about pace, not speed",
            },
            {
                "type": "repeat",
                "prompt": "Let me share something interesting with you. I think you'll find this really valuable.",
                "focus": "Use a lower, steady pitch — this signals authority and confidence",
            },
        ],
        "tips": [
            "Nervousness and excitement feel the same — choose to call it excitement",
            "Pause before speaking — it signals confidence, not uncertainty",
            "Your accent is an asset — it shows you speak multiple languages",
        ],
    },
    {
        "day": 10,
        "title": "Professional Communication at Work",
        "duration": "5 min",
        "category": "professional",
        "description": "Master the phrases, tone, and communication style used in American workplaces. From meetings to emails to water-cooler chat.",
        "objectives": [
            "Learn key professional phrases",
            "Practice meeting participation language",
            "Master polite disagreement and suggestions",
            "Build your professional vocabulary",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "I'd like to piggyback on what Sarah said. I think we should also consider the timeline for Q3.",
                "focus": "'Piggyback' is common American workplace slang for building on someone's idea",
            },
            {
                "type": "repeat",
                "prompt": "I see where you're coming from, but I have a slightly different perspective on this.",
                "focus": "Polite disagreement — acknowledge first, then share your view",
            },
            {
                "type": "record",
                "prompt": "Practice presenting a project update: 'The project is on track. We've completed phase one and are moving into testing. The main challenge we're facing is...'",
                "tip": "Keep your tone professional but warm — not monotone",
            },
        ],
        "tips": [
            "Americans use indirect language for criticism: 'Have you considered...' means 'You should change...'",
            "In meetings, it's okay to speak up — silence is often seen as disengagement",
            "Use 'I think' and 'I believe' to soften strong opinions",
        ],
    },
    {
        "day": 11,
        "title": "Small Talk & Social Conversations",
        "duration": "5 min",
        "category": "social",
        "description": "Master the art of American small talk — the gateway to building relationships, networking, and making connections.",
        "objectives": [
            "Learn safe small talk topics",
            "Practice conversation starters and follow-ups",
            "Master the art of active listening responses",
            "Build confidence in casual settings",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "Hey! How's it going? Did you catch the game last night? No? Well, you didn't miss much!",
                "focus": "Casual, friendly tone — contractions and relaxed pronunciation",
            },
            {
                "type": "repeat",
                "prompt": "Oh really? That's so cool! How did you get into that? I've always wanted to try something like that.",
                "focus": "Show genuine interest with varied intonation and follow-up questions",
            },
            {
                "type": "record",
                "prompt": "Imagine you're at a networking event. Introduce yourself and ask the other person about their weekend plans.",
                "tip": "Be warm, curious, and keep it light — small talk is about connection, not information",
            },
        ],
        "tips": [
            "Safe topics: weather, sports, food, travel, weekend plans, pets",
            "Avoid: politics, salary, age, weight, religion (in casual settings)",
            "The key to small talk is asking follow-up questions, not sharing your own stories",
        ],
    },
    {
        "day": 12,
        "title": "Say 'No' & Set Boundaries Politely",
        "duration": "5 min",
        "category": "professional",
        "description": "Learn how Americans say no without actually saying 'no.' Master diplomatic refusals, boundary-setting, and assertive-yet-kind communication.",
        "objectives": [
            "Learn indirect refusal phrases",
            "Practice setting boundaries at work",
            "Master the sandwich technique (positive-negative-positive)",
            "Build assertiveness without aggression",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "I really appreciate you thinking of me, but I'm going to have to pass on this one. Maybe next time!",
                "focus": "Warm but firm — appreciate, decline, offer alternative",
            },
            {
                "type": "repeat",
                "prompt": "That sounds like a great opportunity, but my plate is really full right now. Can we revisit this next month?",
                "focus": "'My plate is full' = I'm too busy. Always offer a future possibility.",
            },
            {
                "type": "record",
                "prompt": "Practice declining a meeting invitation: Your boss asks you to join a meeting that conflicts with a deadline.",
                "tip": "Be respectful but clear — don't over-apologize",
            },
        ],
        "tips": [
            "Americans rarely say a flat 'no' — they soften it with context and alternatives",
            "'Let me think about it' is often a polite no",
            "You can be both kind and firm — assertiveness is respected in American culture",
        ],
    },
    {
        "day": 13,
        "title": "Crafting a Powerful Speech",
        "duration": "5 min",
        "category": "advanced",
        "description": "Learn the structure and delivery techniques behind powerful speeches. From TED talks to team presentations, master the art of structured speaking.",
        "objectives": [
            "Learn the hook-body-close structure",
            "Practice powerful opening hooks",
            "Use the 'rule of three' for memorable messages",
            "Master the art of the pause",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "What if I told you that the biggest barrier to your success isn't talent, isn't resources, isn't luck — it's fear?",
                "focus": "The 'rule of three' with a dramatic reveal — pause before 'it's fear'",
            },
            {
                "type": "record",
                "prompt": "Create a 30-second speech opening about a topic you're passionate about. Start with a question, a surprising fact, or a short story.",
                "tip": "The first 10 seconds determine if people keep listening",
            },
            {
                "type": "repeat",
                "prompt": "In conclusion, I want to leave you with three things. First, believe in your voice. Second, practice every day. And third, never apologize for your accent.",
                "focus": "Slow down for the conclusion — each point gets its own beat",
            },
        ],
        "tips": [
            "Great speakers use simple words — clarity beats complexity",
            "Pause for 2-3 seconds after key points to let them sink in",
            "Tell stories — humans remember stories 22x better than facts",
        ],
    },
    {
        "day": 14,
        "title": "Phone & Video Call Mastery",
        "duration": "5 min",
        "category": "professional",
        "description": "Conquer the unique challenges of phone and video calls where you can't rely on gestures or lip-reading. Clarity is everything.",
        "objectives": [
            "Speak clearly without visual cues",
            "Master phone etiquette phrases",
            "Handle connection issues gracefully",
            "Practice video call presence",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "Hi, this is Alex calling from the marketing team. Is this a good time to chat for about ten minutes?",
                "focus": "Identify yourself clearly and ask permission — this is standard American phone etiquette",
            },
            {
                "type": "repeat",
                "prompt": "Sorry, I think you cut out for a second. Could you repeat that last part? I want to make sure I caught everything.",
                "focus": "Polite way to ask for repetition — never say 'I don't understand'",
            },
            {
                "type": "record",
                "prompt": "Practice leaving a voicemail: State your name, reason for calling, and callback number — all in under 30 seconds.",
                "tip": "Speak 20% slower on phone calls — there's no visual context to help",
            },
        ],
        "tips": [
            "On phone calls, over-articulate slightly — you'll sound perfectly clear",
            "Use 'filler-reducers': pause instead of saying um, uh, like",
            "On video calls, look at the camera (not the screen) to make eye contact",
        ],
    },
    {
        "day": 15,
        "title": "Handle Conflicts Like a Pro",
        "duration": "5 min",
        "category": "advanced",
        "description": "Learn to navigate disagreements, misunderstandings, and difficult conversations with grace and clarity in American English.",
        "objectives": [
            "Use 'I' statements instead of 'you' accusations",
            "Practice de-escalation language",
            "Master the art of empathetic listening responses",
            "Resolve misunderstandings without losing face",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "I understand your concern, and I appreciate you bringing this up. Here's how I see the situation...",
                "focus": "Acknowledge, appreciate, then share your perspective",
            },
            {
                "type": "repeat",
                "prompt": "I feel frustrated when deadlines change without notice, because it affects the whole team's workflow. Could we find a way to communicate changes earlier?",
                "focus": "I-statement formula: I feel [emotion] when [situation] because [impact]. Can we [solution]?",
            },
            {
                "type": "record",
                "prompt": "Practice responding to unfair criticism: Your coworker says your report was 'terrible.' Respond calmly and professionally.",
                "tip": "Stay calm, ask for specifics, and propose a solution",
            },
        ],
        "tips": [
            "Never respond to conflict in the heat of the moment — take a breath first",
            "Americans respect direct but respectful communication in conflicts",
            "'Let's find a solution together' is powerful — it shifts from blame to teamwork",
        ],
    },
    {
        "day": 16,
        "title": "Persuade & Influence with Words",
        "duration": "5 min",
        "category": "advanced",
        "description": "Master the art of persuasion in American English. Learn rhetorical techniques that make your arguments compelling and memorable.",
        "objectives": [
            "Use power words that trigger action",
            "Master the 'because' technique",
            "Practice framing and reframing",
            "Build compelling arguments",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "I believe this approach will save us time, reduce costs, and improve customer satisfaction. Here's why...",
                "focus": "Lead with benefits, then explain — people buy the 'what' before the 'how'",
            },
            {
                "type": "repeat",
                "prompt": "Can I go ahead and use the printer? Because I really need to print this document right away.",
                "focus": "The word 'because' increases compliance by 34% — even with weak reasons!",
            },
            {
                "type": "record",
                "prompt": "Persuade your team to adopt a new tool or process. Give three compelling reasons and end with a call to action.",
                "tip": "Use 'imagine' and 'what if' to paint a picture of the future",
            },
        ],
        "tips": [
            "Power words: imagine, discover, proven, guaranteed, free, new, you",
            "People are persuaded by stories more than statistics",
            "Always frame your request in terms of what THEY gain, not what YOU need",
        ],
    },
    {
        "day": 17,
        "title": "Storytelling That Captivates",
        "duration": "5 min",
        "category": "advanced",
        "description": "Learn to tell stories that hold attention, make points memorable, and create emotional connections — a superpower in American culture.",
        "objectives": [
            "Master the story arc (setup, conflict, resolution)",
            "Use sensory details to paint pictures",
            "Practice timing and dramatic pauses",
            "Connect stories to your main message",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "So there I was, standing in front of 200 people, and I completely forgot my speech. My hands were shaking, my mind went blank, and then... something amazing happened.",
                "focus": "Build tension with details, pause before the reveal",
            },
            {
                "type": "record",
                "prompt": "Tell a 1-minute story about a challenge you overcame. Include: the setting, the problem, what you did, and what you learned.",
                "tip": "Great stories have emotion — let your voice convey how you felt",
            },
            {
                "type": "repeat",
                "prompt": "You know what the best part was? It wasn't the success. It was realizing that I had it in me all along.",
                "focus": "End with an insight or lesson — this is what makes stories stick",
            },
        ],
        "tips": [
            "Every good story has a character, a conflict, and a change",
            "Use present tense for vivid moments: 'So I walk in, and there's...'",
            "The best business stories are personal stories with a professional lesson",
        ],
    },
    {
        "day": 18,
        "title": "Active Listening & Powerful Responses",
        "duration": "5 min",
        "category": "social",
        "description": "Communication is 50% listening. Master the verbal and vocal cues that show you're truly engaged and build deeper connections.",
        "objectives": [
            "Learn American back-channel cues (uh-huh, right, totally)",
            "Practice paraphrasing and summarizing",
            "Ask questions that deepen conversations",
            "Show empathy through vocal tone",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "So what you're saying is... you felt like the decision was made without your input, and that was really frustrating. Did I get that right?",
                "focus": "Paraphrase + check = the person feels truly heard",
            },
            {
                "type": "repeat",
                "prompt": "Mm-hmm... right... oh wow, really? That must have been tough. What happened next?",
                "focus": "Natural back-channel responses that show active engagement",
            },
            {
                "type": "record",
                "prompt": "Someone tells you they didn't get the promotion they wanted. Respond with empathy, validate their feelings, and offer encouragement.",
                "tip": "Don't jump to solutions — first show you understand how they feel",
            },
        ],
        "tips": [
            "Americans use 'uh-huh', 'right', 'totally', 'for sure' to show they're listening",
            "Repeating the last 2-3 words someone said invites them to continue",
            "The best conversationalists ask great questions, not give great answers",
        ],
    },
    {
        "day": 19,
        "title": "Interview & High-Stakes Speaking",
        "duration": "5 min",
        "category": "professional",
        "description": "Prepare for job interviews, client pitches, and any high-pressure speaking situation with proven frameworks and practice.",
        "objectives": [
            "Master the STAR method (Situation, Task, Action, Result)",
            "Practice common interview questions",
            "Handle unexpected questions with grace",
            "Project competence and warmth simultaneously",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "In my previous role, we faced a tight deadline with a major client. I took the lead on reorganizing our workflow, and we delivered two days early — which led to a contract extension.",
                "focus": "STAR method: Situation → Task → Action → Result — clear and concise",
            },
            {
                "type": "record",
                "prompt": "Answer this: 'Tell me about a time you had to work with someone difficult.' Use the STAR method.",
                "tip": "Keep it under 90 seconds — be specific, not vague",
            },
            {
                "type": "repeat",
                "prompt": "That's a great question. Let me think about that for a moment... I'd say the most important factor is...",
                "focus": "It's okay to pause and think — it shows thoughtfulness, not weakness",
            },
        ],
        "tips": [
            "Prepare 5-7 STAR stories that cover different skills — most questions fit one of them",
            "Research the company's values and mirror their language in your answers",
            "End every answer by connecting back to how you can help THEM",
        ],
    },
    {
        "day": 20,
        "title": "Presentation Skills & Public Speaking",
        "duration": "5 min",
        "category": "advanced",
        "description": "Bring together everything you've learned to deliver presentations that inform, inspire, and persuade any audience.",
        "objectives": [
            "Structure presentations for maximum impact",
            "Use vocal variety to maintain attention",
            "Handle Q&A sessions confidently",
            "Manage presentation anxiety",
        ],
        "exercises": [
            {
                "type": "repeat",
                "prompt": "Today I'm going to share three insights that changed how our team approaches customer feedback. By the end, you'll have a clear action plan you can implement tomorrow.",
                "focus": "Strong opening: set expectations and promise value",
            },
            {
                "type": "record",
                "prompt": "Give a 1-minute presentation on any topic. Include: an attention-grabbing opening, one key point with an example, and a memorable closing.",
                "tip": "Vary your speed, volume, and pitch — monotone kills attention",
            },
            {
                "type": "repeat",
                "prompt": "Thank you for that question. The short answer is yes, and here's why that matters for our Q2 goals...",
                "focus": "Handling Q&A: acknowledge, answer concisely, connect to your message",
            },
        ],
        "tips": [
            "The 10-20-30 rule: 10 slides, 20 minutes, 30-point font minimum",
            "Practice your opening and closing 10x more than the middle",
            "Record yourself presenting and watch it back — painful but powerful",
        ],
    },
    {
        "day": 21,
        "title": "Final Assessment & Your Communication Certificate",
        "duration": "5 min",
        "category": "milestone",
        "description": "Celebrate your journey! Record your final assessment, compare with Day 1, and receive your Communication Skills Certificate.",
        "objectives": [
            "Record your final self-introduction (compare with Day 1)",
            "Deliver a 2-minute showcase speech",
            "Reflect on your growth and set future goals",
            "Earn your certificate!",
        ],
        "exercises": [
            {
                "type": "record",
                "prompt": "Record the same self-introduction from Day 1: 'Hi, my name is ___ and I'm from ___. I work as a ___ and I'm excited about improving my English communication skills.'",
                "tip": "Compare this with your Day 1 recording — notice the difference!",
            },
            {
                "type": "record",
                "prompt": "Deliver a 2-minute speech on: 'The most important thing I've learned about communication.' Use everything you've practiced.",
                "tip": "Include: a hook, personal story, clear structure, and powerful closing",
            },
            {
                "type": "record",
                "prompt": "Record your commitment: 'My top 3 communication goals for the next 3 months are...'",
                "tip": "Be specific — vague goals don't get achieved",
            },
        ],
        "tips": [
            "You've come incredibly far — celebrate your progress!",
            "Communication is a lifelong skill — keep practicing daily",
            "Share what you've learned with others — teaching is the best way to solidify knowledge",
        ],
    },
]


PHRASEBOOK = {
    "idioms": {
        "title": "Common American Idioms & Phrases",
        "icon": "chat",
        "description": "Everyday expressions that Americans use constantly in casual and professional settings.",
        "categories": [
            {
                "name": "Everyday Conversation",
                "color": "purple",
                "phrases": [
                    {
                        "phrase": "Break the ice",
                        "meaning": "To initiate conversation in a social setting, especially with strangers",
                        "example": "I told a funny story to break the ice at the networking event.",
                        "usage_note": "Very common at parties, meetings, and first encounters.",
                    },
                    {
                        "phrase": "Hit the nail on the head",
                        "meaning": "To describe exactly what is causing a situation or problem",
                        "example": "You hit the nail on the head — the real issue is communication, not the budget.",
                        "usage_note": "Use to strongly agree with someone's analysis.",
                    },
                    {
                        "phrase": "Piece of cake",
                        "meaning": "Something very easy to do",
                        "example": "Don't worry about the presentation — it'll be a piece of cake.",
                        "usage_note": "Casual — great for reassuring someone.",
                    },
                    {
                        "phrase": "Under the weather",
                        "meaning": "Feeling sick or unwell",
                        "example": "I'm feeling a bit under the weather today, so I'll work from home.",
                        "usage_note": "Polite way to say you're sick without details.",
                    },
                    {
                        "phrase": "The ball is in your court",
                        "meaning": "It's your decision or responsibility to act next",
                        "example": "I've sent the proposal. The ball is in their court now.",
                        "usage_note": "Common in both casual and business contexts.",
                    },
                    {
                        "phrase": "Bite off more than you can chew",
                        "meaning": "To take on more responsibility than you can handle",
                        "example": "I think I bit off more than I could chew with three projects at once.",
                        "usage_note": "Often used to admit overcommitment.",
                    },
                    {
                        "phrase": "Cost an arm and a leg",
                        "meaning": "Very expensive",
                        "example": "That new laptop costs an arm and a leg, but it's worth it.",
                        "usage_note": "Casual — never used in formal writing.",
                    },
                    {
                        "phrase": "Get the hang of it",
                        "meaning": "To learn how to do something, to become skilled at something",
                        "example": "The software is confusing at first, but you'll get the hang of it.",
                        "usage_note": "Encouraging phrase — great for helping new team members.",
                    },
                    {
                        "phrase": "On the same page",
                        "meaning": "To have the same understanding or agreement about something",
                        "example": "Let's make sure we're all on the same page before the client meeting.",
                        "usage_note": "Extremely common in workplace conversations.",
                    },
                    {
                        "phrase": "Go the extra mile",
                        "meaning": "To do more than what is expected",
                        "example": "She always goes the extra mile for her clients. That's why they love her.",
                        "usage_note": "Great compliment in professional settings.",
                    },
                ],
            },
            {
                "name": "Agreement & Disagreement",
                "color": "blue",
                "phrases": [
                    {
                        "phrase": "I couldn't agree more",
                        "meaning": "I completely agree with you",
                        "example": "I couldn't agree more — we need to prioritize user experience.",
                        "usage_note": "Strong agreement. Formal and casual.",
                    },
                    {
                        "phrase": "That makes two of us",
                        "meaning": "I feel the same way / I agree",
                        "example": "You're tired of these long meetings? That makes two of us!",
                        "usage_note": "Casual, friendly way to agree.",
                    },
                    {
                        "phrase": "I see where you're coming from, but...",
                        "meaning": "I understand your perspective, however I disagree",
                        "example": "I see where you're coming from, but I think there's a better approach.",
                        "usage_note": "The #1 polite disagreement phrase in American English.",
                    },
                    {
                        "phrase": "Let's agree to disagree",
                        "meaning": "Accept that we have different opinions and move on",
                        "example": "We clearly see this differently. Let's agree to disagree and focus on what we can control.",
                        "usage_note": "De-escalation phrase — ends debates gracefully.",
                    },
                    {
                        "phrase": "You have a point there",
                        "meaning": "What you said is valid / partially correct",
                        "example": "You have a point there. We should consider the timeline more carefully.",
                        "usage_note": "Acknowledges someone's argument without full agreement.",
                    },
                    {
                        "phrase": "Fair enough",
                        "meaning": "That's reasonable / I accept your reasoning",
                        "example": "You want to take a different approach? Fair enough, let's try it.",
                        "usage_note": "Very common in American casual conversation.",
                    },
                ],
            },
            {
                "name": "Time & Urgency",
                "color": "orange",
                "phrases": [
                    {
                        "phrase": "At the end of the day",
                        "meaning": "Ultimately, when everything is considered",
                        "example": "At the end of the day, what matters most is the user's experience.",
                        "usage_note": "Very popular in meetings and discussions.",
                    },
                    {
                        "phrase": "In the nick of time",
                        "meaning": "Just barely in time, at the last possible moment",
                        "example": "We submitted the proposal in the nick of time — five minutes before the deadline.",
                        "usage_note": "Implies a close call or narrow escape.",
                    },
                    {
                        "phrase": "Down the road",
                        "meaning": "In the future",
                        "example": "We can add that feature down the road, but let's focus on the MVP first.",
                        "usage_note": "Very common in planning and strategy discussions.",
                    },
                    {
                        "phrase": "Crunch time",
                        "meaning": "A critical period when intense effort is needed",
                        "example": "It's crunch time — the release is next Friday and we still have bugs to fix.",
                        "usage_note": "Very common in tech and project management.",
                    },
                    {
                        "phrase": "Burning the midnight oil",
                        "meaning": "Working very late into the night",
                        "example": "The team has been burning the midnight oil to meet the deadline.",
                        "usage_note": "Can be admiring or cautionary depending on tone.",
                    },
                    {
                        "phrase": "On the back burner",
                        "meaning": "Postponed, given low priority for now",
                        "example": "Let's put that feature on the back burner and revisit it next quarter.",
                        "usage_note": "Extremely common in business — implies 'not forgotten, just delayed'.",
                    },
                ],
            },
            {
                "name": "Success & Failure",
                "color": "green",
                "phrases": [
                    {
                        "phrase": "Knock it out of the park",
                        "meaning": "To do something extremely well, to exceed expectations",
                        "example": "Your presentation knocked it out of the park! The client was impressed.",
                        "usage_note": "Baseball metaphor — very American. Great compliment.",
                    },
                    {
                        "phrase": "Back to the drawing board",
                        "meaning": "Start over because the current plan failed",
                        "example": "The client rejected our proposal, so it's back to the drawing board.",
                        "usage_note": "Common but not negative — implies resilience.",
                    },
                    {
                        "phrase": "Up and running",
                        "meaning": "Working, operational, functioning properly",
                        "example": "The new server is finally up and running after the migration.",
                        "usage_note": "Very common in tech for systems and services.",
                    },
                    {
                        "phrase": "The sky's the limit",
                        "meaning": "There's no upper boundary to what can be achieved",
                        "example": "With your skills and this team, the sky's the limit.",
                        "usage_note": "Motivational — used to encourage ambition.",
                    },
                    {
                        "phrase": "Drop the ball",
                        "meaning": "To make a mistake, to fail to do something important",
                        "example": "I dropped the ball on sending the follow-up email. I'll do it right now.",
                        "usage_note": "Taking accountability for a mistake — shows maturity when used about yourself.",
                    },
                    {
                        "phrase": "Raise the bar",
                        "meaning": "To set a higher standard",
                        "example": "This new design really raises the bar for our product quality.",
                        "usage_note": "Positive — implies continuous improvement.",
                    },
                ],
            },
            {
                "name": "Decision Making",
                "color": "red",
                "phrases": [
                    {
                        "phrase": "A no-brainer",
                        "meaning": "An easy decision, the choice is obvious",
                        "example": "Upgrading to the faster server is a no-brainer — it pays for itself in a month.",
                        "usage_note": "Casual but used in business all the time.",
                    },
                    {
                        "phrase": "Think outside the box",
                        "meaning": "To think creatively or unconventionally",
                        "example": "We need to think outside the box to solve this scalability issue.",
                        "usage_note": "Overused but still understood everywhere.",
                    },
                    {
                        "phrase": "Play it by ear",
                        "meaning": "To decide as you go, without a fixed plan",
                        "example": "I'm not sure how the meeting will go. Let's play it by ear.",
                        "usage_note": "Common when plans are uncertain.",
                    },
                    {
                        "phrase": "Take it with a grain of salt",
                        "meaning": "Don't take it too seriously, be skeptical",
                        "example": "The benchmark numbers are impressive, but take them with a grain of salt.",
                        "usage_note": "Healthy skepticism — very useful in tech discussions.",
                    },
                    {
                        "phrase": "Cut to the chase",
                        "meaning": "Get to the point, skip the unnecessary details",
                        "example": "Let me cut to the chase — we need more budget or we'll miss the deadline.",
                        "usage_note": "Direct but not rude. Shows respect for people's time.",
                    },
                    {
                        "phrase": "Weigh the pros and cons",
                        "meaning": "Consider the advantages and disadvantages",
                        "example": "Before we switch frameworks, let's weigh the pros and cons.",
                        "usage_note": "Standard phrase for structured decision-making.",
                    },
                ],
            },
        ],
    },
    "tech": {
        "title": "Software Engineering English",
        "icon": "code",
        "description": "Essential vocabulary, phrases, and jargon used daily in software engineering teams, standups, code reviews, and tech interviews.",
        "categories": [
            {
                "name": "Daily Standup & Agile",
                "color": "indigo",
                "phrases": [
                    {
                        "phrase": "I'm blocked on this task",
                        "meaning": "I cannot continue because something is preventing progress",
                        "example": "I'm blocked on the API integration — I need the credentials from DevOps.",
                        "usage_note": "Key standup phrase. Always explain WHAT is blocking you.",
                    },
                    {
                        "phrase": "I'm picking up a new ticket",
                        "meaning": "I'm starting work on a new task from the backlog",
                        "example": "I wrapped up the login bug, so I'm picking up the dashboard ticket next.",
                        "usage_note": "Common in Agile/Scrum teams.",
                    },
                    {
                        "phrase": "Let's table that for now",
                        "meaning": "Let's postpone discussing this topic",
                        "example": "Good point, but let's table that for now and discuss it in the retro.",
                        "usage_note": "Polite way to keep a meeting focused.",
                    },
                    {
                        "phrase": "Can you give me an ETA?",
                        "meaning": "When do you estimate this will be done?",
                        "example": "The PM is asking for an ETA on the payment feature. Any estimate?",
                        "usage_note": "ETA = Estimated Time of Arrival. Standard in tech.",
                    },
                    {
                        "phrase": "We need to scope this out",
                        "meaning": "We need to define the boundaries and requirements of this work",
                        "example": "Before we commit to it, we need to scope this out properly.",
                        "usage_note": "Critical phrase in sprint planning.",
                    },
                    {
                        "phrase": "That's out of scope",
                        "meaning": "That task/feature is not included in the current plan",
                        "example": "Adding dark mode is nice to have, but it's out of scope for this sprint.",
                        "usage_note": "Boundary-setting phrase. Prevents scope creep.",
                    },
                    {
                        "phrase": "Let's circle back on this",
                        "meaning": "Let's return to this topic later",
                        "example": "We don't have enough data yet. Let's circle back on this after the A/B test.",
                        "usage_note": "Very common in tech meetings. Sometimes overused.",
                    },
                    {
                        "phrase": "Ship it!",
                        "meaning": "Release / deploy the code to production",
                        "example": "All tests pass, code review approved — let's ship it!",
                        "usage_note": "Energetic and decisive. Used when code is ready for release.",
                    },
                ],
            },
            {
                "name": "Code Reviews & Technical Discussion",
                "color": "teal",
                "phrases": [
                    {
                        "phrase": "Can you walk me through this?",
                        "meaning": "Can you explain this step by step?",
                        "example": "I see you refactored the auth module. Can you walk me through your approach?",
                        "usage_note": "Non-confrontational way to ask for explanation in code reviews.",
                    },
                    {
                        "phrase": "This is a code smell",
                        "meaning": "This code pattern suggests a deeper design problem",
                        "example": "Having six parameters in one function is a code smell. Can we refactor?",
                        "usage_note": "Technical term — means the code works but could be better.",
                    },
                    {
                        "phrase": "That's a good catch",
                        "meaning": "Thanks for noticing that issue / bug",
                        "example": "Oh, you're right — there's a race condition there. Good catch!",
                        "usage_note": "Positive feedback in code reviews. Very encouraging.",
                    },
                    {
                        "phrase": "Let's not reinvent the wheel",
                        "meaning": "Let's use an existing solution instead of building from scratch",
                        "example": "There's already a well-tested library for this. Let's not reinvent the wheel.",
                        "usage_note": "Common argument for using existing tools/libraries.",
                    },
                    {
                        "phrase": "This is a breaking change",
                        "meaning": "This change will cause existing functionality to stop working",
                        "example": "Renaming the API endpoint is a breaking change — we need a migration plan.",
                        "usage_note": "Critical technical phrase. Signals caution required.",
                    },
                    {
                        "phrase": "Can we add a unit test for this?",
                        "meaning": "This code path needs test coverage",
                        "example": "This edge case is tricky. Can we add a unit test to make sure it doesn't regress?",
                        "usage_note": "Constructive code review feedback.",
                    },
                    {
                        "phrase": "LGTM",
                        "meaning": "Looks Good To Me — approval in code review",
                        "example": "Nice refactor, clean and readable. LGTM!",
                        "usage_note": "Standard code review approval abbreviation.",
                    },
                    {
                        "phrase": "Nit: minor suggestion",
                        "meaning": "A small, non-critical suggestion (short for 'nitpick')",
                        "example": "Nit: Can we rename this variable to something more descriptive?",
                        "usage_note": "Prefix 'nit' signals it's optional, not a blocker.",
                    },
                ],
            },
            {
                "name": "Architecture & Design",
                "color": "violet",
                "phrases": [
                    {
                        "phrase": "Separation of concerns",
                        "meaning": "Each module/component should handle one specific responsibility",
                        "example": "We should keep the business logic separate from the UI — separation of concerns.",
                        "usage_note": "Fundamental design principle. Used in design discussions.",
                    },
                    {
                        "phrase": "That doesn't scale",
                        "meaning": "This approach will fail as the system grows",
                        "example": "Storing sessions in memory doesn't scale. We need Redis or a database.",
                        "usage_note": "Common pushback in architecture discussions.",
                    },
                    {
                        "phrase": "Technical debt",
                        "meaning": "Shortcuts in code that save time now but cost more effort later",
                        "example": "We've accumulated a lot of technical debt in the auth module. We need a refactoring sprint.",
                        "usage_note": "Key concept for justifying refactoring time to managers.",
                    },
                    {
                        "phrase": "Single point of failure",
                        "meaning": "A component that, if it fails, will bring down the entire system",
                        "example": "The database server is a single point of failure. We need replication.",
                        "usage_note": "Used in reliability and infrastructure discussions.",
                    },
                    {
                        "phrase": "MVP — Minimum Viable Product",
                        "meaning": "The simplest version of a product that can be released to users",
                        "example": "For the MVP, let's just support email login. We can add OAuth later.",
                        "usage_note": "Startup and product development staple.",
                    },
                    {
                        "phrase": "Edge case",
                        "meaning": "An unusual or extreme scenario that might cause problems",
                        "example": "What happens if the user submits an empty form? That's an edge case we need to handle.",
                        "usage_note": "Very frequent in testing and code review conversations.",
                    },
                    {
                        "phrase": "Boilerplate code",
                        "meaning": "Repetitive standard code that's needed but isn't unique logic",
                        "example": "There's too much boilerplate in these controllers. Can we use a base class?",
                        "usage_note": "Often discussed when evaluating frameworks or reducing repetition.",
                    },
                    {
                        "phrase": "Over-engineering",
                        "meaning": "Making something more complex than necessary",
                        "example": "Building a microservice for this is over-engineering. A simple function will do.",
                        "usage_note": "Common criticism — implies unnecessary complexity.",
                    },
                ],
            },
            {
                "name": "Debugging & Incidents",
                "color": "red",
                "phrases": [
                    {
                        "phrase": "It works on my machine",
                        "meaning": "The bug only appears in certain environments, not on my local setup",
                        "example": "I can't reproduce it locally — it works on my machine. Must be an environment issue.",
                        "usage_note": "Famous developer phrase (often said jokingly). Points to environment differences.",
                    },
                    {
                        "phrase": "Root cause analysis",
                        "meaning": "Investigation to find the fundamental reason for a bug or outage",
                        "example": "Before we patch it, let's do a root cause analysis to understand why this happened.",
                        "usage_note": "Standard post-incident process.",
                    },
                    {
                        "phrase": "Can you reproduce the issue?",
                        "meaning": "Can you make the bug happen again consistently?",
                        "example": "Can you reproduce the issue? I need the exact steps to debug it.",
                        "usage_note": "First question in any bug investigation.",
                    },
                    {
                        "phrase": "It's a regression",
                        "meaning": "Something that previously worked is now broken",
                        "example": "The login page worked fine last week. This is a regression from yesterday's deploy.",
                        "usage_note": "Implies a recent change introduced the bug.",
                    },
                    {
                        "phrase": "Hotfix",
                        "meaning": "An urgent code fix deployed directly to production",
                        "example": "Users can't check out. We need to push a hotfix immediately.",
                        "usage_note": "Emergency fix — bypasses normal release process.",
                    },
                    {
                        "phrase": "Let's roll it back",
                        "meaning": "Revert to the previous version to fix a problem",
                        "example": "The new release is causing errors. Let's roll it back and investigate.",
                        "usage_note": "Common incident response action. Quick way to restore stability.",
                    },
                    {
                        "phrase": "Post-mortem",
                        "meaning": "A meeting/document that reviews what went wrong after an incident",
                        "example": "We should schedule a post-mortem to discuss the outage and prevent it from happening again.",
                        "usage_note": "Blameless post-mortems are standard in good engineering cultures.",
                    },
                    {
                        "phrase": "Rubber duck debugging",
                        "meaning": "Explaining your code line by line (even to an object) to find bugs",
                        "example": "I was stuck for an hour, then I tried rubber duck debugging and found the issue in two minutes.",
                        "usage_note": "Humor-tinged but genuinely used technique.",
                    },
                ],
            },
            {
                "name": "Collaboration & Communication",
                "color": "blue",
                "phrases": [
                    {
                        "phrase": "Can you pair with me on this?",
                        "meaning": "Can we work together on this task (pair programming)?",
                        "example": "This auth flow is tricky. Can you pair with me on this for an hour?",
                        "usage_note": "Pair programming request — not a sign of weakness, it's professional.",
                    },
                    {
                        "phrase": "I'll ping you on Slack",
                        "meaning": "I'll send you a message",
                        "example": "Let me look into it and I'll ping you on Slack when I have an update.",
                        "usage_note": "'Ping' = send a quick message. Very common in tech.",
                    },
                    {
                        "phrase": "Can I get your eyes on this?",
                        "meaning": "Can you review this / look at this?",
                        "example": "I just opened a PR. Can I get your eyes on it before end of day?",
                        "usage_note": "Casual way to request a code review.",
                    },
                    {
                        "phrase": "Let's sync up",
                        "meaning": "Let's have a quick meeting to align on something",
                        "example": "Hey, I have questions about the API contract. Can we sync up for 15 minutes?",
                        "usage_note": "Short, focused meeting request. Very common.",
                    },
                    {
                        "phrase": "I'll take an action item on that",
                        "meaning": "I'll take responsibility for doing that task",
                        "example": "Good point about the docs. I'll take an action item on updating the README.",
                        "usage_note": "Shows accountability. Makes meetings productive.",
                    },
                    {
                        "phrase": "We're on the same page",
                        "meaning": "We have the same understanding",
                        "example": "After the design review, I think we're all on the same page about the approach.",
                        "usage_note": "Confirms alignment — very common in team settings.",
                    },
                    {
                        "phrase": "Heads up",
                        "meaning": "A warning or advance notice about something",
                        "example": "Heads up — I'm going to merge the database migration this afternoon. Expect some downtime.",
                        "usage_note": "Proactive communication. Shows good team citizenship.",
                    },
                    {
                        "phrase": "That's a rabbit hole",
                        "meaning": "That topic/task is much more complex than it appears",
                        "example": "Don't start refactoring the date library — that's a rabbit hole. Trust me.",
                        "usage_note": "Warning that something will consume much more time than expected.",
                    },
                ],
            },
            {
                "name": "Tech Interview Phrases",
                "color": "green",
                "phrases": [
                    {
                        "phrase": "Let me think out loud",
                        "meaning": "I'll share my reasoning process as I work through this",
                        "example": "Let me think out loud. The brute force approach would be O(n²), but we can optimize with a hash map...",
                        "usage_note": "Essential interview skill — interviewers want to hear your thought process.",
                    },
                    {
                        "phrase": "What are the constraints?",
                        "meaning": "What are the limits (input size, time, memory)?",
                        "example": "Before I start coding, what are the constraints? How large can the input array be?",
                        "usage_note": "Shows structured thinking. Always ask this in interviews.",
                    },
                    {
                        "phrase": "The trade-off here is...",
                        "meaning": "The advantage/disadvantage balance is...",
                        "example": "The trade-off here is memory versus speed. We can use more memory to get O(1) lookup.",
                        "usage_note": "Shows engineering maturity — every design has trade-offs.",
                    },
                    {
                        "phrase": "Let me walk through an example",
                        "meaning": "Let me demonstrate with a specific case",
                        "example": "Let me walk through an example with the input [3, 1, 4, 1, 5] to make sure my logic works.",
                        "usage_note": "Great practice before coding — catches bugs early.",
                    },
                    {
                        "phrase": "I'd optimize this by...",
                        "meaning": "I'd improve the performance/efficiency by...",
                        "example": "I'd optimize this by using a sliding window instead of nested loops, bringing it down to O(n).",
                        "usage_note": "Shows you think about efficiency beyond the first solution.",
                    },
                    {
                        "phrase": "In my previous role, I...",
                        "meaning": "Drawing on past experience to answer behavioral questions",
                        "example": "In my previous role, I led the migration from a monolith to microservices, which reduced deploy times by 60%.",
                        "usage_note": "STAR method starter — Situation/Task is built in.",
                    },
                    {
                        "phrase": "Could you clarify the requirements?",
                        "meaning": "Can you explain more about what exactly is expected?",
                        "example": "Could you clarify the requirements? Should the search be case-sensitive?",
                        "usage_note": "Shows attention to detail. Never assume — always ask.",
                    },
                    {
                        "phrase": "That's a good question — let me think about that",
                        "meaning": "Buying time to formulate a thoughtful answer",
                        "example": "That's a good question — let me think about that for a second. I'd approach it by...",
                        "usage_note": "Perfectly acceptable to pause and think in interviews.",
                    },
                ],
            },
        ],
    },
}


def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None, None
    users = load_users()
    return user_id, users.get(user_id)


def get_user_progress():
    user_id, user = get_current_user()
    if user:
        return user.get("progress", {"completed_days": []})
    return {"completed_days": []}


def save_user_progress(progress):
    user_id = session.get("user_id")
    if not user_id:
        return
    users = load_users()
    if user_id in users:
        users[user_id]["progress"] = progress
        save_users(users)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


# ========== Auth Routes ==========


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip().lower()

        if not user_id:
            error = "Please enter a User ID."
        elif not re.match(r"^[a-z0-9_]{3,20}$", user_id):
            error = "User ID must be 3-20 characters: letters, numbers, and underscores only."
        else:
            users = load_users()
            if user_id in users:
                session["user_id"] = user_id
                return redirect(url_for("index"))
            else:
                error = f'User ID "{user_id}" not found. Click "Create Account" below to register.'

    return render_template("login.html", error=error, mode="login")


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip().lower()
        display_name = request.form.get("display_name", "").strip()

        if not user_id:
            error = "Please enter a User ID."
        elif not re.match(r"^[a-z0-9_]{3,20}$", user_id):
            error = "User ID must be 3-20 characters: letters, numbers, and underscores only."
        elif not display_name:
            error = "Please enter your name."
        elif len(display_name) > 50:
            error = "Name must be 50 characters or fewer."
        else:
            users = load_users()
            if user_id in users:
                error = f'User ID "{user_id}" is already taken. Please choose a different one.'
            else:
                users[user_id] = {
                    "display_name": display_name,
                    "created": datetime.now().isoformat(),
                    "progress": {"completed_days": []},
                }
                save_users(users)
                session["user_id"] = user_id
                return redirect(url_for("index"))

    return render_template("login.html", error=error, success=success, mode="register")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


# ========== App Routes ==========


@app.route("/")
@login_required
def index():
    user_id, user = get_current_user()
    progress = get_user_progress()
    return render_template(
        "index.html",
        lessons=CURRICULUM,
        progress=progress,
        user_id=user_id,
        user=user,
    )


@app.route("/lesson/<int:day>")
@login_required
def lesson(day):
    lesson_data = next((l for l in CURRICULUM if l["day"] == day), None)
    if not lesson_data:
        return "Lesson not found", 404
    user_id, user = get_current_user()
    progress = get_user_progress()
    prev_day = day - 1 if day > 1 else None
    next_day = day + 1 if day < len(CURRICULUM) else None
    return render_template(
        "lesson.html",
        lesson=lesson_data,
        progress=progress,
        prev_day=prev_day,
        next_day=next_day,
        total_lessons=len(CURRICULUM),
        user_id=user_id,
        user=user,
    )


@app.route("/api/progress", methods=["GET"])
@login_required
def get_progress():
    return jsonify(get_user_progress())


@app.route("/api/progress/complete", methods=["POST"])
@login_required
def complete_day():
    data = request.json
    day = data.get("day")
    progress = get_user_progress()
    if day not in progress["completed_days"]:
        progress["completed_days"].append(day)
        progress["completed_days"].sort()
    save_user_progress(progress)
    return jsonify({"success": True, "progress": progress})


@app.route("/api/progress/uncomplete", methods=["POST"])
@login_required
def uncomplete_day():
    data = request.json
    day = data.get("day")
    progress = get_user_progress()
    if day in progress["completed_days"]:
        progress["completed_days"].remove(day)
    save_user_progress(progress)
    return jsonify({"success": True, "progress": progress})


@app.route("/api/progress/reset", methods=["POST"])
@login_required
def reset_progress():
    progress = {"completed_days": []}
    save_user_progress(progress)
    return jsonify({"success": True, "progress": progress})


@app.route("/phrasebook")
@login_required
def phrasebook():
    user_id, user = get_current_user()
    section = request.args.get("section", "idioms")
    data = PHRASEBOOK.get(section, PHRASEBOOK["idioms"])
    return render_template(
        "phrasebook.html",
        section=section,
        data=data,
        sections=PHRASEBOOK,
        user_id=user_id,
        user=user,
    )


@app.route("/certificate")
@login_required
def certificate():
    user_id, user = get_current_user()
    progress = get_user_progress()
    total = len(CURRICULUM)
    completed = len(progress["completed_days"])
    return render_template(
        "certificate.html",
        total=total,
        completed=completed,
        progress=progress,
        user_id=user_id,
        user=user,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, host="0.0.0.0", port=port)
