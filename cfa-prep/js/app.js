(() => {
  const STORAGE_KEY = "cfa-prep-v1";
  const DAILY_COUNT = 10;
  const KEYS = ["A", "B", "C", "D"];

  const state = {
    view: "home",
    mode: null,
    queue: [],
    index: 0,
    selected: null,
    revealed: false,
    sessionCorrect: 0,
    sessionWrong: 0,
    sessionMisses: [],
  };

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  function loadStore() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultStore();
      return { ...defaultStore(), ...JSON.parse(raw) };
    } catch {
      return defaultStore();
    }
  }

  function defaultStore() {
    return {
      answered: 0,
      correct: 0,
      streak: 0,
      lastDailyDate: null,
      wrongIds: [],
      wrongDetails: {},
      topicStats: {},
      history: [],
    };
  }

  let store = loadStore();

  function saveStore() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  }

  function todayKey() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  }

  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function byId(id) {
    return window.CFA_QUESTIONS.find((q) => q.id === id);
  }

  function topics() {
    const map = new Map();
    for (const q of window.CFA_QUESTIONS) {
      map.set(q.topic, (map.get(q.topic) || 0) + 1);
    }
    return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }

  function showScreen(name) {
    state.view = name;
    $$(".screen").forEach((el) => el.classList.toggle("active", el.dataset.screen === name));
    const back = $("#btn-back");
    back.classList.toggle("hidden", name === "home");
  }

  function accuracy() {
    if (!store.answered) return 0;
    return Math.round((store.correct / store.answered) * 100);
  }

  function renderHome() {
    showScreen("home");
    $("#stat-streak").textContent = String(store.streak);
    $("#stat-accuracy").textContent = `${accuracy()}%`;
    $("#stat-wrong").textContent = String(store.wrongIds.length);
    $("#wrong-count-badge").textContent = String(store.wrongIds.length);

    const dailyDone = store.lastDailyDate === todayKey();
    $("#daily-cta").textContent = dailyDone ? "Practice 10 more" : "Start daily drill";
    $("#daily-hint").textContent = dailyDone
      ? "You already completed today’s set — keep going if you want."
      : `${DAILY_COUNT} mixed questions · ~8–12 minutes`;

    const list = $("#topic-list");
    list.innerHTML = "";
    for (const [topic, count] of topics()) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "topic-item";
      btn.innerHTML = `<div><strong>${topic}</strong><span>${count} questions</span></div><span class="chev" aria-hidden="true">→</span>`;
      btn.addEventListener("click", () => startTopic(topic));
      list.appendChild(btn);
    }
  }

  function startDaily() {
    const pool = shuffle(window.CFA_QUESTIONS).slice(0, Math.min(DAILY_COUNT, window.CFA_QUESTIONS.length));
    beginSession("daily", pool);
  }

  function startTopic(topic) {
    const pool = shuffle(window.CFA_QUESTIONS.filter((q) => q.topic === topic));
    beginSession("topic", pool);
  }

  function startMixed(n = 15) {
    beginSession("mixed", shuffle(window.CFA_QUESTIONS).slice(0, n));
  }

  function startWrongReview() {
    const pool = store.wrongIds.map(byId).filter(Boolean);
    if (!pool.length) {
      alert("No wrong answers yet. Practice a few questions first.");
      return;
    }
    beginSession("review", shuffle(pool));
  }

  function beginSession(mode, queue) {
    state.mode = mode;
    state.queue = queue;
    state.index = 0;
    state.selected = null;
    state.revealed = false;
    state.sessionCorrect = 0;
    state.sessionWrong = 0;
    state.sessionMisses = [];
    renderQuestion();
  }

  function renderQuestion() {
    if (state.index >= state.queue.length) {
      finishSession();
      return;
    }

    showScreen("quiz");
    const q = state.queue[state.index];
    const total = state.queue.length;
    const current = state.index + 1;

    $("#quiz-progress-label").textContent = `Question ${current} of ${total}`;
    $("#quiz-mode-label").textContent =
      state.mode === "daily"
        ? "Daily drill"
        : state.mode === "review"
          ? "Wrong-answer review"
          : state.mode === "topic"
            ? q.topic
            : "Mixed practice";
    $("#progress-fill").style.width = `${((current - 1) / total) * 100}%`;
    $("#topic-chip").textContent = `${q.topic} · Level ${q.level} · ${q.difficulty}`;
    $("#stem").textContent = q.stem;

    const choices = $("#choices");
    choices.innerHTML = "";
    q.choices.forEach((text, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice";
      btn.dataset.index = String(i);
      btn.innerHTML = `<span class="choice-key">${KEYS[i]}</span><span>${text}</span>`;
      btn.addEventListener("click", () => selectChoice(i));
      choices.appendChild(btn);
    });

    $("#feedback").classList.add("hidden");
    $("#feedback").innerHTML = "";
    $("#quiz-actions").classList.add("hidden");
    state.selected = null;
    state.revealed = false;
  }

  function selectChoice(i) {
    if (state.revealed) return;
    state.selected = i;
    state.revealed = true;

    const q = state.queue[state.index];
    const correct = i === q.answer;

    $$(".choice").forEach((el) => {
      const idx = Number(el.dataset.index);
      el.disabled = true;
      if (idx === q.answer) el.classList.add("correct");
      if (idx === i && !correct) el.classList.add("wrong");
      if (idx === i) el.classList.add("selected");
    });

    recordAnswer(q, i, correct);

    const feedback = $("#feedback");
    feedback.classList.remove("hidden", "ok", "bad");
    feedback.classList.add(correct ? "ok" : "bad");
    feedback.innerHTML = `
      <div class="feedback-title ${correct ? "ok" : "bad"}">${correct ? "Correct" : "Not quite"}</div>
      <p>${q.explanation}</p>
      ${
        correct
          ? ""
          : `<p style="margin-top:10px"><strong>Correct answer:</strong> ${KEYS[q.answer]}. ${q.choices[q.answer]}</p>`
      }
    `;

    $("#quiz-actions").classList.remove("hidden");
    $("#btn-next").textContent = state.index + 1 >= state.queue.length ? "See results" : "Next question";
    $("#progress-fill").style.width = `${((state.index + 1) / state.queue.length) * 100}%`;
  }

  function recordAnswer(q, chosen, correct) {
    store.answered += 1;
    if (!store.topicStats[q.topic]) store.topicStats[q.topic] = { answered: 0, correct: 0 };
    store.topicStats[q.topic].answered += 1;

    if (correct) {
      state.sessionCorrect += 1;
      store.correct += 1;
      store.topicStats[q.topic].correct += 1;
      store.wrongIds = store.wrongIds.filter((id) => id !== q.id);
      delete store.wrongDetails[q.id];
    } else {
      state.sessionWrong += 1;
      state.sessionMisses.push({ id: q.id, chosen });
      if (!store.wrongIds.includes(q.id)) store.wrongIds.unshift(q.id);
      store.wrongDetails[q.id] = {
        chosen,
        at: Date.now(),
        topic: q.topic,
      };
    }

    if (state.mode === "daily" && state.index + 1 >= state.queue.length) {
      const today = todayKey();
      if (store.lastDailyDate !== today) {
        store.streak = store.lastDailyDate && isYesterday(store.lastDailyDate, today) ? store.streak + 1 : 1;
        store.lastDailyDate = today;
      }
    }

    saveStore();
  }

  function isYesterday(prev, today) {
    const [py, pm, pd] = prev.split("-").map(Number);
    const [ty, tm, td] = today.split("-").map(Number);
    const a = new Date(py, pm - 1, pd);
    const b = new Date(ty, tm - 1, td);
    return (b - a) / 86400000 === 1;
  }

  function finishSession() {
    showScreen("results");
    const total = state.sessionCorrect + state.sessionWrong;
    const pct = total ? Math.round((state.sessionCorrect / total) * 100) : 0;
    $("#result-score").textContent = `${pct}%`;
    $("#result-detail").textContent = `${state.sessionCorrect} correct · ${state.sessionWrong} missed · ${total} total`;
    $("#result-note").textContent =
      state.mode === "review"
        ? "Mastered items are cleared from your wrong-answer book when you get them right."
        : state.sessionWrong
          ? "Missed questions were saved to your Wrong-Answer Book for later review."
          : "Clean session — nothing added to the Wrong-Answer Book.";

    store.history.unshift({
      at: Date.now(),
      mode: state.mode,
      correct: state.sessionCorrect,
      wrong: state.sessionWrong,
    });
    store.history = store.history.slice(0, 30);
    saveStore();
  }

  function renderWrongBook() {
    showScreen("wrongbook");
    const root = $("#wrong-list");
    root.innerHTML = "";

    if (!store.wrongIds.length) {
      root.innerHTML = `<div class="empty"><h2>All clear</h2><p>No wrong answers saved. Keep practicing daily.</p></div>`;
      $("#btn-review-wrongs").classList.add("hidden");
      return;
    }

    $("#btn-review-wrongs").classList.remove("hidden");

    for (const id of store.wrongIds) {
      const q = byId(id);
      const detail = store.wrongDetails[id];
      if (!q) continue;
      const chosen = detail?.chosen ?? null;
      const el = document.createElement("article");
      el.className = "review-item";
      el.innerHTML = `
        <div class="review-meta">
          <span class="topic-chip" style="margin:0">${q.topic}</span>
          <span class="pill danger">Needs review</span>
        </div>
        <h3>${q.stem}</h3>
        ${
          chosen != null
            ? `<div class="your-answer"><strong>Your answer:</strong> ${KEYS[chosen]}. ${q.choices[chosen]}</div>`
            : ""
        }
        <div class="correct-answer"><strong>Correct:</strong> ${KEYS[q.answer]}. ${q.choices[q.answer]}</div>
        <div class="explain"><strong>Explanation:</strong> ${q.explanation}</div>
      `;
      root.appendChild(el);
    }
  }

  function renderProgress() {
    showScreen("progress");
    $("#prog-answered").textContent = String(store.answered);
    $("#prog-correct").textContent = String(store.correct);
    $("#prog-accuracy").textContent = `${accuracy()}%`;
    $("#prog-streak").textContent = String(store.streak);

    const topicRoot = $("#topic-stats");
    topicRoot.innerHTML = "";
    const entries = Object.entries(store.topicStats).sort((a, b) => a[0].localeCompare(b[0]));
    if (!entries.length) {
      topicRoot.innerHTML = `<p class="empty" style="padding:12px">Topic stats appear after you answer questions.</p>`;
      return;
    }
    for (const [topic, s] of entries) {
      const pct = s.answered ? Math.round((s.correct / s.answered) * 100) : 0;
      const row = document.createElement("button");
      row.type = "button";
      row.className = "topic-item";
      row.innerHTML = `<div><strong>${topic}</strong><span>${s.correct}/${s.answered} correct</span></div><span class="badge">${pct}%</span>`;
      row.addEventListener("click", () => startTopic(topic));
      topicRoot.appendChild(row);
    }
  }

  function clearWrongBook() {
    if (!confirm("Clear all items from the Wrong-Answer Book?")) return;
    store.wrongIds = [];
    store.wrongDetails = {};
    saveStore();
    renderWrongBook();
    renderHome();
  }

  function resetAll() {
    if (!confirm("Reset all progress, streak, and wrong answers on this device?")) return;
    store = defaultStore();
    saveStore();
    renderHome();
  }

  function bind() {
    $("#btn-back").addEventListener("click", () => {
      if (state.view === "quiz" && !confirm("Leave this session?")) return;
      renderHome();
    });

    $("#btn-daily").addEventListener("click", startDaily);
    $("#btn-mixed").addEventListener("click", () => startMixed(15));
    $("#btn-wrongbook").addEventListener("click", renderWrongBook);
    $("#btn-progress").addEventListener("click", renderProgress);
    $("#btn-next").addEventListener("click", () => {
      state.index += 1;
      renderQuestion();
    });
    $("#btn-results-home").addEventListener("click", renderHome);
    $("#btn-results-review").addEventListener("click", () => {
      if (state.sessionMisses.length) {
        const pool = state.sessionMisses.map((m) => byId(m.id)).filter(Boolean);
        beginSession("review", shuffle(pool));
      } else {
        renderWrongBook();
      }
    });
    $("#btn-review-wrongs").addEventListener("click", startWrongReview);
    $("#btn-clear-wrongs").addEventListener("click", clearWrongBook);
    $("#btn-reset").addEventListener("click", resetAll);
  }

  document.addEventListener("DOMContentLoaded", () => {
    bind();
    renderHome();
  });
})();
