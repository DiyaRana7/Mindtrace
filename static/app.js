"use strict";

const home = document.getElementById("home");
const quizScreen = document.getElementById("quiz");
const challengeScreen = document.getElementById("challenge");
const reportScreen = document.getElementById("results");
const toast = document.getElementById("toast");
let questions = [];
let answers = [];
let current = 0;
let challengeQuestions = [];
let challengeAnswers = [];
let challengeCurrent = 0;
let result = null;
let timer;

function notify(text) {
  toast.textContent = text;
  toast.classList.add("visible");
  clearTimeout(timer);
  timer = setTimeout(() => toast.classList.remove("visible"), 2700);
}

function show(name) {
  home.classList.toggle("hidden", name !== "home");
  quizScreen.classList.toggle("hidden", name !== "quiz");
  challengeScreen.classList.toggle("hidden", name !== "challenge");
  reportScreen.classList.toggle("hidden", name !== "results");
  const step = name === "results" ? 2 : name === "challenge" ? 1 : 0;
  document.querySelectorAll(".top-step").forEach((indicator, index) => {
    indicator.classList.toggle("active", index === step);
    indicator.classList.toggle("complete", index < step);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function begin() {
  const button = document.getElementById("start-button");
  button.disabled = true;
  try {
    const response = await fetch("/api/quiz", { cache: "no-store" });
    if (!response.ok) throw new Error("Assessment could not start. Please try again.");
    questions = (await response.json()).questions;
    answers = Array(questions.length).fill(null);
    challengeAnswers = [];
    challengeQuestions = [];
    current = 0;
    renderQuestion();
    show("quiz");
  } catch (error) { notify(error.message); }
  finally { button.disabled = false; }
}

function renderQuestion() {
  const question = questions[current];
  document.getElementById("quiz-counter").textContent = `${String(current + 1).padStart(2, "0")} / ${questions.length}`;
  document.getElementById("progress-fill").style.width = `${(current + 1) / questions.length * 100}%`;
  document.getElementById("question-category").textContent = `🧭 DEEP PERSONALITY · ${question.category}`;
  document.getElementById("question-title").textContent = question.text;
  document.getElementById("answers").replaceChildren(...question.answers.map((answer, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "answer-option";
    button.setAttribute("aria-label", `Option ${String.fromCharCode(65 + index)}: ${answer}`);
    const letter = document.createElement("span");
    letter.className = "answer-letter";
    letter.textContent = String.fromCharCode(65 + index);
    const copy = document.createElement("span");
    copy.className = "answer-copy";
    copy.textContent = answer;
    button.append(letter, copy);
    button.addEventListener("click", () => selectAnswer(index));
    return button;
  }));
  const back = document.getElementById("home-link");
  back.classList.toggle("disabled", current === 0);
  back.setAttribute("aria-disabled", String(current === 0));
  document.querySelector(".question-content").style.animation = "none";
  requestAnimationFrame(() => { document.querySelector(".question-content").style.animation = ""; });
}

function selectAnswer(index) {
  if (answers[current] !== null) return;
  answers[current] = index;
  const answeredQuestion = current;
  const choices = [...document.querySelectorAll(".answer-option")];
  choices.forEach((choice, choiceIndex) => {
    choice.disabled = true;
    choice.classList.toggle("selected", choiceIndex === index);
  });
  setTimeout(() => {
    if (current !== answeredQuestion) return;
    if (current === questions.length - 1) startChallenge();
    else { current += 1; renderQuestion(); }
  }, 220);
}

async function startChallenge() {
  try {
    const response = await fetch("/api/challenge", { cache: "no-store" });
    if (!response.ok) throw new Error("The First Instinct Challenge could not start.");
    challengeQuestions = (await response.json()).questions;
    challengeAnswers = Array(challengeQuestions.length).fill(null);
    challengeCurrent = 0;
    renderChallenge();
    show("challenge");
  } catch (error) { show("quiz"); notify(error.message); }
}

function renderChallenge() {
  const question = challengeQuestions[challengeCurrent];
  document.getElementById("challenge-counter").textContent = `${String(challengeCurrent + 1).padStart(2, "0")} / ${challengeQuestions.length}`;
  document.getElementById("challenge-progress").style.width = `${(challengeCurrent + 1) / challengeQuestions.length * 100}%`;
  document.getElementById("challenge-title").textContent = question.text;
  document.getElementById("challenge-answers").replaceChildren(...question.answers.map((answer, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "answer-option instinct-option";
    button.setAttribute("aria-label", `Option ${String.fromCharCode(65 + index)}: ${answer}`);
    const letter = document.createElement("span");
    letter.className = "answer-letter";
    letter.textContent = String.fromCharCode(65 + index);
    const copy = document.createElement("span");
    copy.className = "answer-copy";
    copy.textContent = answer;
    button.append(letter, copy);
    button.addEventListener("click", () => selectInstinct(index));
    return button;
  }));
}

function selectInstinct(index) {
  if (challengeAnswers[challengeCurrent] !== null) return;
  challengeAnswers[challengeCurrent] = index;
  const answeredQuestion = challengeCurrent;
  document.querySelectorAll(".instinct-option").forEach((choice, choiceIndex) => {
    choice.disabled = true;
    choice.classList.toggle("selected", choiceIndex === index);
  });
  setTimeout(() => {
    if (challengeCurrent !== answeredQuestion) return;
    if (challengeCurrent === challengeQuestions.length - 1) finish();
    else { challengeCurrent += 1; renderChallenge(); }
  }, 220);
}

async function finish() {
  show("home");
  const loading = document.getElementById("start-button");
  const previous = loading.textContent;
  loading.textContent = "Preparing your personal reflection…";
  loading.disabled = true;
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answers, challengeAnswers }), cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || "Your report could not be prepared.");
    result = data;
    renderReport(data);
    show("results");
  } catch (error) { show("quiz"); notify(error.message); }
  finally { loading.textContent = previous; loading.disabled = false; }
}

function renderReport(data) {
  document.getElementById("report-intro").textContent = data.profile.description;
  document.getElementById("profile-badge").textContent = `✨ ${data.profile.name} · ${data.profile.tagline}`;
  const traits = document.getElementById("trait-list");
  traits.replaceChildren(...data.traits.map((trait) => {
    const row = document.createElement("div");
    row.className = "trait-row";
    const heading = document.createElement("div");
    heading.className = "trait-heading";
    const label = document.createElement("strong");
    const traitIcons = { ambition: "🎯", connection: "💙", authenticity: "🌟", curiosity: "🔎", resilience: "🧭" };
    label.textContent = `${traitIcons[trait.key] || "✦"}  ${trait.name}`;
    const score = document.createElement("span");
    score.textContent = `${trait.score}%`;
    heading.append(label, score);
    const track = document.createElement("div");
    track.className = "trait-track";
    track.setAttribute("role", "meter");
    track.setAttribute("aria-label", trait.name);
    track.setAttribute("aria-valuemin", "0");
    track.setAttribute("aria-valuemax", "100");
    track.setAttribute("aria-valuenow", String(trait.score));
    const fill = document.createElement("div");
    fill.className = "trait-fill";
    fill.style.width = `${trait.score}%`;
    fill.style.backgroundColor = trait.color;
    track.append(fill);
    const hint = document.createElement("div");
    hint.className = "trait-hint";
    hint.textContent = trait.score >= 65 ? trait.high : trait.score <= 35 ? trait.low : `${trait.low}  ·  ${trait.high}`;
    row.append(heading, track, hint);
    return row;
  }));
  document.getElementById("insights").replaceChildren(...data.insights.map((item) => {
    const card = document.createElement("article");
    card.className = "insight-card";
    const title = document.createElement("h3"); title.textContent = `💡 ${item.title}`;
    const copy = document.createElement("p"); copy.textContent = item.copy;
    card.append(title, copy);
    return card;
  }));
  document.getElementById("hobbies").replaceChildren(...data.hobbies.map((item) => {
    const card = document.createElement("article");
    card.className = "hobby-card";
    const title = document.createElement("strong"); title.textContent = `🌱 ${item.title}`;
    const copy = document.createElement("p"); copy.textContent = item.copy;
    card.append(title, copy);
    return card;
  }));
  document.getElementById("reflection").textContent = data.reflection;
}

async function downloadReport() {
  const button = document.getElementById("download-button");
  button.disabled = true;
  try {
    const response = await fetch("/api/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ answers, challengeAnswers }), cache: "no-store" });
    if (!response.ok) throw new Error("The report could not be downloaded.");
    const link = document.createElement("a");
    link.href = URL.createObjectURL(await response.blob());
    link.download = "personality-detective-report.html";
    link.click();
    URL.revokeObjectURL(link.href);
    notify("Your personal report is ready to open or print.");
  } catch (error) { notify(error.message); }
  finally { button.disabled = false; }
}

document.getElementById("start-button").addEventListener("click", begin);
document.getElementById("home-link").addEventListener("click", (event) => {
  event.preventDefault();
  if (current === 0) show("home");
  else { current -= 1; answers[current] = null; renderQuestion(); }
});
document.getElementById("challenge-back").addEventListener("click", (event) => {
  event.preventDefault();
  current = questions.length - 1;
  answers[current] = null;
  renderQuestion();
  show("quiz");
});
document.getElementById("download-button").addEventListener("click", downloadReport);
document.getElementById("restart-button").addEventListener("click", () => { result = null; show("home"); });
document.addEventListener("keydown", (event) => {
  if (quizScreen.classList.contains("hidden") || event.altKey || event.ctrlKey || event.metaKey) return;
  if (/^[1-4]$/.test(event.key)) { event.preventDefault(); selectAnswer(Number(event.key) - 1); }
  if (event.key === "ArrowLeft" && current > 0) { current -= 1; answers[current] = null; renderQuestion(); }
});
document.addEventListener("keydown", (event) => {
  if (challengeScreen.classList.contains("hidden") || event.altKey || event.ctrlKey || event.metaKey) return;
  if (/^[1-2]$/.test(event.key)) { event.preventDefault(); selectInstinct(Number(event.key) - 1); }
  if (event.key === "ArrowLeft" && challengeCurrent > 0) { challengeCurrent -= 1; challengeAnswers[challengeCurrent] = null; renderChallenge(); }
});
