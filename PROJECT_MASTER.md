# PROJECT_MASTER.md
# AIPR — 멀티 AI 에이전트 광고 소재 자동화 시스템
> Codex CLI + Warp 전달용 통합 작업지시서  
> Version: 2.1  
> Environment: Windows / Warp / Codex CLI / Python 3.11  
> Workspace: D:\AIPR

---

# 0. 이 문서의 목적

이 문서는 Codex CLI가 `D:\AIPR` 폴더에서 작업할 때 반드시 먼저 읽어야 하는 최상위 마스터 지시서다.

Codex는 본 문서를 기준으로 다음 작업을 수행한다.

- 프로젝트 아키텍처 설계
- 폴더 구조 생성
- 멀티 에이전트 파이프라인 개발
- 광고 성과 수집 자동화
- 트렌드 수집 자동화
- 이미지 생성 자동화
- 품질 검수 자동화
- Winner / Loser 판단 및 학습
- Google Drive / GitHub 저장 자동화
- Dashboard HTML 연동 및 실시간화
- GitHub Actions 자동 실행
- 비용 통제 및 로그 관리

---

# 1. 시작 명령 메뉴얼

## 1-1. Warp 실행

Warp Terminal을 실행한다.

---

## 1-2. 프로젝트 폴더 이동

```powershell
cd D:\AIPR
```

---

## 1-3. Codex 실행

```powershell
codex
```

---

## 1-4. Codex 최초 시작 명령

Codex 창에서 아래 내용을 그대로 입력한다.

```text
PROJECT_MASTER.md와 AGENTS.md를 먼저 읽고,
현재 D:\AIPR 프로젝트 상태를 분석해줘.

반드시 아래 순서를 지켜라.

1. 현재 프로젝트 파일/폴더 상태 확인
2. 현재 Phase 확인
3. 누락 파일 확인
4. 기존 AIPR_Dashboard.html 확인
5. 작업 리스크 설명
6. 변경 계획 설명
7. 승인 후 구현
8. 테스트
9. 로그 기록
10. 결과 요약

절대 한 번에 전체 시스템을 구현하지 마라.

작업은 반드시 PHASE 단위로 수행한다.

현재 목표:
PHASE 1 기반 세팅과 아키텍처 문서화 진행

우선 아래 작업만 수행해줘.

- 전체 폴더 구조 생성
- requirements.txt 생성
- .env.example 생성
- state 구조 생성
- logs 구조 생성
- README 작성
- 각 에이전트 skeleton 생성
- docs/ARCHITECTURE.md 생성
- 기존 AIPR_Dashboard.html을 dashboard/AIPR_Dashboard.html로 배치 또는 유지 관리
- 대시보드와 향후 FastAPI 데이터 연동 구조를 문서화

실행 전 반드시 작업 계획부터 설명해줘.
```

---

# 2. 프로젝트 핵심 목표

본 프로젝트는 마케팅 대행사의 5개 클라이언트 브랜드 광고 소재를 매일 평일 새벽 02:00에 자동 생성·검수·저장하는 멀티 AI 에이전트 운영 시스템이다.

핵심 목표:

- 광고 성과 데이터 자동 수집
- 브랜드별 트렌드 및 시즌 이슈 수집
- 팀장 AI가 브랜드별 소재 방향 도출
- 팀원 AI가 스토리보드와 이미지 프롬프트 생성
- 이미지 생성 AI가 브랜드별 소재 생성
- 팀장 AI가 품질 검수 및 재생성 판단
- 광고 집행 후 Winner / Loser 분류
- 누적 패턴을 다음 소재 방향에 반영
- Google Drive에 소재 저장
- GitHub에 실행 이력 저장
- Dashboard에서 팀/자동화/브랜드 성과 확인
- 비용 초과 시 자동 중단 및 알림

---

# 3. 전체 시스템 구조

```text
사용자
 ↓
Warp Terminal
 ↓
Codex CLI
 ↓
D:\AIPR 프로젝트
 ↓
멀티 에이전트 파이프라인
 ├── manager.py
 ├── data_collector.py
 ├── trend_collector.py
 ├── prompt_engineer.py
 └── image_designer.py
 ↓
광고 API / 트렌드 API / OpenAI API
 ↓
history / outputs / logs / state
 ↓
Google Drive / GitHub / Dashboard
```

---

# 4. 최종 폴더 구조

Codex는 아래 구조를 기준으로 프로젝트를 구성한다.

```text
D:\AIPR\
├── PROJECT_MASTER.md
├── AGENTS.md
├── README.md
├── .env
├── .env.example
├── requirements.txt
├── agents/
│   ├── manager.py
│   ├── data_collector.py
│   ├── trend_collector.py
│   ├── prompt_engineer.py
│   └── image_designer.py
├── brands/
│   ├── someud/
│   │   ├── brand_context.md
│   │   └── config.toml
│   ├── kinda/
│   │   ├── brand_context.md
│   │   └── config.toml
│   ├── melliance/
│   │   ├── brand_context.md
│   │   └── config.toml
│   ├── paperback/
│   │   ├── brand_context.md
│   │   └── config.toml
│   └── baren/
│       ├── brand_context.md
│       └── config.toml
├── prompts/
├── outputs/
├── history/
│   ├── daily/
│   ├── weekly/
│   └── winner_loser_patterns.json
├── logs/
│   ├── system.log
│   ├── api_errors.log
│   ├── image_generation.log
│   ├── cost_tracking.log
│   └── execution.log
├── state/
│   ├── current_phase.json
│   └── runtime.json
├── dashboard/
│   └── AIPR_Dashboard.html
├── automation/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_CONNECTIONS.md
│   ├── DASHBOARD_SPEC.md
│   └── PHASE_LOG.md
├── tests/
├── scripts/
├── utils/
│   ├── gdrive_upload.py
│   ├── github_history.py
│   └── cost_tracker.py
└── .github/
    └── workflows/
        └── daily_run.yml
```

---

# 5. 기존 대시보드 반영 규칙

사용자는 이미 `AIPR_Dashboard.html` 대시보드 초안을 제작해두었다.

Codex는 이 파일을 반드시 프로젝트에 포함해야 한다.

## 5-1. 대시보드 파일 위치

기존 파일이 `D:\AIPR\AIPR_Dashboard.html`에 있으면 다음 위치로 복사 또는 이동한다.

```text
D:\AIPR\dashboard\AIPR_Dashboard.html
```

단, 기존 파일 원본을 삭제하지 않는다. 필요 시 백업한다.

```text
D:\AIPR\dashboard\backup\AIPR_Dashboard_original.html
```

---

## 5-2. 대시보드 현재 기능

현재 HTML 대시보드는 다음 구조를 포함한다.

- 팀 대시보드
- 자동화 루틴
- 브랜드 분석
- 팀장/팀원 A/B/C/D 업무 현황
- 일간/주간/월간 토큰 현황
- 팀장 수행력 지수
- 팀원별 활동 이력
- 월 비용 내역
- 단계별 자동화 실행 현황
- 브랜드별 KPI
- 브랜드별 Winner / Loser 소재 패턴
- 소재 제작 이력

---

## 5-3. 대시보드 연동 목표

PHASE 10에서 정적 HTML을 FastAPI 또는 JSON 기반 실시간 대시보드로 확장한다.

연동 대상 데이터:

```text
history/daily/{date}.json
history/winner_loser_patterns.json
state/runtime.json
logs/execution.log
logs/cost_tracking.log
```

---

## 5-4. Dashboard API 설계 목표

향후 FastAPI에서 아래 API를 제공한다.

```text
GET /api/status
GET /api/agents
GET /api/costs
GET /api/brands
GET /api/brands/{brand}
GET /api/history/daily
GET /api/winner-loser
GET /api/logs
```

---

## 5-5. PHASE 1에서 할 일

PHASE 1에서는 대시보드 기능 구현까지 하지 않는다.

PHASE 1에서는 아래 작업만 수행한다.

- `dashboard/` 폴더 생성
- 기존 `AIPR_Dashboard.html` 확인
- `dashboard/AIPR_Dashboard.html` 배치
- `docs/DASHBOARD_SPEC.md` 작성
- 향후 API 연동 구조 문서화

---

# 6. Codex 행동 규칙

## 6-1. 필수 규칙

Codex는 모든 작업에서 다음 규칙을 반드시 따른다.

- 작업 전 반드시 계획 설명
- 한 번에 전체 구현 금지
- PHASE 단위 개발
- 승인 후 구현
- 모든 변경사항 로그 기록
- 테스트 후 결과 요약
- 실패 시 원인 분석
- API 키 하드코딩 금지
- `.env` 사용 필수
- 상태 파일 기반 운영
- 기존 사용자 파일 삭제 금지
- 대시보드 원본 파일 보존

---

## 6-2. 절대 금지

- 전체 시스템 한 번에 구현
- 승인 없이 구조 변경
- `.env` 파일 수정
- API 키 코드 하드코딩
- 기존 대시보드 원본 삭제
- outputs/history/logs 임의 삭제
- 브랜드 설정 임의 변경
- PHASE 건너뛰기

---

# 7. 기술 스택

## 기본

- Python 3.11+
- OpenAI gpt-5.5 API
- OpenAI gpt-image-2 API
- OpenAI Batch API
- Google Drive API
- GitHub API
- GitHub Actions
- FastAPI
- HTML/CSS/JavaScript Dashboard

---

## 광고 API

- Meta Marketing API
- 네이버 검색광고 API
- 카카오모먼트 API

---

## 트렌드 API

- 네이버 트렌드 API
- Google Trends / pytrends
- 네이버 뉴스 API

---

# 8. 에이전트 구성

## 8-1. 팀장 — `agents/manager.py`

모델:

```text
gpt-5.5
reasoning: high
```

업무:

- 팀원 A/B 수집 데이터 분석
- 브랜드별 소재 방향 결정
- 팀원 C 스토리보드 승인/반려
- 이미지 품질 검수
- 재생성 피드백 작성
- Winner / Loser 판단
- 비용 초과 시 중단 판단
- 일일 실행 요약 작성

월 비용 목표:

```text
$7
```

---

## 8-2. 팀원 A — `agents/data_collector.py`

모델:

```text
gpt-5.5
reasoning: medium
```

업무:

- Meta 광고 성과 수집
- 네이버SA 광고 성과 수집
- 카카오모먼트 광고 성과 수집
- 캠페인/소재 단위 성과 저장

수집 지표:

- CTR
- CVR
- CPA
- ROAS
- 노출
- 클릭
- 비용
- 전환수

출력:

```text
history/daily/{YYYY-MM-DD}_ad_data.json
```

월 비용 목표:

```text
$2
```

---

## 8-3. 팀원 B — `agents/trend_collector.py`

모델:

```text
gpt-5.5
reasoning: low
```

업무:

- 네이버 트렌드 수집
- 구글 트렌드 수집
- 뉴스 이슈 수집
- 시즌 키워드 수집
- 경쟁사 동향 수집

출력:

```text
history/daily/{YYYY-MM-DD}_trend_data.json
```

월 비용 목표:

```text
$1
```

---

## 8-4. 팀원 C — `agents/prompt_engineer.py`

모델:

```text
gpt-5.5
reasoning: high
```

업무:

- 브랜드별 텍스트 스토리보드 작성
- 팀장 승인 후 이미지 프롬프트 생성
- 팀장 불합격 피드백 반영
- 재생성 프롬프트 수정

프롬프트 필수 구조:

```text
[브랜드 정체성]
[오늘의 방향]
[이미지 스펙]
[카피 영역]
[금지사항]
```

출력:

```text
history/daily/{YYYY-MM-DD}_prompts.json
```

월 비용 목표:

```text
$5
```

---

## 8-5. 팀원 D — `agents/image_designer.py`

모델:

```text
gpt-image-2
Batch API
```

업무:

- 이미지 생성
- 브랜드별 n=4 배칭
- 실사 2장 + 일러스트 2장 생성
- 재생성 수행
- 파일명 규칙 적용
- outputs 저장

출력:

```text
outputs/{brand}/{YYYY-MM-DD}/{filename}.png
```

월 비용 목표:

```text
$61
```

---

# 9. 에이전트 권한 규칙

| 에이전트 | 수정 가능 영역 |
|---|---|
| manager.py | history, state, logs |
| data_collector.py | history/daily, logs |
| trend_collector.py | history/daily, logs |
| prompt_engineer.py | prompts, history/daily, logs |
| image_designer.py | outputs, history/daily, logs |
| gdrive_upload.py | outputs 읽기, Google Drive 업로드 |
| github_history.py | history 읽기, GitHub 커밋 |
| cost_tracker.py | state, logs |

주의:

- image_designer.py는 브랜드 config를 수정하지 않는다.
- prompt_engineer.py는 outputs 이미지를 삭제하지 않는다.
- data_collector.py는 prompts를 수정하지 않는다.
- dashboard HTML은 PHASE 10 이전에는 구조 보존을 우선한다.

---

# 10. 브랜드 목록

운영 브랜드:

```text
someud      소머드
kinda       킨다
melliance   멜리언스
paperback   페이퍼백
baren       바렌
```

---

## 10-1. 브랜드 config 예시

```toml
[brand]
name = "소머드"
name_en = "someud"
industry = "매트리스"
target = "40-60대 여성"
active = true

[style]
primary_color = "#8B6355"
secondary_color = "#F5F0E8"
accent_color = "#C9A84C"
tone = "프리미엄 오가닉, 따뜻하고 신뢰감"
forbidden = ["할인", "특가", "최저가", "경쟁사명"]

[performance_targets]
ctr_target = 2.5
cvr_target = 5.0
cpa_target_krw = 15000
roas_target = 300

[image_config]
real_photo_count = 2
illustration_count = 2
copy_area_bottom_pct = 25
```

---

# 11. 일일 자동화 루프

평일 02:00 KST 실행 기준.

```text
[02:00] STEP 1+2 병렬 실행
  ├── 팀원 A: 광고 성과 수집
  └── 팀원 B: 트렌드·시즌·경쟁사 수집

[02:06] STEP 3
  └── 팀장: 수집 데이터 분석 → 브랜드별 소재 방향 + 개선안

[02:11] STEP 4
  └── 팀원 C: 텍스트 스토리보드 작성
      → 팀장 승인/반려
      → 승인 후 이미지 프롬프트 생성

[02:20] STEP 5
  └── 팀원 D: 이미지 생성 Batch 요청
      → 5브랜드 × 실사 2장 + 일러스트 2장

[02:38] STEP 6
  └── 팀장: 품질 검수
      ├── 합격 → 저장
      └── 불합격 → 피드백 → 재생성

[02:45] STEP 7
  └── 팀원 C: 피드백 반영 프롬프트 수정

[02:48] STEP 8
  └── 팀원 D: 재생성

[03:05] STEP 9
  └── 파일 라벨링
  └── Google Drive 업로드
  └── GitHub 이력 커밋
  └── winner_loser_patterns.json 업데이트
```

---

# 12. 이미지 생성 규칙

## 12-1. 품질 설정

```python
IMAGE_CONFIG = {
    "실사": {
        "size": "2048x2048",
        "quality": "high",
        "batch": True,
        "cost_per_image": 0.211
    },
    "일러스트": {
        "size": "2048x2048",
        "quality": "medium",
        "batch": True,
        "cost_per_image": 0.053
    }
}
```

---

## 12-2. 브랜드당 일일 생성 수량

```text
브랜드당 4장
- 실사 2장
- 일러스트 2장
```

총 일일 생성량:

```text
5브랜드 × 4장 = 20장
```

---

## 12-3. 프롬프트 필수 규칙

모든 이미지 프롬프트에는 반드시 아래 문구를 포함한다.

```text
NO text
NO watermark
NO logo
Leave 25% bottom space for copywriting
```

---

## 12-4. 재생성 제한

```python
MAX_RETRY = 2
```

소재당 재생성은 최대 2회까지만 허용한다.

2회 초과 시:

```text
status = "보류"
```

---

# 13. 파일 명명 규칙

```text
{브랜드}_{YYYYMMDD}_{유형}_{키워드1}-{키워드2}-{키워드3}_{품질}.png
```

예시:

```text
someud_20260512_실사_어버이날-부부-황토침대_high.png
kinda_20260512_일러스트_극손상-비포애프터-핑크_medium.png
melliance_20260512_실사_봄-컬렉션-모델_high.png
```

---

# 14. 저장 구조

## 14-1. Google Drive

```text
AIPR_소재관리/
├── someud/
│   ├── 2026-05-12/
│   │   ├── winner/
│   │   ├── loser/
│   │   └── pending/
├── kinda/
├── melliance/
├── paperback/
└── baren/
```

---

## 14-2. GitHub history

```text
history/
├── daily/
│   ├── 2026-05-12.json
│   └── 2026-05-13.json
├── weekly/
│   └── 2026-W19.json
└── winner_loser_patterns.json
```

---

## 14-3. daily JSON 구조

```json
{
  "date": "2026-05-12",
  "execution": {
    "start_time": "02:04",
    "end_time": "03:05",
    "total_cost_usd": 2.92,
    "images_generated": 22,
    "images_approved": 20,
    "retry_count": 2
  },
  "market_data": {
    "top_keywords": ["어버이날", "황토침대"],
    "trend_change": "+23%"
  },
  "manager_brief": "어버이날 시즌 감성 소구 집중",
  "brands": {
    "someud": {
      "images": [
        {
          "filename": "someud_20260512_실사_어버이날-부부-황토침대_high.png",
          "type": "실사",
          "quality": "high",
          "concept_keywords": ["어버이날", "부부", "황토침대"],
          "generation_attempts": 1,
          "approved": true,
          "classification": "pending",
          "ad_performance": {
            "status": "집행중",
            "ctr": null,
            "cvr": null,
            "cpa": null,
            "roas": null
          }
        }
      ]
    }
  }
}
```

---

# 15. Winner / Loser 판단 기준

## 15-1. Winner

AND 조건:

```text
CTR >= 2.0%
ROAS >= 250%
CPA <= 목표 CPA × 1.2
```

---

## 15-2. Loser

OR 조건:

```text
CTR < 0.8%
ROAS < 120%
CPA > 목표 CPA × 2.0
```

---

## 15-3. Pending

```text
집행 3일 미만
OR
노출 1,000회 미만
```

---

# 16. 비용 관리

## 16-1. 월 비용 목표

| 구성요소 | 월 비용 |
|---|---:|
| 팀장 gpt-5.5 high | $7 |
| 팀원 A gpt-5.5 medium | $2 |
| 팀원 B gpt-5.5 low | $1 |
| 팀원 C gpt-5.5 high | $5 |
| 팀원 D gpt-image-2 Batch | $61 |
| 이력 분석 | $3 |
| 합계 | $79 |

---

## 16-2. 비용 제한

```text
DAILY_COST_LIMIT_USD=5.00
MONTHLY_COST_LIMIT_USD=79.00
```

일일 비용이 $5를 초과하면 즉시 중단한다.

월 비용이 $79를 초과할 위험이 있으면 Slack 경고를 발송한다.

---

# 17. .env.example 키 목록

```bash
# OpenAI
OPENAI_API_KEY=

# Meta
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=

# 네이버 검색광고
NAVER_SA_API_KEY=
NAVER_SA_SECRET_KEY=
NAVER_SA_CUSTOMER_ID=

# 네이버 뉴스/트렌드
NAVER_NEWS_CLIENT_ID=
NAVER_NEWS_CLIENT_SECRET=
NAVER_TRENDS_CLIENT_ID=
NAVER_TRENDS_CLIENT_SECRET=

# 카카오모먼트
KAKAO_MOMENT_ACCESS_TOKEN=

# Google
GOOGLE_SERVICE_ACCOUNT_JSON=

# Slack
SLACK_WEBHOOK_URL=

# Cost Limit
DAILY_COST_LIMIT_USD=5.00
MONTHLY_COST_LIMIT_USD=79.00
```

---

# 18. 상태 관리

## 18-1. state/current_phase.json

```json
{
  "current_phase": 1,
  "status": "running",
  "active_brand": null,
  "last_success": null,
  "last_error": null
}
```

---

## 18-2. state/runtime.json

```json
{
  "daily_cost_usd": 0,
  "monthly_cost_usd": 0,
  "images_generated": 0,
  "images_approved": 0,
  "retry_count": 0,
  "execution_start": null,
  "execution_end": null
}
```

---

# 19. 로그 관리

```text
logs/
├── system.log
├── api_errors.log
├── image_generation.log
├── cost_tracking.log
└── execution.log
```

로그 필수 기록 항목:

- 실행 시작/종료 시간
- API 호출 결과
- 실패 원인
- 재시도 횟수
- 이미지 생성 비용
- 일일 누적 비용
- Slack 알림 발송 여부
- GitHub 커밋 결과
- Google Drive 업로드 결과

---

# 20. 실패 및 예외 처리

## API 실패

```text
3회 재시도
→ 실패 시 logs/api_errors.log 기록
→ Slack 알림
→ 해당 단계 중단 또는 fallback 적용
```

---

## 트렌드 데이터 없음

```text
최근 7일 평균 데이터 사용
```

---

## 브랜드 config 없음

```text
해당 브랜드 skip
logs/system.log 기록
```

---

## 대시보드 파일 없음

```text
dashboard/AIPR_Dashboard.html 생성 전 중단하지 않는다.
docs/DASHBOARD_SPEC.md에 누락 상태 기록 후 기본 placeholder HTML 생성
```

---

## 비용 초과

```text
즉시 중단
state/runtime.json 업데이트
Slack 알림
manager 승인 전까지 재실행 금지
```

---

# 21. GitHub Actions 스케줄러

파일:

```text
.github/workflows/daily_run.yml
```

실행 시간:

```yaml
on:
  schedule:
    - cron: '0 17 * * 1-5'
  workflow_dispatch:
```

주의:

```text
UTC 17:00 = KST 02:00
```

---

# 22. Git 커밋 규칙

## 커밋 메시지 예시

```text
[PHASE 1] 프로젝트 초기 구조 생성
[PHASE 2] 광고 데이터 수집 skeleton 구현
[PHASE 10] Dashboard API 연동 구조 추가
[FIX] image regeneration retry bug
```

---

## 일일 자동 커밋 메시지 예시

```text
📊 [2026-05-12] 소머드 W:2 L:1 P:1 | 킨다 W:3 L:0 P:1 | 총비용 $2.92
```

---

# 23. PHASE별 개발 로드맵

# PHASE 1 — 프로젝트 기반 세팅 + 아키텍처 정리

## 목표

- 폴더 구조 생성
- `.env.example` 생성
- `requirements.txt` 생성
- `README.md` 생성
- `state/` 생성
- `logs/` 생성
- 각 에이전트 skeleton 생성
- 기존 Dashboard HTML 배치
- 아키텍처 문서 작성

## 수행 작업

```text
1. D:\AIPR 구조 확인
2. dashboard/AIPR_Dashboard.html 존재 여부 확인
3. 없으면 루트의 AIPR_Dashboard.html 탐색
4. dashboard 폴더로 복사
5. docs/ARCHITECTURE.md 작성
6. docs/DASHBOARD_SPEC.md 작성
7. agents/*.py skeleton 생성
8. utils/*.py skeleton 생성
9. state/current_phase.json 생성
10. state/runtime.json 생성
11. logs 기본 파일 생성
12. README.md 작성
```

## 완료 조건

- Codex가 `D:\AIPR` 구조를 인식한다.
- Dashboard HTML이 `dashboard/AIPR_Dashboard.html`에 존재한다.
- ARCHITECTURE.md가 존재한다.
- DASHBOARD_SPEC.md가 존재한다.
- 에이전트 skeleton이 존재한다.
- `.env.example`이 존재한다.
- `requirements.txt`가 존재한다.

---

# PHASE 2 — 광고 데이터 수집

## 목표

- Meta Marketing API 연동
- 네이버 검색광고 API 연동
- 카카오모먼트 API 연동

## 출력

```text
history/daily/{YYYY-MM-DD}_ad_data.json
```

## 완료 조건

- 각 매체별 dummy/mock 수집 구조 완성
- 실제 API 키 입력 시 데이터 수집 가능
- 실패 시 3회 retry 가능

---

# PHASE 3 — 트렌드 수집

## 목표

- 네이버 트렌드 수집
- 구글 트렌드 수집
- 뉴스 이슈 수집
- 경쟁사 이슈 수집

## 출력

```text
history/daily/{YYYY-MM-DD}_trend_data.json
```

---

# PHASE 4 — 팀장 분석 엔진

## 목표

- 광고 성과 + 트렌드 데이터 종합
- 브랜드별 소재 방향 도출
- 개선안 생성

## 출력

```text
history/daily/{YYYY-MM-DD}_manager_brief.json
```

---

# PHASE 5 — 프롬프트 엔지니어링

## 목표

- 텍스트 스토리보드 생성
- 팀장 승인/반려 구조
- 이미지 프롬프트 생성

## 출력

```text
history/daily/{YYYY-MM-DD}_prompts.json
```

---

# PHASE 6 — 이미지 생성

## 목표

- gpt-image-2 Batch API 연동
- 브랜드별 n=4 이미지 생성
- outputs 저장
- 파일명 규칙 적용

## 출력

```text
outputs/{brand}/{YYYY-MM-DD}/
```

---

# PHASE 7 — 품질 검수 및 재생성

## 목표

- 팀장 품질 검수
- 불합격 피드백 작성
- 소재당 최대 2회 재생성
- 보류 처리

---

# PHASE 8 — Winner / Loser 학습

## 목표

- 광고 성과 반영
- Winner / Loser / Pending 분류
- 누적 패턴 저장
- 다음날 소재 방향에 반영

## 출력

```text
history/winner_loser_patterns.json
```

---

# PHASE 9 — 저장소 연동

## 목표

- Google Drive 업로드
- GitHub 이력 커밋
- daily/weekly history 정리

---

# PHASE 10 — Dashboard 실시간화

## 목표

- 기존 `dashboard/AIPR_Dashboard.html` 유지
- 정적 데이터를 JSON 또는 API 기반으로 교체
- FastAPI 서버 구성
- Dashboard API 엔드포인트 구성
- 팀/자동화/브랜드 분석 데이터를 실시간 표시

## 대상 파일

```text
dashboard/AIPR_Dashboard.html
docs/DASHBOARD_SPEC.md
dashboard_api.py 또는 app/main.py
```

## API 목표

```text
GET /api/status
GET /api/agents
GET /api/costs
GET /api/brands
GET /api/brands/{brand}
GET /api/history/daily
GET /api/winner-loser
GET /api/logs
```

---

# PHASE 11 — GitHub Actions 자동화

## 목표

- 평일 02:00 KST 자동 실행
- workflow_dispatch 수동 실행
- Slack 알림
- 비용 초과 중단
- GitHub history 커밋

---

# PHASE 12 — 안정화

## 목표

- 예외처리 강화
- 비용 최적화
- 로그 가독성 개선
- 테스트 추가
- 신규 브랜드 추가 편의성 개선
- Dashboard UX 개선

---

# 24. PHASE 진행 규칙

Codex는 반드시 아래 방식으로 진행한다.

```text
1. 현재 Phase 확인
2. 필요한 파일 확인
3. 작업 계획 설명
4. 사용자 승인 대기
5. 구현
6. 테스트
7. 결과 요약
8. PHASE_LOG.md 업데이트
9. Git 커밋 제안
```

다음 Phase로 넘어가기 전 반드시 현재 Phase 완료 조건을 확인한다.

---

# 25. 테스트 규칙

PHASE별 최소 테스트:

```text
PHASE 1:
- 폴더 존재 여부 확인
- 파일 존재 여부 확인
- Python import 가능 여부 확인

PHASE 2:
- mock 광고 데이터 저장 테스트

PHASE 3:
- mock 트렌드 데이터 저장 테스트

PHASE 4:
- manager brief 생성 테스트

PHASE 5:
- prompt JSON 생성 테스트

PHASE 6:
- 이미지 생성 dry-run 테스트

PHASE 10:
- dashboard HTML 열림 확인
- API mock JSON 로드 확인
```

---

# 26. 현재 최우선 작업

현재 최우선 작업은 PHASE 1이다.

Codex는 PHASE 1에서 다음까지만 진행한다.

```text
- 전체 폴더 구조 생성
- Dashboard HTML 배치
- ARCHITECTURE.md 작성
- DASHBOARD_SPEC.md 작성
- README.md 작성
- .env.example 작성
- requirements.txt 작성
- state 파일 생성
- logs 파일 생성
- 에이전트 skeleton 생성
- utils skeleton 생성
```

PHASE 1에서는 실제 API 연동을 하지 않는다.

---

# 27. 최종 운영 원칙

```text
1. 사람은 디렉터다.
2. AI는 작업자다.
3. 모든 작업은 PHASE 단위로 한다.
4. 모든 실행은 로그로 남긴다.
5. 모든 비용은 추적한다.
6. 모든 소재는 Winner/Loser 학습으로 연결한다.
7. 기존 파일은 보존한다.
8. 대시보드는 운영 현황의 중심이다.
9. 최종 승인은 사람이 한다.
```

---

# 28. Codex에게 마지막으로 강조할 내용

Codex는 아래 원칙을 항상 지켜야 한다.

```text
PROJECT_MASTER.md
AGENTS.md
AIPR_Dashboard.html

이 세 파일을 반드시 기준 파일로 취급한다.

PROJECT_MASTER.md는 최상위 지시서다.
AGENTS.md는 에이전트 운영 규칙이다.
AIPR_Dashboard.html은 대시보드 UI 초안이다.

기존 파일의 핵심 내용을 삭제하거나 축소하지 말고,
PHASE별로 확장하라.
```
