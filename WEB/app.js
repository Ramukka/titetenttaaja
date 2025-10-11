const QUIZ_MANIFEST = [
  {
    id: "tietoliikenne",
    label: "Tietoliikenne",
    path: "../tentit/tietoliikenne.json",
  },
];

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
  quiz: null,
  currentQuestionIndex: 0,
  score: 0,
  hasAnswered: false,
};

const cache = new Map();

function populateExamSelect() {
  if (!elements.examSelect) {
    console.error("exam-select element puuttuu DOMista.");
    return;
  }

  elements.examSelect.innerHTML = "";
  QUIZ_MANIFEST.forEach(({ id, label }) => {
    const option = document.createElement("option");
    option.value = id;
    option.textContent = label;
    elements.examSelect.append(option);
  });
}

async function loadQuiz(examId) {
  const manifestEntry = QUIZ_MANIFEST.find((entry) => entry.id === examId);
  if (!manifestEntry) {
    throw new Error(`Tuntematon tentti: ${examId}`);
  }

  if (cache.has(examId)) {
    return cache.get(examId);
  }

  const response = await fetch(manifestEntry.path);
  if (!response.ok) {
    throw new Error(`Tenttitiedostoa ei voitu hakea (${response.status})`);
  }

  const data = await response.json();
  if (!data || !Array.isArray(data.questions)) {
    throw new Error("Tenttitiedoston rakenne on virheellinen");
  }

  cache.set(examId, data);
  return data;
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function cloneQuestionsWithShuffledOptions(questions) {
  return questions.map((question) => ({
    ...question,
    options: shuffle([...question.options]),
  }));
}

function determineQuestionSet(quiz) {
  const requestedCountRaw = elements.questionCountInput?.value.trim();
  const total = quiz.questions.length;

  if (!requestedCountRaw) {
    return {
      questions: cloneQuestionsWithShuffledOptions([...quiz.questions]),
      message: "",
    };
  }

  const requested = Number.parseInt(requestedCountRaw, 10);
  if (Number.isNaN(requested)) {
    return {
      questions: cloneQuestionsWithShuffledOptions([...quiz.questions]),
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
      questions: cloneQuestionsWithShuffledOptions([...quiz.questions]),
      message,
    };
  }

  const shuffledQuestions = shuffle([...quiz.questions]);
  const selectedQuestions = shuffledQuestions.slice(0, clamped);

  return {
    questions: cloneQuestionsWithShuffledOptions(selectedQuestions),
    message,
  };
}

function startQuiz(quiz, questions) {
  state.quiz = {
    TITLE: quiz.TITLE,
    questions,
  };
  state.currentQuestionIndex = 0;
  state.score = 0;

  elements.quizTitle.textContent = quiz.TITLE ?? "Monivalintatentti";
  elements.scoreLabel.textContent = "Pisteet: 0";

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
  elements.status.textContent = "";
  elements.quizSection.classList.add("hidden");
  elements.resultsSection.classList.add("hidden");
  elements.nextButton.classList.add("hidden");
  elements.optionsList.innerHTML = "";
  elements.questionText.textContent = "";
  elements.progressLabel.textContent = "";
  elements.scoreLabel.textContent = "";
}

function setLoading(isLoading, message) {
  elements.startButton.disabled = isLoading;
  if (typeof message === "string") {
    elements.status.textContent = message;
  }
}

elements.startButton.addEventListener("click", async () => {
  const selectedExam = elements.examSelect.value;
  resetUI();
  setLoading(true, "Ladataan tenttiä...");
  try {
    const quiz = await loadQuiz(selectedExam);
    const { questions, message } = determineQuestionSet(quiz);
    startQuiz(quiz, questions);
    elements.status.textContent = message;
  } catch (error) {
    console.error(error);
    elements.status.textContent = error instanceof Error ? error.message : "Tuntematon virhe";
  } finally {
    setLoading(false);
  }
});

elements.nextButton.addEventListener("click", () => {
  nextQuestion();
});

elements.restartButton.addEventListener("click", async () => {
  const selectedExam = elements.examSelect.value;
  if (!selectedExam) {
    return;
  }

  elements.resultsSection.classList.add("hidden");
  try {
    let quiz = cache.get(selectedExam);
    if (!quiz) {
      setLoading(true, "Ladataan tenttiä...");
      quiz = await loadQuiz(selectedExam);
    }
    const { questions, message } = determineQuestionSet(quiz);
    startQuiz(quiz, questions);
    elements.status.textContent = message;
  } catch (error) {
    console.error(error);
    elements.status.textContent = error instanceof Error ? error.message : "Tuntematon virhe";
  } finally {
    setLoading(false);
  }
});

populateExamSelect();
