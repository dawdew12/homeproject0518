# Dashboard Spec

## 기준 파일

기존 대시보드 초안은 `AIPR_Dashboard.html`이며, PHASE 1에서 `dashboard/AIPR_Dashboard.html`로 복사해 관리한다. 원본은 삭제하지 않는다.

## 현재 정적 화면 구성

- 팀 대시보드.
- 자동화 루틴.
- 브랜드 분석.
- 팀장/팀원 A/B/C/D 업무 현황.
- 일간/주간/월간 토큰 현황.
- 팀장 수행력 지수.
- 팀원별 활동 이력.
- 월 비용 내역.
- 단계별 자동화 실행 현황.
- 브랜드별 KPI.
- 브랜드별 Winner/Loser 소재 패턴.
- 소재 제작 이력.

## PHASE 10 연동 대상

- `history/daily/{date}.json`.
- `history/winner_loser_patterns.json`.
- `state/runtime.json`.
- `logs/execution.log`.
- `logs/cost_tracking.log`.

## API 목표

- `GET /api/status`.
- `GET /api/agents`.
- `GET /api/costs`.
- `GET /api/brands`.
- `GET /api/brands/{brand}`.
- `GET /api/history/daily`.
- `GET /api/winner-loser`.
- `GET /api/logs`.

## PHASE 1 결정

PHASE 1에서는 HTML 구조를 바꾸지 않는다. 정적 데이터는 유지하고, 향후 FastAPI 또는 JSON 기반 연동을 위한 데이터 계약만 문서화한다.