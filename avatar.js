/* ═══ ANIME AVATAR AI CHAT WIDGET ═══
   Connects to a FastAPI backend at window.__AVATAR_API_URL
   Falls back to a static offline persona if no API URL is set.
   Pipeline: Web Speech API STT → backend /api/avatar-chat → base64 WAV → play
*/
(function () {
  'use strict';

  // ── Config ──────────────────────────────────────────────────────────────
  const API_URL  = (window.__AVATAR_API_URL || '').replace(/\/$/, '');
  const MAX_HIST = 8; // keep last N turns in context

  // ── DOM refs (resolved after DOMContentLoaded) ───────────────────────────
  let wrap, bubble, btn, micNote;

  // ── State ─────────────────────────────────────────────────────────────────
  let state       = 'idle';  // idle | listening | thinking | speaking
  let history     = [];      // [{role,content}]
  let recognition = null;
  let audioCtx    = null;
  let currentSrc  = null;
  let isOpen      = false;

  // ── Offline fallback answers ──────────────────────────────────────────────
  const OFFLINE = [
    "Hi! I'm Seeshuraj's anime avatar. My backend isn't connected yet — but I can tell you I'm an AI & Software Engineer with an MSc in HPC from Trinity College Dublin.",
    "I specialise in LLM-powered apps, cloud infrastructure, and full-stack development. Check my projects section!",
    "I'm actively looking for graduate / junior SWE roles in Dublin, EU, and remote. Drop me an email at bhoopals@tcd.ie!",
    "I've worked with LangGraph, FastAPI, Next.js, AWS, Azure, CUDA, and more. What would you like to know?",
  ];
  let offlineIdx = 0;

  // ── Helpers ───────────────────────────────────────────────────────────────
  function setState(s) {
    if (!wrap) return;
    ['idle','listening','thinking','speaking'].forEach(c => wrap.classList.remove('avatar-state-'+c));
    wrap.classList.add('avatar-state-'+s);
    state = s;
  }

  function showBubble(html) {
    if (!bubble) return;
    bubble.innerHTML = html;
    bubble.classList.add('visible');
  }

  function hideBubble() {
    if (!bubble) return;
    bubble.classList.remove('visible');
  }

  function thinkingHTML() {
    return '<span class="thinking-dots"><span></span><span></span><span></span></span>';
  }

  // ── Audio playback via AudioContext ───────────────────────────────────────
  function playBase64Wav(b64) {
    return new Promise((resolve) => {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const bytes   = atob(b64);
        const buf     = new Uint8Array(bytes.length);
        for (let i = 0; i < bytes.length; i++) buf[i] = bytes.charCodeAt(i);
        audioCtx.decodeAudioData(buf.buffer, (decoded) => {
          if (currentSrc) { try { currentSrc.stop(); } catch(e) {} }
          currentSrc = audioCtx.createBufferSource();
          currentSrc.buffer = decoded;
          currentSrc.connect(audioCtx.destination);
          currentSrc.onended = resolve;
          currentSrc.start(0);
        }, resolve);
      } catch (e) {
        console.warn('[avatar] audio playback error', e);
        resolve();
      }
    });
  }

  // ── API call ──────────────────────────────────────────────────────────────
  async function queryBackend(userMsg) {
    if (!API_URL) {
      // offline mode
      const ans = OFFLINE[offlineIdx % OFFLINE.length];
      offlineIdx++;
      await new Promise(r => setTimeout(r, 700));
      return { answer_text: ans, audio_base64: null };
    }
    const res = await fetch(API_URL + '/api/avatar-chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: userMsg, history: history.slice(-MAX_HIST) }),
    });
    if (!res.ok) throw new Error('API ' + res.status);
    return res.json();
  }

  // ── Main chat handler ─────────────────────────────────────────────────────
  async function handleUserInput(text) {
    if (!text.trim()) return;
    history.push({ role: 'user', content: text });

    setState('thinking');
    showBubble(thinkingHTML());

    try {
      const data = await queryBackend(text);
      const answer = data.answer_text || '...';
      history.push({ role: 'assistant', content: answer });

      setState('speaking');
      showBubble(answer);

      if (data.audio_base64) {
        await playBase64Wav(data.audio_base64);
      } else {
        // no audio — just show text for 4 seconds
        await new Promise(r => setTimeout(r, Math.min(answer.length * 55, 6000)));
      }
    } catch (err) {
      console.warn('[avatar] query error', err);
      showBubble('Hmm, something went wrong. Try again?');
      await new Promise(r => setTimeout(r, 3000));
    }

    setState('idle');
    hideBubble();
    isOpen = false;
    btn.classList.remove('active');
    if (micNote) micNote.textContent = '';
  }

  // ── Web Speech API (STT) ──────────────────────────────────────────────────
  function buildRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return null;
    const r = new SpeechRecognition();
    r.lang        = 'en-US';
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      if (micNote) micNote.textContent = '"' + transcript + '"';
      stopListening();
      handleUserInput(transcript);
    };
    r.onerror = (e) => {
      console.warn('[avatar] STT error', e.error);
      stopListening();
      // If no mic or denied, fall back to a typed prompt
      const typed = prompt('Type your question for Seeshuraj:');
      if (typed) handleUserInput(typed);
    };
    r.onend = () => {
      if (state === 'listening') setState('idle');
    };
    return r;
  }

  function startListening() {
    if (!recognition) recognition = buildRecognition();
    if (!recognition) {
      // no STT — ask via prompt
      const typed = prompt('Type your question for Seeshuraj:');
      if (typed) handleUserInput(typed);
      return;
    }
    setState('listening');
    showBubble('Listening…');
    if (micNote) micNote.textContent = 'Speak now…';
    try { recognition.start(); } catch(e) {}
  }

  function stopListening() {
    try { if (recognition) recognition.stop(); } catch(e) {}
  }

  // ── Button handler ────────────────────────────────────────────────────────
  function onTalkClick() {
    if (state === 'thinking' || state === 'speaking') return; // busy
    if (state === 'listening') {
      stopListening();
      setState('idle');
      hideBubble();
      isOpen = false;
      btn.classList.remove('active');
      return;
    }
    isOpen = true;
    btn.classList.add('active');
    startListening();
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  function init() {
    wrap    = document.querySelector('.anime-wrap');
    bubble  = document.getElementById('avatarBubble');
    btn     = document.getElementById('animeTalkBtn');
    micNote = document.getElementById('avatarMicNote');

    if (!wrap || !btn) return; // elements not in DOM

    setState('idle');

    btn.addEventListener('click', onTalkClick);

    // Also allow clicking the avatar image itself
    const img = wrap.querySelector('.anime-avatar');
    if (img) img.addEventListener('click', onTalkClick);

    console.log('[avatar] ready. API:', API_URL || '(offline mode)');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
