const practiceRoot = document.querySelector("#practiceApp");
const practiceQuestionsNode = document.querySelector("#practiceQuestions");

if (practiceRoot && practiceQuestionsNode) {
  const questions = JSON.parse(practiceQuestionsNode.textContent);
  const promptText = document.querySelector("#promptText");
  const promptHeading = document.querySelector(".prompt-heading");
  const promptSymbols = document.querySelector("#promptSymbols");
  const replayButton = document.querySelector("#replayPromptButton");
  const vocabularyCards = [...document.querySelectorAll(".vocabulary-card")];
  const responsePlaceholder = document.querySelector("#responsePlaceholder");
  const responseItems = document.querySelector("#responseItems");
  const responseStatus = document.querySelector("#responseStatus");
  const speakResponseButton = document.querySelector("#speakResponseButton");
  const submitResponseButton = document.querySelector("#submitResponseButton");
  const nextQuestionButton = document.querySelector("#nextQuestionButton");
  const finishSessionButton = document.querySelector("#finishSessionButton");
  const textMeasurer = document.createElement("canvas").getContext("2d");
  const choiceMode = practiceRoot.dataset.practiceFormat === "choice";

  let activeIndex = 0;
  let presentedAt = null;
  let verbalPromptAt = null;
  let modeledPromptAt = null;
  let verbalCueTimer = null;
  let modeledCueTimer = null;
  let questionSpeakTimer = null;
  let selectedSymbols = [];
  let answeredCorrectly = false;
  let answeredIncorrectly = false;
  let submitting = false;
  let hasSavedResponse = false;
  let audioContext = null;

  function fitPromptQuestion() {
    if (!textMeasurer || !promptText.clientWidth || !promptText.textContent) return;
    promptText.style.fontSize = "";
    const style = window.getComputedStyle(promptText);
    const preferredSize = Number.parseFloat(style.fontSize);
    textMeasurer.font = style.font;
    const textWidth = textMeasurer.measureText(promptText.textContent).width;
    if (!textWidth) return;
    const fitScale = Math.min(1, (promptText.clientWidth - 2) / textWidth);
    promptText.style.fontSize = `${preferredSize * fitScale * 0.98}px`;
  }

  function speakText(text) {
    if (!text || !("speechSynthesis" in window)) return;
    // Avoid calling cancel() before the first utterance. Chrome can drop that
    // initial utterance when cancel() is issued while its speech queue is empty.
    if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
      window.speechSynthesis.cancel();
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    window.speechSynthesis.speak(utterance);
  }

  function symbolWord(symbolId) {
    return vocabularyCards.find((card) => Number(card.dataset.symbolId) === Number(symbolId))?.dataset.word || "";
  }

  function playFeedbackSound(correct) {
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return;
      audioContext ||= new AudioContextClass();
      if (audioContext.state === "suspended") audioContext.resume();
      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();
      const now = audioContext.currentTime;
      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(correct ? 660 : 420, now);
      if (correct) oscillator.frequency.setValueAtTime(880, now + 0.12);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + (correct ? 0.32 : 0.07));
      oscillator.connect(gain);
      gain.connect(audioContext.destination);
      oscillator.start(now);
      oscillator.stop(now + (correct ? 0.32 : 0.07));
    } catch (error) {
      console.warn("Could not play answer feedback sound.", error);
    }
  }

  function updateVocabularyAvailability(question) {
    const choices = new Set(question.available_symbol_ids || []);
    for (const card of vocabularyCards) {
      const available = !choiceMode || choices.has(Number(card.dataset.symbolId));
      card.disabled = !available;
      card.setAttribute("aria-disabled", String(!available));
      card.classList.toggle("is-unavailable", !available);
    }
  }

  function clearAnswerFeedback() {
    for (const card of vocabularyCards) {
      card.classList.remove("is-selected", "feedback-correct", "feedback-wrong");
    }
  }

  function renderResponse() {
    responsePlaceholder.hidden = selectedSymbols.length > 0;
    responseItems.replaceChildren();
    const selectedIds = new Set(selectedSymbols.map((symbol) => symbol.id));
    for (const card of vocabularyCards) {
      card.classList.toggle("is-selected", selectedIds.has(Number(card.dataset.symbolId)));
    }

    selectedSymbols.forEach((symbol, index) => {
      const item = document.createElement("button");
      item.className = "response-item";
      if (answeredCorrectly && choiceMode) item.classList.add("is-correct");
      if (answeredIncorrectly && choiceMode) item.classList.add("is-incorrect");
      item.type = "button";
      item.dataset.symbolId = String(symbol.id);
      item.setAttribute("aria-label", `Remove ${symbol.word}`);
      item.title = `Remove ${symbol.word}`;
      const image = document.createElement("img");
      image.src = symbol.imageUrl;
      image.alt = "";
      item.append(image);
      item.addEventListener("click", () => {
        if (answeredCorrectly) return;
        selectedSymbols.splice(index, 1);
        responseStatus.textContent = "";
        clearAnswerFeedback();
        renderResponse();
      });
      responseItems.append(item);
    });

    const hasResponse = selectedSymbols.length > 0;
    speakResponseButton.disabled = !hasResponse;
    submitResponseButton.disabled = !hasResponse || submitting || answeredCorrectly;
  }

  function chooseSymbol(card) {
    if (card.disabled || answeredCorrectly) return;
    const symbol = {
      id: Number(card.dataset.symbolId),
      word: card.dataset.word,
      imageUrl: card.querySelector("img").src,
    };
    if (choiceMode) selectedSymbols = [symbol];
    else selectedSymbols.push(symbol);
    answeredIncorrectly = false;
    responseStatus.textContent = "";
    clearAnswerFeedback();
    renderResponse();
    speakText(symbol.word);
  }

  function triggerVerbalCue() {
    if (!choiceMode || verbalPromptAt) return;
    verbalPromptAt = new Date().toISOString();
    const question = questions[activeIndex];
    speakText((question.expected_response || []).map(symbolWord).filter(Boolean).join(" "));
  }

  function triggerModeledCue() {
    if (!choiceMode || modeledPromptAt) return;
    modeledPromptAt = new Date().toISOString();
    const expectedIds = new Set(questions[activeIndex].expected_response || []);
    for (const card of vocabularyCards) {
      if (expectedIds.has(Number(card.dataset.symbolId))) card.classList.add("is-cue-highlight");
    }
  }

  function clearQuestionTimers() {
    window.clearTimeout(verbalCueTimer);
    window.clearTimeout(modeledCueTimer);
    verbalCueTimer = null;
    modeledCueTimer = null;
    for (const card of vocabularyCards) card.classList.remove("is-cue-highlight");
  }

  function setNavigationHighlight(highlighted) {
    const forwardButton = activeIndex === questions.length - 1 ? finishSessionButton : nextQuestionButton;
    for (const button of [nextQuestionButton, finishSessionButton]) {
      const isHighlighted = highlighted && button === forwardButton;
      button.classList.toggle("is-ready", isHighlighted);
    }
  }

  function renderPrompt(index) {
    const question = questions[index];
    if (!question) return;
    promptText.textContent = question.question;
    fitPromptQuestion();
    updateVocabularyAvailability(question);
    promptSymbols.replaceChildren();
    if (practiceRoot.dataset.promptDisplay === "symbols_and_text") {
      for (const symbol of question.question_symbols || []) {
        const figure = document.createElement("figure");
        figure.className = "prompt-symbol";
        const image = document.createElement("img");
        image.src = symbol.image_url;
        image.alt = "";
        figure.append(image);
        promptSymbols.append(figure);
      }
      promptSymbols.hidden = false;
    } else {
      promptSymbols.hidden = true;
    }
  }

  function beginQuestion(index) {
    clearQuestionTimers();
    window.clearTimeout(questionSpeakTimer);
    questionSpeakTimer = null;
    activeIndex = index;
    presentedAt = new Date();
    verbalPromptAt = null;
    modeledPromptAt = null;
    selectedSymbols = [];
    answeredCorrectly = false;
    answeredIncorrectly = false;
    submitting = false;
    hasSavedResponse = false;
    responseStatus.textContent = "";
    clearAnswerFeedback();
    renderResponse();
    renderPrompt(index);
    questionSpeakTimer = window.setTimeout(() => {
      speakText(questions[index].question);
      questionSpeakTimer = null;
    }, 1000);
    const isLastQuestion = index === questions.length - 1;
    nextQuestionButton.hidden = isLastQuestion;
    finishSessionButton.hidden = !isLastQuestion;
    setNavigationHighlight(false);

    if (choiceMode) {
      verbalCueTimer = window.setTimeout(triggerVerbalCue, 10000);
      modeledCueTimer = window.setTimeout(triggerModeledCue, 20000);
    }
  }

  function arraysMatch(left, right) {
    if (left.length !== right.length) return false;
    const sortedLeft = [...left].sort((a, b) => a - b);
    const sortedRight = [...right].sort((a, b) => a - b);
    return sortedLeft.every((value, index) => value === sortedRight[index]);
  }

  function showChoiceFeedback(correct, selectedIds) {
    playFeedbackSound(correct);
    for (const card of vocabularyCards) {
      if (selectedIds.includes(Number(card.dataset.symbolId))) {
        card.classList.add(correct ? "feedback-correct" : "feedback-wrong");
        window.setTimeout(() => card.classList.remove("feedback-correct", "feedback-wrong"), 800);
      }
    }
    responseStatus.textContent = correct ? "" : "Try again, or choose Next.";
    if (correct) {
      clearQuestionTimers();
      answeredCorrectly = true;
      renderResponse();
    } else {
      answeredIncorrectly = true;
      renderResponse();
    }
  }

  function appendTextElement(parent, tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    element.textContent = text;
    parent.append(element);
    return element;
  }

  function renderCompletion(session) {
    clearQuestionTimers();
    window.clearTimeout(questionSpeakTimer);
    questionSpeakTimer = null;
    practiceRoot.classList.add("is-complete");
    const summary = session.summary || {};
    const results = summary.results || {};
    practiceRoot.replaceChildren();

    const heading = appendTextElement(practiceRoot, "h1", "completion-title", "Session complete");
    heading.tabIndex = -1;
    appendTextElement(practiceRoot, "p", "completion-intro", "Here is a summary of this practice session.");

    const stats = document.createElement("dl");
    stats.className = "completion-stats";
    const statEntries = [
      ["Questions", `${results.answered_count ?? 0} of ${results.total_questions ?? questions.length} answered`],
      ["Correct", `${results.correct_count ?? 0}`],
      ["Accuracy", results.accuracy == null ? "—" : `${Math.round(results.accuracy)}%`],
      ["Independent", results.independent == null ? "—" : `${Math.round(results.independent)}%`],
      ["Verbal prompt", results.verbal_prompt == null ? "—" : `${Math.round(results.verbal_prompt)}%`],
      ["Modeled", results.modeled == null ? "—" : `${Math.round(results.modeled)}%`],
    ];
    for (const [label, value] of statEntries) {
      const item = document.createElement("div");
      appendTextElement(item, "dt", "", label);
      appendTextElement(item, "dd", "", value);
      stats.append(item);
    }
    practiceRoot.append(stats);

    const questionResults = summary.question_results || [];
    if (questionResults.length) {
      appendTextElement(practiceRoot, "h2", "completion-section-title", "Question results");
      const list = document.createElement("ol");
      list.className = "completion-question-list";
      for (const result of questionResults) {
        const item = document.createElement("li");
        appendTextElement(item, "h3", "", result.question || `Question ${result.question_id}`);
        const response = (result.response_words || []).join(", ") || "No response recorded";
        const expected = (result.expected_response_words || []).join(", ") || "Not available";
        appendTextElement(item, "p", "", `Response: ${response}`);
        appendTextElement(item, "p", "", `Expected: ${expected}`);
        appendTextElement(item, "p", result.correct ? "completion-correct" : "completion-incorrect", result.correct ? "Correct" : "Keep practising");
        if ((result.response_attempts || []).length > 1) {
          const attemptWords = result.response_attempts.map((attempt) => (attempt.response_words || []).join(", ") || "No symbols");
          appendTextElement(item, "p", "completion-attempts", `Responses submitted: ${attemptWords.join(" → ")}`);
        }
        list.append(item);
      }
      practiceRoot.append(list);
    }

    const unanswered = summary.unanswered_questions || [];
    if (unanswered.length) {
      appendTextElement(practiceRoot, "h2", "completion-section-title", "Not answered");
      const list = document.createElement("ul");
      list.className = "completion-unanswered-list";
      for (const item of unanswered) appendTextElement(list, "li", "", item.question || `Question ${item.question_id}`);
      practiceRoot.append(list);
    }

    if (summary.review) {
      appendTextElement(practiceRoot, "h2", "completion-section-title", "Review");
      appendTextElement(practiceRoot, "p", "completion-review", summary.review);
    } else if (summary.review_status === "unavailable") {
      appendTextElement(practiceRoot, "p", "completion-review-unavailable", "The session review is unavailable right now.");
    }

    const returnLink = document.createElement("a");
    returnLink.className = "button button-primary completion-return";
    returnLink.href = "/";
    returnLink.textContent = "Return to profiles";
    practiceRoot.append(returnLink);
    heading.focus();
  }

  async function finishSession() {
    finishSessionButton.disabled = true;
    responseStatus.textContent = "Saving your session…";
    try {
      const response = await fetch(`/sessions/${practiceRoot.dataset.sessionId}/complete`, {
        method: "POST",
        headers: { Accept: "application/json" },
      });
      const session = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(session.detail || "The session could not be completed.");
      renderCompletion(session);
    } catch (error) {
      responseStatus.textContent = error.message || "The session could not be completed.";
      finishSessionButton.disabled = false;
    }
  }

  async function submitResponse() {
    if (!selectedSymbols.length || submitting) return;
    if (choiceMode) {
      const elapsed = Date.now() - presentedAt.getTime();
      if (elapsed >= 10000) triggerVerbalCue();
      if (elapsed >= 20000) triggerModeledCue();
    }

    const question = questions[activeIndex];
    const answerIds = selectedSymbols.map((symbol) => symbol.id);
    const responseText = selectedSymbols.map((symbol) => symbol.word).join(" ");
    speakText(responseText);
    const correct = choiceMode && arraysMatch(answerIds, question.expected_response || []);
    if (choiceMode) showChoiceFeedback(correct, answerIds);
    else responseStatus.textContent = "Response submitted.";

    submitting = true;
    submitResponseButton.disabled = true;
    setNavigationHighlight(true);
    try {
      const result = await fetch(`/sessions/${practiceRoot.dataset.sessionId}/attempt`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          question_id: question.question_id,
          answer_symbol_ids: answerIds,
          question_presented_at: presentedAt.toISOString(),
          verbal_prompt_at: verbalPromptAt,
          modeled_prompt_at: modeledPromptAt,
        }),
      });
      if (!result.ok) {
        const detail = await result.json().catch(() => ({}));
        throw new Error(detail.detail || "Your response could not be saved.");
      }
      hasSavedResponse = true;
      setNavigationHighlight(true);
    } catch (error) {
      responseStatus.textContent = error.message || "Your response could not be saved.";
      setNavigationHighlight(hasSavedResponse);
    } finally {
      submitting = false;
      renderResponse();
    }
  }

  for (const card of vocabularyCards) {
    card.addEventListener("click", () => chooseSymbol(card));
  }
  replayButton.addEventListener("click", () => speakText(promptText.textContent));
  speakResponseButton.addEventListener("click", () => speakText(selectedSymbols.map((symbol) => symbol.word).join(" ")));
  submitResponseButton.addEventListener("click", submitResponse);
  nextQuestionButton.addEventListener("click", () => {
    if (activeIndex < questions.length - 1) beginQuestion(activeIndex + 1);
  });
  finishSessionButton.addEventListener("click", finishSession);

  if (promptHeading && "ResizeObserver" in window) {
    new ResizeObserver(fitPromptQuestion).observe(promptHeading);
  }
  window.addEventListener("resize", fitPromptQuestion);
  beginQuestion(0);
}
