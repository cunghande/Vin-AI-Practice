from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT / "outputs"
DATA_DIR = ROOT / "data"

JOB_LOCK = threading.Lock()
ACTIVE_JOB: dict | None = None


HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Reflexion Lab UI</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --line: #d8dee9;
      --text: #111827;
      --muted: #667085;
      --accent: #2563eb;
      --accent-2: #059669;
      --danger: #b42318;
      --shadow: 0 8px 22px rgba(17, 24, 39, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      letter-spacing: 0;
    }
    header {
      background: #101828;
      color: white;
      padding: 22px 28px;
      border-bottom: 4px solid var(--accent);
    }
    header h1 { margin: 0; font-size: 26px; font-weight: 750; }
    header p { margin: 6px 0 0; color: #cbd5e1; font-size: 14px; }
    main {
      display: grid;
      grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
      gap: 18px;
      padding: 18px;
      max-width: 1440px;
      margin: 0 auto;
    }
    section, aside {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    .panel-title {
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }
    h2 { margin: 0; font-size: 17px; }
    form { padding: 16px 18px 18px; display: grid; gap: 14px; }
    label { display: grid; gap: 6px; color: var(--muted); font-size: 13px; font-weight: 650; }
    input, select {
      width: 100%;
      height: 38px;
      border: 1px solid #cfd6e2;
      border-radius: 6px;
      padding: 8px 10px;
      font: inherit;
      color: var(--text);
      background: white;
    }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    button {
      height: 40px;
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      font-weight: 750;
      cursor: pointer;
    }
    button.secondary { background: #475467; }
    button:disabled { opacity: 0.55; cursor: not-allowed; }
    .hint { color: var(--muted); font-size: 12px; line-height: 1.45; margin: -4px 0 0; }
    .status {
      padding: 12px 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
    }
    .content { padding: 16px 18px 18px; }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 10px;
      margin-bottom: 16px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfe;
      min-height: 82px;
    }
    .metric span { color: var(--muted); font-size: 12px; font-weight: 700; }
    .metric strong { display: block; margin-top: 8px; font-size: 24px; }
    table {
      width: 100%;
      border-collapse: collapse;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      font-size: 13px;
    }
    th, td { padding: 10px 11px; border-bottom: 1px solid var(--line); text-align: right; }
    th:first-child, td:first-child { text-align: left; }
    th { background: #eef2f7; color: #344054; font-size: 12px; text-transform: uppercase; }
    tr:last-child td { border-bottom: 0; }
    .runs {
      display: grid;
      gap: 10px;
      max-height: 360px;
      overflow: auto;
      padding-right: 4px;
    }
    .run {
      width: 100%;
      text-align: left;
      background: #fbfcfe;
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-height: 62px;
      padding: 10px 12px;
      display: grid;
      gap: 4px;
    }
    .run.active { border-color: var(--accent); box-shadow: inset 3px 0 0 var(--accent); }
    .run-name { font-weight: 750; }
    .run-meta { color: var(--muted); font-size: 12px; }
    pre {
      margin: 0;
      background: #0b1220;
      color: #dbeafe;
      border-radius: 8px;
      padding: 12px;
      min-height: 120px;
      max-height: 260px;
      overflow: auto;
      white-space: pre-wrap;
      font-size: 12px;
      line-height: 1.45;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      height: 24px;
      padding: 0 8px;
      border-radius: 999px;
      background: #e0f2fe;
      color: #075985;
      font-size: 12px;
      font-weight: 750;
    }
    .error { color: var(--danger); }
    @media (max-width: 900px) {
      main { grid-template-columns: 1fr; padding: 12px; }
      .metrics { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
    }
  </style>
</head>
<body>
  <header>
    <h1>Reflexion Lab Runner</h1>
    <p>Run ReAct vs Reflexion benchmarks and inspect previous reports.</p>
  </header>
  <main>
    <aside>
      <div class="panel-title"><h2>Run Benchmark</h2><span id="jobBadge" class="badge">idle</span></div>
      <form id="runForm">
        <label>Dataset
          <select id="dataset"></select>
        </label>
        <div class="row">
          <label>Mode
            <select id="mode">
              <option value="mock">mock</option>
              <option value="llm">llm</option>
            </select>
          </label>
          <label>Limit
            <input id="limit" type="number" min="0" value="10" />
          </label>
        </div>
        <div class="row">
          <label>Model
            <input id="model" value="gpt-5.4-nano" />
          </label>
          <label>Attempts
            <input id="attempts" type="number" min="1" max="10" value="3" />
          </label>
        </div>
        <label>Output folder
          <input id="outDir" value="outputs/ui_run" />
        </label>
        <label>OpenAI API key
          <input id="apiKey" type="password" autocomplete="off" placeholder="Only required for llm mode" />
        </label>
        <p class="hint">The key is sent only to the local Python process as an environment variable and is not written to disk.</p>
        <button id="runButton" type="submit">Run</button>
      </form>
      <div class="status" id="status">Ready.</div>
    </aside>

    <section>
      <div class="panel-title">
        <h2>Current Report</h2>
        <button class="secondary" id="refreshButton" type="button">Refresh</button>
      </div>
      <div class="content">
        <div class="metrics" id="cards"></div>
        <div id="tableWrap"></div>
      </div>
    </section>

    <section>
      <div class="panel-title"><h2>Previous Runs</h2><span id="runCount" class="badge">0</span></div>
      <div class="content"><div class="runs" id="runs"></div></div>
    </section>

    <section>
      <div class="panel-title"><h2>Live Log</h2></div>
      <div class="content"><pre id="log">No active run.</pre></div>
    </section>
  </main>

  <script>
    let selectedRun = null;
    let pollTimer = null;

    const $ = (id) => document.getElementById(id);
    const fmtPct = (value) => `${(Number(value || 0) * 100).toFixed(2)}%`;
    const fmtNum = (value) => Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 2 });

    async function api(path, options) {
      const response = await fetch(path, options);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || response.statusText);
      return data;
    }

    async function loadDatasets() {
      const data = await api('/api/datasets');
      $('dataset').innerHTML = data.datasets.map((item) => `<option value="${item}">${item}</option>`).join('');
      if (data.datasets.includes('data/hotpot_data.json')) $('dataset').value = 'data/hotpot_data.json';
    }

    function metricCards(report) {
      const s = report?.summary || {};
      const react = s.react || {};
      const reflexion = s.reflexion || {};
      const delta = s.delta_reflexion_minus_react || {};
      return [
        ['ReAct EM', fmtPct(react.em)],
        ['Reflexion EM', fmtPct(reflexion.em)],
        ['EM Delta', fmtPct(delta.em_abs)],
        ['Extra Tokens', fmtNum(delta.tokens_abs)],
      ].map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${value}</strong></div>`).join('');
    }

    function metricsTable(report) {
      const s = report?.summary || {};
      const react = s.react || {};
      const reflexion = s.reflexion || {};
      const delta = s.delta_reflexion_minus_react || {};
      const rows = [
        ['Records', react.count, reflexion.count, ''],
        ['Correct', react.correct, reflexion.correct, ''],
        ['EM', fmtPct(react.em), fmtPct(reflexion.em), fmtPct(delta.em_abs)],
        ['Avg attempts', react.avg_attempts, reflexion.avg_attempts, delta.attempts_abs],
        ['Total tokens', react.total_token_estimate, reflexion.total_token_estimate, delta.tokens_abs],
        ['Avg tokens', react.avg_token_estimate, reflexion.avg_token_estimate, delta.avg_tokens_abs],
        ['Total latency ms', react.total_latency_ms, reflexion.total_latency_ms, delta.latency_abs],
        ['Avg latency ms', react.avg_latency_ms, reflexion.avg_latency_ms, delta.avg_latency_abs],
      ];
      return `<table><thead><tr><th>Metric</th><th>ReAct</th><th>Reflexion</th><th>Delta</th></tr></thead><tbody>${
        rows.map((row) => `<tr><td>${row[0]}</td><td>${fmtCell(row[1])}</td><td>${fmtCell(row[2])}</td><td>${fmtCell(row[3])}</td></tr>`).join('')
      }</tbody></table>`;
    }

    function fmtCell(value) {
      if (value === '') return '';
      if (typeof value === 'string' && value.endsWith('%')) return value;
      return fmtNum(value);
    }

    function renderReport(report) {
      $('cards').innerHTML = metricCards(report);
      $('tableWrap').innerHTML = metricsTable(report);
    }

    async function loadRuns() {
      const data = await api('/api/runs');
      $('runCount').textContent = String(data.runs.length);
      $('runs').innerHTML = data.runs.map((run) => {
        const active = run.path === selectedRun ? ' active' : '';
        const em = run.summary?.reflexion?.em !== undefined ? fmtPct(run.summary.reflexion.em) : 'n/a';
        return `<button class="run${active}" data-path="${run.path}">
          <span class="run-name">${run.name}</span>
          <span class="run-meta">${run.mode || 'unknown'} · ${run.records || 0} records · Reflexion EM ${em}</span>
        </button>`;
      }).join('');
      document.querySelectorAll('.run').forEach((button) => {
        button.addEventListener('click', () => selectRun(button.dataset.path));
      });
      if (!selectedRun && data.runs[0]) selectRun(data.runs[0].path);
    }

    async function selectRun(path) {
      selectedRun = path;
      const data = await api(`/api/report?path=${encodeURIComponent(path)}`);
      renderReport(data.report);
      await loadRuns();
    }

    async function startRun(event) {
      event.preventDefault();
      const body = {
        dataset: $('dataset').value,
        mode: $('mode').value,
        model: $('model').value,
        limit: Number($('limit').value || 0),
        reflexion_attempts: Number($('attempts').value || 3),
        out_dir: $('outDir').value,
        api_key: $('apiKey').value,
      };
      $('runButton').disabled = true;
      try {
        const data = await api('/api/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        $('status').textContent = data.message;
        $('apiKey').value = '';
        startPolling();
      } catch (error) {
        $('status').innerHTML = `<span class="error">${error.message}</span>`;
        $('runButton').disabled = false;
      }
    }

    async function pollJob() {
      const data = await api('/api/job');
      $('jobBadge').textContent = data.running ? 'running' : (data.status || 'idle');
      $('log').textContent = data.log || 'No active run.';
      $('runButton').disabled = data.running;
      if (!data.running) {
        clearInterval(pollTimer);
        pollTimer = null;
        if (data.report_path) {
          selectedRun = data.report_path;
          await loadRuns();
          await selectRun(data.report_path);
        } else {
          await loadRuns();
        }
      }
    }

    function startPolling() {
      if (pollTimer) clearInterval(pollTimer);
      pollTimer = setInterval(pollJob, 1200);
      pollJob();
    }

    $('runForm').addEventListener('submit', startRun);
    $('refreshButton').addEventListener('click', loadRuns);
    loadDatasets().then(loadRuns).then(pollJob);
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/":
                self._send_html(HTML)
            elif parsed.path == "/api/datasets":
                self._send_json({"datasets": list_datasets()})
            elif parsed.path == "/api/runs":
                self._send_json({"runs": list_runs()})
            elif parsed.path == "/api/report":
                query = _query(parsed.query)
                self._send_json({"report": load_report(query.get("path", ""))})
            elif parsed.path == "/api/job":
                self._send_json(get_job())
            else:
                self._send_json({"error": "not found"}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        try:
            if urlparse(self.path).path != "/api/run":
                self._send_json({"error": "not found"}, status=404)
                return
            payload = self._read_json()
            start_job(payload)
            self._send_json({"message": "Benchmark started."})
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def _read_json(self) -> dict:
        length = int(self.headers.get("content-length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def _send_html(self, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, body: dict, status: int = 200) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def _query(query_string: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for part in query_string.split("&"):
        if not part:
            continue
        key, _, value = part.partition("=")
        from urllib.parse import unquote_plus

        values[unquote_plus(key)] = unquote_plus(value)
    return values


def list_datasets() -> list[str]:
    files = sorted(path for path in DATA_DIR.glob("*.json") if path.is_file())
    return [str(path.relative_to(ROOT)).replace("\\", "/") for path in files]


def list_runs() -> list[dict]:
    runs = []
    for report_path in OUTPUTS_DIR.glob("*/report.json"):
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        runs.append(
            {
                "name": report_path.parent.name,
                "path": str(report_path.relative_to(ROOT)).replace("\\", "/"),
                "mode": report.get("meta", {}).get("mode", ""),
                "records": report.get("meta", {}).get("num_records", 0),
                "summary": report.get("summary", {}),
                "mtime": report_path.stat().st_mtime,
            }
        )
    runs.sort(key=lambda item: item["mtime"], reverse=True)
    return runs


def load_report(path_text: str) -> dict:
    path = (ROOT / path_text).resolve()
    if not _is_inside(path, OUTPUTS_DIR.resolve()) or path.name != "report.json":
        raise ValueError("Invalid report path.")
    return json.loads(path.read_text(encoding="utf-8"))


def start_job(payload: dict) -> None:
    global ACTIVE_JOB
    with JOB_LOCK:
        if ACTIVE_JOB and ACTIVE_JOB.get("running"):
            raise RuntimeError("A benchmark is already running.")
        ACTIVE_JOB = {
            "running": True,
            "status": "running",
            "log": "",
            "report_path": "",
            "started_at": time.time(),
        }
    thread = threading.Thread(target=_run_job, args=(payload,), daemon=True)
    thread.start()


def _run_job(payload: dict) -> None:
    dataset = str(payload.get("dataset") or "data/hotpot_data.json")
    mode = str(payload.get("mode") or "mock")
    model = str(payload.get("model") or "gpt-5.4-nano")
    out_dir = str(payload.get("out_dir") or "outputs/ui_run")
    limit = int(payload.get("limit") or 0)
    attempts = int(payload.get("reflexion_attempts") or 3)
    api_key = str(payload.get("api_key") or "").strip()

    if mode not in {"mock", "llm"}:
        _finish_job("failed", "Mode must be mock or llm.", "")
        return
    if mode == "llm" and not api_key and not os.getenv("OPENAI_API_KEY"):
        _finish_job("failed", "LLM mode needs an API key in the UI field or environment.", "")
        return

    command = [
        sys.executable,
        "run_benchmark.py",
        "--dataset",
        dataset,
        "--out-dir",
        out_dir,
        "--mode",
        mode,
        "--reflexion-attempts",
        str(attempts),
    ]
    if model:
        command.extend(["--model", model])
    if limit:
        command.extend(["--limit", str(limit)])

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    if api_key:
        env["OPENAI_API_KEY"] = api_key

    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        log_lines: list[str] = []
        assert process.stdout is not None
        for line in process.stdout:
            log_lines.append(line)
            _update_job_log("".join(log_lines)[-12000:])
        code = process.wait()
        report_path = str((Path(out_dir) / "report.json").as_posix())
        status = "complete" if code == 0 else "failed"
        _finish_job(status, "".join(log_lines)[-12000:], report_path if code == 0 else "")
    except Exception as exc:
        _finish_job("failed", str(exc), "")


def _update_job_log(log: str) -> None:
    with JOB_LOCK:
        if ACTIVE_JOB:
            ACTIVE_JOB["log"] = log


def _finish_job(status: str, log: str, report_path: str) -> None:
    with JOB_LOCK:
        if ACTIVE_JOB:
            ACTIVE_JOB.update({"running": False, "status": status, "log": log, "report_path": report_path})


def get_job() -> dict:
    with JOB_LOCK:
        if not ACTIVE_JOB:
            return {"running": False, "status": "idle", "log": "", "report_path": ""}
        return dict(ACTIVE_JOB)


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def main() -> None:
    port = int(os.getenv("REFLEXION_UI_PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Reflexion Lab UI running at http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
