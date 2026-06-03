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

## 2026-05-18 PHASE 3 시장조사 출처 보강

- 사용자가 전달한 `codex_marketing_ad_trend_sources.md`를 팀원 B의 시장조사 출처 기준으로 채택했다.
- 문서는 `docs/MARKETING_AD_TREND_SOURCES.md`에 저장했다.
- `agents/trend_collector.py`가 해당 문서의 Markdown 표를 읽어 daily, weekly, monthly 출처를 구분한다.
- 매일 수집 payload에는 daily 출처 13개가 `monitoring_sources.daily`로 포함된다.
- 실제 웹 방문과 본문 수집은 후속 자동화 단계에서 연결한다.

## 2026-05-31 PHASE 3.5 Vercel 대시보드 시작

- 사용자는 Vercel 프로젝트 `homeproject0518`을 생성했고 Project ID `prj_Pe7nqm93OZ6yPog5DJVGJwS0h3Ce`를 제공했다.
- Vercel 팀은 `raw22226-9071s-projects`, Team ID는 `team_sSX5hPGMzUn68TtAYcIXIMmr`로 확인했다.
- 프로젝트에는 아직 배포가 없고 framework는 `null` 상태다.
- 커스텀 도메인은 지금 단계에서 쓰지 않는다. 기본 Vercel 도메인으로 먼저 운영하고, 외부 공유가 필요할 때 붙인다.
- 초기 대시보드는 정적 HTML과 JSON으로 구성한다. API 기반 실시간화는 PHASE 10에서 확장한다.

## 2026-05-31 PHASE 3.5 Vercel 대시보드 완료

- 루트 `vercel.json`을 추가해 Vercel 출력 폴더를 `web`으로 지정했다.
- `web/index.html`은 `web/data/latest_status.json`을 읽어 현재 Phase, 수집 데이터, 검증, 최근 커밋, 리스크를 표시한다.
- `scripts/build_dashboard_data.py`가 `state`, `history`, Git 이력을 읽어 Vercel용 JSON을 생성한다.
- `tests/test_build_dashboard_data.py`로 대시보드 데이터 생성 결과를 검증한다.
- Vercel 프로젝트의 첫 배포는 GitHub push 후 Vercel 프로젝트에서 Git 연결이 활성화되어 있으면 자동으로 시작된다.

## 2026-05-31 PHASE 3.5 운영형 대시보드 보강

- 사용자는 지금까지 구현된 기능도 대시보드에서 실전처럼 확인하길 요청했다.
- `scripts/build_dashboard_data.py`에 기능 현황, 에이전트 운영 상태, 자동화 파이프라인, 브랜드별 mock 지표, 데이터 미리보기, 시장조사 출처 미리보기를 추가했다.
- `web/index.html`은 진행 현황 중심에서 운영 모니터링 화면으로 확장했다.
- 현재 표시 가능한 실전형 항목은 광고 mock 15개, 트렌드 mock 20개, 브랜드별 집계 5개, daily 시장조사 출처 8개 미리보기다.
- 실제 API 연결 전까지 대시보드의 수치는 mock 기반 운영 리허설 데이터다.

## 2026-05-31 PHASE 4 시작

- 사용자는 다음 단계를 승인했고, 이전 지시에 따라 Phase 단위로 자율 검토 후 진행한다.
- PHASE 4의 범위는 팀장 에이전트가 광고 성과 mock과 트렌드 mock을 종합해 브랜드별 우선순위, 소재 방향, 프롬프트 엔지니어 handoff를 만드는 것이다.
- 실제 LLM API 호출은 아직 연결하지 않는다. 현재 단계는 deterministic rule 기반 mock 분석으로 운영 흐름과 데이터 계약을 먼저 고정한다.
- 대시보드는 `history/daily/{date}_manager_brief.json`의 결과를 읽어 팀장 분석 Brief를 표시해야 한다.

## 2026-05-31 PHASE 4 완료

- `agents/manager.py`가 광고 성과와 트렌드 데이터를 읽어 브랜드별 priority, creative_direction, visual_concept, recommended_actions, prompt handoff를 생성한다.
- 검증용 `history/daily/2026-05-18_manager_brief.json`에는 5개 브랜드 분석과 팀원 C handoff 5개가 저장되었다.
- 현재 우선순위는 baren, melliance를 scale, paperback을 high, someud와 kinda를 test로 판단한다.
- `scripts/build_dashboard_data.py`와 `web/index.html`은 팀장 분석 Brief와 브랜드별 팀장 판단을 표시한다.
- 실제 LLM 분석과 API 실데이터 판단은 후속 Phase에서 연결한다.

## 2026-05-31 PHASE 5 시작

- PHASE 5의 범위는 팀원 C가 PHASE 4의 `manager_brief`를 입력으로 받아 브랜드별 스토리보드와 이미지 생성 프롬프트를 만드는 것이다.
- 실제 OpenAI API 호출은 아직 연결하지 않고, deterministic rule 기반으로 프롬프트 데이터 계약을 만든다.
- AGENTS.md 이미지 규칙에 따라 초안 이미지는 생성하지 않고 텍스트 스토리보드만 만든다.
- 브랜드 컨텍스트 파일은 아직 placeholder이므로 이번 단계는 브랜드 config와 팀장 handoff를 우선 기준으로 사용한다.

## 2026-05-31 PHASE 5 완료

- `agents/prompt_engineer.py`가 `manager_brief`를 읽어 브랜드별 스토리보드 4개와 이미지 프롬프트 4개를 생성한다.
- 검증용 `history/daily/2026-05-18_prompts.json`에는 5개 브랜드, 총 20개 스토리보드와 20개 프롬프트가 저장되었다.
- 프롬프트는 실사 high 10개, 일러스트 medium 10개로 구성했고, 모든 프롬프트에 no-text, no-logo, 하단 25% 카피 영역 규칙을 포함했다.
- 파일명 preview에는 sequence를 넣어 같은 브랜드와 키워드 조합에서도 덮어쓰기 위험을 줄였다.
- 실제 이미지 생성은 하지 않았고, 팀원 D가 PHASE 6에서 dry-run으로 이어받는다.

## 2026-05-31 Dashboard Architecture View 시작

- 사용자는 PHASE 6 진행 전 전체 소프트웨어 아키텍처를 도식화하고, 전체 진행도와 Phase별 테스트 결과를 수치로 보여주는 대시보드 보강을 요청했다.
- 이번 작업은 새 기능 Phase가 아니라 운영 대시보드 가시성 개선으로 처리한다.
- 전체 진행률은 공식 로드맵 PHASE 1-12 기준으로 계산하고, PHASE 3.5 같은 보조 마일스톤은 별도 대시보드/배포 마일스톤으로 표시한다.
- 아키텍처는 실제 코드를 기준으로 수집, 분석, 생성 준비, 저장, 배포 레이어를 나눠 표현한다.

## 2026-05-31 Dashboard Architecture View 구현

- `scripts/build_dashboard_data.py`에 공식 PHASE 1-12 로드맵, 전체 진행률, 아키텍처 레이어, 데이터 흐름, 저장 계약, Phase별 테스트 결과를 추가했다.
- `web/index.html`은 전체 진행률 바, 로드맵 타일, 소프트웨어 아키텍처 도식, 데이터 흐름, Phase별 검증 표를 렌더링한다.
- 현재 공식 로드맵 기준 진행률은 PHASE 1-5 완료로 5/12, 42%다.

## 2026-05-31 Dashboard Metadata Sync 시작

- 이전 작업은 커밋과 Vercel 배포까지 완료됐지만, `web/data/latest_status.json`은 커밋 전에 생성되어 최근 커밋 목록에 대시보드 아키텍처 커밋이 아직 반영되지 않았다.
- 운영 대시보드의 자기 보고 정확도를 맞추기 위해 데이터 JSON만 재생성하고 검증 후 별도 커밋으로 저장한다.

## 2026-05-31 Dashboard Metadata Sync 구현

- `scripts/build_dashboard_data.py`를 재실행해 `web/data/latest_status.json`의 최근 커밋 목록에 `bcefd8e [DASHBOARD] 아키텍처 진행도 시각화 추가`가 표시되도록 갱신했다.
- 동일한 16개 단위 테스트를 다시 실행해 대시보드 데이터 구조가 유지되는지 확인했다.

## 2026-05-31 Dashboard Live Commit Sync 시작

- 정적 JSON을 커밋에 포함하는 현재 방식은 최근 커밋 목록이 한 커밋 늦게 보일 수 있다.
- 최근 커밋 영역은 정적 JSON을 fallback으로 유지하되, 화면 로드 후 GitHub 공개 API에서 main 브랜치 최신 커밋을 받아 다시 렌더링하도록 보강한다.

## 2026-05-31 Dashboard Live Commit Sync 구현

- `web/index.html`에 GitHub commits API 호출을 추가해 최근 커밋 영역을 화면 로드 후 최신 main 브랜치 기준으로 다시 그린다.
- GitHub API가 실패해도 `latest_status.json`에 포함된 커밋 목록을 그대로 보여주도록 fallback을 유지했다.
- 기존 Python 단위 테스트 16개와 HTML script parse 검증을 통과했다.

## 2026-05-31 PHASE 6 Image Dry Run 시작

- 다음 단계는 팀원 D가 팀원 C의 `history/daily/{date}_prompts.json`을 입력으로 받아 이미지 생성 dry-run 요청을 만드는 것이다.
- 실제 gpt-image-2 API 호출은 아직 실행하지 않고, 모델, 품질, batch 구성, 출력 파일 경로, 예상 비용을 검증 가능한 JSON으로 남긴다.
- `outputs/`는 `.gitignore`에 포함되어 있으므로 추적 가능한 운영 기록은 `history/daily/{date}_image_dry_run.json`에 저장한다.
- 성공 기준은 5개 브랜드, 20개 이미지 요청, 실사 10개와 일러스트 10개, 총 예상 비용 $2.64가 단위 테스트와 대시보드에 반영되는 것이다.

## 2026-05-31 PHASE 6 Image Dry Run 구현

- `agents/image_designer.py`가 프롬프트 pack을 읽어 브랜드별 4개 요청 batch를 만들고, 요청별 출력 경로와 예상 비용을 계산한다.
- 실제 이미지는 생성하지 않으며 `charged: false`로 기록해 비용이 청구되지 않는 dry-run임을 명시한다.
- `history/daily/2026-05-18_image_dry_run.json`에는 5개 batch, 20개 요청, 예상 비용 $2.64, 일일/월간 한도 통과 여부가 저장되었다.
- 대시보드 JSON과 화면은 PHASE 6 완료, 전체 진행도 50%, 다음 단계 PHASE 7 품질 검수로 갱신되었다.

## 2026-06-01 PHASE 7 Quality Review 시작

- PHASE 7의 범위는 팀장이 팀원 D의 이미지 dry-run 요청을 검수하고 재생성 필요 여부를 판단하는 것이다.
- 실제 이미지 파일은 아직 생성되지 않았으므로 이번 검수는 픽셀 품질이 아니라 생성 요청의 운영 적합성을 점검한다.
- 검수 기준은 모델, 2K 사이즈, 이미지 유형별 품질, no-text 규칙, 하단 25% 카피 여백, 출력 경로, negative prompt의 텍스트 차단 항목이다.
- 산출물은 `history/daily/{date}_quality_review.json`이며, 다음 PHASE 8 Winner/Loser 학습 입력 전의 승인 게이트로 사용한다.

## 2026-06-01 PHASE 7 Quality Review 구현

- `agents/manager.py`에 품질 검수 기준, 점수화, 재생성 필요 여부, 최대 재시도 2회 handoff 구조를 구현했다.
- `history/daily/2026-05-18_quality_review.json`은 20개 요청을 모두 승인했고 평균 점수는 100.0이다.
- 재생성 필요 요청은 0개이며, no-text 규칙과 하단 25% 카피 여백 검수는 모두 통과했다.
- 대시보드는 PHASE 7 완료, 전체 진행도 58%, 다음 단계 PHASE 8 Winner/Loser 학습으로 갱신한다.
- GitHub 원격 main은 PHASE 7 커밋을 가리키는 것을 확인했다.
- Vercel 연결 앱 토큰은 만료되었고 배포 URL은 401 보호 상태라 원격 배포 반영 확인은 재인증 후 진행해야 한다.

## 2026-06-03 PHASE 8 Winner/Loser Learning 시작

- 사용자는 Vercel 재인증 후 다음 단계 진행을 승인했다.
- PHASE 8의 범위는 광고 성과 mock을 Winner, Loser, Pending으로 분류하고 학습 패턴 저장 파일을 갱신하는 것이다.
- AGENTS.md 기준에 따라 Winner는 CTR, ROAS, CPA 조건을 모두 통과해야 하고, Loser는 CTR, ROAS, CPA 중 하나라도 악화 기준을 넘으면 된다.
- 광고 mock의 CPA는 USD이고 브랜드 config의 CPA 목표는 KRW이므로, 이번 단계는 1 USD = 1300 KRW 기준으로 목표 CPA를 USD로 환산해 비교한다.
- mock 데이터에는 집행일수 필드가 없으므로 mock 기준 기본 집행일수 3일을 적용하고, 실제 API 연결 후에는 매체별 집행 시작일 또는 age 필드로 대체한다.

## 2026-06-03 PHASE 8 Winner/Loser Learning 구현

- `agents/manager.py`에 Winner, Loser, Pending 분류와 일별 학습 JSON 저장, 누적 패턴 파일 갱신을 구현했다.
- 기존 `history/winner_loser_patterns.json`은 UTF-8 BOM이 포함되어 있어 `read_json`이 `utf-8-sig`로 읽도록 수정했다.
- `history/daily/2026-05-18_winner_loser.json`에는 15개 광고 성과 중 Winner 12개, Loser 0개, Pending 3개가 저장되었다.
- Pending 3개는 someud의 ROAS가 247%로 Winner 기준 250%에 미달해 `mixed_signal`로 남긴다.
- 대시보드는 PHASE 8 완료, 전체 진행도 67%, 다음 단계 PHASE 9 저장소 연동으로 갱신한다.
- GitHub main에 `537b27c [PHASE 8] Winner Loser 학습 구현` 커밋을 푸시했다.
- Vercel 배포 `homeproject0518-fmyrldjy5-raw22226-9071s-projects.vercel.app`은 해당 커밋으로 production READY 상태가 되었다.
- 배포 본문 fetch는 Deployment Protection으로 401이 반환되어, 콘텐츠 응답 검증은 로컬 HTTP 검증과 Vercel 배포 메타데이터 확인으로 대체했다.

## 2026-06-03 Vercel Root Route Fix

- Deployment Protection 해제 후 `/data/latest_status.json`과 `/index.html`은 200으로 열렸지만 루트 `/`만 인증 페이지가 남았다.
- `vercel.json`에 `/`를 `/index.html`로 보내는 rewrite를 추가해 기본 대시보드 주소가 바로 열리도록 한다.

## 2026-06-03 PHASE 9 Storage Integration 시작

- PHASE 9의 범위는 이미지 산출물 저장과 GitHub history 정리를 운영 흐름에 연결하는 것이다.
- 실제 Google Drive API 인증 정보는 아직 없으므로 이번 단계에서는 업로드 API 호출이 아니라 검증 가능한 dry-run manifest를 만든다.
- 이미지 prompt ID와 기존 광고 creative ID는 아직 1대1로 연결되지 않는다.
- 따라서 이번 저장 manifest는 브랜드별 Winner/Loser `top_label`을 적용해 someud 4개는 pending, 나머지 브랜드 16개는 winner 폴더에 배치한다.
- GitHub history 유틸은 실제 git commit을 직접 실행하지 않고 daily와 weekly summary, planned commit 메시지를 생성한다.

## 2026-06-03 PHASE 9 Storage Integration 구현

- `utils/gdrive_upload.py`는 `history/daily/{date}_image_dry_run.json`과 `history/daily/{date}_winner_loser.json`을 읽어 `AIPR_소재관리/{brand}/{date}/{classification}/...` 경로 manifest를 만든다.
- 현재 실제 이미지 파일은 생성되지 않았으므로 manifest에는 `missing_file_count: 20`, `ready_to_upload: false`로 기록한다.
- `utils/github_history.py`는 daily 산출물 수와 핵심 지표를 요약하고, ISO 주차 기준 `history/weekly/2026-W21.json`을 만든다.
- 대시보드는 저장소 연동 요약, planned upload 수, missing 파일 수, weekly history 키, Drive 경로 preview를 표시한다.
- 실제 업로드와 실제 git commit 실행은 인증 정보와 운영 승인 조건이 갖춰진 뒤 별도 단계에서 연결한다.

## 2026-06-03 PHASE 9 배포 확인

- GitHub main에 `30d3079 [PHASE 9] 저장소 연동 dry-run 구현` 커밋을 push했다.
- Vercel production deployment `dpl_AR5qNnGoCrLCj9YMUCMV7cwr7zyw`는 해당 커밋으로 READY 상태다.
- Vercel 인증 fetch로 루트 HTML과 `/data/latest_status.json` 모두 200 OK를 확인했다.
- 일반 unauthenticated fetch는 Vercel Authentication 페이지를 반환하므로, 비로그인 공개 접근은 Deployment Protection 설정을 한 번 더 확인해야 한다.

## 2026-06-03 PHASE 10 Dashboard Realtime 시작

- PHASE 10의 목표는 대시보드가 정적 HTML 내부 데이터가 아니라 API 계약을 통해 상태, 에이전트, 비용, 브랜드, history, Winner/Loser, 로그를 읽게 만드는 것이다.
- 현재 Vercel 설정은 `web` 폴더 정적 배포이므로 서버 런타임을 갑자기 바꾸지 않는다.
- 이번 단계에서는 `web/api/*.json` 정적 API와 Vercel rewrite를 만들어 `/api/status` 같은 API 경로로 접근 가능하게 한다.
- 로컬과 향후 서버 운영을 위해 같은 payload를 반환하는 `dashboard_api.py` FastAPI skeleton도 추가한다.
- 화면 실시간화는 30초 polling과 cache-busting으로 구현하고, 실제 백엔드 push/SSE/WebSocket은 후속 안정화 범위로 남긴다.

## 2026-06-03 PHASE 10 Dashboard Realtime 구현

- `scripts/build_dashboard_data.py`가 `web/api/status.json`, `agents.json`, `costs.json`, `brands.json`, `history/daily.json`, `winner-loser.json`, `logs.json`, 브랜드 상세 JSON 5개를 생성한다.
- `vercel.json`에 `/api/*` rewrite를 추가해 Vercel에서 확장자 없는 API 경로로 접근 가능하게 했다.
- `dashboard_api.py`는 FastAPI가 설치된 운영 환경에서는 라우트를 등록하고, 현재 번들 Python처럼 FastAPI가 없으면 함수 호출로 payload를 검증할 수 있다.
- `web/index.html`은 30초마다 latest status와 API endpoint를 다시 읽고, API 상태표와 실행 로그를 화면에 표시한다.
- 로컬 검증은 `http://localhost:4173` 정적 서버에서 루트 HTML, `/api/status.json`, `/api/logs.json` 200 응답으로 확인했다.

## 2026-06-03 PHASE 10 배포 확인

- GitHub main에 `3f7947f [PHASE 10] Dashboard API 실시간화 구현` 커밋을 push했다.
- Vercel production deployment `dpl_7WWBYC8RmWsddjDH4xDUzxhQFThi`는 해당 커밋으로 READY 상태다.
- 배포 URL의 `/api/status` 직접 fetch는 Vercel Authentication 401을 반환했다.
- 따라서 원격 콘텐츠 검증은 배포 메타데이터 확인으로 대체하고, 실제 API 응답 검증은 로컬 HTTP 서버에서 수행했다.
- 비로그인 공개 확인이 필요하면 Vercel Deployment Protection을 프로젝트 단위로 완전히 해제하거나 Trusted Sources 또는 bypass token을 별도로 구성해야 한다.

