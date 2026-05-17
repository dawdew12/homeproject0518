# Context Notes

## 2026-05-17 PHASE 1 시작

- 사용자는 `update_0517` 폴더의 최신 작업지시서와 대시보드를 기준으로 PHASE 1 진행을 승인했다.
- 최신 기준 문서는 `update_0517/PROJECT_MASTER_v2_1.md`이며, `PROJECT4_작업지시서 (2).md`는 구버전 상세 명세로 참고한다.
- 루트의 기존 `AIPR_Dashboard.html`은 원본으로 보존하고, `dashboard/AIPR_Dashboard.html`에는 복사본을 배치한다.
- PHASE 1에서는 실제 API 연동을 구현하지 않고, 폴더/문서/skeleton/state/log 기반만 만든다.
- `.env` 파일은 수정하거나 생성하지 않는다. 키 슬롯은 `.env.example`에만 작성한다.
## 2026-05-17 PHASE 1 구조 생성

- 최신 마스터 문서를 루트 PROJECT_MASTER.md로 복사했다.
- 루트 대시보드는 보존하고 dashboard/AIPR_Dashboard.html과 dashboard/backup/AIPR_Dashboard_original.html에 복사했다.
- 브랜드 config는 운영 시작용 기본값이며 실제 브랜드 세부 가이드는 후속 Phase에서 사용자 확인 후 보강해야 한다.
- GitHub Actions 파일은 PHASE 11 전까지 placeholder로 둔다.


## 2026-05-17 PHASE 1 검증

- 필수 파일 존재 여부 확인이 모두 통과했다.
- 시스템의 python 명령은 Microsoft Store 실행 별칭으로 보여 사용할 수 없었다.
- Codex 번들 Python으로 skeleton import 검증을 통과했다.
- state/current_phase.json의 상태를 completed로 갱신했다.

## 2026-05-18 PHASE 2 시작

- 사용자는 현재 진행상황 브리핑 후 다음 작업 진행을 승인했다.
- PHASE 2의 범위는 팀원 A 광고 데이터 수집이다.
- 실제 광고 API 키와 계정 권한은 아직 제공되지 않았으므로, 이번 단계는 mock 수집, 저장, retry, credential 확인 골격까지 구현한다.
- 실제 API 요청 매핑은 매체별 응답 샘플과 권한 확인 후 이어서 연결한다.

## 2026-05-18 PHASE 2 검증

- `agents/data_collector.py`는 Meta, 네이버SA, 카카오모먼트별 mock 수집 결과를 생성한다.
- `retry_call`은 실패 후 재시도해 3번째 호출에서 성공하는 테스트를 통과했다.
- `history/daily/2026-05-18_ad_data.json`에 3개 매체 x 5개 브랜드, 총 15개 mock 레코드를 저장했다.
- 실제 API 호출은 아직 연결하지 않았고, live 모드에서는 필요한 환경변수 존재 여부만 확인한다.

## 2026-05-18 PHASE 3 시작

- PHASE 3의 범위는 팀원 B 트렌드 수집이다.
- 실제 네이버 트렌드, Google Trends, 뉴스 API 연결 전 단계로 mock 수집, 저장, retry, credential 확인 골격까지 구현한다.
- 경쟁사 이슈는 별도 mock 소스로 분리해 팀장 분석 단계에서 시즌 이슈와 경쟁사 신호를 구분할 수 있게 한다.

## 2026-05-18 PHASE 3 검증

- `agents/trend_collector.py`는 네이버 트렌드, Google Trends, 뉴스, 경쟁사 이슈별 mock 수집 결과를 생성한다.
- `retry_call`은 실패 후 재시도해 3번째 호출에서 성공하는 테스트를 통과했다.
- `history/daily/2026-05-18_trend_data.json`에 4개 소스 x 5개 브랜드, 총 20개 mock 레코드를 저장했다.
- 실제 API 호출은 아직 연결하지 않았고, live 모드에서는 필요한 환경변수 존재 여부만 확인한다.

