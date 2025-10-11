const isTauri = typeof window !== "undefined" && !!window.__TAURI__;

const CONFIG = {
  basePath: isTauri ? "tentit/" : "../tentit/",
  get manifestPath() {
    return `${this.basePath}manifest.json`;
  },
};

const elements = {
  examSelect: document.querySelector("#exam-select"),
  questionCountInput: document.querySelector("#question-count"),
  startButton: document.querySelector("#start-btn"),
  status: document.querySelector("#status"),
  quizSection: document.querySelector("#quiz"),
  quizTitle: document.querySelector("#quiz-title"),
  progressLabel: document.querySelector("#progress-label"),
  scoreLabel: document.querySelector("#score-label"),
  questionText: document.querySelector("#question-text"),
  optionsList: document.querySelector("#options-list"),
  nextButton: document.querySelector("#next-btn"),
  resultsSection: document.querySelector("#results"),
  resultsSummary: document.querySelector("#results-summary"),
  restartButton: document.querySelector("#restart-btn"),
};

const state = {
  manifest: [],
  manifestLoaded: false,
  quiz: null,
  currentQuestionIndex: 0,
  score: 0,
  hasAnswered: false,
};

async function fetchManifest() {
  if (state.manifestLoaded) {
    return state.manifest;
  }

  const response = await fetch(CONFIG.manifestPath, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Tenttilistaa ei voitu ladata.");
  }

  const manifestData = await response.json();
  state.manifest = manifestData.map((entry) => ({
    ...entry,
    id: entry.id ?? entry.file.replace(/\.json$/i, ""),
    label: entry.label ?? entry.id ?? entry.file,
    file: entry.file,
  }));
  state.manifestLoaded = true;
  return state.manifest;
}

function populateExamSelect() {
  const previousValue = elements.examSelect.value;
  elements.examSelect.innerHTML = "";
  state.manifest.forEach((entry) => {
    const option = document.createElement("option");
    option.value = entry.id;
    option.textContent = entry.label;
    elements.examSelect.append(option);
  });

  if (!state.manifest.length) {
    elements.examSelect.value = "";
    return;
  }

  const hasPrevious = state.manifest.some((entry) => entry.id === previousValue);
  elements.examSelect.value = hasPrevious ? previousValue : state.manifest[0].id;
}

function buildAssetPath(file) {
  return `${CONFIG.basePath}${file}`;
}

async function loadQuiz(examId) {
  const manifest = await fetchManifest();
  const manifestEntry = manifest.find((entry) => entry.id === examId);
  if (!manifestEntry) {
    throw new Error(`Tenttiä ei löydy: ${examId}`);
  }

  const response = await fetch(buildAssetPath(manifestEntry.file), { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Tenttitiedostoa ei voitu hakea (${response.status})`);
  }

  const quizData = await response.json();
  if (!quizData || !Array.isArray(quizData.questions)) {
    throw new Error("Tenttitiedoston rakenne on virheellinen.");
  }

  return { manifestEntry, quizData };
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function determineQuestionSet(quizData) {
  const requestedCountRaw = elements.questionCountInput?.value.trim() ?? "";
  const total = quizData.questions.length;

  if (!requestedCountRaw) {
    return {
      questions: shuffle([...quizData.questions]),
      message: "",
    };
  }

  const requested = Number.parseInt(requestedCountRaw, 10);
  if (Number.isNaN(requested)) {
    return {
      questions: shuffle([...quizData.questions]),
      message: "Kysymysten määrän pitää olla numero. Käytetään kaikkia kysymyksiä.",
    };
  }

  const clamped = Math.max(1, Math.min(requested, total));
  const message =
    clamped !== requested
      ? `Kysymysten määrä rajattiin arvoon ${clamped}/${total}.`
      : "";

  if (clamped >= total) {
    return {
      questions: shuffle([...quizData.questions]),
      message,
    };
  }

  const selected = shuffle([...quizData.questions]).slice(0, clamped);
  return {
    questions: selected,
    message,
  };
}

function startQuiz(manifestEntry, quizData, questions) {
  state.quiz = {
    manifestEntry,
    title: quizData.TITLE ?? manifestEntry.label ?? "Monivalintatentti",
    questions,
  };
  state.currentQuestionIndex = 0;
  state.score = 0;
  state.hasAnswered = false;

  elements.quizTitle.textContent = state.quiz.title;
  elements.scoreLabel.textContent = "Pisteet: 0";
  elements.progressLabel.textContent = "";

  elements.quizSection.classList.remove("hidden");
  elements.resultsSection.classList.add("hidden");
  elements.nextButton.classList.add("hidden");

  renderQuestion();
}

function renderQuestion() {
  const question = state.quiz.questions[state.currentQuestionIndex];
  if (!question) {
    showResults();
    return;
  }

  state.hasAnswered = false;
  elements.progressLabel.textContent = `Kysymys ${state.currentQuestionIndex + 1}/${state.quiz.questions.length}`;
  elements.questionText.textContent = question.question;
  elements.optionsList.innerHTML = "";

  question.options.forEach((optionText, index) => {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "option";
    button.textContent = optionText;
    button.dataset.index = index.toString();
    button.addEventListener("click", () => handleAnswer(button, question));
    li.append(button);
    elements.optionsList.append(li);
  });
}

function handleAnswer(button, question) {
  if (state.hasAnswered) {
    return;
  }
  state.hasAnswered = true;

  const selectedAnswer = button.textContent ?? "";
  const isCorrect = selectedAnswer === question.correct;

  if (isCorrect) {
    state.score += 1;
    button.classList.add("correct");
  } else {
    button.classList.add("incorrect");
    for (const optionButton of elements.optionsList.querySelectorAll("button")) {
      if (optionButton.textContent === question.correct) {
        optionButton.classList.add("correct");
        break;
      }
    }
  }

  elements.scoreLabel.textContent = `Pisteet: ${state.score}`;
  elements.nextButton.classList.remove("hidden");

  for (const optionButton of elements.optionsList.querySelectorAll("button")) {
    optionButton.disabled = true;
  }
}

function nextQuestion() {
  if (!state.quiz) {
    return;
  }

  state.currentQuestionIndex += 1;
  if (state.currentQuestionIndex >= state.quiz.questions.length) {
    showResults();
    return;
  }

  elements.nextButton.classList.add("hidden");
  renderQuestion();
}

function showResults() {
  const total = state.quiz?.questions.length ?? 0;
  elements.quizSection.classList.add("hidden");
  elements.resultsSection.classList.remove("hidden");
  elements.resultsSummary.textContent = `Sait ${state.score}/${total} pistettä.`;
}

function resetUI() {
  elements.quizSection.classList.add("hidden");
  elements.resultsSection.classList.add("hidden");
  elements.nextButton.classList.add("hidden");
  elements.optionsList.innerHTML = "";
  elements.questionText.textContent = "";
  elements.progressLabel.textContent = "";
  elements.scoreLabel.textContent = "";
}

function setLoading(isLoading, message = "") {
  elements.startButton.disabled = isLoading;
  elements.status.textContent = message;
}

elements.startButton.addEventListener("click", async () => {
  const selectedExam = elements.examSelect.value;
  if (!selectedExam) {
    elements.status.textContent = "Valitse tentti ennen aloittamista.";
    return;
  }

  resetUI();
  setLoading(true, "Ladataan tenttiä...");
  try {
    const { manifestEntry, quizData } = await loadQuiz(selectedExam);
    const { questions, message } = determineQuestionSet(quizData);
    startQuiz(manifestEntry, quizData, questions);
    elements.status.textContent = message ?? "";
  } catch (error) {
    console.error(error);
    elements.status.textContent =
      error instanceof Error ? error.message : "Tuntematon virhe tenttiä ladattaessa.";
  } finally {
    setLoading(false);
  }
});

elements.nextButton.addEventListener("click", () => {
  nextQuestion();
});

elements.restartButton.addEventListener("click", async () => {
  const activeExamId = state.quiz?.manifestEntry?.id;
  if (!activeExamId) {
    return;
  }

  resetUI();
  setLoading(true, "Käynnistetään tenttiä uudelleen...");
  try {
    const { manifestEntry, quizData } = await loadQuiz(activeExamId);
    const { questions, message } = determineQuestionSet(quizData);
    startQuiz(manifestEntry, quizData, questions);
    elements.status.textContent = message ?? "";
  } catch (error) {
    console.error(error);
    elements.status.textContent =
      error instanceof Error ? error.message : "Tenttiä ei voitu käynnistää uudelleen.";
  } finally {
    setLoading(false);
  }
});

async function initialize() {
  setLoading(true, "Ladataan tenttilistaa...");
  try {
    await fetchManifest();
    populateExamSelect();
    elements.status.textContent = "";
  } catch (error) {
    console.error(error);
    elements.status.textContent =
      error instanceof Error ? error.message : "Tenttilistan lataus epäonnistui.";
  } finally {
    setLoading(false);
  }
}

initialize();
