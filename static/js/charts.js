// RuralCare AI – Chart.js Analytics
const RC_COLORS = {
  green:  ["#22C55E", "#16A34A", "#15803D", "#166534", "#14532D"],
  blue:   ["#3B82F6", "#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A"],
  mixed:  ["#22C55E","#3B82F6","#F59E0B","#EF4444","#8B5CF6","#EC4899","#06B6D4"],
  pastel: ["#BBF7D0","#BAE6FD","#FDE68A","#FCA5A5","#DDD6FE","#FBCFE8","#A5F3FC"]
};

const defaultFont = { family: "'Inter', sans-serif", size: 12 };

Chart.defaults.font = defaultFont;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 20;
Chart.defaults.plugins.tooltip.backgroundColor = "rgba(17,24,39,0.9)";
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleFont = { ...defaultFont, weight: "bold", size: 13 };

// ─── Appointments per Week ─────────────────────────────────────────────────────
function renderAppointmentsChart(data) {
  const ctx = document.getElementById("appointmentsChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "Appointments",
        data: data.data,
        backgroundColor: RC_COLORS.green.map(c => c + "CC"),
        borderColor: RC_COLORS.green,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} appointments` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#6B7280" } },
        y: {
          beginAtZero: true,
          grid: { color: "#F3F4F6", lineWidth: 1.5 },
          ticks: { color: "#6B7280", stepSize: 1 }
        }
      },
      animation: { duration: 1000, easing: "easeInOutQuart" }
    }
  });
}

// ─── Patient Age Distribution ──────────────────────────────────────────────────
function renderAgeChart(data) {
  const ctx = document.getElementById("ageChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "pie",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.data,
        backgroundColor: RC_COLORS.mixed,
        borderColor: "#fff",
        borderWidth: 3,
        hoverBorderWidth: 4,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} patients` } }
      },
      animation: { duration: 1000, animateRotate: true }
    }
  });
}

// ─── Disease Categories ────────────────────────────────────────────────────────
function renderDiseaseChart(data) {
  const ctx = document.getElementById("diseaseChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.data,
        backgroundColor: RC_COLORS.blue.concat(RC_COLORS.green),
        borderColor: "#fff",
        borderWidth: 3,
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: "65%",
      plugins: {
        legend: { position: "right" },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} cases` } }
      },
      animation: { duration: 1200, animateRotate: true }
    }
  });
}

// ─── Consultation Trends ───────────────────────────────────────────────────────
function renderTrendChart(data) {
  const ctx = document.getElementById("trendChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [{
        label: "Consultations",
        data: data.data,
        borderColor: "#22C55E",
        backgroundColor: "rgba(34,197,94,0.08)",
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: "#22C55E",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 9
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.y} consultations` } }
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#6B7280" } },
        y: {
          beginAtZero: true,
          grid: { color: "#F3F4F6" },
          ticks: { color: "#6B7280", stepSize: 1 }
        }
      },
      animation: { duration: 1200, easing: "easeInOutCubic" }
    }
  });
}

// ─── Gender Distribution ───────────────────────────────────────────────────────
function renderGenderChart(data) {
  const ctx = document.getElementById("genderChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: data.labels,
      datasets: [{
        data: data.data,
        backgroundColor: ["#3B82F6", "#EC4899", "#8B5CF6"],
        borderColor: "#fff",
        borderWidth: 3,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: "60%",
      plugins: { legend: { position: "bottom" } },
      animation: { duration: 1000 }
    }
  });
}

// ─── Appointment Types ─────────────────────────────────────────────────────────
function renderApptTypeChart(data) {
  const ctx = document.getElementById("apptTypeChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "Count",
        data: data.data,
        backgroundColor: RC_COLORS.mixed.map(c => c + "CC"),
        borderColor: RC_COLORS.mixed,
        borderWidth: 2,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, grid: { color: "#F3F4F6" }, ticks: { stepSize: 1 } },
        y: { grid: { display: false } }
      },
      animation: { duration: 800 }
    }
  });
}

// ─── Medicine Frequency ────────────────────────────────────────────────────────
function renderMedicineChart(data) {
  const ctx = document.getElementById("medicineChart");
  if (!ctx) return;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [{
        label: "Prescriptions",
        data: data.data,
        backgroundColor: RC_COLORS.mixed.map(c => c + "CC"),
        borderColor: RC_COLORS.mixed,
        borderWidth: 2,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      indexAxis: "y",
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x} times` } }
      },
      scales: {
        x: { beginAtZero: true, grid: { color: "#F3F4F6" }, ticks: { stepSize: 1, color: "#6B7280" } },
        y: { grid: { display: false }, ticks: { color: "#6B7280" } }
      },
      animation: { duration: 900 }
    }
  });
}

// ─── Load all charts from API ──────────────────────────────────────────────────
async function loadCharts() {
  try {
    const res = await fetch("/analytics/data");
    const d = await res.json();
    renderAppointmentsChart(d.appointments_per_week);
    renderAgeChart(d.age_distribution);
    renderDiseaseChart(d.disease_categories);
    renderTrendChart(d.consultation_trends);
    renderGenderChart(d.gender_distribution);
    renderApptTypeChart(d.appointment_types);
    if (d.medicine_frequency) renderMedicineChart(d.medicine_frequency);

    // Update summary cards
    const s = d.summary || {};
    const summaryMap = {
      "stat-patients":      s.total_patients      || 0,
      "stat-appointments":  s.total_appointments  || 0,
      "stat-consultations": s.total_consultations || 0,
      "stat-today":         s.today_appointments  || 0,
      "stat-pending":       s.pending_appointments || 0,
      "stat-approved":      s.approved_appointments || 0,
      "stat-rejected":      s.rejected_appointments || 0,
      "stat-reminders":     s.active_reminders     || 0,
    };
    Object.entries(summaryMap).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (el) { el.dataset.counter = val; animateCounter(el, val); }
    });
  } catch (e) { console.error("Failed to load chart data:", e); }
}

if (document.getElementById("appointmentsChart")) loadCharts();
