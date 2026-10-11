const API_BASE = `http://${location.hostname || "127.0.0.1"}:8000`;
const DEMO_TOKEN = "demo-learner-one";
const app = document.querySelector("#app");
const drafts = new Map();

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${DEMO_TOKEN}`,
      ...(options.body ? { "Content-Type": "application/json" } : {}),
    },
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error?.message || "Не удалось связаться с сервером.");
  return body;
}

function supported(block) {
  return block?.schemaVersion === 1 &&
    ["intro", "vocabulary", "exercise", "summary"].includes(block.blockType) &&
    (block.blockType !== "exercise" || ["single_choice", "fill_blanks"].includes(block.activityType));
}

function renderError(error) {
  app.replaceChildren();
  const panel = node("div", "error-panel");
  panel.append(node("p", "eyebrow", "НЕ УДАЛОСЬ ОТКРЫТЬ УРОК"));
  panel.append(node("h1", "error-title", "Связь с уроком потерялась"));
  panel.append(node("p", "muted", error.message));
  panel.append(node("p", "muted", "Запусти сервер бекенда и обнови страницу."));
  const button = node("button", "button button-primary", "Попробовать снова");
  button.addEventListener("click", load);
  panel.append(button);
  app.append(panel);
}

function renderSidebar(lesson, progress) {
  const aside = node("aside", "lesson-sidebar");
  const head = node("div", "sidebar-head");
  head.append(node("span", "sidebar-kicker", "ТВОЙ МАРШРУТ"));
  head.append(node("h2", "sidebar-title", "Урок 01"));
  aside.append(head);

  const exercises = lesson.blocks.filter((block) => block.blockType === "exercise");
  const finished = exercises.filter((exercise) => {
    const state = progress.exercises[exercise.id];
    return state?.completed || state?.lastResult?.attemptsRemaining === 0;
  }).length;
  const summary = node("div", "sidebar-progress");
  const row = node("div", "progress-row");
  row.append(node("span", "progress-label", "Прогресс"));
  row.append(node("span", "progress-count", `${finished} из ${exercises.length}`));
  summary.append(row);
  const track = node("div", "progress-track");
  const fill = node("div", "progress-fill");
  fill.style.width = `${exercises.length ? finished / exercises.length * 100 : 0}%`;
  track.append(fill);
  summary.append(track);
  aside.append(summary);

  const nav = node("nav", "lesson-nav");
  nav.setAttribute("aria-label", "Разделы урока");
  const entries = [
    ["#learn", "01", "Новые слова", "Читаем и запоминаем", true],
    ...exercises.map((exercise, index) => {
      const state = progress.exercises[exercise.id];
      return [`#${exercise.id}`, `0${index + 2}`, index === 0 ? "Выбери ответ" : "Напиши ответ", "Проверяем себя", Boolean(state?.attemptsUsed)];
    }),
  ];
  for (const [href, number, title, caption, active] of entries) {
    const link = node("a", `nav-link${active ? " nav-link-active" : ""}`);
    link.href = href;
    link.append(node("span", "nav-number", number));
    const labels = node("span", "nav-labels");
    labels.append(node("strong", "", title), node("small", "", caption));
    link.append(labels);
    nav.append(link);
  }
  aside.append(nav);

  const note = node("div", "sidebar-note");
  note.append(node("span", "sidebar-note-icon", "✦"));
  note.append(node("p", "", "Ошибаться здесь можно. Количество попыток указано в каждом задании."));
  aside.append(note);
  return aside;
}

function renderHero(lesson) {
  const hero = node("section", "hero");
  const copy = node("div", "hero-copy");
  const eyebrow = node("div", "hero-eyebrow");
  eyebrow.append(node("span", "eyebrow-line"), node("span", "", `ЭСТОНСКИЙ · ${lesson.level} · ${lesson.estimatedMinutes} МИН`));
  copy.append(eyebrow);
  copy.append(node("h1", "hero-title", lesson.title));
  copy.append(node("p", "hero-subtitle", lesson.subtitle));
  const tags = node("div", "hero-tags");
  tags.append(node("span", "tag", "4 новых слова"), node("span", "tag", "2 задания"));
  copy.append(tags);
  hero.append(copy);
  const art = node("div", "hero-art");
  art.setAttribute("aria-hidden", "true");
  art.append(node("div", "art-circle circle-one"), node("div", "art-circle circle-two"));
  const bubble = node("div", "art-bubble");
  bubble.append(node("span", "bubble-small", "сегодня говорим"), node("strong", "", "Tere!"), node("span", "bubble-underline", ""));
  art.append(bubble);
  art.append(node("span", "art-star star-one", "✳"), node("span", "art-star star-two", "✦"));
  hero.append(art);
  return hero;
}

function renderIntro(block) {
  const section = node("section", "learn-section");
  section.id = "learn";
  section.append(node("p", "eyebrow", block.content.eyebrow));
  section.append(node("h2", "section-title", block.content.title));
  section.append(node("p", "section-description", block.content.body));
  return section;
}

function renderVocabulary(block) {
  const grid = node("div", "vocab-grid");
  for (const [index, item] of block.content.items.entries()) {
    const card = node("div", "vocab-card");
    card.append(node("span", "vocab-number", String(index + 1).padStart(2, "0")));
    card.append(node("strong", "vocab-term", item.term));
    card.append(node("span", "vocab-translation", item.translation));
    grid.append(card);
  }
  return grid;
}

function renderResult(result) {
  const panel = node("div", `result-panel result-${result.status}`);
  panel.setAttribute("role", "status");
  const title = result.status === "correct" ? "Отлично, всё верно!" : result.status === "partial" ? "Почти получилось" : "Давай попробуем ещё";
  panel.append(node("strong", "result-title", title));
  const list = node("div", "result-items");
  for (const item of result.items) {
    const row = node("div", "result-item");
    row.append(node("span", `result-icon ${item.status}`, item.status === "correct" ? "✓" : "↻"));
    const text = node("span", "result-item-copy", item.feedback);
    if (Object.hasOwn(item, "correctAnswer")) {
      text.append(node("span", "revealed-answer", ` Ответ: ${item.correctAnswer}`));
    }
    row.append(text);
    list.append(row);
  }
  panel.append(list);
  if (result.attemptsRemaining > 0) panel.append(node("p", "result-foot", `Осталась ${result.attemptsRemaining} попытка.`));
  return panel;
}

function renderExercise(block, index, state, onSubmitted) {
  const section = node("section", "exercise-card");
  section.id = block.id;
  const top = node("div", "exercise-top");
  const number = node("span", "exercise-number", `ЗАДАНИЕ 0${index + 1}`);
  const kind = node("span", "exercise-kind", block.activityType === "single_choice" ? "ВЫБЕРИ ОТВЕТ" : "НАПИШИ ОТВЕТ");
  top.append(number, kind);
  section.append(top);
  section.append(node("h2", "exercise-title", block.prompt));
  section.append(node("p", "exercise-help", block.activityType === "single_choice" ? "Выбери один вариант и проверь себя." : "Впиши перевод для каждой фразы."));

  const form = node("form", "exercise-form");
  const draft = drafts.get(block.id) || {};
  const locked = Boolean(state?.completed || state?.lastResult?.attemptsRemaining === 0);
  if (block.activityType === "single_choice") {
    const item = block.items[0];
    const options = node("fieldset", "options-list");
    options.append(node("legend", "visually-hidden", block.prompt));
    for (const option of item.options) {
      const label = node("label", "option-label");
      const input = node("input", "option-input");
      input.type = "radio";
      input.name = item.id;
      input.value = option.id;
      input.checked = draft[item.id] === option.id;
      input.disabled = locked;
      label.append(input, node("span", "option-radio"), node("span", "option-text", option.label));
      options.append(label);
    }
    form.append(options);
  } else {
    const fields = node("div", "blank-list");
    for (const [itemIndex, item] of block.items.entries()) {
      const row = node("label", "blank-row");
      row.append(node("span", "blank-number", String(itemIndex + 1).padStart(2, "0")));
      const body = node("span", "blank-body");
      body.append(node("span", "blank-label", item.label));
      const input = node("input", "blank-input");
      input.type = "text";
      input.name = item.id;
      input.placeholder = item.placeholder;
      input.autocomplete = "off";
      input.maxLength = 200;
      input.required = true;
      input.value = draft[item.id] || "";
      input.disabled = locked;
      body.append(input);
      row.append(body);
      fields.append(row);
    }
    form.append(fields);
  }

  const disclosure = node("div", "exercise-disclosure");
  disclosure.append(node("span", "disclosure-icon", "i"));
  disclosure.append(node("span", "", block.gradingDisclosure.equivalentAnswersMayBeAccepted ? "Возможны несколько правильных вариантов ответа." : "Проверим выбранный вариант сразу после отправки."));
  form.append(disclosure);
  const controls = node("div", "exercise-controls");
  const button = node("button", "button button-primary", locked ? "Задание завершено" : state?.attemptsUsed ? "Проверить ещё раз" : "Проверить ответ");
  button.type = "submit";
  button.disabled = locked;
  controls.append(button, node("span", "attempt-counter", `${state?.attemptsUsed || 0} / ${block.feedbackPolicy.maxAttempts} попытки`));
  form.append(controls);
  const error = node("p", "form-error");
  error.setAttribute("role", "alert");
  form.append(error);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (locked) return;
    const responses = {};
    for (const item of block.items) {
      const input = form.elements.namedItem(item.id);
      responses[item.id] = block.activityType === "single_choice" ? input.value : input.value;
    }
    if (Object.values(responses).some((value) => !value)) {
      error.textContent = "Заполни все ответы перед проверкой.";
      return;
    }
    drafts.set(block.id, responses);
    button.disabled = true;
    button.textContent = "Проверяем…";
    error.textContent = "";
    try {
      const result = await api("/api/v1/attempts", {
        method: "POST",
        body: JSON.stringify({
          exerciseId: block.id,
          exerciseVersion: block.exerciseVersion,
          responses,
          idempotencyKey: crypto.randomUUID(),
        }),
      });
      await onSubmitted(block.id, result);
    } catch (failure) {
      error.textContent = failure.message;
      button.disabled = false;
      button.textContent = "Проверить ответ";
    }
  });
  section.append(form);
  if (state?.lastResult) section.append(renderResult(state.lastResult));
  return section;
}

function renderSummary(block, progress, lesson) {
  const section = node("section", "summary-card");
  const exercises = lesson.blocks.filter((entry) => entry.blockType === "exercise");
  const finished = exercises.every((entry) => {
    const state = progress.exercises[entry.id];
    return state?.completed || state?.lastResult?.attemptsRemaining === 0;
  });
  section.append(node("span", "summary-spark", "✳"));
  const copy = node("div", "summary-copy");
  copy.append(node("p", "eyebrow", finished ? "УРОК ПРОЙДЕН" : "ВПЕРЕДИ ЕЩЁ НЕМНОГО"));
  copy.append(node("h2", "", block.content.title));
  copy.append(node("p", "", block.content.body));
  section.append(copy);
  return section;
}

function render(lesson, progress) {
  app.replaceChildren();
  const layout = node("div", "layout");
  layout.append(renderSidebar(lesson, progress));
  const main = node("main", "lesson-main");
  main.append(renderHero(lesson));
  let exerciseIndex = 0;
  for (const block of lesson.blocks) {
    if (!supported(block)) {
      const fallback = node("div", "unsupported-block", "Этот блок пока не поддерживается в демоверсии.");
      main.append(fallback);
      continue;
    }
    if (block.blockType === "intro") main.append(renderIntro(block));
    if (block.blockType === "vocabulary") main.append(renderVocabulary(block));
    if (block.blockType === "exercise") {
      exerciseIndex += 1;
      main.append(renderExercise(block, exerciseIndex, progress.exercises[block.id], async (id, result) => {
        progress.exercises[id] = {
          attemptsUsed: result.attemptsUsed,
          completed: result.status === "correct",
          lastResult: result,
        };
        const y = document.getElementById(id)?.getBoundingClientRect().top || 0;
        render(lesson, progress);
        window.scrollBy(0, (document.getElementById(id)?.getBoundingClientRect().top || 0) - y);
      }));
    }
    if (block.blockType === "summary") main.append(renderSummary(block, progress, lesson));
  }
  const reset = node("button", "reset-button", "Начать демо заново ↗");
  reset.type = "button";
  reset.addEventListener("click", async () => {
    reset.disabled = true;
    try {
      await api("/api/v1/demo/reset", { method: "POST" });
      drafts.clear();
      await load();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
      reset.textContent = error.message;
      reset.disabled = false;
    }
  });
  main.append(reset);
  layout.append(main);
  app.append(layout);
}

async function load() {
  try {
    const [lesson, progress] = await Promise.all([
      api("/api/v1/lessons/estonian-first-words"),
      api("/api/v1/progress"),
    ]);
    if (lesson.schemaVersion !== 1 || progress.schemaVersion !== 1) throw new Error("Эта версия урока пока не поддерживается.");
    render(lesson, progress);
  } catch (error) {
    renderError(error);
  }
}

load();
