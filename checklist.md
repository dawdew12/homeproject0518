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
- [ ] GitHub 저장 및 Vercel 반영 확인
