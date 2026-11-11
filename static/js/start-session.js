const startSessionForm = document.querySelector("#startSessionForm");

if (startSessionForm) {
  const startButton = document.querySelector("#startPracticeButton");
  const statusMessage = document.querySelector("#sessionStartStatus");

  startSessionForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const selectedGoal = startSessionForm.querySelector('input[name="communication_goal"]:checked');
    if (!selectedGoal) {
      statusMessage.textContent = "Choose a communication goal to begin.";
      return;
    }

    const location = startSessionForm.querySelector('[name="location"]')?.value || null;
    const payload = {
      user_id: Number(startSessionForm.dataset.userId),
      communication_goal: selectedGoal.value,
      practice_format: startSessionForm.dataset.practiceFormat,
      location,
    };

    startButton.disabled = true;
    statusMessage.textContent = "Preparing your questions…";
    statusMessage.classList.remove("form-status--error");

    try {
      const response = await fetch("/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(result.detail)
          ? result.detail.map((item) => item.msg).join(" ")
          : result.detail;
        throw new Error(detail || "A practice session could not be started.");
      }

      window.location.assign(`/practice/${result.session_id}`);
    } catch (error) {
      statusMessage.textContent = error.message || "A practice session could not be started. Try again.";
      statusMessage.classList.add("form-status--error");
      startButton.disabled = false;
    }
  });
}
