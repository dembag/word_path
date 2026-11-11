const settingsForm = document.querySelector("#profileSettingsForm");

if (settingsForm) {
  const statusMessage = document.querySelector("#settingsStatus");
  const saveButton = document.querySelector("#saveProfileButton");

  settingsForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    statusMessage.textContent = "Saving settings…";
    statusMessage.classList.remove("form-status--error");
    saveButton.disabled = true;

    const formData = new FormData(settingsForm);
    const locations = String(formData.get("locations") || "")
      .split(/\r?\n|,/)
      .map((location) => location.trim())
      .filter(Boolean);
    const communicationGoals = Array.from(
      settingsForm.querySelectorAll('input[name="communication_goals"]:checked'),
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
      const response = await fetch(`/users/${settingsForm.dataset.userId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(result.detail)
          ? result.detail.map((item) => item.msg).join(" ")
          : result.detail;
        throw new Error(detail || "Settings could not be saved.");
      }

      window.location.assign(`/profiles/${settingsForm.dataset.userId}`);
    } catch (error) {
      statusMessage.textContent = error.message || "Settings could not be saved. Try again.";
      statusMessage.classList.add("form-status--error");
      saveButton.disabled = false;
    }
  });
}
