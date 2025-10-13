const CONFIG = {
  manifestPath: "./tentit/manifest.json",
  basePath: "./tentit/",
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

const resolveAssetUrl = async (relativePath) => relativePath;

const CATEGORY_FALLBACK_KEY = "muut";
const CATEGORY_DISPLAY_NAMES = {
  fysiikka: "Fysiikka",
  ohjelmointi: "Ohjelmointi",
  tietotekniikka: "Tietotekniikka",
  [CATEGORY_FALLBACK_KEY]: "Muut",
};
const CATEGORY_KEY_ORDER = ["fysiikka", "ohjelmointi", "tietotekniikka", CATEGORY_FALLBACK_KEY];

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
    title: entry.title ?? entry.label ?? entry.id ?? entry.file,
    file: entry.file,
  }));
  state.manifestLoaded = true;
  return state.manifest;
}

function populateExamSelect() {
  const select = elements.examSelect;
  const manifest = state.manifest;
  select.innerHTML = "";

  const grouped = new Map();
  manifest.forEach((exam) => {
    const rawCategory = typeof exam.category === "string" ? exam.category.trim() : "";
    const categoryKey = rawCategory ? rawCategory.toLowerCase() : CATEGORY_FALLBACK_KEY;
    const displayName =
      CATEGORY_DISPLAY_NAMES[categoryKey] ?? (rawCategory || CATEGORY_DISPLAY_NAMES[CATEGORY_FALLBACK_KEY]);

    if (!grouped.has(categoryKey)) {
      grouped.set(categoryKey, { displayName, exams: [] });
    }
    const group = grouped.get(categoryKey);
    if (rawCategory && !CATEGORY_DISPLAY_NAMES[categoryKey]) {
      group.displayName = rawCategory;
    }
    group.exams.push(exam);
  });

  const orderedKeys = [
    ...CATEGORY_KEY_ORDER.filter((key) => grouped.has(key)),
    ...[...grouped.keys()]
      .filter((key) => !CATEGORY_KEY_ORDER.includes(key))
      .sort((a, b) =>
        grouped.get(a).displayName.localeCompare(
          grouped.get(b).displayName, 
          "fi", { sensitivity: "base" },
        ),
      ),
  ];

  orderedKeys.forEach((key) => {
    const group = grouped.get(key);
    if (!group) {
      return;
    }

    group.exams.sort((a, b) => (a.title ?? "").localeCompare(b.title ?? "", "fi", { sensitivity: "base" }));

    const headerOption = document.createElement("option");
    headerOption.textContent = `— ${group.displayName} —`;
    headerOption.disabled = true;
    headerOption.value = "";
    headerOption.dataset.category = key;
    select.append(headerOption);

    group.exams.forEach((exam) => {
      const option = document.createElement("option");
      option.value = exam.id;
      option.textContent = `  ${exam.title ?? exam.id}`;
      option.dataset.category = key;
      select.append(option);
    });
  });
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

  const assetUrl = await resolveAssetUrl(buildAssetPath(manifestEntry.file));
  const response = await fetch(assetUrl, { cache: "no-store" });
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

function cloneQuestionWithShuffledOptions(question) {
  const options = Array.isArray(question.options) ? [...question.options] : [];
  return {
    ...question,
    options: shuffle(options),
  };
}

function determineQuestionSet(quizData) {
  const requestedCountRaw = elements.questionCountInput?.value.trim() ?? "";
  const total = quizData.questions.length;

  if (!requestedCountRaw) {
    return {
      questions: shuffle([...quizData.questions]).map(cloneQuestionWithShuffledOptions),
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
      questions: shuffle([...quizData.questions]).map(cloneQuestionWithShuffledOptions),
      message,
    };
  }

  const selected = shuffle([...quizData.questions])
    .slice(0, clamped)
    .map(cloneQuestionWithShuffledOptions);
  return {
    questions: selected,
    message,
  };
}

function startQuiz(manifestEntry, quizData, questions) {
  state.quiz = {
    manifestEntry,
    title: quizData.TITLE ?? manifestEntry.title ?? "Monivalintatentti",
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
