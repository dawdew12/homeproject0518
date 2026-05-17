# AIPR Architecture

## 목적

AIPR은 광고 성과, 트렌드, 브랜드 컨텍스트를 바탕으로 매일 광고 소재를 자동 생성하고 검수하는 멀티 에이전트 파이프라인이다.

## 주요 구성

- `agents/data_collector.py`: Meta, 네이버SA, 카카오모먼트 성과 수집.
- `agents/trend_collector.py`: 네이버/구글 트렌드, 뉴스, 시즌 이슈 수집.
- `agents/manager.py`: 분석, 스토리보드 승인, 이미지 검수, Winner/Loser 판단.
- `agents/prompt_engineer.py`: 텍스트 스토리보드와 이미지 프롬프트 작성.
- `agents/image_designer.py`: gpt-image-2 Batch 기반 이미지 생성과 재생성 요청 처리.
- `utils/cost_tracker.py`: 일일/월간 비용 계산과 한도 확인.
- `utils/gdrive_upload.py`: outputs 폴더 결과를 Google Drive 구조에 업로드.
- `utils/github_history.py`: history 변경사항 요약과 GitHub 커밋.

## 데이터 흐름

1. 팀원 A와 팀원 B가 병렬로 데이터를 수집한다.
2. 팀장이 광고 성과와 트렌드를 분석해 브랜드별 방향을 만든다.
3. 팀원 C가 스토리보드와 이미지 프롬프트를 작성한다.
4. 팀원 D가 브랜드별 4장씩 이미지를 생성한다.
5. 팀장이 이미지 품질을 검수하고 필요 시 재생성을 요청한다.
6. 결과는 `outputs`, `history`, `logs`, `state`에 기록된다.
7. PHASE 10에서 Dashboard가 JSON 또는 FastAPI API를 통해 상태를 표시한다.

## 상태 파일

- `state/current_phase.json`: 현재 Phase와 마지막 성공/오류 상태.
- `state/runtime.json`: 비용, 이미지 생성 수, 승인 수, 재시도 수, 실행 시간.

## 저장 위치

- `history/daily`: 일별 광고, 트렌드, 프롬프트, 실행 결과.
- `history/weekly`: 주간 요약.
- `history/winner_loser_patterns.json`: 누적 Winner/Loser 패턴.
- `outputs/{brand}/{date}`: 생성 이미지.
- `logs`: 실행, API 오류, 이미지 생성, 비용 추적 로그.

## PHASE 1 범위

현재 문서는 기반 구조를 설명한다. 실제 API 호출, 이미지 생성, 대시보드 실시간화는 후속 Phase에서 구현한다.