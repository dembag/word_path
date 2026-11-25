const manager = document.querySelector("#vocabularyManager");

if (manager) {
  const userId = manager.dataset.userId;
  const catalogSearch = document.querySelector("#catalogSearch");
  const catalogResults = document.querySelector("#catalogResults");
  const catalogStatus = document.querySelector("#catalogStatus");
  const sectionPicker = document.querySelector("#sectionPicker");
  const sectionPickerWord = document.querySelector("#sectionPickerWord");
  const sectionPickerForm = document.querySelector("#sectionPickerForm");
  const confirmSectionPicker = document.querySelector("#confirmSectionPicker");
  const boardStatus = document.querySelector("#boardStatus");
  const customForm = document.querySelector("#customSymbolForm");
  const customStatus = document.querySelector("#customStatus");
  const assignedIds = new Set(
    [...document.querySelectorAll(".manager-symbol")].map((item) => Number(item.dataset.symbolId)),
  );
  let catalog = [];
  let pointerDrag = null;
  let pendingSymbol = null;

  function showApiError(result, fallback) {
    if (Array.isArray(result?.detail)) return result.detail.map((item) => item.msg).join(" ");
    return result?.detail || fallback;
  }

  function imageUrl(reference) {
    let path = String(reference || "").replaceAll("\\", "/").replace(/^\/+/, "");
    if (path.startsWith("static/")) path = path.slice("static/".length);
    return `/static/${path}`;
  }

  function renderCatalog() {
    const query = catalogSearch.value.trim().toLocaleLowerCase();
    const matches = catalog.filter((symbol) =>
      symbol.word.toLocaleLowerCase().includes(query) && !assignedIds.has(symbol.symbol_id),
    );
    catalogResults.replaceChildren();
    if (!matches.length) {
      const empty = document.createElement("p");
      empty.className = "empty-note";
      empty.textContent = query ? "No unassigned symbols match that word." : "No unassigned symbols are available.";
      catalogResults.append(empty);
      return;
    }
    for (const symbol of matches) {
      const row = document.createElement("div");
      row.className = "catalog-symbol";
      const image = document.createElement("img");
      image.src = imageUrl(symbol.image_reference);
      image.alt = symbol.word;
      const addButton = document.createElement("button");
      addButton.className = "button button-secondary";
      addButton.type = "button";
      addButton.textContent = "Add";
      addButton.setAttribute("aria-label", `Add ${symbol.word}`);
      addButton.addEventListener("click", () => openSectionPicker(symbol, addButton));
      row.append(image, addButton);
      catalogResults.append(row);
    }
  }

  function openSectionPicker(symbol, button) {
    pendingSymbol = { symbol, button };
    sectionPickerWord.textContent = symbol.word;
    sectionPickerForm.reset();
    confirmSectionPicker.disabled = true;
    sectionPicker.showModal();
  }

  sectionPickerForm.querySelectorAll('input[name="section"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      confirmSectionPicker.disabled = false;
    });
  });

  sectionPickerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!pendingSymbol) return;
    const section = new FormData(sectionPickerForm).get("section");
    if (!section) return;
    const selected = pendingSymbol;
    pendingSymbol = null;
    sectionPicker.close();
    await addCatalogSymbol(selected.symbol, selected.button, section);
  });

  document.querySelector("#cancelSectionPicker").addEventListener("click", () => {
    sectionPicker.close();
  });

  sectionPicker.addEventListener("close", () => {
    pendingSymbol = null;
  });

  async function loadCatalog() {
    catalogStatus.textContent = "Loading symbols…";
    try {
      const response = await fetch(`/symbols?user_id=${encodeURIComponent(userId)}`, { headers: { Accept: "application/json" } });
      const result = await response.json();
      if (!response.ok) throw new Error(showApiError(result, "Could not load the symbol catalog."));
      catalog = result;
      catalogStatus.textContent = `${catalog.length} symbols available. Search by word or browse the list.`;
      renderCatalog();
    } catch (error) {
      catalogStatus.textContent = error.message || "Could not load the symbol catalog.";
      catalogStatus.classList.add("form-status--error");
    }
  }

  async function addCatalogSymbol(symbol, button, section) {
    button.disabled = true;
    catalogStatus.textContent = `Adding ${symbol.word}…`;
    try {
      const params = new URLSearchParams({ symbol_id: symbol.symbol_id, page: section });
      const response = await fetch(`/vocabulary/${userId}?${params}`, { method: "POST" });
      const result = response.status === 204 ? null : await response.json();
      if (!response.ok) throw new Error(showApiError(result, `Could not add ${symbol.word}.`));
      assignedIds.add(symbol.symbol_id);
      window.location.reload();
    } catch (error) {
      catalogStatus.textContent = error.message || `Could not add ${symbol.word}.`;
      catalogStatus.classList.add("form-status--error");
      button.disabled = false;
    }
  }

  catalogSearch.addEventListener("input", renderCatalog);
  loadCatalog();

  customForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    customStatus.textContent = "Uploading symbol…";
    customStatus.classList.remove("form-status--error");
    const uploadButton = document.querySelector("#uploadCustomButton");
    uploadButton.disabled = true;
    const formData = new FormData(customForm);
    formData.set("user_id", userId);
    try {
      const response = await fetch("/symbols/custom", { method: "POST", body: formData });
      const result = await response.json();
      if (!response.ok) throw new Error(showApiError(result, "Could not upload the symbol."));
      window.location.reload();
    } catch (error) {
      customStatus.textContent = error.message || "Could not upload the symbol.";
      customStatus.classList.add("form-status--error");
      uploadButton.disabled = false;
    }
  });

  async function saveOrder() {
    const sections = {};
    for (const list of document.querySelectorAll("[data-section-list]")) {
      sections[list.dataset.sectionList] = [...list.querySelectorAll(".manager-symbol")]
        .map((item) => Number(item.dataset.symbolId));
    }
    boardStatus.textContent = "Saving board order…";
    boardStatus.classList.remove("form-status--error");
    try {
      const response = await fetch(`/vocabulary/${userId}/order`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ sections }),
      });
      if (!response.ok) {
        const result = await response.json();
        throw new Error(showApiError(result, "Could not save the board order."));
      }
      boardStatus.textContent = "Board order saved.";
    } catch (error) {
      boardStatus.textContent = error.message || "Could not save the board order.";
      boardStatus.classList.add("form-status--error");
    }
  }

  document.addEventListener("pointermove", (event) => {
    if (!pointerDrag || pointerDrag.pointerId !== event.pointerId) return;
    const item = pointerDrag.item;
    if (!pointerDrag.dragging) {
      const distance = Math.hypot(event.clientX - pointerDrag.startX, event.clientY - pointerDrag.startY);
      if (distance < 6) return;
      pointerDrag.dragging = true;
      item.classList.add("is-dragging");
    }

    event.preventDefault();
    const hovered = document.elementFromPoint(event.clientX, event.clientY);
    const section = hovered?.closest(".manager-board-section");
    if (!section || !manager.contains(section)) return;
    document.querySelectorAll(".manager-board-section.is-drop-target").forEach((candidate) => {
      candidate.classList.toggle("is-drop-target", candidate === section);
    });
    const list = section.querySelector(".manager-symbol-list");
    const target = hovered.closest(".manager-symbol");
    if (target === item) return;
    let insertBefore = null;
    if (target) {
      const bounds = target.getBoundingClientRect();
      const dx = event.clientX - (bounds.left + bounds.width / 2);
      const dy = event.clientY - (bounds.top + bounds.height / 2);
      const afterTarget = Math.abs(dx) > Math.abs(dy) ? dx > 0 : dy > 0;
      insertBefore = afterTarget ? target.nextSibling : target;
    }
    if (insertBefore === item || (insertBefore === null && list.lastElementChild === item)) return;
    if (item.parentElement !== list || item.nextSibling !== insertBefore) {
      list.insertBefore(item, insertBefore);
      pointerDrag.changed = true;
    }
    if (item.dataset.page !== section.dataset.section) {
      item.dataset.page = section.dataset.section;
      pointerDrag.changed = true;
    }
  });

  document.addEventListener("pointerup", async (event) => {
    if (!pointerDrag || pointerDrag.pointerId !== event.pointerId) return;
    const finishedDrag = pointerDrag;
    pointerDrag = null;
    finishedDrag.item.classList.remove("is-dragging");
    document.querySelectorAll(".manager-board-section.is-drop-target").forEach((section) => section.classList.remove("is-drop-target"));
    if (finishedDrag.dragging && finishedDrag.changed) await saveOrder();
  });

  document.addEventListener("pointercancel", (event) => {
    if (!pointerDrag || pointerDrag.pointerId !== event.pointerId) return;
    pointerDrag.item.classList.remove("is-dragging");
    document.querySelectorAll(".manager-board-section.is-drop-target").forEach((section) => section.classList.remove("is-drop-target"));
    pointerDrag = null;
  });

  document.querySelectorAll(".manager-symbol").forEach((item) => {
    item.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 || event.target.closest("button")) return;
      pointerDrag = {
        item,
        pointerId: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        dragging: false,
        changed: false,
      };
    });
    item.addEventListener("click", async (event) => {
      if (!event.target.closest(".remove-symbol-button")) return;
      const word = item.querySelector("span").textContent;
      if (!window.confirm(`Remove ${word} from this learner's board?`)) return;
      const button = event.target.closest("button");
      button.disabled = true;
      try {
        const params = new URLSearchParams({ symbol_id: item.dataset.symbolId });
        const response = await fetch(`/vocabulary/${userId}?${params}`, { method: "DELETE" });
        if (!response.ok) {
          const result = await response.json();
          throw new Error(showApiError(result, `Could not remove ${word}.`));
        }
        item.remove();
        assignedIds.delete(Number(item.dataset.symbolId));
        catalogStatus.textContent = `${word} is available to add again.`;
        renderCatalog();
        await saveOrder();
      } catch (error) {
        boardStatus.textContent = error.message || `Could not remove ${word}.`;
        boardStatus.classList.add("form-status--error");
        button.disabled = false;
      }
    });
  });
}
