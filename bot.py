<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>포사원 — 이슈 추출 에이전트</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  :root {
    --bg: #0a0e1a;
    --surface: #131826;
    --surface-2: #1a2034;
    --border: #2a3048;
    --text: #e8ecf5;
    --text-dim: #8b93a7;
    --accent: #4f8cff;
    --accent-soft: rgba(79, 140, 255, 0.12);
    --green: #34d399;
    --green-soft: rgba(52, 211, 153, 0.12);
    --amber: #fbbf24;
    --amber-soft: rgba(251, 191, 36, 0.12);
    --red: #f87171;
    --red-soft: rgba(248, 113, 113, 0.12);
    --excel-green: #107C41;
    --excel-light: #f3f9f6;
  }
  html, body {
    font-family: 'Pretendard', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    font-size: 14px;
    line-height: 1.5;
  }
  body {
    background-image:
      radial-gradient(circle at 15% 10%, rgba(79, 140, 255, 0.08) 0%, transparent 40%),
      radial-gradient(circle at 85% 90%, rgba(52, 211, 153, 0.06) 0%, transparent 40%);
  }

  /* ========= HEADER ========= */
  .header {
    border-bottom: 1px solid var(--border);
    background: rgba(10, 14, 26, 0.85);
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 50;
  }
  .header-inner {
    max-width: 1400px;
    margin: 0 auto;
    padding: 16px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .logo-mark {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, var(--accent), #6366f1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
    color: white;
  }
  .logo-text {
    display: flex;
    flex-direction: column;
  }
  .logo-text strong {
    font-size: 15px;
    font-weight: 700;
  }
  .logo-text span {
    font-size: 12px;
    color: var(--text-dim);
  }
  .status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-dim);
    padding: 6px 12px;
    border: 1px solid var(--border);
    border-radius: 999px;
  }
  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
  }

  /* ========= MAIN ========= */
  .main {
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px;
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 24px;
  }
  @media (max-width: 1024px) {
    .main { grid-template-columns: 1fr; }
  }

  /* ========= SIDEBAR ========= */
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
  }
  .card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
  }
  .date-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  .date-row label {
    font-size: 11px;
    color: var(--text-dim);
    margin-bottom: 4px;
    display: block;
  }
  .date-row input {
    width: 100%;
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 8px 10px;
    border-radius: 6px;
    font-family: inherit;
    font-size: 13px;
  }
  .source-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .source-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    cursor: pointer;
    transition: all 0.15s;
    text-align: left;
    font-family: inherit;
    color: var(--text);
  }
  .source-btn:hover {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .source-btn.active {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .source-icon {
    width: 32px;
    height: 32px;
    background: var(--surface);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }
  .source-info {
    flex: 1;
    min-width: 0;
  }
  .source-info strong {
    font-size: 13px;
    font-weight: 600;
    display: block;
  }
  .source-info span {
    font-size: 11px;
    color: var(--text-dim);
  }
  .upload-area {
    margin-top: 12px;
    padding: 16px;
    border: 1.5px dashed var(--border);
    border-radius: 8px;
    text-align: center;
    transition: all 0.15s;
  }
  .upload-area.dragover {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .upload-area input[type="file"] {
    display: none;
  }
  .upload-label {
    cursor: pointer;
    color: var(--accent);
    font-size: 13px;
    font-weight: 500;
  }
  .upload-hint {
    font-size: 11px;
    color: var(--text-dim);
    margin-top: 4px;
  }
  .file-loaded {
    margin-top: 8px;
    padding: 8px 10px;
    background: var(--green-soft);
    border-radius: 6px;
    font-size: 12px;
    color: var(--green);
    display: none;
    align-items: center;
    gap: 6px;
  }
  .file-loaded.show { display: flex; }
  .file-loaded strong { color: var(--text); margin-left: 4px; }

  textarea.paste-area {
    width: 100%;
    min-height: 100px;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    resize: vertical;
    margin-top: 12px;
    display: none;
  }
  textarea.paste-area.show { display: block; }

  .btn-analyze {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, var(--accent), #6366f1);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-family: inherit;
    transition: all 0.15s;
  }
  .btn-analyze:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(79, 140, 255, 0.3); }
  .btn-analyze:disabled {
    background: var(--surface-2);
    color: var(--text-dim);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  /* ========= CONTENT ========= */
  .content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
  }
  .content-header h2 {
    font-size: 16px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .count-badge {
    background: var(--accent-soft);
    color: var(--accent);
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
  }
  .btn-teams {
    padding: 10px 18px;
    background: var(--excel-green);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    font-family: inherit;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.15s;
  }
  .btn-teams:hover { background: #0e6638; }
  .btn-teams:disabled { opacity: 0.4; cursor: not-allowed; }

  .empty-state {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 80px 32px;
    text-align: center;
    color: var(--text-dim);
  }
  .empty-state .icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
  .empty-state h3 { color: var(--text); font-size: 15px; margin-bottom: 8px; }

  .results-table {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  thead {
    background: var(--surface-2);
  }
  th {
    padding: 12px 16px;
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border);
  }
  td {
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: var(--surface-2); }

  .col-date { white-space: nowrap; color: var(--text-dim); width: 90px; }
  .col-media { white-space: nowrap; width: 130px; }
  .media-name { font-weight: 600; }
  .reporter { color: var(--text-dim); font-size: 12px; }
  .col-title { font-weight: 500; }
  .col-action-type { width: 100px; }
  .col-action-content { font-size: 12px; color: var(--text-dim); line-height: 1.55; max-width: 320px; }

  .tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
  }
  .tag-cancel { background: var(--red-soft); color: var(--red); }
  .tag-correct { background: var(--amber-soft); color: var(--amber); }
  .tag-monitor { background: var(--accent-soft); color: var(--accent); }
  .tag-comment { background: var(--green-soft); color: var(--green); }

  /* analysis loading */
  .analyzing {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 60px 32px;
    text-align: center;
  }
  .analyzing-spinner {
    width: 36px;
    height: 36px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 16px;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .analyzing-text { font-size: 14px; color: var(--text-dim); }
  .analyzing-step {
    font-size: 12px;
    color: var(--text-dim);
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
  }

  /* ========= EXCEL MODAL ========= */
  .excel-modal {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(4px);
    z-index: 100;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 24px;
    opacity: 0;
    transition: opacity 0.3s;
  }
  .excel-modal.show {
    display: flex;
    opacity: 1;
  }
  .excel-window {
    background: white;
    color: #1f2937;
    border-radius: 8px;
    width: 100%;
    max-width: 1100px;
    max-height: 90vh;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    transform: scale(0.92) translateY(20px);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    font-family: 'Segoe UI', 'Pretendard', sans-serif;
  }
  .excel-modal.show .excel-window {
    transform: scale(1) translateY(0);
  }

  .excel-titlebar {
    background: var(--excel-green);
    color: white;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
  }
  .excel-titlebar-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .excel-icon {
    width: 18px;
    height: 18px;
    background: white;
    color: var(--excel-green);
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 11px;
  }
  .excel-close {
    background: transparent;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 18px;
    padding: 0 8px;
    line-height: 1;
  }
  .excel-close:hover { background: rgba(255,255,255,0.15); }

  .excel-ribbon {
    background: #f3f2f1;
    border-bottom: 1px solid #e1dfdd;
    padding: 6px 16px;
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: #605e5c;
  }
  .excel-ribbon span.active { color: var(--excel-green); font-weight: 600; }

  .excel-formula-bar {
    background: white;
    border-bottom: 1px solid #e1dfdd;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-family: 'Segoe UI', sans-serif;
  }
  .cell-ref {
    background: #f3f2f1;
    padding: 4px 10px;
    border: 1px solid #e1dfdd;
    border-radius: 2px;
    min-width: 70px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
  }
  .formula-input {
    flex: 1;
    color: #605e5c;
    font-style: italic;
  }

  .excel-table-wrap {
    flex: 1;
    overflow: auto;
    background: white;
  }
  .excel-table {
    border-collapse: collapse;
    width: 100%;
    font-family: 'Segoe UI', 'Pretendard', sans-serif;
    font-size: 12px;
  }
  .excel-table th, .excel-table td {
    border: 1px solid #d4d2d0;
    padding: 0;
    text-align: left;
    vertical-align: top;
    background: white;
  }
  .excel-row-num {
    background: #f3f2f1 !important;
    color: #605e5c;
    text-align: center !important;
    font-weight: 500;
    width: 40px;
    padding: 4px !important;
    user-select: none;
  }
  .excel-col-letter {
    background: #f3f2f1 !important;
    color: #605e5c;
    text-align: center !important;
    font-weight: 500;
    height: 22px;
    user-select: none;
  }
  .excel-table thead th {
    background: var(--excel-green) !important;
    color: white;
    font-weight: 600;
    padding: 8px 10px !important;
    font-size: 12px;
  }
  .excel-table tbody td {
    padding: 6px 10px !important;
    color: #1f2937;
    line-height: 1.4;
  }
  .excel-existing { background: #fafafa !important; }
  .excel-new {
    background: #fff9e6 !important;
    animation: highlight-row 0.6s ease-out;
  }
  @keyframes highlight-row {
    0% { background: #ffd966 !important; transform: translateX(-20px); opacity: 0; }
    50% { background: #fff2b3 !important; transform: translateX(0); opacity: 1; }
    100% { background: #fff9e6 !important; }
  }
  .excel-new-flash {
    background: #ffd966 !important;
    box-shadow: inset 3px 0 0 #ff9500;
  }

  .excel-statusbar {
    background: var(--excel-green);
    color: white;
    padding: 4px 16px;
    font-size: 11px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .excel-status-text {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .excel-status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #fbbf24;
    animation: pulse-dot 1s infinite;
  }
  @keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }
  .excel-status-text.done .excel-status-dot {
    background: #34d399;
    animation: none;
  }

  .excel-header-action {
    background: white;
    border-bottom: 1px solid #e1dfdd;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .excel-header-action h3 {
    font-size: 14px;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .teams-tag {
    background: #5059c9;
    color: white;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
</style>
</head>
<body>

<header class="header">
  <div class="header-inner">
    <div class="logo">
      <div class="logo-mark">P</div>
      <div class="logo-text">
        <strong>포사원</strong>
        <span>이슈 추출 에이전트</span>
      </div>
    </div>
    <div class="status">
      <div class="status-dot"></div>
      분석 엔진 준비됨
    </div>
  </div>
</header>

<main class="main">
  <aside class="sidebar">
    <div class="card">
      <div class="card-title">조회 기간</div>
      <div class="date-row">
        <div>
          <label>시작일</label>
          <input type="date" id="startDate" value="2026-04-21">
        </div>
        <div>
          <label>종료일</label>
          <input type="date" id="endDate" value="2026-04-28">
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">💬 카카오톡 대화 불러오기</div>
      <div class="source-list">
        <button class="source-btn active" data-source="file">
          <div class="source-icon">📁</div>
          <div class="source-info">
            <strong>파일 업로드</strong>
            <span>카톡 내보내기 .txt 파일</span>
          </div>
        </button>
        <button class="source-btn" data-source="paste">
          <div class="source-icon">📋</div>
          <div class="source-info">
            <strong>텍스트 붙여넣기</strong>
            <span>대화 내용 직접 입력</span>
          </div>
        </button>
        <button class="source-btn" data-source="sample">
          <div class="source-icon">✨</div>
          <div class="source-info">
            <strong>샘플 데이터 사용</strong>
            <span>준비된 예시로 바로 체험</span>
          </div>
        </button>
      </div>

      <div class="upload-area" id="uploadArea">
        <input type="file" id="fileInput" accept=".txt">
        <label for="fileInput" class="upload-label">📎 .txt 파일 선택</label>
        <div class="upload-hint">또는 여기로 드래그</div>
      </div>

      <textarea class="paste-area" id="pasteArea" placeholder="카톡 대화 내용을 붙여넣으세요..."></textarea>

      <div class="file-loaded" id="fileLoaded">
        <span>✅</span> 데이터 로드 완료 <strong id="fileName"></strong>
      </div>
    </div>

    <button class="btn-analyze" id="btnAnalyze" disabled>분석하기</button>
  </aside>

  <section class="content">
    <div class="content-header">
      <h2>
        추출 결과 리스트
        <span class="count-badge" id="countBadge">0건</span>
      </h2>
      <button class="btn-teams" id="btnTeams" disabled>
        <span>📊</span>
        Teams 파일로 업데이트
      </button>
    </div>

    <div id="resultPanel">
      <div class="empty-state">
        <div class="icon">📋</div>
        <h3>대화를 불러온 뒤 분석 버튼을 눌러주세요</h3>
        <p>카카오톡 대화에서 언론 이슈와 조치 사항을 자동으로 추출합니다</p>
      </div>
    </div>
  </section>
</main>

<!-- Excel Modal -->
<div class="excel-modal" id="excelModal">
  <div class="excel-window">
    <div class="excel-titlebar">
      <div class="excel-titlebar-left">
        <div class="excel-icon">X</div>
        <span>언론이슈_조치현황_2026Q2.xlsx — Teams</span>
      </div>
      <button class="excel-close" id="excelClose">×</button>
    </div>
    <div class="excel-header-action">
      <h3>
        <span class="teams-tag">TEAMS</span>
        언론이슈 조치현황 — 4월 4주차
      </h3>
      <span style="font-size:12px;color:#605e5c;" id="excelMeta">행 추가 중...</span>
    </div>
    <div class="excel-ribbon">
      <span class="active">홈</span>
      <span>삽입</span>
      <span>페이지 레이아웃</span>
      <span>수식</span>
      <span>데이터</span>
      <span>검토</span>
      <span>보기</span>
    </div>
    <div class="excel-formula-bar">
      <div class="cell-ref" id="cellRef">A1</div>
      <span style="color:#605e5c;">fx</span>
      <div class="formula-input" id="formulaInput">보도일</div>
    </div>
    <div class="excel-table-wrap">
      <table class="excel-table">
        <thead>
          <tr>
            <th class="excel-row-num"></th>
            <th class="excel-col-letter" style="width:90px;">A</th>
            <th class="excel-col-letter" style="width:110px;">B</th>
            <th class="excel-col-letter" style="width:90px;">C</th>
            <th class="excel-col-letter">D</th>
            <th class="excel-col-letter" style="width:100px;">E</th>
            <th class="excel-col-letter">F</th>
          </tr>
          <tr>
            <th class="excel-row-num">1</th>
            <th>보도일</th>
            <th>매체</th>
            <th>기자</th>
            <th>기사 제목</th>
            <th>조치유형</th>
            <th>조치내용</th>
          </tr>
        </thead>
        <tbody id="excelBody">
          <!-- 기존 행들 + 새 행들 -->
        </tbody>
      </table>
    </div>
    <div class="excel-statusbar">
      <div class="excel-status-text" id="statusText">
        <div class="excel-status-dot"></div>
        <span id="statusLabel">Teams 파일 동기화 중...</span>
      </div>
      <div id="excelCount">행 1개</div>
    </div>
  </div>
</div>

<script>
// =========================================
// 가상 데이터
// =========================================
const SAMPLE_KAKAO = `2026년 4월 27일 월요일
오전 9:14, 김팀장 : 다들 출근했어? 이번주 언론 이슈 정리해서 올려줘 🙏
오전 9:15, 박과장 : 네 팀장님~ 어제 한겨레 이지훈 기자님 기사 건 우선 정리할게요
오전 9:17, 박과장 : 4월 26일자 한겨레 이지훈 기자 "포스코 포항제철소 환경오염 의혹" 기사 → 사실관계 다르다고 정정보도 요청 진행 중입니다. 환경팀에서 측정 데이터 송부했고, 데스크와 통화 완료
오전 9:22, 이대리 : 4월 25일 매일경제 정수아 기자 "철강업계 실적 부진 전망" 기사는 모니터링만 유지하기로 했어요. 사실 기반이라 별도 대응 불필요 판단
오전 10:03, 박과장 : 4월 24일 조선일보 김상철 기자가 쓴 "포스코 임원 인사 잡음" 기사 → 비공식 코멘트로 풀었습니다. 인사팀과 협의해서 백그라운드 설명 드렸고 후속 보도는 없을 듯
오전 10:45, 김팀장 : ㅇㅇ 굿. 4월 23일 머니투데이 윤재호 기자 "포항공장 가동률 저하" 건은 어떻게 됐어?
오전 10:47, 이대리 : 그건 기사 자체를 취소 요청했습니다. 데이터 오류 확인되어서 매체측에서 23일 오후에 자진 삭제했어요
오전 11:12, 박과장 : 그리고 4월 22일 동아일보 한지원 기자 "ESG 보고서 신뢰성 의문" 기사 → 정정보도 받았습니다. 어제 정정문 게재 확인했고 캡처 공유 드릴게요
오후 1:30, 이대리 : 4월 22일 뉴스1 강민호 기자 "포스코홀딩스 주가 하락 분석" 기사는 모니터링 중입니다. 추이 보고 주말까지 판단 예정
오후 2:50, 박과장 : 마지막으로 4월 21일 연합뉴스 송혜린 기자 "포항제철소 안전사고 우려" 기사 → 비공식 코멘트로 안전관리 현황 설명 드렸어요. 추가 취재 요청 들어오면 공식 자료 준비하기로
오후 3:15, 김팀장 : 좋아 다들 수고했어. 정리해서 Teams 시트에 올려줘 ✅`;

const PARSED_RESULTS = [
  {
    date: '2026-04-26', media: '한겨레', reporter: '이지훈',
    title: '포스코 포항제철소 환경오염 의혹',
    actionType: '정정보도', actionTag: 'tag-correct',
    actionContent: '사실관계가 다름을 환경팀 측정 데이터로 입증, 데스크와 통화 후 정정보도 요청 진행 중'
  },
  {
    date: '2026-04-25', media: '매일경제', reporter: '정수아',
    title: '철강업계 실적 부진 전망',
    actionType: '모니터링', actionTag: 'tag-monitor',
    actionContent: '사실 기반 보도로 별도 대응 불필요 판단, 모니터링만 유지'
  },
  {
    date: '2026-04-24', media: '조선일보', reporter: '김상철',
    title: '포스코 임원 인사 잡음',
    actionType: '비공식 코멘트', actionTag: 'tag-comment',
    actionContent: '인사팀과 협의 후 백그라운드 설명 진행, 후속 보도 없음'
  },
  {
    date: '2026-04-23', media: '머니투데이', reporter: '윤재호',
    title: '포항공장 가동률 저하',
    actionType: '기사 취소', actionTag: 'tag-cancel',
    actionContent: '데이터 오류 확인, 매체 측에서 23일 오후 자진 삭제 완료'
  },
  {
    date: '2026-04-22', media: '동아일보', reporter: '한지원',
    title: 'ESG 보고서 신뢰성 의문',
    actionType: '정정보도', actionTag: 'tag-correct',
    actionContent: '정정보도 게재 완료, 정정문 캡처 보관'
  },
  {
    date: '2026-04-22', media: '뉴스1', reporter: '강민호',
    title: '포스코홀딩스 주가 하락 분석',
    actionType: '모니터링', actionTag: 'tag-monitor',
    actionContent: '추이 모니터링 중, 주말까지 추가 대응 여부 판단 예정'
  },
  {
    date: '2026-04-21', media: '연합뉴스', reporter: '송혜린',
    title: '포항제철소 안전사고 우려',
    actionType: '비공식 코멘트', actionTag: 'tag-comment',
    actionContent: '안전관리 현황 백그라운드 설명, 추가 취재 시 공식 자료 준비 예정'
  }
];

const EXISTING_ROWS = [
  { date: '2026-04-15', media: '한국경제', reporter: '최영민', title: '포스코 1분기 실적 발표', actionType: '모니터링', actionContent: '실적 기반 보도, 별도 대응 없음' },
  { date: '2026-04-17', media: 'SBS', reporter: '강은비', title: '포스코 신사업 진출 관련', actionType: '비공식 코멘트', actionContent: 'IR팀 백그라운드 설명 진행' },
  { date: '2026-04-19', media: '서울경제', reporter: '오세훈', title: '철강 수출 회복세', actionType: '모니터링', actionContent: '긍정 보도, 모니터링 유지' }
];

// =========================================
// 상태
// =========================================
let currentSource = 'file';
let dataLoaded = false;
let analyzed = false;

// =========================================
// 소스 선택
// =========================================
const sourceBtns = document.querySelectorAll('.source-btn');
const uploadArea = document.getElementById('uploadArea');
const pasteArea = document.getElementById('pasteArea');
const fileLoaded = document.getElementById('fileLoaded');
const fileName = document.getElementById('fileName');
const fileInput = document.getElementById('fileInput');
const btnAnalyze = document.getElementById('btnAnalyze');

sourceBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    sourceBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentSource = btn.dataset.source;

    uploadArea.style.display = currentSource === 'file' ? 'block' : 'none';
    pasteArea.classList.toggle('show', currentSource === 'paste');

    if (currentSource === 'sample') {
      loadData('카톡대화_4월4주차_샘플.txt');
    } else {
      dataLoaded = false;
      fileLoaded.classList.remove('show');
      btnAnalyze.disabled = true;
    }
  });
});

// 파일 업로드
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) loadData(file.name);
});

// 드래그 앤 드롭
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith('.txt')) loadData(file.name);
});

// 텍스트 붙여넣기
pasteArea.addEventListener('input', () => {
  if (pasteArea.value.trim().length > 20) {
    loadData('붙여넣은 텍스트');
  } else {
    dataLoaded = false;
    fileLoaded.classList.remove('show');
    btnAnalyze.disabled = true;
  }
});

function loadData(name) {
  dataLoaded = true;
  fileName.textContent = name;
  fileLoaded.classList.add('show');
  btnAnalyze.disabled = false;
}

// =========================================
// 분석
// =========================================
const resultPanel = document.getElementById('resultPanel');
const countBadge = document.getElementById('countBadge');
const btnTeams = document.getElementById('btnTeams');

btnAnalyze.addEventListener('click', () => {
  if (!dataLoaded) return;
  runAnalysis();
});

function runAnalysis() {
  resultPanel.innerHTML = `
    <div class="analyzing">
      <div class="analyzing-spinner"></div>
      <div class="analyzing-text">대화 내용 분석 중...</div>
      <div class="analyzing-step" id="analyzeStep">› 메시지 파싱 중</div>
    </div>
  `;

  const steps = [
    '› 메시지 파싱 중',
    '› 언론 이슈 키워드 추출',
    '› 매체/기자 정보 매칭',
    '› 조치 유형 분류',
    '› 조치 내용 요약'
  ];
  let i = 0;
  const stepEl = document.getElementById('analyzeStep');
  const stepInterval = setInterval(() => {
    i++;
    if (i < steps.length) {
      stepEl.textContent = steps[i];
    } else {
      clearInterval(stepInterval);
      renderResults();
    }
  }, 500);
}

function renderResults() {
  analyzed = true;
  countBadge.textContent = `${PARSED_RESULTS.length}건`;
  btnTeams.disabled = false;

  let rows = PARSED_RESULTS.map(r => `
    <tr>
      <td class="col-date">${r.date}</td>
      <td class="col-media">
        <div class="media-name">${r.media}</div>
        <div class="reporter">${r.reporter} 기자</div>
      </td>
      <td class="col-title">${r.title}</td>
      <td class="col-action-type"><span class="tag ${r.actionTag}">${r.actionType}</span></td>
      <td class="col-action-content">${r.actionContent}</td>
    </tr>
  `).join('');

  resultPanel.innerHTML = `
    <div class="results-table">
      <table>
        <thead>
          <tr>
            <th>보도일</th>
            <th>매체 / 기자</th>
            <th>기사 제목</th>
            <th>조치유형</th>
            <th>조치내용</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

// =========================================
// 엑셀 시뮬레이션
// =========================================
const excelModal = document.getElementById('excelModal');
const excelClose = document.getElementById('excelClose');
const excelBody = document.getElementById('excelBody');
const excelCount = document.getElementById('excelCount');
const excelMeta = document.getElementById('excelMeta');
const cellRef = document.getElementById('cellRef');
const formulaInput = document.getElementById('formulaInput');
const statusText = document.getElementById('statusText');
const statusLabel = document.getElementById('statusLabel');

btnTeams.addEventListener('click', () => {
  if (!analyzed) return;
  openExcelSim();
});

excelClose.addEventListener('click', () => {
  excelModal.classList.remove('show');
});

function openExcelSim() {
  // 기존 행 채우기
  excelBody.innerHTML = '';
  EXISTING_ROWS.forEach((r, idx) => {
    const rowNum = idx + 2; // 1행은 헤더
    const tr = document.createElement('tr');
    tr.className = 'excel-existing';
    tr.innerHTML = `
      <td class="excel-row-num">${rowNum}</td>
      <td>${r.date}</td>
      <td>${r.media}</td>
      <td>${r.reporter}</td>
      <td>${r.title}</td>
      <td>${r.actionType}</td>
      <td>${r.actionContent}</td>
    `;
    excelBody.appendChild(tr);
  });
  excelCount.textContent = `행 ${EXISTING_ROWS.length}개`;
  excelMeta.textContent = '대기 중...';
  statusText.classList.remove('done');
  statusLabel.textContent = 'Teams 파일 로드 중...';

  excelModal.classList.add('show');

  // 약간 대기 후 새 행 추가 시작
  setTimeout(() => {
    statusLabel.textContent = '포사원 → 새 항목 추가 중...';
    addRowsSequentially();
  }, 800);
}

function addRowsSequentially() {
  let idx = 0;
  const startRowNum = EXISTING_ROWS.length + 2;

  function addNext() {
    if (idx >= PARSED_RESULTS.length) {
      // 완료
      statusText.classList.add('done');
      statusLabel.textContent = `✓ Teams 동기화 완료 — 신규 ${PARSED_RESULTS.length}건 추가`;
      excelMeta.textContent = `마지막 업데이트: 방금 전`;
      // 마지막 행으로 스크롤
      const wrap = document.querySelector('.excel-table-wrap');
      wrap.scrollTop = wrap.scrollHeight;
      return;
    }

    const r = PARSED_RESULTS[idx];
    const rowNum = startRowNum + idx;
    const tr = document.createElement('tr');
    tr.className = 'excel-new';
    tr.innerHTML = `
      <td class="excel-row-num">${rowNum}</td>
      <td>${r.date}</td>
      <td>${r.media}</td>
      <td>${r.reporter}</td>
      <td>${r.title}</td>
      <td>${r.actionType}</td>
      <td>${r.actionContent}</td>
    `;
    excelBody.appendChild(tr);

    // 셀 레퍼런스 업데이트
    cellRef.textContent = `A${rowNum}`;
    formulaInput.textContent = r.date;

    // 카운트 / 메타
    excelCount.textContent = `행 ${EXISTING_ROWS.length + idx + 1}개`;
    excelMeta.textContent = `${idx + 1} / ${PARSED_RESULTS.length} 행 추가됨`;

    // 스크롤 따라가기
    const wrap = document.querySelector('.excel-table-wrap');
    wrap.scrollTop = wrap.scrollHeight;

    idx++;
    setTimeout(addNext, 700);
  }

  addNext();
}

// 모달 배경 클릭으로 닫기
excelModal.addEventListener('click', (e) => {
  if (e.target === excelModal) excelModal.classList.remove('show');
});
</script>

</body>
</html>
