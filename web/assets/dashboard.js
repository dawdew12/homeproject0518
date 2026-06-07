// AIPR 분리형 대시보드 페이지를 렌더링한다.
const REFRESH_INTERVAL_MS = 30000;

const API_ENDPOINTS = [
  ["status", "api/status.json"],
  ["agents", "api/agents.json"],
  ["costs", "api/costs.json"],
  ["brands", "api/brands.json"],
  ["history", "api/history/daily.json"],
  ["winner_loser", "api/winner-loser.json"],
  ["logs", "api/logs.json"]
];

const contentState = {
  selectedBrand: null,
  summary: {},
  brands: []
};

function $(id) {
  return document.getElementById(id);
}

function setText(id, value) {
  const node = $(id);
  if (node) node.textContent = value;
}

function setHtml(id, value) {
  const node = $(id);
  if (node) node.innerHTML = value;
}

function setWidth(id, value) {
  const node = $(id);
  if (node) node.style.width = value;
}

function tagClass(status) {
  return String(status || "").replaceAll(".", "_").replaceAll(" ", "_");
}

function tag(status) {
  return `<span class="tag ${tagClass(status)}">${status || "-"}</span>`;
}

function fmt(value, suffix = "") {
  if (value === null || value === undefined || value === "") return "-";
  return `${value}${suffix}`;
}

function money(value) {
  if (value === null || value === undefined || value === "") return "-";
  return `$${value}`;
}

function renderMetricGrid(id, items) {
  setHtml(id, items.map(item => `
    <div class="metric">
      <div class="label">${item.label}</div>
      <div class="value ${item.tone || ""}">${item.value}</div>
      ${item.note ? `<div class="page-note">${item.note}</div>` : ""}
    </div>
  `).join(""));
}

function renderTable(id, headers, rows, emptyText = "데이터 없음.") {
  const node = $(id);
  if (!node) return;
  const body = rows.length
    ? rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("")
    : `<tr><td colspan="${headers.length}" class="empty">${emptyText}</td></tr>`;
  node.innerHTML = `
    <table>
      <thead><tr>${headers.map(header => `<th>${header}</th>`).join("")}</tr></thead>
      <tbody>${body}</tbody>
    </table>
  `;
}

function renderCards(id, items, emptyText = "데이터 없음.") {
  setHtml(id, items.length ? items.join("") : `<div class="empty">${emptyText}</div>`);
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} 로드 실패`);
  return response.json();
}

async function loadDashboard() {
  return loadJson("data/latest_status.json");
}

async function loadApiSnapshot() {
  const now = new Date().toLocaleTimeString("ko-KR");
  return Promise.all(API_ENDPOINTS.map(async ([label, path]) => {
    try {
      await loadJson(path);
      return { label, ok: true, fetchedAt: now, path };
    } catch (error) {
      return { label, ok: false, fetchedAt: now, path, error: error.message };
    }
  }));
}

function renderCommon(data) {
  const page = document.body.dataset.page || "team";
  document.querySelectorAll(".page-nav a").forEach(link => {
    link.classList.toggle("active", link.dataset.page === page);
  });
  setText("deploy-status", `생성 시각 ${data.generated_at || "-"}`);
  setText("page-generated-at", data.generated_at || "-");
}

function renderApiStatus(results) {
  const successful = results.filter(result => result.ok).length;
  setText("api-refresh-state", `${successful}/${results.length}`);
  renderTable(
    "api-table",
    ["엔드포인트", "상태", "갱신 시각", "파일"],
    results.map(result => [
      `<code>${result.label}</code>`,
      tag(result.ok ? "passed" : "regeneration_required"),
      result.fetchedAt,
      `<code>${result.path}</code>`
    ])
  );
}

function renderTeamPage(data) {
  const current = data.current_phase || {};
  const dashboardData = data.data || {};
  const ad = dashboardData.ad || {};
  const trend = dashboardData.trend || {};
  const manager = dashboardData.manager || {};
  const prompts = dashboardData.prompts || {};
  const images = dashboardData.images || {};
  const quality = dashboardData.quality_review || {};
  const learning = dashboardData.winner_loser || {};
  const storage = dashboardData.storage || {};
  const gdrive = storage.gdrive || {};
  const content = dashboardData.content_generation || {};
  const portal = dashboardData.portal_sns_clips || {};
  const verification = data.verification || {};

  renderMetricGrid("overview-metrics", [
    { label: "현재 Phase", value: current.current_phase ?? "-", tone: "info" },
    { label: "상태", value: current.status || "-", tone: "ok" },
    { label: "광고 레코드", value: ad.record_count ?? 0 },
    { label: "트렌드 레코드", value: trend.record_count ?? 0 },
    { label: "팀장 분석", value: manager.brand_count ?? 0, tone: "info" },
    { label: "저장 계획", value: gdrive.planned_upload_count ?? 0, tone: "info" }
  ]);

  renderMetricGrid("live-test-grid", [
    { label: "검증 결과", value: `${verification.test_count ?? 0} 통과`, tone: "ok", note: verification.last_result || "-" },
    { label: "콘텐츠 생성", value: `${content.brand_count ?? 0}브랜드`, tone: "info", note: `시트 ${content.generated_sheet_count ?? 0}장 · 슬롯 ${content.image_slot_count ?? 0}개` },
    { label: "포털/SNS 수집", value: `${portal.clip_count ?? 0}클립`, tone: "info", note: `기사 ${portal.article_link_count ?? 0}건 · 요약 ${portal.summary_line_count ?? 0}줄` },
    { label: "프로젝트 API 과금", value: content.charged_in_project_budget ? "과금 있음" : "$0", tone: "ok", note: content.api_call_skip_reason || "내장 도구 테스트" }
  ]);

  const progress = data.architecture?.overall_progress || {};
  setText("overall-percent", `${progress.percent ?? 0}%`);
  setText("overall-summary", `${progress.completed_phase_count ?? 0}/${progress.total_phase_count ?? 0} phases completed · 다음 ${progress.next_phase || "-"}`);
  setWidth("overall-progress-fill", `${progress.percent ?? 0}%`);

  renderCards("phase-roadmap", (data.architecture?.phase_roadmap || []).map(item => `
    <div class="phase ${tagClass(item.status)}">
      <strong>${item.phase}</strong>
      <div class="label">${item.title}</div>
      ${tag(item.status)}
    </div>
  `));

  renderCards("architecture-map", (data.architecture?.layers || []).map(layer => `
    <div class="arch-layer">
      <h3>${layer.layer}</h3>
      <div class="label">${layer.title}</div>
      ${(layer.nodes || []).map(node => `
        <div class="arch-node">
          <span class="node-title">${node.label}</span>
          <span class="node-metric">${node.metric}</span>
          ${tag(node.status)}
        </div>
      `).join("")}
    </div>
  `));

  renderCards("architecture-flow", (data.architecture?.flow || []).map(item => `
    <div class="flow-item">
      <strong>${item.from}</strong><span class="flow-arrow">→</span><strong>${item.to}</strong>
      <div class="label">${item.artifact}</div>
      ${tag(item.status)}
    </div>
  `));

  renderTable(
    "phase-tests",
    ["Phase", "범위", "검증", "결과", "테스트", "산출물"],
    (data.quality?.phase_test_results || []).map(item => [
      `<strong>${item.phase}</strong>`,
      item.scope,
      `<code>${item.check}</code>`,
      tag(item.result),
      item.test_count,
      `<code>${item.artifact}</code>`
    ])
  );

  renderCards("feature-status", (data.operations?.feature_status || []).map(item => `
    <div class="tile">
      <h3>${item.name}</h3>
      ${tag(item.status)}
      <ul>${(item.details || []).map(detail => `<li>${detail}</li>`).join("")}</ul>
    </div>
  `));

  renderTable(
    "data-status-table",
    ["항목", "상태", "수치"],
    [
      ["광고 데이터", tag(ad.status), `${ad.record_count ?? 0} records · ${ad.source_count ?? 0} sources`],
      ["트렌드 데이터", tag(trend.status), `${trend.record_count ?? 0} records · ${trend.source_count ?? 0} sources`],
      ["팀장 분석", tag(manager.status), `${manager.brand_count ?? 0} brands · ${manager.handoff_count ?? 0} handoff`],
      ["프롬프트 Pack", tag(prompts.status), `${prompts.storyboard_count ?? 0} storyboards · ${prompts.prompt_count ?? 0} prompts`],
      ["이미지 요청", tag(images.status), `${images.request_count ?? 0} requests · ${money(images.estimated_cost_usd)}`],
      ["품질 검수", tag(quality.status), `${quality.approved_count ?? 0}/${quality.request_count ?? 0} approved`],
      ["Winner/Loser", tag(learning.status), `winner ${learning.winner_count ?? 0} · pending ${learning.pending_count ?? 0}`]
    ]
  );

  const next = data.next_step || {};
  setHtml("next-step", `
    <h3>${next.phase || "-"} · ${next.title || ""}</h3>
    <p class="sub">${next.summary || "-"}</p>
  `);
  setHtml("risks", (data.risks || []).map(risk => `<li>${risk}</li>`).join(""));
}

function routinePartLines(part) {
  const metrics = part.metrics || {};
  if (part.part_no === "1") {
    return [
      `광고 ${metrics.record_count ?? 0}건 · 매체 ${metrics.source_count ?? 0}`,
      `CTR ${fmt(metrics.avg_ctr, "%")} · ROAS ${fmt(metrics.avg_roas, "%")}`,
      `클릭 ${metrics.total_clicks ?? 0} · 전환 ${metrics.total_conversions ?? 0}`
    ];
  }
  if (part.part_no === "2") {
    return [
      `트렌드 ${metrics.record_count ?? 0}건 · 출처 ${metrics.source_count ?? 0}`,
      `점수 ${metrics.avg_trend_score ?? 0} · 변화율 ${fmt(metrics.avg_trend_change_pct, "%")}`,
      (metrics.top_keywords || []).slice(0, 3).join(", ") || "-"
    ];
  }
  if (part.part_no === "3") {
    return [
      `우선순위 ${metrics.priority || "-"}`,
      `점수 ${metrics.score || 0}`,
      metrics.creative_direction || "-"
    ];
  }
  return [
    `스토리보드 ${metrics.storyboard_count ?? 0}개 · 프롬프트 ${metrics.prompt_count ?? 0}개`,
    `이미지 요청 ${metrics.image_request_count ?? 0}개 · 비용 ${money(metrics.estimated_cost_usd)}`,
    metrics.output_dir || "-"
  ];
}

function renderAutomationPage(data, apiResults) {
  renderCards("pipeline", (data.operations?.pipeline_steps || []).map(step => `
    <div class="step">
      <div class="step-num">STEP ${step.step}</div>
      <strong>${step.title}</strong>
      <div class="label">${step.owner}</div>
      ${tag(step.status)}
    </div>
  `));

  renderCards("agent-list", (data.operations?.agent_status || []).map(agent => `
    <div class="agent">
      <h3>${agent.agent}</h3>
      <div class="label">${agent.file}</div>
      ${tag(agent.status)}
      <ul>${(agent.implemented || []).map(item => `<li>${item}</li>`).join("")}</ul>
      <div class="label">출력 ${agent.output}</div>
    </div>
  `));

  renderCards("brand-routine-board", (data.data?.brand_routine_matrix || []).map(brand => `
    <div class="routine-brand">
      <div class="routine-head">
        <div>
          <h3>${brand.display_name || brand.brand}</h3>
          <div class="label">${brand.brand} · ${brand.date || "-"}</div>
        </div>
        ${tag(`${brand.ready_part_count}/${brand.total_part_count}`)}
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:${brand.completion_percent || 0}%"></div></div>
      <div class="routine-parts" style="margin-top:10px">
        ${(brand.parts || []).map(part => `
          <div class="routine-part">
            <div class="routine-part-top">
              <div>
                <div class="routine-no">PART ${part.part_no}</div>
                <strong>${part.label}</strong>
                <div class="label">${part.owner}</div>
              </div>
              ${tag(part.status)}
            </div>
            <div class="routine-lines">${routinePartLines(part).map(line => `<div>${line}</div>`).join("")}</div>
          </div>
        `).join("")}
      </div>
    </div>
  `));

  const logs = apiResults.find(result => result.label === "logs")?.payload?.execution || [];
  renderTable(
    "log-table",
    ["라인", "내용"],
    logs.slice(-10).reverse().map(line => [line.line_no, line.text]),
    "실행 로그 없음."
  );

  renderTable(
    "storage-table",
    ["Prompt ID", "브랜드", "분류", "원본 파일", "상태", "Google Drive 경로"],
    (data.data?.storage?.gdrive_preview || []).map(item => [
      `<code>${item.prompt_id}</code>`,
      item.brand,
      tag(item.classification),
      item.source_exists ? "있음" : "미생성",
      tag(item.status),
      `<code>${item.drive_path}</code>`
    ])
  );
}

function renderContentPage(data) {
  const content = data.data?.content_generation || {};
  const brands = data.data?.content_generation_brands || [];
  const chatgptImage = data.data?.chatgpt_image_test || {};
  const quality = data.data?.quality_review || {};

  renderMetricGrid("content-summary-grid", [
    { label: "브랜드", value: content.brand_count ?? brands.length, tone: "info" },
    { label: "생성 시트", value: content.generated_sheet_count ?? brands.length },
    { label: "소재 슬롯", value: content.image_slot_count ?? 0 },
    { label: "검수", value: content.visual_check_status || "-", tone: "ok" }
  ]);

  renderContentGeneration(content, brands);

  const preview = $("generated-image-preview");
  if (preview && chatgptImage.dashboard_asset_path) {
    preview.src = chatgptImage.dashboard_asset_path;
    preview.hidden = false;
  }
  renderTable(
    "generated-image-table",
    ["항목", "값"],
    [
      ["상태", `${chatgptImage.status || "-"} · ${chatgptImage.mode || "-"}`],
      ["브랜드", `${chatgptImage.brand || "-"} · ${chatgptImage.image_type_label || "-"}`],
      ["크기", chatgptImage.exists ? `${chatgptImage.width || "-"}x${chatgptImage.height || "-"} · ${chatgptImage.file_size_bytes || 0} bytes` : "-"],
      ["프로젝트 API 호출", chatgptImage.project_openai_api_call_attempted ? "호출" : `미호출 · ${chatgptImage.api_call_skip_reason || "-"}`],
      ["저장 위치", `<code>${chatgptImage.local_output_path || "-"}</code>`]
    ]
  );

  renderTable(
    "prompt-table",
    ["Prompt ID", "브랜드", "유형", "품질", "파일명", "규칙"],
    (data.data?.prompt_preview || []).map(item => [
      `<code>${item.prompt_id}</code>`,
      item.brand,
      item.image_type_label,
      item.quality,
      `<code>${item.file_name_preview}</code>`,
      (item.rules || []).join("<br>")
    ])
  );

  renderTable(
    "image-table",
    ["Prompt ID", "브랜드", "유형", "품질", "예상 비용", "상태", "출력 경로"],
    (data.data?.image_preview || []).map(item => [
      `<code>${item.prompt_id}</code>`,
      item.brand,
      item.image_type_label,
      item.quality,
      money(item.estimated_cost_usd),
      tag(item.status),
      `<code>${item.output_path}</code>`
    ])
  );

  renderTable(
    "quality-table",
    ["Prompt ID", "브랜드", "유형", "점수", "상태", "재생성", "사유"],
    (data.data?.quality_preview || []).map(item => [
      `<code>${item.prompt_id}</code>`,
      item.brand,
      item.image_type_label,
      item.score,
      tag(item.status),
      item.regeneration_needed ? "필요" : "없음",
      item.reason || "-"
    ])
  );

  renderTable(
    "learning-table",
    ["Creative ID", "브랜드", "매체", "분류", "CTR", "ROAS", "CPA", "사유", "다음 액션"],
    (data.data?.learning_preview || []).map(item => [
      `<code>${item.creative_id}</code>`,
      item.brand,
      item.source,
      tag(item.label),
      fmt(item.ctr, "%"),
      fmt(item.roas, "%"),
      money(item.cpa),
      item.reason || "-",
      item.action || "-"
    ])
  );

  renderMetricGrid("content-quality-metrics", [
    { label: "품질 요청", value: quality.request_count ?? 0 },
    { label: "승인", value: quality.approved_count ?? 0, tone: "ok" },
    { label: "평균 점수", value: quality.avg_score ?? 0, tone: "info" },
    { label: "재생성", value: quality.regeneration_required_count ?? 0, tone: "warn" }
  ]);
}

function renderContentGeneration(summary, brands) {
  if (!brands.length) {
    setHtml("content-asset", `<div class="empty">콘텐츠 생성 데이터 없음.</div>`);
    setHtml("content-brand-tabs", "");
    setHtml("content-concepts", "");
    setHtml("content-process", "");
    return;
  }

  const selected = brands.some(item => item.brand === contentState.selectedBrand)
    ? contentState.selectedBrand
    : brands[0].brand;
  const active = brands.find(item => item.brand === selected) || brands[0];
  contentState.selectedBrand = selected;
  contentState.summary = summary;
  contentState.brands = brands;

  setHtml("content-brand-tabs", brands.map(brand => `
    <button class="${brand.brand === selected ? "on" : ""}" onclick="selectContentBrand('${brand.brand}')">${brand.display_name || brand.brand}</button>
  `).join(""));

  setHtml("content-asset", `
    <h3>${active.display_name || active.brand}</h3>
    <p class="sub">${active.category || "-"} · ${summary.mode || "-"}</p>
    <img src="${active.sheet_asset_path}" alt="${active.display_name || active.brand} 5컷 콘텐츠 시트">
    <div class="label">${active.width || "-"}x${active.height || "-"} · ${active.file_size_bytes || 0} bytes</div>
    <div class="label"><code>${active.local_output_path || active.sheet_asset_path}</code></div>
  `);

  setHtml("content-concepts", (active.concepts || []).map(concept => `
    <div class="concept-card">
      <strong>${concept.slot}. ${concept.title}</strong>
      <div class="label">${concept.format || "-"} · ${concept.status || "-"}</div>
      <div>${concept.angle || "-"}</div>
    </div>
  `).join(""));

  setHtml("content-process", (summary.process_steps || []).map(step => `
    <div class="process-card">
      <strong>STEP ${step.step}. ${step.label}</strong>
      <div class="label">${step.status || "-"}</div>
      <div>${step.note || "-"}</div>
    </div>
  `).join(""));
}

function selectContentBrand(brand) {
  contentState.selectedBrand = brand;
  renderContentGeneration(contentState.summary, contentState.brands);
}

window.selectContentBrand = selectContentBrand;

function renderResearchPage(data) {
  const trend = data.data?.trend || {};
  const portal = data.data?.portal_sns_clips || {};
  const sourceCounts = data.data?.marketing_source_counts || {};

  renderMetricGrid("research-snapshot-grid", [
    { label: "포털/SNS 클립", value: `${portal.clip_count ?? 0}건`, tone: "info", note: `${portal.date || "-"} live 수집` },
    { label: "기사 링크", value: `${portal.article_link_count ?? 0}건`, tone: "info", note: "전체 시사점 1줄 포함" },
    { label: "트렌드 브리핑", value: `${trend.record_count ?? 0}건`, tone: "ok", note: `${trend.source_count ?? 0}출처 × ${trend.brand_count ?? 0}브랜드` }
  ]);

  setHtml("portal-article-brief", `<strong>전체 시사점.</strong> ${portal.overall_implication || "기사 링크 시사점 데이터 없음."}`);
  renderCards("portal-article-links", (data.data?.portal_sns_article_links || []).map(item => `
    <div class="article-link-item">
      <div class="label">${item.display_name || item.brand} · ${item.source_site || "기사"}</div>
      <a href="${item.url}" target="_blank" rel="noreferrer">${item.title || item.query || "기사 링크"}</a>
    </div>
  `), "수집된 기사 링크 없음.");

  renderCards("portal-sns-board", (data.data?.portal_sns_daily_briefs || []).map(brand => {
    const clips = (brand.clips || []).slice(0, 6);
    return `
      <div class="portal-sns-card">
        <div class="routine-head">
          <div>
            <h3>${brand.display_name || brand.brand}</h3>
            <div class="label">${brand.brand} · ${brand.date || "-"}</div>
          </div>
          ${tag(`포털 ${brand.portal_clip_count || 0} · SNS ${brand.sns_clip_count || 0}`)}
        </div>
        <ol class="summary-lines">${(brand.summary_3_lines || []).map(line => `<li>${line}</li>`).join("")}</ol>
        <div class="clip-links">
          ${clips.map(clip => `
            <a class="clip-link" href="${clip.url}" target="_blank" rel="noreferrer">${clip.source_type === "portal_news" ? "포털" : "SNS"} · ${clip.source_site || clip.source_name}</a>
          `).join("")}
        </div>
      </div>
    `;
  }), "포털/SNS 일간 클리핑 데이터 없음.");

  renderTable(
    "trend-briefing-table",
    ["No", "브랜드", "수집 출처", "키워드", "점수", "변화율", "시즌 이슈", "경쟁사", "브리핑"],
    (data.data?.trend_briefing_list || []).map(item => [
      item.sequence,
      `<strong>${item.display_name || item.brand}</strong><br><code>${item.brand}</code>`,
      item.source_label,
      (item.keywords || []).join(", "),
      item.trend_score,
      `${item.trend_change_pct}%`,
      `${item.seasonal_issue_title || "-"}<br>${tag(item.seasonal_issue_level)}`,
      item.competitor_detected ? "감지" : "없음",
      item.briefing || "-"
    ])
  );

  setHtml("monitoring-sources", (data.data?.monitoring_preview?.daily || [])
    .map(source => `<span class="chip">${source.source_name}</span>`)
    .join(""));

  renderMetricGrid("source-counts", [
    { label: "Daily 출처", value: sourceCounts.daily ?? 0 },
    { label: "Weekly 출처", value: sourceCounts.weekly ?? 0 },
    { label: "Monthly 출처", value: sourceCounts.monthly ?? 0 }
  ]);

  renderTable(
    "brand-table",
    ["브랜드", "광고", "트렌드", "CTR", "ROAS", "CPA", "팀장 판단", "키워드"],
    (data.data?.brand_snapshots || []).map(brand => [
      `<strong>${brand.brand}</strong>`,
      brand.ad_records,
      brand.trend_records,
      fmt(brand.avg_ctr, "%"),
      fmt(brand.avg_roas, "%"),
      money(brand.avg_cpa),
      tag(brand.manager_priority),
      (brand.top_keywords || []).slice(0, 3).join(", ")
    ])
  );

  renderTable(
    "data-preview-table",
    ["구분", "출처", "브랜드", "핵심 수치", "메모"],
    [
      ...(data.data?.ad_preview || []).map(record => [
        "광고",
        record.source,
        record.brand,
        `CTR ${record.metrics?.ctr}% · ROAS ${record.metrics?.roas}%`,
        `전환 ${record.metrics?.conversions}`
      ]),
      ...(data.data?.trend_preview || []).map(record => [
        "트렌드",
        record.source,
        record.brand,
        `점수 ${record.trend_score} · 변화율 ${record.trend_change_pct}%`,
        record.seasonal_issue?.title || "-"
      ])
    ]
  );
}

async function refreshDashboard() {
  const data = await loadDashboard();
  const apiResults = await loadApiSnapshot();
  apiResults.forEach(result => {
    if (result.ok) {
      result.payload = null;
    }
  });
  const logsResult = apiResults.find(result => result.label === "logs");
  if (logsResult?.ok) {
    logsResult.payload = await loadJson(logsResult.path).catch(() => null);
  }

  renderCommon(data);
  const page = document.body.dataset.page || "team";
  if (page === "team") renderTeamPage(data);
  if (page === "automation") renderAutomationPage(data, apiResults);
  if (page === "content") renderContentPage(data);
  if (page === "research") renderResearchPage(data);
  renderApiStatus(apiResults);
}

refreshDashboard().catch(error => {
  setText("deploy-status", "데이터 로드 실패");
  setHtml("page-error", `<pre>${error.message}</pre>`);
});

window.setInterval(() => {
  refreshDashboard().catch(() => {
    setText("api-refresh-state", "fail");
  });
}, REFRESH_INTERVAL_MS);
