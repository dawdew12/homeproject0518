# PHASE 1 Checklist

- [x] 기준 문서 확인: AGENTS.md, PROJECT_MASTER_v2_1.md, AIPR_Dashboard.html
- [x] 최신 PROJECT_MASTER.md 루트 배치
- [x] 전체 폴더 구조 생성
- [x] .env.example 생성
- [x] requirements.txt 생성
- [x] README.md 생성
- [x] state/current_phase.json 생성
- [x] state/runtime.json 생성
- [x] logs 기본 파일 생성
- [x] agents skeleton 생성
- [x] utils skeleton 생성
- [x] 브랜드 기본 폴더와 설정 파일 생성
- [x] docs/ARCHITECTURE.md 생성
- [x] docs/DASHBOARD_SPEC.md 생성
- [x] docs/PHASE_LOG.md 생성
- [x] 기존 대시보드 원본 보존 및 dashboard/AIPR_Dashboard.html 배치
- [x] PHASE 1 검증 실행

# PHASE 2 Checklist

- [x] PHASE 1 완료 상태 확인
- [x] 광고 수집 대상 파일 확인
- [x] Meta mock 수집 구조 구현
- [x] 네이버SA mock 수집 구조 구현
- [x] 카카오모먼트 mock 수집 구조 구현
- [x] 3회 retry 공통 함수 구현
- [x] `history/daily/{date}_ad_data.json` 저장 함수 구현
- [x] 수집기 단위 테스트 추가
- [x] PHASE 2 검증 실행

# PHASE 3 Checklist

- [x] PHASE 2 완료 상태 확인
- [x] 트렌드 수집 대상 파일 확인
- [x] 네이버 트렌드 mock 수집 구조 구현
- [x] Google Trends mock 수집 구조 구현
- [x] 뉴스 이슈 mock 수집 구조 구현
- [x] 경쟁사 이슈 mock 수집 구조 구현
- [x] 3회 retry 공통 함수 구현
- [x] `history/daily/{date}_trend_data.json` 저장 함수 구현
- [x] 수집기 단위 테스트 추가
- [x] PHASE 3 검증 실행

# PHASE 3 Source Catalog Update

- [x] 첨부 시장조사 출처 문서를 `docs/MARKETING_AD_TREND_SOURCES.md`로 배치
- [x] 팀원 B가 출처 카탈로그를 daily/weekly/monthly로 읽는 구조 구현
- [x] daily 시장조사 출처를 트렌드 수집 payload에 포함
- [x] 출처 카탈로그 로드 테스트 추가
- [x] 검증용 트렌드 JSON 재생성

# PHASE 3.5 Vercel Dashboard Checklist

- [x] Vercel 프로젝트 ID와 팀 ID 확인
- [x] 커스텀 도메인은 보류하고 기본 Vercel 도메인 사용 결정
- [x] Vercel 정적 배포 설정 `vercel.json` 생성
- [x] `web/index.html` 진행 현황 대시보드 생성
- [x] `scripts/build_dashboard_data.py` 생성
- [x] `web/data/latest_status.json` 생성 구조 구현
- [x] 대시보드 데이터 생성 테스트 추가
- [x] Vercel 대시보드 검증 실행

# PHASE 3.5 Dashboard Operations View Update

- [x] 구현 기능 현황을 대시보드 JSON에 추가
- [x] 에이전트별 구현 상태를 대시보드 JSON에 추가
- [x] 자동화 파이프라인 단계별 상태를 대시보드 JSON에 추가
- [x] 브랜드별 광고/트렌드 mock 지표를 대시보드 JSON에 추가
- [x] 광고/트렌드 수집 데이터 미리보기를 대시보드에 표시
- [x] 시장조사 daily 출처를 대시보드에 표시
- [x] 운영형 대시보드 테스트 실행

# PHASE 4 Manager Analysis Checklist

- [x] PHASE 3.5 완료 상태 확인
- [x] 광고와 트렌드 daily JSON 구조 확인
- [x] 팀장 분석 엔진 구현
- [x] 브랜드별 우선순위와 소재 방향 생성
- [x] 프롬프트 엔지니어 handoff 생성
- [x] `history/daily/{date}_manager_brief.json` 저장 함수 구현
- [x] 팀장 분석 단위 테스트 추가
- [x] 대시보드 JSON에 팀장 분석 결과 추가
- [x] 대시보드 화면에 팀장 분석 Brief 표시
- [x] PHASE 4 검증 실행

# PHASE 5 Prompt Engineering Checklist

- [x] PHASE 4 완료 상태 확인
- [x] 팀장 분석 Brief와 브랜드 설정 구조 확인
- [x] 팀원 C 스토리보드 생성 로직 구현
- [x] 브랜드별 이미지 프롬프트 4개 생성 로직 구현
- [x] 검수 피드백 반영 로직 구현
- [x] `history/daily/{date}_prompts.json` 저장 함수 구현
- [x] 프롬프트 엔지니어 단위 테스트 추가
- [x] 대시보드 JSON에 프롬프트 생성 결과 추가
- [x] 대시보드 화면에 프롬프트 미리보기 표시
- [x] PHASE 5 검증 실행

# Dashboard Architecture View Update

- [x] 현재 대시보드 데이터 구조 확인
- [x] 전체 진행률 수치 모델 추가
- [x] 소프트웨어 아키텍처 레이어와 데이터 흐름 모델 추가
- [x] Phase별 검증 결과 모델 추가
- [x] 대시보드 화면에 도식형 아키텍처 섹션 추가
- [x] 대시보드 화면에 전체 진행도와 Phase별 테스트 결과 표시
- [x] 대시보드 데이터 테스트 보강
- [x] 검증 실행

# Dashboard Metadata Sync

- [x] 이전 작업 후 남은 누락 여부 확인
- [x] 최신 커밋이 대시보드 JSON에 반영되도록 재생성
- [x] 대시보드 데이터 테스트 재실행
- [x] GitHub 저장 및 Vercel 반영 확인

# Dashboard Live Commit Sync

- [x] 정적 JSON 최근 커밋 목록의 한 커밋 지연 구조 확인
- [x] GitHub 공개 API 기반 최근 커밋 실시간 로딩 추가
- [x] GitHub API 실패 시 기존 JSON 커밋 목록 fallback 유지
- [x] 검증 실행

# PHASE 6 Image Dry Run Checklist

- [x] PHASE 5 프롬프트 pack 구조 확인
- [x] 팀원 D 이미지 dry-run batch 생성 로직 구현
- [x] 브랜드별 출력 경로와 예상 비용 계산 구현
- [x] `history/daily/{date}_image_dry_run.json` 저장 구현
- [x] 이미지 dry-run 단위 테스트 추가
- [x] 대시보드 JSON에 이미지 dry-run 결과 추가
- [x] 대시보드 화면에 이미지 dry-run 요약 표시
- [x] PHASE 6 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# PHASE 7 Quality Review Checklist

- [x] PHASE 6 이미지 dry-run 구조 확인
- [x] 팀장 품질 검수 기준 구현
- [x] 재생성 필요 여부와 retry 제한 판단 구현
- [x] `history/daily/{date}_quality_review.json` 저장 구현
- [x] 품질 검수 단위 테스트 추가
- [x] 대시보드 JSON에 품질 검수 결과 추가
- [x] 대시보드 화면에 품질 검수 요약 표시
- [x] PHASE 7 검증 실행
- [x] GitHub 저장 확인
- [ ] Vercel 반영 확인은 앱 토큰 재인증 후 진행

# PHASE 8 Winner/Loser Learning Checklist

- [x] PHASE 7 완료 상태와 기존 분류 로직 확인
- [x] 광고 성과 mock과 브랜드별 목표 기준 확인
- [x] Winner, Loser, Pending 판정 기준 구현
- [x] `history/daily/{date}_winner_loser.json` 저장 구현
- [x] `history/winner_loser_patterns.json` 학습 패턴 갱신 구현
- [x] Winner/Loser 단위 테스트 추가
- [x] 대시보드 JSON에 학습 결과 추가
- [x] 대시보드 화면에 학습 결과 표시
- [x] PHASE 8 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# PHASE 9 Storage Integration Checklist

- [x] PHASE 8 완료 상태와 저장소 skeleton 확인
- [x] Google Drive 저장 manifest 생성 로직 구현
- [x] GitHub daily history 요약 로직 구현
- [x] GitHub weekly history 요약 로직 구현
- [x] `history/daily/{date}_gdrive_manifest.json` 저장
- [x] `history/daily/{date}_github_history_summary.json` 저장
- [x] `history/weekly/{week}.json` 저장
- [x] 저장소 연동 단위 테스트 추가
- [x] 대시보드 JSON에 저장소 연동 결과 추가
- [x] 대시보드 화면에 저장소 연동 미리보기 표시
- [x] PHASE 9 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# PHASE 10 Dashboard Realtime Checklist

- [x] PHASE 9 완료 상태와 대시보드 요구사항 확인
- [x] 정적 JSON API payload 생성 구조 구현
- [x] FastAPI dashboard API skeleton 구현
- [x] Vercel `/api/*` rewrite 구성
- [x] 대시보드 30초 polling 구현
- [x] API 상태와 실행 로그 화면 표시
- [x] Dashboard API 단위 테스트 추가
- [x] 대시보드 JSON과 API JSON 재생성
- [x] PHASE 10 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# PHASE 11 GitHub Actions Automation Checklist

- [x] PHASE 10 완료 상태와 workflow placeholder 확인
- [x] daily pipeline runner 구현
- [x] 비용 초과 중단 guard 구현
- [x] GitHub Actions schedule과 workflow_dispatch 연결
- [x] Slack 알림 step 조건부 연결
- [x] history와 dashboard 변경사항 자동 커밋 step 연결
- [x] PHASE 11 단위 테스트 추가
- [x] 대시보드 JSON과 API JSON 재생성
- [x] PHASE 11 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# PHASE 12 Stabilization Checklist

- [x] PHASE 11 완료 상태와 안정화 요구사항 확인
- [x] 운영 preflight 유틸 구현
- [x] 브랜드 설정 검증과 추가 가이드 구현
- [x] 비용 최적화 리포트 구현
- [x] pipeline 실패 기록과 error log 저장 보강
- [x] 대시보드 안정화 섹션 추가
- [x] PHASE 12 단위 테스트 추가
- [x] 대시보드 JSON과 API JSON 재생성
- [x] PHASE 12 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# ChatGPT Image Generation Test Checklist

- [x] `AGENTS.md`와 현재 작업트리 확인
- [x] OpenAI API 키 존재 여부 확인
- [x] 실제 이미지 생성 테스트 실행
- [x] 이미지 생성 테스트 결과를 history에 기록
- [x] `AIPR_Dashboard.html` 제작 여부와 해시 확인
- [x] 대시보드 데이터 재생성 또는 보강
- [x] 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# Brand Routine Dashboard Checklist

- [x] `AGENTS.md`와 현재 자동화 산출물 구조 확인
- [x] 기존 `AIPR_Dashboard.html`과 `web/index.html` 표시 범위 확인
- [x] 브랜드별 파트별 실행 결과 payload 생성
- [x] 광고성과, 트렌드, 분석·개선안, 소재 생성 UI 추가
- [x] 루트 `AIPR_Dashboard.html`에서도 바로 확인 가능하게 반영
- [x] 대시보드 JSON과 API JSON 재생성
- [x] 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인

# Trend Briefing Dashboard Checklist

- [x] `AGENTS.md`와 현재 작업트리 확인
- [x] 최신 트렌드 수집 산출물 구조 확인
- [x] 수집 트렌드 브리핑 payload 생성
- [x] Vercel용 `web/index.html`에 트렌드 브리핑 목록 표시
- [x] 루트 `AIPR_Dashboard.html`에 트렌드 브리핑 목록 표시
- [x] 대시보드 JSON과 API JSON 재생성
- [x] 검증 실행
- [x] GitHub 저장 및 Vercel 반영 확인
 
# Portal SNS Daily Clip Checklist

- [x] `AGENTS.md`와 기존 트렌드 수집 구조 확인
- [x] 포털 뉴스와 SNS 공개 검색 기준 수집 범위 확정
- [x] 일간 브랜드별 3줄 요약 JSON 산출물 생성
- [x] Vercel용 대시보드에 브랜드별 클리핑 요약 표시
- [x] 루트 `AIPR_Dashboard.html`에 브랜드별 클리핑 요약 표시
- [x] 테스트와 브라우저 렌더링 검증
- [x] GitHub 저장 및 Vercel 배포 확인

# Team B Article Link Brief Checklist

- [x] `AGENTS.md`와 기존 팀원 B 클리핑 구조 확인
- [x] 전체 관련 기사 링크 목록 생성
- [x] 모든 기사 링크의 공통 시사점 한 줄 생성
- [x] Vercel용 대시보드 상단에 시사점과 기사 링크 표시
- [x] 루트 `AIPR_Dashboard.html` 상단에 시사점과 기사 링크 표시
- [x] 오늘 날짜 live 수집과 대시보드 JSON 재생성
- [x] 테스트와 로컬 렌더링 검증
- [x] GitHub 저장 및 Vercel 배포 확인

# Content Tab Image Generation Checklist

- [x] 기존 이미지 생성 테스트와 대시보드 구조 확인.
- [x] 브랜드별 5개 콘텐츠 소재 데이터 설계.
- [x] ChatGPT 이미지 생성 테스트 산출물 저장.
- [x] 루트 `AIPR_Dashboard.html`에 콘텐츠 탭 추가.
- [x] Vercel용 `web/index.html`과 JSON/API에 콘텐츠 데이터 노출.
- [x] 대시보드 데이터 재생성.
- [x] 테스트와 로컬 렌더링 검증.
- [x] GitHub 저장과 Vercel 배포 확인.

# Team Dashboard Live Test Data And Research Tab Checklist

- [x] 현재 대시보드 탭 구조와 실제 테스트 데이터 위치 확인.
- [x] `checklist.md`와 `context-notes.md`에 작업 의사결정 기록.
- [x] 팀 대시보드에 실제 테스트 수치 연결.
- [x] 포털/SNS 일간 3줄 요약과 트렌드 수집 브리핑 목록을 별도 리서치 탭으로 분리.
- [x] Vercel용 `web/index.html`에도 같은 분류와 실제 수치 반영.
- [x] 대시보드 데이터 재생성 및 테스트 실행.
- [x] 로컬 브라우저 렌더링 검증.
- [ ] GitHub 저장과 Vercel 배포 확인.
