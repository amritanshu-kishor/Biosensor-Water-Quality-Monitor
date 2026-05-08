/* Frontend-only demo logic with optional backend integration.
   Backend endpoints (Flask): /water/generate and /water/report/advanced */

const CONFIG = {
  preAnalysis: {
    // You can adjust these ranges to match your calibration.
    ppi: { min: 0.6, max: 0.95 },
    ri: { min: 1.32, max: 1.345 },
  },
  advanced: {
    // Commonly used drinking-water heuristics (adjust to your project spec).
    tds: { max: 500 }, // ppm
    ph: { min: 6.5, max: 8.5 },
    turbidity: { max: 5 }, // NTU
  },
  charts: {
    maxPoints: 120,
    streamIntervalMs: 600,
    chartFps: 10,
  },
};

const $ = (id) => document.getElementById(id);

const els = {
  preForm: $("preForm"),
  ppi: $("ppi"),
  ri: $("ri"),
  btnRunPre: $("btnRunPre"),
  btnSkipToAdv: $("btnSkipToAdv"),
  preResult: $("preResult"),
  preBadge: $("preBadge"),

  advCard: $("advCard"),
  advBadge: $("advBadge"),
  advResult: $("advResult"),
  btnRunAdv: $("btnRunAdv"),
  btnSimulateStream: $("btnSimulateStream"),

  tdsVal: $("tdsVal"),
  phVal: $("phVal"),
  turbVal: $("turbVal"),
  tdsStatus: $("tdsStatus"),
  phStatus: $("phStatus"),
  turbStatus: $("turbStatus"),
  decisionVal: $("decisionVal"),
  decisionSub: $("decisionSub"),

  verdictCard: $("verdictCard"),
  chipText: $("chipText"),
  meterFill: $("meterFill"),
  meterValue: $("meterValue"),
  verdictHeadline: $("verdictHeadline"),
  verdictSub: $("verdictSub"),
  miniPre: $("miniPre"),
  miniAdv: $("miniAdv"),
  miniFinal: $("miniFinal"),

  stepPre: $("stepPre"),
  stepAdv: $("stepAdv"),

  btnReset: $("btnReset"),
  btnDemo: $("btnDemo"),
  btnRealtimeSample: $("btnRealtimeSample"),
  apiBaseLabel: $("apiBaseLabel"),
};

let state = {
  prePassed: false,
  lastReading: null,
  streaming: false,
  streamTimer: null,
  api: { base: null, enabled: false },
};

let charts = null;
const chartScaleConfig = {
  tds: { floor: 0, minRange: 60, padRatio: 0.15 },
  ph: { floor: 0, minRange: 0.8, padRatio: 0.2 },
  turb: { floor: 0, minRange: 1.2, padRatio: 0.2 },
};

function getApiBase() {
  const q = new URLSearchParams(window.location.search);
  const api = q.get("api");
  if (api && api.trim()) return api.trim().replace(/\/+$/, "");
  // If served by Flask, use same-origin automatically.
  if (window.location.protocol !== "file:") return window.location.origin;
  // Fallback: common local dev when opening via a separate static server.
  return "http://127.0.0.1:5000";
}

function setApiUi() {
  const base = state.api.enabled ? state.api.base : "demo mode";
  if (els.apiBaseLabel) els.apiBaseLabel.textContent = base;
}

function clamp01(x) {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

function parseNum(v) {
  const n = Number(String(v).trim());
  return Number.isFinite(n) ? n : null;
}

function inRange(val, { min, max }) {
  return val >= min && val <= max;
}

function setBadge(el, kind, text) {
  el.classList.remove("badge--soft", "badge--good", "badge--bad");
  el.classList.add(kind);
  el.textContent = text;
}

function setResult(el, kind, text) {
  el.classList.remove("result--muted", "result--good", "result--bad");
  el.classList.add(kind);
  el.textContent = text;
}

function setVerdictCard({ tone = "idle", chip = "Waiting for input", conf = null, headline, sub }) {
  els.verdictCard.dataset.state = tone;
  els.chipText.textContent = chip;

  const pct = conf == null ? 0 : Math.round(clamp01(conf) * 100);
  els.meterFill.style.width = `${pct}%`;
  els.meterValue.textContent = conf == null ? "—" : `${pct}%`;

  if (headline) els.verdictHeadline.textContent = headline;
  if (sub) els.verdictSub.textContent = sub;
}

function setStepper({ pre = "active", adv = "idle" }) {
  els.stepPre.classList.remove("step--active", "step--done");
  els.stepAdv.classList.remove("step--active", "step--done");

  if (pre === "active") els.stepPre.classList.add("step--active");
  if (pre === "done") els.stepPre.classList.add("step--done");

  if (adv === "active") els.stepAdv.classList.add("step--active");
  if (adv === "done") els.stepAdv.classList.add("step--done");
}

function unlockAdvancedLayer() {
  els.advCard.classList.remove("card--disabled");
  setBadge(els.advBadge, "badge--soft", "Ready");
  els.btnRunAdv.disabled = false;
  els.btnSimulateStream.disabled = false;
  els.btnSkipToAdv.disabled = false;
  els.btnSkipToAdv.textContent = "Go to advanced layer";
  els.advResult.textContent = "Advanced layer ready. Run tests to get final verdict + charts.";
  els.miniAdv.textContent = "Ready";
  setStepper({ pre: "done", adv: "active" });
}

function lockAdvancedLayer() {
  els.advCard.classList.add("card--disabled");
  setBadge(els.advBadge, "badge--soft", "Locked");
  els.btnRunAdv.disabled = true;
  els.btnSimulateStream.disabled = true;
  els.btnSkipToAdv.disabled = true;
  els.btnSkipToAdv.textContent = "Advanced layer locked";
  setResult(els.advResult, "result--muted", "Advanced layer is locked until pre-analysis passes.");
  els.miniAdv.textContent = "Locked";
  setStepper({ pre: "active", adv: "idle" });
}

function preAnalysis(ppi, ri) {
  const ppiOk = inRange(ppi, CONFIG.preAnalysis.ppi);
  const riOk = inRange(ri, CONFIG.preAnalysis.ri);

  // Simple confidence: average normalized closeness to range centers.
  const ppiCenter = (CONFIG.preAnalysis.ppi.min + CONFIG.preAnalysis.ppi.max) / 2;
  const riCenter = (CONFIG.preAnalysis.ri.min + CONFIG.preAnalysis.ri.max) / 2;
  const ppiSpan = (CONFIG.preAnalysis.ppi.max - CONFIG.preAnalysis.ppi.min) / 2;
  const riSpan = (CONFIG.preAnalysis.ri.max - CONFIG.preAnalysis.ri.min) / 2;

  const ppiScore = clamp01(1 - Math.abs(ppi - ppiCenter) / (ppiSpan * 1.8));
  const riScore = clamp01(1 - Math.abs(ri - riCenter) / (riSpan * 1.8));
  const confidence = (ppiScore + riScore) / 2;

  return {
    pass: ppiOk && riOk,
    confidence,
    checks: { ppiOk, riOk },
  };
}

function evaluateAdvanced(reading) {
  const tdsOk = reading.tds <= CONFIG.advanced.tds.max;
  const phOk = inRange(reading.ph, CONFIG.advanced.ph);
  const turbOk = reading.turbidity <= CONFIG.advanced.turbidity.max;

  const score = (Number(tdsOk) + Number(phOk) + Number(turbOk)) / 3;

  // Final rule: if any advanced metric is clearly unsafe, mark non-drinkable.
  const drinkable = tdsOk && phOk && turbOk;

  return { drinkable, score, checks: { tdsOk, phOk, turbOk } };
}

function formatReading(reading) {
  els.tdsVal.textContent = reading.tds.toFixed(0);
  els.phVal.textContent = reading.ph.toFixed(2);
  els.turbVal.textContent = reading.turbidity.toFixed(2);
}

function setMetricStatus(metricEl, statusEl, ok, labelOk, labelBad) {
  metricEl.classList.remove("good", "bad", "warn");
  statusEl.textContent = ok ? labelOk : labelBad;
  metricEl.classList.add(ok ? "good" : "bad");
}

function ensureCharts() {
  if (charts) return charts;

  const common = {
    type: "line",
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350 },
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(7,10,18,.88)",
          borderColor: "rgba(255,255,255,.10)",
          borderWidth: 1,
          titleColor: "#EAF0FF",
          bodyColor: "#A9B3D3",
          displayColors: false,
        },
      },
      scales: {
        x: {
          ticks: { color: "rgba(169,179,211,.75)", maxTicksLimit: 6 },
          grid: { color: "rgba(255,255,255,.06)" },
        },
        y: {
          ticks: { color: "rgba(169,179,211,.75)", maxTicksLimit: 5 },
          grid: { color: "rgba(255,255,255,.06)" },
        },
      },
    },
  };

  const mk = (canvasId, color) => {
    const ctx = $(canvasId).getContext("2d");
    return new Chart(ctx, {
      ...common,
      data: {
        labels: [],
        datasets: [
          {
            data: [],
            borderColor: color,
            pointRadius: 1.8,
            pointHoverRadius: 3,
            pointHitRadius: 10,
            borderWidth: 2,
            tension: 0.35,
            spanGaps: true,
            showLine: true,
            pointBackgroundColor: color,
            pointBorderColor: color,
            fill: false,
            backgroundColor: gradient(ctx, color),
          },
        ],
      },
    });
  };

  charts = {
    tds: mk("chartTds", "rgba(93,225,255,1)"),
    ph: mk("chartPh", "rgba(166,139,255,1)"),
    turb: mk("chartTurb", "rgba(255,139,212,1)"),
  };

  return charts;
}

function gradient(ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 160);
  g.addColorStop(0, color.replace("1)", "0.22)"));
  g.addColorStop(1, "rgba(255,255,255,0)");
  return g;
}

function pushChartPoint(chart, label, value) {
  if (!Number.isFinite(value)) return;
  chart.data.labels.push(label);
  chart.data.datasets[0].data.push(value);
  while (chart.data.labels.length > CONFIG.charts.maxPoints) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
  }
}

function autoscaleY(chart, { floor = 0, minRange = 1, padRatio = 0.15 } = {}) {
  const vals = chart.data.datasets[0].data.filter((v) => Number.isFinite(v));
  if (!vals.length) return;

  const rawMin = Math.min(...vals);
  const rawMax = Math.max(...vals);
  const center = (rawMin + rawMax) / 2;
  const range = Math.max(rawMax - rawMin, minRange);
  const pad = range * padRatio;

  let min = center - range / 2 - pad;
  let max = center + range / 2 + pad;
  if (Number.isFinite(floor)) min = Math.max(floor, min);
  if (max <= min) max = min + minRange;

  chart.options.scales.y.min = Number(min.toFixed(2));
  chart.options.scales.y.max = Number(max.toFixed(2));
}

function updateCharts(chartGroup, mode = "none") {
  autoscaleY(chartGroup.tds, chartScaleConfig.tds);
  autoscaleY(chartGroup.ph, chartScaleConfig.ph);
  autoscaleY(chartGroup.turb, chartScaleConfig.turb);
  chartGroup.tds.update(mode);
  chartGroup.ph.update(mode);
  chartGroup.turb.update(mode);
}

function clearChartData(chart) {
  chart.data.labels = [];
  chart.data.datasets[0].data = [];
}

function nowLabel() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(
    d.getSeconds()
  ).padStart(2, "0")}`;
}

async function fetchLatestReading() {
  if (!state.api.enabled) return await fetchLatestReadingDemo();
  try {
    return await fetchLatestReadingFromBackend();
  } catch (e) {
    // Fail-safe: if backend is down / misconfigured, auto-fallback to demo mode.
    state.api.enabled = false;
    setApiUi();
    return await fetchLatestReadingDemo();
  }
}

async function fetchLatestReadingDemo() {
  // Demo reading generator (slightly noisy, biased towards safe water).
  return {
    tds: randNormal(220, 95, 60, 900),
    ph: randNormal(7.2, 0.35, 4.8, 10.2),
    turbidity: randNormal(1.8, 1.1, 0.1, 18),
    // Provide RI so "Use realtime sample" can still work in demo mode.
    ri: randNormal(1.333, 0.007, 1.28, 1.40),
    water_level: randNormal(60, 18, 0, 120),
    timestamp: new Date().toISOString(),
  };
}

async function apiGet(path) {
  const url = `${state.api.base}${path}`;
  const res = await fetch(url, { method: "GET" });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${path}`);
  return await res.json();
}

async function fetchLatestReadingFromBackend() {
  // Ensure there is at least one record.
  await apiGet("/water/generate");
  // Use raw latest row (always present if generate succeeded).
  const latest = await apiGet("/water/latest");
  return {
    tds: Number(latest.tds),
    ph: Number(latest.ph),
    turbidity: Number(latest.turbidity),
    ri: Number(latest.ri),
    water_level: Number(latest.water_level),
    timestamp: String(latest.timestamp ?? new Date().toISOString()),
  };
}

async function fetchTrendReadingsFromBackend(limit = 20) {
  const out = await apiGet(`/water/trend?limit=${encodeURIComponent(String(limit))}`);
  const points = Array.isArray(out?.points) ? out.points : [];
  return points.map((p) => ({
    tds: Number(p.tds),
    ph: Number(p.ph),
    turbidity: Number(p.turbidity),
    timestamp: String(p.timestamp ?? new Date().toISOString()),
  }));
}

function randNormal(mean, sd, min, max) {
  // Box-Muller transform
  let u = 0,
    v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
  const n = mean + z * sd;
  return Math.max(min, Math.min(max, n));
}

async function runAdvancedOnce() {
  if (!state.prePassed) return;

  setBadge(els.advBadge, "badge--soft", "Running…");
  setResult(els.advResult, "result--muted", "Collecting TDS, pH, Turbidity…");

  els.btnRunAdv.disabled = true;
  els.btnSimulateStream.disabled = true;

  // Small delay for UI feel
  await sleep(650);

  const reading = await fetchLatestReading();
  state.lastReading = reading;

  const evald = evaluateAdvanced(reading);

  const c = ensureCharts();
  // "Run advanced layer" should show the latest test only.
  // Continuous history is reserved for the dedicated stream button.
  clearChartData(c.tds);
  clearChartData(c.ph);
  clearChartData(c.turb);

  let plotted = false;
  if (state.api.enabled) {
    try {
      const trend = await fetchTrendReadingsFromBackend(24);
      for (const p of trend) {
        const label = p.timestamp ? new Date(p.timestamp).toLocaleTimeString() : nowLabel();
        const before = c.tds.data.datasets[0].data.length;
        pushChartPoint(c.tds, label, p.tds);
        pushChartPoint(c.ph, label, p.ph);
        pushChartPoint(c.turb, label, p.turbidity);
        if (c.tds.data.datasets[0].data.length > before) plotted = true;
      }
    } catch (e) {
      // If trend endpoint is unavailable, fall back to plotting the latest point.
    }
  }

  if (!plotted) {
    const label = nowLabel();
    const before = c.tds.data.datasets[0].data.length;
    pushChartPoint(c.tds, label, reading.tds);
    pushChartPoint(c.ph, label, reading.ph);
    pushChartPoint(c.turb, label, reading.turbidity);
    plotted = c.tds.data.datasets[0].data.length > before;
  }

  if (!plotted) {
    setResult(
      els.advResult,
      "result--bad",
      "No valid chart data returned from backend. Check /water/latest and /water/trend values."
    );
  }
  updateCharts(c, "none");

  formatReading(reading);

  setMetricStatus(
    $("metricTds"),
    els.tdsStatus,
    evald.checks.tdsOk,
    `Good (≤ ${CONFIG.advanced.tds.max} ppm)`,
    `High (> ${CONFIG.advanced.tds.max} ppm)`
  );
  setMetricStatus(
    $("metricPh"),
    els.phStatus,
    evald.checks.phOk,
    `Good (${CONFIG.advanced.ph.min}–${CONFIG.advanced.ph.max})`,
    `Out of range`
  );
  setMetricStatus(
    $("metricTurb"),
    els.turbStatus,
    evald.checks.turbOk,
    `Good (≤ ${CONFIG.advanced.turbidity.max} NTU)`,
    `High (> ${CONFIG.advanced.turbidity.max} NTU)`
  );

  const tone = evald.drinkable ? "good" : "bad";
  const headline = evald.drinkable ? "Drinkable (passes advanced layer)" : "Non‑drinkable (fails advanced layer)";
  const chip = evald.drinkable ? "Drinkable" : "Non‑drinkable";
  const conf = 0.55 + evald.score * 0.45;

  els.decisionVal.textContent = chip;
  els.decisionSub.textContent = evald.drinkable
    ? "All advanced checks are within thresholds."
    : "One or more advanced checks exceeded thresholds.";

  setResult(
    els.advResult,
    evald.drinkable ? "result--good" : "result--bad",
    evald.drinkable
      ? "Advanced layer passed. Water is considered drinkable."
      : "Advanced layer failed. Water is considered non-drinkable."
  );

  setVerdictCard({
    tone,
    chip,
    conf,
    headline,
    sub: state.prePassed
      ? "Pre-analysis passed. Final verdict is based on advanced tests + thresholds."
      : "Pre-analysis failed, so advanced layer did not run.",
  });

  els.miniAdv.textContent = "Completed";
  els.miniFinal.textContent = evald.drinkable ? "Drinkable" : "Non‑drinkable";
  setStepper({ pre: "done", adv: "done" });

  setBadge(els.advBadge, evald.drinkable ? "badge--good" : "badge--bad", evald.drinkable ? "Passed" : "Failed");

  els.btnRunAdv.disabled = false;
  els.btnSimulateStream.disabled = false;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function simulateStream(msTotal = 15000, interval = 1000) {
  if (!state.prePassed || state.streaming) return;
  state.streaming = true;

  setBadge(els.advBadge, "badge--soft", "Streaming…");
  setResult(
    els.advResult,
    "result--muted",
    state.api.enabled
      ? "Streaming from backend… (polling /water/generate + /water/latest)"
      : "Simulating sensor stream… (updating charts)"
  );

  els.btnRunAdv.disabled = true;
  els.btnSimulateStream.disabled = true;

  const c = ensureCharts();
  const started = Date.now();
  const prevAnim = {
    tds: c.tds.options.animation?.duration ?? 0,
    ph: c.ph.options.animation?.duration ?? 0,
    turb: c.turb.options.animation?.duration ?? 0,
  };
  // Disable animation for smoother realtime streams.
  c.tds.options.animation = false;
  c.ph.options.animation = false;
  c.turb.options.animation = false;

  // Batch chart updates to reduce main-thread work.
  let buffered = [];
  let lastChartFlush = 0;

  const flushCharts = () => {
    if (!buffered.length) return;
    const points = buffered;
    buffered = [];

    for (const p of points) {
      pushChartPoint(c.tds, p.label, p.tds);
      pushChartPoint(c.ph, p.label, p.ph);
      pushChartPoint(c.turb, p.label, p.turbidity);
    }

    updateCharts(c, "none");
  };

  while (Date.now() - started < msTotal) {
    const reading = await fetchLatestReading();
    state.lastReading = reading;
    formatReading(reading);

    buffered.push({ label: nowLabel(), ...reading });

    const now = performance.now();
    const minDelta = 1000 / CONFIG.charts.chartFps;
    if (now - lastChartFlush >= minDelta) {
      lastChartFlush = now;
      flushCharts();
    }

    await sleep(interval);
  }

  flushCharts();
  c.tds.options.animation = { duration: prevAnim.tds };
  c.ph.options.animation = { duration: prevAnim.ph };
  c.turb.options.animation = { duration: prevAnim.turb };

  state.streaming = false;
  setBadge(els.advBadge, "badge--soft", "Ready");
  setResult(els.advResult, "result--muted", "Stream ended. Run advanced layer to compute final verdict.");
  els.btnRunAdv.disabled = false;
  els.btnSimulateStream.disabled = false;
}

function resetAll() {
  // Preserve API config across resets.
  state = {
    ...state,
    prePassed: false,
    lastReading: null,
    streaming: false,
    streamTimer: null,
  };

  els.preForm.reset();
  setBadge(els.preBadge, "badge--soft", "Not evaluated");
  setResult(els.preResult, "result--muted", "Enter PPI and RI to start screening.");
  els.miniPre.textContent = "Pending";

  lockAdvancedLayer();

  els.tdsVal.textContent = "—";
  els.phVal.textContent = "—";
  els.turbVal.textContent = "—";
  els.tdsStatus.textContent = "Awaiting test";
  els.phStatus.textContent = "Awaiting test";
  els.turbStatus.textContent = "Awaiting test";
  $("metricTds").classList.remove("good", "bad", "warn");
  $("metricPh").classList.remove("good", "bad", "warn");
  $("metricTurb").classList.remove("good", "bad", "warn");

  els.decisionVal.textContent = "—";
  els.decisionSub.textContent = "Run the advanced layer to see final verdict.";
  els.miniFinal.textContent = "—";

  setVerdictCard({
    tone: "idle",
    chip: "Waiting for input",
    conf: null,
    headline: "Run pre-analysis to begin",
    sub: "Enter PPI and RI. If screening passes, advanced layer runs automatically.",
  });

  setStepper({ pre: "active", adv: "idle" });

  if (charts) {
    Object.values(charts).forEach((ch) => {
      ch.data.labels = [];
      ch.data.datasets[0].data = [];
      ch.update();
    });
  }
}

function setDemoSample() {
  // A "good" sample by default.
  els.ppi.value = "0.78";
  els.ri.value = "1.333";
}

function scrollToAdvanced() {
  els.advCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Event wiring
els.preForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const ppi = parseNum(els.ppi.value);
  const ri = parseNum(els.ri.value);

  if (ppi == null || ri == null) {
    setResult(els.preResult, "result--bad", "Please enter valid numbers for PPI and RI.");
    return;
  }

  const out = preAnalysis(ppi, ri);
  state.prePassed = out.pass;

  if (out.pass) {
    setBadge(els.preBadge, "badge--good", "Passed");
    setResult(
      els.preResult,
      "result--good",
      `Pre-analysis passed. (PPI OK: ${out.checks.ppiOk ? "yes" : "no"}, RI OK: ${out.checks.riOk ? "yes" : "no"})`
    );
    els.miniPre.textContent = "Passed";
    setVerdictCard({
      tone: "warn",
      chip: "Pre-analysis passed",
      conf: out.confidence,
      headline: "Pre-analysis passed",
      sub: "Advanced layer unlocked. Run advanced tests for final drinkable verdict.",
    });
    unlockAdvancedLayer();
    await sleep(150);
    scrollToAdvanced();
  } else {
    setBadge(els.preBadge, "badge--bad", "Failed");
    setResult(
      els.preResult,
      "result--bad",
      `Pre-analysis failed. Water is considered non-drinkable (advanced layer will not run).`
    );
    els.miniPre.textContent = "Failed";
    els.miniFinal.textContent = "Non‑drinkable";
    lockAdvancedLayer();
    setStepper({ pre: "done", adv: "idle" });
    setVerdictCard({
      tone: "bad",
      chip: "Non‑drinkable",
      conf: out.confidence,
      headline: "Non‑drinkable (failed pre-analysis)",
      sub: "Advanced layer is skipped because screening failed.",
    });
  }
});

els.btnRunAdv.addEventListener("click", runAdvancedOnce);
els.btnSimulateStream.addEventListener("click", () => simulateStream(15000, CONFIG.charts.streamIntervalMs));
els.btnSkipToAdv.addEventListener("click", scrollToAdvanced);
els.btnReset.addEventListener("click", resetAll);
els.btnDemo.addEventListener("click", () => {
  setDemoSample();
  setResult(els.preResult, "result--muted", "Demo sample filled. Click “Run pre-analysis”.");
});

els.btnRealtimeSample?.addEventListener("click", async () => {
  try {
    const r = await fetchLatestReading();
    // Use RI from reading; PPI is still a separate (optical) measure, so we set a sensible placeholder.
    els.ppi.value = String((CONFIG.preAnalysis.ppi.min + CONFIG.preAnalysis.ppi.max) / 2);
    els.ri.value = r.ri != null ? String(Number(r.ri).toFixed(4)) : "1.3330";
    setResult(
      els.preResult,
      "result--muted",
      state.api.enabled
        ? "Realtime sample fetched from backend. Click “Run pre-analysis”."
        : "Sample generated locally. Click “Run pre-analysis”."
    );
  } catch (e) {
    // If anything goes wrong, fall back to a demo sample instead of erroring.
    setDemoSample();
    setResult(els.preResult, "result--muted", "Backend not reachable. Demo sample filled. Click “Run pre-analysis”.");
  }
});

state.api.base = getApiBase();

state.api.enabled = window.location.protocol !== "file:" || new URLSearchParams(window.location.search).has("api");
setApiUi();

resetAll();