/**
 * Shared utility functions for the Inorganic Chemistry Course
 */

export const normalizeAnswer = (value) => {
  return value
    .toLowerCase()
    .replace(/\./g, "")
    .replace(/,/g, "")
    .replace(/-/g, " ")
    .replace(/\s+/g, " ")
    .trim();
};

export const shuffleArray = (array) => {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
};

export const loadSettings = (key, defaultState) => {
  const raw = localStorage.getItem(key);
  if (!raw) return defaultState;
  try {
    const data = JSON.parse(raw);
    return { ...defaultState, ...data };
  } catch (error) {
    console.error("Failed to load settings:", error);
    return defaultState;
  }
};

export const saveSettings = (key, state) => {
  try {
    localStorage.setItem(key, JSON.stringify(state));
  } catch (error) {
    console.error("Failed to save settings:", error);
  }
};

export const updateUI = (elements, state) => {
  if (elements.streak) elements.streak.textContent = state.streak;
  if (elements.questionCount) elements.questionCount.textContent = state.total;
  
  const percent = state.total === 0 ? 0 : Math.round((state.correct / state.total) * 100);
  if (elements.accuracy) elements.accuracy.textContent = `${percent}%`;
  
  if (elements.adaptiveToggle) {
    elements.adaptiveToggle.textContent = state.adaptive ? "On" : "Off";
    elements.adaptiveToggle.classList.toggle("off", !state.adaptive);
  }
  
  if (elements.rigorToggle) {
    elements.rigorToggle.textContent = state.rigorMode ? "On" : "Off";
    elements.rigorToggle.classList.toggle("off", !state.rigorMode);
  }
};

export const createElement = (tag, className, textContent = "") => {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (textContent) el.textContent = textContent;
  return el;
};
