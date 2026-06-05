# PHASE LOG

## 2026-05-17 PHASE 1

- 목표: 프로젝트 기반 세팅과 아키텍처 문서화.
- 범위: 폴더 구조, state/logs, skeleton, docs, 대시보드 배치.
- 실제 API 연동과 이미지 생성은 후속 Phase로 보류.
## 2026-05-17 PHASE 1 완료

- 폴더 구조, state, logs, docs, agents, utils, 브랜드 기본 파일을 생성했다.
- 기존 대시보드 원본을 보존하고 dashboard 폴더에 복사했다.
- 필수 파일 존재 여부 확인을 통과했다.
- Codex 번들 Python으로 skeleton import 검증을 통과했다.
- 남은 리스크: 로컬 python 명령이 실제 Python 3.11로 연결되어 있지 않다.

## 2026-05-18 PHASE 2 시작

- 목표: Meta, 네이버SA, 카카오모먼트 광고 성과 수집 구조 구현.
- 범위: mock 데이터 수집, 3회 retry, `history/daily/{date}_ad_data.json` 저장, 단위 테스트.
- 보류: 실제 API 요청 매핑은 광고 계정 권한과 응답 샘플 확인 후 연결한다.

## 2026-05-18 PHASE 2 완료

- `agents/data_collector.py`에 매체별 mock 수집, credential 확인, 3회 retry, JSON 저장 함수를 구현했다.
- `tests/test_data_collector.py`로 mock 수집, 저장, retry 동작을 검증했다.
- `history/daily/2026-05-18_ad_data.json`에 검증용 mock 광고 데이터를 저장했다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_data_collector`.
- 결과: 3개 테스트 통과.
- 남은 리스크: 실제 Meta, 네이버SA, 카카오모먼트 API 응답 매핑은 계정 권한과 샘플 응답 확인 후 연결해야 한다.

## 2026-05-18 PHASE 3 시작

- 목표: 네이버 트렌드, Google Trends, 뉴스 이슈, 경쟁사 이슈 수집 구조 구현.
- 범위: mock 데이터 수집, 3회 retry, `history/daily/{date}_trend_data.json` 저장, 단위 테스트.
- 보류: 실제 트렌드/뉴스 API 요청 매핑은 API 키와 응답 샘플 확인 후 연결한다.

## 2026-05-18 PHASE 3 완료

- `agents/trend_collector.py`에 네이버 트렌드, Google Trends, 뉴스 이슈, 경쟁사 이슈 mock 수집과 JSON 저장 함수를 구현했다.
- `tests/test_trend_collector.py`로 mock 수집, 저장, retry 동작을 검증했다.
- `history/daily/2026-05-18_trend_data.json`에 검증용 mock 트렌드 데이터를 저장했다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector` 및 `python -m unittest tests.test_data_collector`.
- 결과: 각 3개 테스트 통과.
- 남은 리스크: 실제 네이버 트렌드, Google Trends, 뉴스 API 응답 매핑은 API 키와 샘플 응답 확인 후 연결해야 한다.

## 2026-05-18 PHASE 3 시장조사 출처 보강

- 사용자 첨부 문서 `codex_marketing_ad_trend_sources.md`를 `docs/MARKETING_AD_TREND_SOURCES.md`로 배치했다.
- 팀원 B 트렌드 수집기에 시장조사 출처 카탈로그 로더를 추가했다.
- 카탈로그는 Markdown 표에서 category, priority, cadence, source_name, url, use_case, codex_task를 읽는다.
- `collect_trend_data` 결과에 daily, weekly, monthly 출처 계획을 포함한다.
- 검증용 `history/daily/2026-05-18_trend_data.json`에는 daily 출처 13개가 포함된다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector`.
- 결과: 7개 테스트 통과.

## 2026-05-31 PHASE 3.5 Vercel 대시보드 시작

- 목표: GitHub push 후 Vercel에서 진행 현황을 확인할 수 있는 정적 대시보드 기반 구축.
- Vercel 프로젝트: `homeproject0518`.
- Project ID: `prj_Pe7nqm93OZ6yPog5DJVGJwS0h3Ce`.
- Team ID: `team_sSX5hPGMzUn68TtAYcIXIMmr`.
- 커스텀 도메인: 보류. 기본 Vercel 도메인 사용.
- 구현 범위: `vercel.json`, `web/index.html`, `scripts/build_dashboard_data.py`, `web/data/latest_status.json`, 단위 테스트.
- 보류: 초 단위 실행 로그 실시간화와 API 기반 대시보드는 PHASE 10에서 진행한다.

## 2026-05-31 PHASE 3.5 Vercel 대시보드 완료

- `vercel.json`을 추가해 Vercel이 `web` 폴더를 정적 출력으로 배포하도록 설정했다.
- `web/index.html` 정적 대시보드를 생성했다.
- `scripts/build_dashboard_data.py`로 `web/data/latest_status.json`을 생성했다.
- `tests/test_build_dashboard_data.py`로 상태 JSON 생성 결과를 검증했다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_build_dashboard_data`.
- 결과: 9개 테스트 통과.
- 남은 리스크: Vercel 프로젝트가 GitHub 저장소와 연결되어 있어야 push 후 자동 배포가 생성된다. 자동 배포가 생성되지 않으면 Vercel UI에서 Git Repository 연결과 Root Directory 설정을 확인해야 한다.

## 2026-05-31 PHASE 3.5 운영형 대시보드 보강

- 목표: 진행 기록뿐 아니라 현재 구현된 기능을 운영 화면처럼 확인하도록 대시보드 확장.
- `scripts/build_dashboard_data.py`에 구현 기능, 에이전트 상태, 파이프라인 단계, 브랜드별 mock 지표, 수집 데이터 미리보기, 시장조사 소스 미리보기를 추가했다.
- `web/index.html`에 구현 기능 현황, 에이전트 운영판, 자동화 파이프라인, 브랜드별 mock 지표, 수집 데이터 미리보기, 시장조사 소스 섹션을 추가했다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_build_dashboard_data`.
- 결과: 9개 테스트 통과.
- 남은 리스크: 표시 수치는 아직 mock 데이터 기준이며, 실제 API 연결 후 운영 데이터로 교체해야 한다.

## 2026-05-31 PHASE 4 완료

- 목표: 팀장 에이전트가 광고 성과와 트렌드 데이터를 종합해 브랜드별 소재 방향과 개선안을 생성.
- `agents/manager.py`에 manager brief 생성, 브랜드별 우선순위 판단, 소재 방향, 추천 액션, 팀원 C handoff, 기본 Winner/Loser 분류를 구현했다.
- `history/daily/2026-05-18_manager_brief.json`에 5개 브랜드 분석 결과를 저장했다.
- `scripts/build_dashboard_data.py`와 `web/index.html`에 팀장 분석 Brief 표시를 추가했다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_build_dashboard_data`.
- 결과: 12개 테스트 통과.
- 남은 리스크: 팀장 판단은 현재 rule 기반 mock 분석이며, 실제 LLM 분석과 API 실데이터 연결은 후속 Phase에서 진행해야 한다.

## 2026-05-31 PHASE 5 완료

- 목표: 팀원 C가 팀장 분석 Brief를 바탕으로 브랜드별 스토리보드와 이미지 프롬프트를 생성.
- `agents/prompt_engineer.py`에 daily prompt pack 생성, 브랜드별 스토리보드 4개, 이미지 프롬프트 4개, 검수 피드백 반영 함수를 구현했다.
- `history/daily/2026-05-18_prompts.json`에 5개 브랜드, 총 20개 스토리보드와 20개 이미지 프롬프트를 저장했다.
- `scripts/build_dashboard_data.py`와 `web/index.html`에 프롬프트 pack 요약과 미리보기를 추가했다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_build_dashboard_data`.
- 결과: 16개 테스트 통과.
- 남은 리스크: 프롬프트는 rule 기반 mock 생성 결과이며, 실제 OpenAI API 호출과 이미지 생성은 PHASE 6 이후에 연결해야 한다.

## 2026-05-31 Dashboard Architecture View 완료

- 목표: PHASE 6 진입 전 소프트웨어 아키텍처, 전체 진행도, Phase별 테스트 결과를 대시보드에서 한눈에 확인.
- `scripts/build_dashboard_data.py`에 공식 PHASE 1-12 로드맵, 전체 진행률, 아키텍처 레이어, 데이터 흐름, 저장 계약, Phase별 테스트 결과를 추가했다.
- `web/index.html`에 전체 진행률 바, 로드맵 타일, 소프트웨어 아키텍처 도식, 데이터 흐름, Phase별 검증 표를 추가했다.
- 현재 공식 로드맵 기준 진행률은 5/12, 42%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_build_dashboard_data`.
- 결과: 16개 테스트 통과.

## 2026-05-31 PHASE 6 완료

- 목표: 팀원 C 프롬프트 pack을 팀원 D 이미지 생성 dry-run 요청으로 변환.
- `agents/image_designer.py`에 브랜드별 batch dry-run, 요청별 출력 경로, 예상 비용, 일일/월간 한도 확인, JSON 저장 명령을 구현했다.
- `history/daily/2026-05-18_image_dry_run.json`에 5개 브랜드, 20개 이미지 요청, 실사 10개와 일러스트 10개, 예상 비용 $2.64를 저장했다.
- `scripts/build_dashboard_data.py`와 `web/index.html`에 이미지 dry-run 요약과 요청 미리보기를 추가했다.
- 현재 공식 로드맵 기준 진행률은 6/12, 50%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_build_dashboard_data`.
- 결과: 20개 테스트 통과.
- 남은 리스크: 실제 gpt-image-2 API 호출은 아직 하지 않았고, 다음 PHASE 7에서 품질 검수와 재생성 판단을 연결해야 한다.

## 2026-06-01 PHASE 7 완료

- 목표: 이미지 dry-run 요청을 팀장이 검수하고 재생성 필요 여부를 판단.
- `agents/manager.py`에 품질 검수 기준, 점수화, 재생성 handoff, 최대 재시도 2회 기준을 구현했다.
- `history/daily/2026-05-18_quality_review.json`에 20개 요청 검수 결과를 저장했다.
- 모든 요청은 approved이며 평균 점수는 100.0, 재생성 필요 요청은 0개다.
- `scripts/build_dashboard_data.py`와 `web/index.html`에 품질 검수 요약과 미리보기를 추가했다.
- 현재 공식 로드맵 기준 진행률은 7/12, 58%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_build_dashboard_data`.
- 결과: 23개 테스트 통과.
- 남은 리스크: 이번 품질 검수는 dry-run 메타데이터 기준이며, 실제 이미지 픽셀 검수는 gpt-image-2 API 연결 후 확장해야 한다.

## 2026-06-03 PHASE 8 완료

- 목표: 광고 성과 mock을 Winner, Loser, Pending으로 분류하고 다음 소재 개선 패턴을 저장.
- `agents/manager.py`에 Winner/Loser 분류, 일별 학습 결과 저장, 누적 패턴 파일 갱신을 구현했다.
- `history/daily/2026-05-18_winner_loser.json`에 15개 광고 성과 분류 결과를 저장했다.
- 결과는 Winner 12개, Loser 0개, Pending 3개이며, Pending은 someud의 ROAS가 Winner 기준에 미달한 `mixed_signal`이다.
- `history/winner_loser_patterns.json`에 브랜드별 winners, losers, pending 패턴을 누적 저장했다.
- `scripts/build_dashboard_data.py`와 `web/index.html`에 Winner/Loser 요약과 학습 미리보기를 추가했다.
- 현재 공식 로드맵 기준 진행률은 8/12, 67%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_build_dashboard_data`.
- 결과: 26개 테스트 통과.
- 남은 리스크: 캠페인 집행일수는 mock 기본값 3일이며, 실제 광고 API 연결 후 매체별 집행 시작일 기준으로 교체해야 한다.

## 2026-06-03 PHASE 9 완료

- 목표: 이미지 산출물 저장 계획과 GitHub history 요약을 운영 흐름에 연결.
- `utils/gdrive_upload.py`에 Google Drive dry-run manifest 생성과 저장 함수를 구현했다.
- `history/daily/2026-05-18_gdrive_manifest.json`에는 20개 이미지 요청의 저장 계획을 저장했다.
- 저장 분류는 브랜드별 학습 top_label 기준이며 Winner 16개, Pending 4개, Loser 0개다.
- `utils/github_history.py`에 daily history 요약과 weekly history 요약 생성을 구현했다.
- `history/daily/2026-05-18_github_history_summary.json`과 `history/weekly/2026-W21.json`을 생성했다.
- `scripts/build_dashboard_data.py`와 `web/index.html`에 저장소 연동 요약과 Google Drive 경로 미리보기를 추가했다.
- 현재 공식 로드맵 기준 진행률은 9/12, 75%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_storage_utils tests.test_build_dashboard_data`.
- 결과: 30개 테스트 통과.
- GitHub main에 `30d3079 [PHASE 9] 저장소 연동 dry-run 구현` 커밋을 push했다.
- Vercel production deployment `dpl_AR5qNnGoCrLCj9YMUCMV7cwr7zyw`는 해당 커밋으로 READY이며, Vercel 인증 fetch로 루트 HTML과 `/data/latest_status.json` 200 OK를 확인했다.
- 남은 리스크: 실제 Google Drive 업로드는 아직 dry-run이며, 서비스 계정 또는 OAuth 인증 연결 후 API 호출로 확장해야 한다.
- 남은 리스크: 일반 비로그인 fetch는 Vercel Authentication 페이지를 반환하므로 공개 공유 전 Deployment Protection 설정을 확인해야 한다.

## 2026-06-03 PHASE 10 완료

- 목표: 대시보드가 정적 상태 JSON뿐 아니라 API 계약과 30초 polling으로 운영 상태를 갱신하도록 구현.
- `scripts/build_dashboard_data.py`가 `web/data/latest_status.json`과 `web/api/*.json` 12개 API 파일을 함께 생성하도록 확장했다.
- `dashboard_api.py`에 FastAPI 호환 skeleton을 추가해 상태, 에이전트, 비용, 브랜드, history, Winner/Loser, 로그 payload를 함수와 라우트로 반환할 수 있게 했다.
- `vercel.json`에 `/api/status`, `/api/agents`, `/api/costs`, `/api/brands`, `/api/brands/{brand}`, `/api/history/daily`, `/api/winner-loser`, `/api/logs` rewrite를 추가했다.
- `web/index.html`은 30초마다 cache-busting으로 대시보드 데이터와 API endpoint를 다시 읽고 API 상태표와 실행 로그를 표시한다.
- 현재 공식 로드맵 기준 진행률은 10/12, 83%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_storage_utils tests.test_dashboard_api tests.test_build_dashboard_data`.
- 결과: 33개 테스트 통과.
- 로컬 HTTP 검증: `http://localhost:4173/`, `http://localhost:4173/api/status.json`, `http://localhost:4173/api/logs.json` 모두 200 응답.
- GitHub main에 `3f7947f [PHASE 10] Dashboard API 실시간화 구현` 커밋을 push했다.
- Vercel production deployment `dpl_7WWBYC8RmWsddjDH4xDUzxhQFThi`는 해당 커밋으로 READY 상태다.
- 배포 URL의 `/api/status` 직접 fetch는 Vercel Authentication 401을 반환해, 원격 콘텐츠 검증은 보호 설정 해제 후 재확인이 필요하다.
- 남은 리스크: Vercel 정적 배포 구조에서는 실제 데이터 갱신 주기가 GitHub Actions 또는 dashboard data build 실행 주기에 묶인다.
- 남은 리스크: 비로그인 공개 접근은 Vercel Deployment Protection 설정에 따라 계속 차단될 수 있다.

## 2026-06-03 PHASE 11 완료

- 목표: 평일 02:00 KST 자동 실행, 수동 실행, 비용 초과 중단, Slack 알림, history와 dashboard 자동 커밋 흐름을 GitHub Actions에 연결.
- `scripts/run_daily_pipeline.py`를 추가해 기존 dry-run 에이전트와 저장 유틸을 일일 실행 순서로 묶었다.
- `.github/workflows/daily_run.yml`은 KST 평일 02:00에 맞춰 `0 17 * * 0-4` cron을 사용하고, `workflow_dispatch` 수동 실행을 지원한다.
- workflow는 테스트 실행, daily pipeline 실행, 생성 변경사항 커밋, Slack 조건부 알림 순서로 구성했다.
- `history/daily/2026-05-18_pipeline_run.json`에 dry-run 실행 결과를 저장했다.
- 비용 guard는 예상 이미지 비용 $2.64가 일일 $5와 월간 $79 한도 안에 있는지 확인했고 통과했다.
- 현재 공식 로드맵 기준 진행률은 11/12, 92%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_storage_utils tests.test_dashboard_api tests.test_daily_pipeline tests.test_build_dashboard_data`.
- 결과: 36개 테스트 통과.
- GitHub main에 `9283742 [PHASE 11] GitHub Actions 자동화 구현` 커밋을 push했다.
- Vercel production deployment `dpl_HdpmT5axyvv13XrYiC1b6e8r9iZn`는 해당 커밋으로 READY 상태다.
- Vercel URL의 `/api/status`는 200 OK를 반환했고, PHASE 11, 진행률 92%, 다음 단계 PHASE 12를 확인했다.
- 남은 리스크: workflow live 모드는 실제 API credential과 운영 승인 후 사용해야 한다.
- 남은 리스크: Slack 알림은 GitHub secret `SLACK_WEBHOOK_URL`이 있을 때만 전송된다.

## 2026-06-03 PHASE 12 완료

- 목표: mock/dry-run 운영을 실제 일정에 올리기 전에 preflight, 브랜드 설정 검증, 비용 리포트, 실패 기록, 대시보드 안정화 화면을 보강.
- `utils/operation_guard.py`에 운영 guard 유틸을 추가해 브랜드 config/context, credential readiness, 비용 한도, preflight 결과, error log를 한 번에 검증할 수 있게 했다.
- `scripts/run_daily_pipeline.py`는 daily 실행마다 `history/daily/{date}_preflight.json`을 저장하고, pipeline summary와 dashboard status에 안정화 결과를 포함한다.
- pipeline 예외 발생 시 `history/daily/{date}_errors.log`, 실패 summary, `state/runtime.json`의 마지막 오류 정보를 기록하도록 보강했다.
- `web/index.html`과 `scripts/build_dashboard_data.py`는 운영 안정화 섹션, 비용 guard, 브랜드 registry, 신규 브랜드 체크리스트를 표시한다.
- 현재 공식 로드맵 기준 진행률은 12/12, 100%다.
- 검증 명령: Codex 번들 Python으로 `python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_storage_utils tests.test_dashboard_api tests.test_daily_pipeline tests.test_operation_guard tests.test_build_dashboard_data`.
- 결과: 41개 테스트 통과.
- GitHub main에 `21da62e [PHASE 12] 운영 안정화 구현` 커밋을 push했다.
- Vercel production deployment `dpl_AHF7GHbUMtHcARNK9NkAM1h2m527`는 해당 커밋으로 READY 상태다.
- Vercel URL의 `/api/status`는 200 OK를 반환했고, PHASE 12, 진행률 100%, 테스트 41개 통과 상태를 확인했다.
- 남은 리스크: live 모드는 실제 API credential과 비용 승인 후 사용해야 한다.
- 남은 리스크: Google Drive 업로드와 이미지 API 호출은 여전히 dry-run이며, 운영 credential을 넣은 뒤 별도 검증이 필요하다.

