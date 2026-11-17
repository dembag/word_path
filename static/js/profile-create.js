const createProfileForm = document.querySelector("#newProfileForm");

if (createProfileForm) {
  const statusMessage = document.querySelector("#settingsStatus");
  const createButton = document.querySelector("#createProfileButton");

  createProfileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    statusMessage.textContent = "Adding learner…";
    statusMessage.classList.remove("form-status--error");
    createButton.disabled = true;

    const formData = new FormData(createProfileForm);
    const locations = String(formData.get("locations") || "")
      .split(/\r?\n|,/)
      .map((location) => location.trim())
      .filter(Boolean);
    const communicationGoals = Array.from(
      createProfileForm.querySelectorAll('input[name="communication_goals"]:checked'),
      (input) => input.value,
    );
    const payload = {
      name: String(formData.get("name") || "").trim(),
      age_band: formData.get("age_band"),
      prompt_display: formData.get("prompt_display"),
      starting_format: formData.get("starting_format"),
      communication_goals: communicationGoals,
      locations,
      card_size: formData.get("card_size"),
    };

    try {
      const response = await fetch("/users", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(result.detail)
          ? result.detail.map((item) => item.msg).join(" ")
          : result.detail;
        throw new Error(detail || "The profile could not be added.");
      }

      window.location.assign(`/profiles/${result.user_id}`);
    } catch (error) {
      statusMessage.textContent = error.message || "The profile could not be added. Try again.";
      statusMessage.classList.add("form-status--error");
      createButton.disabled = false;
    }
  });
}
