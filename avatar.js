/* ═══ ANIME AVATAR AI CHAT WIDGET ═══
   Pipeline: Web Speech API STT → backend /api/avatar-chat → base64 WAV → play
   Cold-start fix: fires a /health wake-ping on page load, shows a toast while warming up.
*/
(function () {
  'use strict';

  const API_URL  = (window.__AVATAR_API_URL || '').replace(/\/$/, '');
  const MAX_HIST = 8;

  let wrap, bubble, btn, micNote, warmupToast;
  let state       = 'idle';
  let history     = [];
  let recognition = null;
  let audioCtx    = null;
  let currentSrc  = null;
  let apiReady    = !API_URL; // true immediately if no API (offline mode)

  // ── Offline fallback ─────────────────────────────────────────────────────
  const OFFLINE = [
    "Hi! I'm Seeshuraj's anime avatar. My backend isn't connected yet — but I can tell you I'm an AI & Software Engineer with an MSc in HPC from Trinity College Dublin.",
    "I specialise in LLM-powered apps, cloud infrastructure, and full-stack development. Check my projects section!",
    "I'm actively looking for graduate / junior SWE roles in Dublin, EU, and remote. Drop me an email at bhoopals@tcd.ie!",
    "I've worked with LangGraph, FastAPI, Next.js, AWS, Azure, CUDA, and more. What would you like to know?",
  ];
  let offlineIdx = 0;

  // ── Wake-ping: hit /health on page load to beat Render cold start ─────────
  function warmUp() {
    if (!API_URL) return;
    warmupToast = document.getElementById('apiWarmup');
    // Show toast only after 2s (don't flash it if API is already warm)
    const toastTimer = setTimeout(() => {
      if (!apiReady && warmupToast) warmupToast.classList.add('show');
    }, 2000);

    fetch(API_URL + '/health', { method: 'GET', signal: AbortSignal.timeout(35000) })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(() => {
        apiReady = true;
        clearTimeout(toastTimer);
        if (warmupToast) warmupToast.classList.remove('show');
        console.log('[avatar] API ready');
      })
      .catch(err => {
        console.warn('[avatar] warm-up failed', err);
        apiReady = true; // allow attempts anyway — API might respond to chat even if health timed out
        clearTimeout(toastTimer);
        if (warmupToast) warmupToast.classList.remove('show');
      });
  }

  // ── State helpers ─────────────────────────────────────────────────────────
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

  // ── Audio ─────────────────────────────────────────────────────────────────
  function playBase64Wav(b64) {
    return new Promise((resolve) => {
      try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const bytes = atob(b64);
        const buf   = new Uint8Array(bytes.length);
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
        console.warn('[avatar] audio error', e);
        resolve();
      }
    });
  }

  // ── API call ──────────────────────────────────────────────────────────────
  async function queryBackend(userMsg) {
    if (!API_URL) {
      const ans = OFFLINE[offlineIdx % OFFLINE.length];
      offlineIdx++;
      await new Promise(r => setTimeout(r, 700));
      return { answer_text: ans, audio_base64: null };
    }

    // If API is still waking up, wait for it (up to 35s)
    if (!apiReady) {
      showBubble('⏳ Waking up the server… (~15s first load)');
      await new Promise(resolve => {
        const iv = setInterval(() => { if (apiReady) { clearInterval(iv); resolve(); } }, 300);
        setTimeout(() => { clearInterval(iv); resolve(); }, 35000);
      });
      showBubble(thinkingHTML());
    }

    const res = await fetch(API_URL + '/api/avatar-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg, history: history.slice(-MAX_HIST) }),
      signal: AbortSignal.timeout(60000),
    });
    if (!res.ok) throw new Error('API ' + res.status);
    return res.json();
  }

  // ── Chat handler ──────────────────────────────────────────────────────────
  async function handleUserInput(text) {
    if (!text.trim()) return;
    history.push({ role: 'user', content: text });
    setState('thinking');
    showBubble(thinkingHTML());
    try {
      const data   = await queryBackend(text);
      const answer = data.answer_text || '...';
      history.push({ role: 'assistant', content: answer });
      setState('speaking');
      showBubble(answer);
      if (data.audio_base64) {
        await playBase64Wav(data.audio_base64);
      } else {
        await new Promise(r => setTimeout(r, Math.min(answer.length * 55, 6000)));
      }
    } catch (err) {
      console.warn('[avatar] query error', err);
      showBubble('Hmm, something went wrong. Try again?');
      await new Promise(r => setTimeout(r, 3000));
    }
    setState('idle');
    hideBubble();
    btn.classList.remove('active');
    if (micNote) micNote.textContent = '';
  }

  // ── Speech recognition ────────────────────────────────────────────────────
  function buildRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return null;
    const r = new SR();
    r.lang = 'en-US'; r.interimResults = false; r.maxAlternatives = 1;
    r.onresult = (e) => {
      const t = e.results[0][0].transcript;
      if (micNote) micNote.textContent = '"' + t + '"';
      stopListening();
      handleUserInput(t);
    };
    r.onerror = (e) => {
      console.warn('[avatar] STT error', e.error);
      stopListening();
      const typed = prompt('Type your question for Seeshuraj:');
      if (typed) handleUserInput(typed);
    };
    r.onend = () => { if (state === 'listening') setState('idle'); };
    return r;
  }

  function startListening() {
    if (!recognition) recognition = buildRecognition();
    if (!recognition) {
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

  // ── Button ────────────────────────────────────────────────────────────────
  function onTalkClick() {
    if (state === 'thinking' || state === 'speaking') return;
    if (state === 'listening') {
      stopListening(); setState('idle'); hideBubble();
      btn.classList.remove('active'); return;
    }
    btn.classList.add('active');
    startListening();
  }

  // ── Init ──────────────────────────────────────────────────────────────────
  function init() {
    wrap    = document.querySelector('.anime-wrap');
    bubble  = document.getElementById('avatarBubble');
    btn     = document.getElementById('animeTalkBtn');
    micNote = document.getElementById('avatarMicNote');
    if (!wrap || !btn) return;
    setState('idle');
    btn.addEventListener('click', onTalkClick);
    const img = wrap.querySelector('.anime-avatar');
    if (img) img.addEventListener('click', onTalkClick);
    warmUp(); // fire /health ping immediately on page load
    console.log('[avatar] ready. API:', API_URL || '(offline mode)');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
