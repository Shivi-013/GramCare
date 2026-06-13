// ─── Language System ───────────────────────────────────────────────────────────
const SUPPORTED_LANGS = ["en", "hi", "ta", "te"];
const LANG_NAMES = { en: "English", hi: "हिंदी", ta: "தமிழ்", te: "తెలుగు" };
let translations = {};
let currentLang = localStorage.getItem("rc_lang") || "en";

async function loadTranslations(lang) {
  try {
    const res = await fetch(`/static/translations/${lang}.json`);
    translations = await res.json();
    applyTranslations();
    localStorage.setItem("rc_lang", lang);
    currentLang = lang;
    // Update old sidebar lang buttons if present
    document.querySelectorAll(".lang-btn").forEach(btn => {
      btn.classList.toggle("active-lang", btn.dataset.lang === lang);
    });
    // Update floating switcher labels
    const LABELS = { en:"EN", hi:"हिं", ta:"த", te:"తె" };
    const label = LABELS[lang] || "EN";
    const badge = document.getElementById("lang-indicator-badge");
    const topBadge = document.getElementById("current-lang-label");
    if (badge) badge.textContent = label;
    if (topBadge) topBadge.textContent = label;
    // Mark active float btn
    document.querySelectorAll(".lang-float-btn").forEach(btn => {
      btn.classList.toggle("active-lang", btn.dataset.lang === lang);
    });
  } catch (e) { console.warn("Translation load failed:", e); }
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (translations[key]) el.textContent = translations[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (translations[key]) el.placeholder = translations[key];
  });
}

// ─── Toast Notifications ───────────────────────────────────────────────────────
function showToast(message, type = "success") {
  const colors = {
    success: "bg-green-500", error: "bg-red-500",
    warning: "bg-yellow-500", info: "bg-blue-500"
  };
  const icons = {
    success: "fa-check-circle", error: "fa-times-circle",
    warning: "fa-exclamation-triangle", info: "fa-info-circle"
  };
  const toast = document.createElement("div");
  toast.className = `fixed top-4 right-4 z-50 flex items-center gap-3 px-5 py-3 rounded-xl text-white shadow-2xl
    transform translate-x-full transition-all duration-300 ${colors[type]}`;
  toast.innerHTML = `<i class="fas ${icons[type]}"></i><span class="font-medium">${message}</span>
    <button onclick="this.parentElement.remove()" class="ml-2 opacity-75 hover:opacity-100">
      <i class="fas fa-times text-sm"></i></button>`;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.replace("translate-x-full", "translate-x-0"));
  setTimeout(() => {
    toast.classList.replace("translate-x-0", "translate-x-full");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ─── Modal System ──────────────────────────────────────────────────────────────
function openModal(id) {
  const m = document.getElementById(id);
  if (!m) return;
  m.classList.remove("hidden");
  m.classList.add("flex");
  document.body.style.overflow = "hidden";
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (!m) return;
  m.classList.add("hidden");
  m.classList.remove("flex");
  document.body.style.overflow = "";
}

// Close modal on backdrop click
document.addEventListener("click", e => {
  if (e.target.classList.contains("modal-backdrop")) {
    e.target.closest(".modal-wrap")?.classList.add("hidden");
    document.body.style.overflow = "";
  }
});

// ─── Search Debounce ───────────────────────────────────────────────────────────
function debounce(fn, delay = 300) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

const searchInput = document.getElementById("global-search");
if (searchInput) {
  searchInput.addEventListener("input", debounce(e => {
    const q = e.target.value.trim();
    if (q.length > 1) window.location.href = `/patients/?search=${encodeURIComponent(q)}`;
  }));
}

// ─── Sidebar Toggle (Mobile) ───────────────────────────────────────────────────
const menuBtn = document.getElementById("menu-toggle");
const sidebar  = document.getElementById("sidebar");
const overlay  = document.getElementById("sidebar-overlay");

if (menuBtn && sidebar) {
  menuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("-translate-x-full");
    overlay?.classList.toggle("hidden");
  });
  overlay?.addEventListener("click", () => {
    sidebar.classList.add("-translate-x-full");
    overlay.classList.add("hidden");
  });
}

// ─── Offline / Online Banner ───────────────────────────────────────────────────
function updateConnectionStatus() {
  const banner = document.getElementById("offline-banner");
  if (!banner) return;
  if (navigator.onLine) {
    banner.classList.add("hidden");
    syncOfflineData();
  } else {
    banner.classList.remove("hidden");
  }
}
window.addEventListener("online", updateConnectionStatus);
window.addEventListener("offline", updateConnectionStatus);
updateConnectionStatus();

// ─── Offline Data Sync ─────────────────────────────────────────────────────────
function saveOffline(key, data) {
  try { localStorage.setItem(`rc_offline_${key}`, JSON.stringify({ data, ts: Date.now() })); }
  catch (e) { console.warn("Offline save failed:", e); }
}

function getOffline(key) {
  try {
    const raw = localStorage.getItem(`rc_offline_${key}`);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

async function syncOfflineData() {
  const keys = Object.keys(localStorage).filter(k => k.startsWith("rc_offline_"));
  for (const key of keys) {
    const item = getOffline(key.replace("rc_offline_", ""));
    if (item) {
      console.log(`[Sync] Syncing offline data: ${key}`);
      localStorage.removeItem(key);
    }
  }
}

// ─── Emergency Alert ───────────────────────────────────────────────────────────
const EMERGENCY_KEYWORDS = [
  "chest pain", "heart attack", "stroke", "difficulty breathing",
  "breathlessness", "unconscious", "fainted", "severe bleeding",
  "paralysis", "choking"
];

function checkEmergency(text) {
  const lower = text.toLowerCase();
  return EMERGENCY_KEYWORDS.some(kw => lower.includes(kw));
}

const symptomInput = document.getElementById("symptoms-input");
const emergencyBanner = document.getElementById("emergency-banner");
if (symptomInput && emergencyBanner) {
  symptomInput.addEventListener("input", () => {
    const isEmergency = checkEmergency(symptomInput.value);
    emergencyBanner.classList.toggle("hidden", !isEmergency);
  });
}

// ─── Number Counter Animation ──────────────────────────────────────────────────
function animateCounter(el, target, duration = 1200) {
  const start = 0;
  const step = target / (duration / 16);
  let current = start;
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = Math.floor(current);
    if (current >= target) clearInterval(timer);
  }, 16);
}

document.querySelectorAll("[data-counter]").forEach(el => {
  const target = parseInt(el.dataset.counter, 10);
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(el, target);
        observer.unobserve(el);
      }
    });
  });
  observer.observe(el);
});

// ─── Confirm Delete ────────────────────────────────────────────────────────────
document.querySelectorAll("[data-confirm]").forEach(el => {
  el.addEventListener("click", e => {
    if (!confirm(el.dataset.confirm || "Are you sure?")) e.preventDefault();
  });
});

// ─── Form Loading State ────────────────────────────────────────────────────────
document.querySelectorAll("form[data-loading]").forEach(form => {
  form.addEventListener("submit", () => {
    const btn = form.querySelector("[type=submit]");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>Processing...`;
    }
  });
});

// ─── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadTranslations(currentLang);

  // Lang switcher buttons
  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.addEventListener("click", () => loadTranslations(btn.dataset.lang));
  });

  // Active nav link
  const path = window.location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href && path.startsWith(href) && href !== "/") {
      link.classList.add("nav-active");
    } else if (href === "/" && path === "/") {
      link.classList.add("nav-active");
    }
  });
});
