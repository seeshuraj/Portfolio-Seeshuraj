/**
 * Seeshuraj Anime Avatar — Voice Chat Controller
 * Pipeline: Web Speech STT → FastAPI (NVIDIA NIM RAG) → Azure Neural TTS → Audio
 * States: idle | listening | thinking | speaking
 */
(function () {
  'use strict';

  // ── Config ───────────────────────────────────────────────────────────────
  const API_URL = (window.__AVATAR_API_URL || 'https://seeshuraj-avatar-api.onrender.com').replace(/\/$/, '');
  const MAX_HISTORY = 6; // turns to keep in memory

  // ── DOM refs ─────────────────────────────────────────────────────────────
  const talkBtn   = document.getElementById('animeTalkBtn');
  const bubble    = document.getElementById('avatarBubble');
  const animeWrap = document.getElementById('animeWrap');
  const warmupBar = document.getElementById('apiWarmup');
  const warmupMsg = document.getElementById('apiWarmupMsg');

  if (!talkBtn || !animeWrap) return; // avatar not on this page

  // ── State ────────────────────────────────────────────────────────────────
  let state        = 'idle';      // idle | listening | thinking | speaking
  let history      = [];          // [{role, content}]
  let recognition  = null;
  let audioCtx     = null;
  let currentAudio = null;
  let warmedUp     = false;

  // ── State machine ────────────────────────────────────────────────────────
  function setState(s) {
    state = s;
    animeWrap.dataset.avatarState = s;
    switch (s) {
      case 'idle':      talkBtn.textContent = 'Talk to Seeshuraj'; talkBtn.disabled = false; break;
      case 'listening': talkBtn.textContent = '🎤 Listening…';     talkBtn.disabled = false; break;
      case 'thinking':  talkBtn.textContent = '⏳ Thinking…';      talkBtn.disabled = true;  break;
      case 'speaking':  talkBtn.textContent = '🔊 Speaking…';      talkBtn.disabled = true;  break;
    }
  }

  // ── Speech bubble ────────────────────────────────────────────────────────
  function showBubble(text) {
    if (!bubble) return;
    bubble.textContent = text;
    bubble.classList.add('visible');
  }
  function hideBubble() {
    if (!bubble) return;
    bubble.classList.remove('visible');
    setTimeout(() => { bubble.textContent = ''; }, 400);
  }

  // ── Warmup toast ─────────────────────────────────────────────────────────
  function showWarmup(msg) {
    if (!warmupBar) return;
    if (warmupMsg) warmupMsg.textContent = msg;
    warmupBar.classList.add('show');
  }
  function hideWarmup() {
    if (!warmupBar) return;
    warmupBar.classList.remove('show');
  }

  // ── Ping backend to warm up Render free instance ─────────────────────────
  async function warmUp() {
    if (warmedUp) return;
    try {
      showWarmup('Waking up AI avatar…');
      const r = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(15000) });
      if (r.ok) {
        warmedUp = true;
        showWarmup('Avatar is ready ✓');
        setTimeout(hideWarmup, 2000);
      }
    } catch {
      hideWarmup();
    }
  }

  // Warm up when user hovers the avatar section
  animeWrap.addEventListener('mouseenter', warmUp, { once: true });
  animeWrap.addEventListener('touchstart', warmUp, { once: true, passive: true });

  // ── Web Speech API setup ─────────────────────────────────────────────────
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const hasSpeech = !!SpeechRecognition;

  function setupRecognition() {
    if (!hasSpeech) return null;
    const r = new SpeechRecognition();
    r.lang = 'en-IE';
    r.interimResults = false;
    r.maxAlternatives = 1;
    r.continuous = false;
    r.onresult = (e) => {
      const transcript = e.results[0][0].transcript.trim();
      if (transcript) sendMessage(transcript);
    };
    r.onerror = (e) => {
      console.warn('Speech recognition error:', e.error);
      if (e.error === 'not-allowed') {
        showBubble('Microphone access denied. Please allow mic and try again.');
        setTimeout(hideBubble, 4000);
      }
      setState('idle');
    };
    r.onend = () => {
      if (state === 'listening') setState('idle');
    };
    return r;
  }

  // ── Play WAV base64 audio ─────────────────────────────────────────────────
  async function playAudio(base64wav) {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') await audioCtx.resume();

      const binary = atob(base64wav);
      const bytes  = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);

      const buffer = await audioCtx.decodeAudioData(bytes.buffer);
      const source = audioCtx.createBufferSource();
      source.buffer = buffer;
      source.connect(audioCtx.destination);

      currentAudio = source;
      setState('speaking');

      await new Promise((resolve) => {
        source.onended = resolve;
        source.start(0);
      });
    } catch (err) {
      console.warn('Audio playback error:', err);
    } finally {
      currentAudio = null;
      setState('idle');
    }
  }

  // ── Core: send message to backend ────────────────────────────────────────
  async function sendMessage(userText) {
    if (state === 'thinking' || state === 'speaking') return;

    setState('thinking');
    showBubble('...');

    try {
      const res = await fetch(`${API_URL}/api/avatar-chat`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message: userText, history }),
        signal:  AbortSignal.timeout(30000),
      });

      if (!res.ok) throw new Error(`API ${res.status}`);

      const data = await res.json();
      const { answer_text, audio_base64 } = data;

      // Update conversation history
      history.push({ role: 'user',      content: userText     });
      history.push({ role: 'assistant', content: answer_text  });
      if (history.length > MAX_HISTORY * 2) history = history.slice(-MAX_HISTORY * 2);

      showBubble(answer_text);

      if (audio_base64) {
        await playAudio(audio_base64);
      } else {
        // Fallback: browser TTS if Azure not configured
        if (window.speechSynthesis) {
          const utt = new SpeechSynthesisUtterance(answer_text);
          utt.lang = 'en-IE';
          utt.rate = 1.05;
          setState('speaking');
          window.speechSynthesis.speak(utt);
          utt.onend = () => setState('idle');
        } else {
          setState('idle');
        }
      }

      // Hide bubble 4s after speaking ends
      setTimeout(hideBubble, 4000);

    } catch (err) {
      console.error('Avatar API error:', err);
      showBubble('Sorry, I had trouble connecting. Try again!');
      setTimeout(hideBubble, 3500);
      setState('idle');
    }
  }

  // ── Text input fallback (if no mic / browser doesn't support STT) ─────────
  function promptTextInput() {
    const userText = window.prompt('Ask me anything about Seeshuraj:');
    if (userText && userText.trim()) sendMessage(userText.trim());
    else setState('idle');
  }

  // ── Talk button click ────────────────────────────────────────────────────
  talkBtn.addEventListener('click', async () => {
    if (state === 'thinking' || state === 'speaking') return;

    // Stop any ongoing speech
    if (currentAudio) { try { currentAudio.stop(); } catch {} }
    if (window.speechSynthesis) window.speechSynthesis.cancel();

    // Warm up backend on first real click
    if (!warmedUp) await warmUp();

    if (state === 'listening') {
      if (recognition) recognition.stop();
      setState('idle');
      return;
    }

    if (!hasSpeech) {
      promptTextInput();
      return;
    }

    recognition = setupRecognition();
    try {
      setState('listening');
      recognition.start();
    } catch {
      promptTextInput();
    }
  });

  // ── Keyboard shortcut: Space bar triggers avatar (when focused) ───────────
  talkBtn.addEventListener('keydown', (e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      talkBtn.click();
    }
  });

  // Init
  setState('idle');
  console.log('[Avatar] Initialised. API:', API_URL);
})();
