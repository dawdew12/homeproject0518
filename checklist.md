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
