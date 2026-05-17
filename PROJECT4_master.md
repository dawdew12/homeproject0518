# PROJECT 4 작업지시서
## AI 이미지 생성 자동화 시스템 — Codex 전달용 개발 명세서
> 작성일: 2026-05-10 | 버전: 1.0 | 환경: Windows / Warp + Codex CLI

---

## 1. 프로젝트 목적

마케팅 대행사의 5개 클라이언트 브랜드 광고 소재를
매일 평일 새벽 2시에 AI가 자동으로 생성·검수·저장하는 시스템.

팀장(gpt-5.5)이 광고 성과 데이터와 트렌드를 분석하여
오늘의 소재 방향을 결정하고, 팀원들이 순서대로 실행한다.

---

## 2. 팀 구성 상세

### 팀장 (manager.py)
- 모델: gpt-5.5 / reasoning: high
- 업무 1: 팀원 A·B 수집 데이터 분석 → 브랜드별 소재 방향 + 개선안 도출
- 업무 2: 팀원 C 텍스트 스토리보드 승인/반려
- 업무 3: 생성된 이미지 품질 검수 (합격/불합격 + 피드백)
- 업무 4: 광고 성과 반영 후 위너/루저 분류
- 월 비용: $7

### 팀원 A (data_collector.py)
- 모델: gpt-5.5 / reasoning: medium
- 업무: Meta / 네이버SA / 카카오모먼트 전일 성과 수집
- 수집 지표: CTR, CVR, CPA, ROAS (캠페인/소재 단위)
- 출력: history/daily/{날짜}_ad_data.json
- 월 비용: $2

### 팀원 B (trend_collector.py)
- 모델: gpt-5.5 / reasoning: low
- 업무: 네이버 트렌드 / 구글 트렌드 / 뉴스 수집
- 수집 항목: 브랜드 관련 키워드 검색량, 시즌 이슈, 경쟁사 동향
- 출력: history/daily/{날짜}_trend_data.json
- 팀원 A와 병렬 실행
- 월 비용: $1

### 팀원 C (prompt_engineer.py)
- 모델: gpt-5.5 / reasoning: high
- 업무 1: 브랜드별 텍스트 스토리보드 작성 (이미지 생성 전 방향 확인)
- 업무 2: 팀장 승인 후 gpt-image-2 프롬프트 생성
- 업무 3: 불합격 소재 피드백 반영 → 재생성 프롬프트 수정
- 프롬프트 구조:
  ```
  [브랜드 정체성] 컬러코드, 톤, 금지사항
  [오늘의 방향] 팀장 개선안 반영
  [이미지 스펙] 해상도, 구도, 여백
  [금지] 텍스트 삽입 금지 / 카피 영역 여백만 확보
  ```
- 출력: history/daily/{날짜}_prompts.json
- 월 비용: $5

### 팀원 D (image_designer.py)
- 모델: gpt-image-2 / Batch API
- 업무: 프롬프트 → 이미지 생성
- 이미지 분류:
  - 실사(인물·배경·풍경): 2048×2048 high / $0.211 Batch
  - 일러스트/3D: 2048×2048 medium / $0.053 Batch
- 배칭: n=4 (브랜드당 1회 API 호출로 4장)
- 캐싱: 브랜드 컨텍스트 프롬프트 캐싱 적용 (75% 할인)
- 출력: outputs/{브랜드}/{날짜}/{파일명}.png
- 월 비용: $61

---

## 3. 일일 자동화 루프 (평일 02:00 실행)

```
[02:00] STEP 1+2 병렬 실행
  ├── 팀원 A: 광고 성과 수집 (Meta/네이버SA/카카오)
  └── 팀원 B: 트렌드·시즌·경쟁사 수집

[02:06] STEP 3
  └── 팀장: 수집 데이터 분석 → 브랜드별 소재 방향 + 개선안

[02:11] STEP 4
  └── 팀원 C: 텍스트 스토리보드 작성 (5브랜드 × 4장)
         → 팀장 자동 승인/반려
         → 승인 후 gpt-image-2 프롬프트 생성

[02:20] STEP 5
  └── 팀원 D: 이미지 생성 Batch 요청
         └── 5브랜드 × 실사 2장(high) + 일러스트 2장(medium)
         └── n=4 배칭 (브랜드당 1번 호출)

[02:38] STEP 6
  └── 팀장: 품질 검수
         ├── 합격 → STEP 9(저장)으로
         └── 불합격 → 피드백 → STEP 7

[재생성 루프 — 최대 2회/소재]
[02:45] STEP 7
  └── 팀원 C: 피드백 반영 프롬프트 수정

[02:48] STEP 8
  └── 팀원 D: 재생성
         └── 2회 초과 시 → "보류" 처리 → 다음날 재시도

[03:05] STEP 9
  └── 파일 라벨링 + 구글 드라이브 업로드
  └── GitHub 이력 커밋
  └── winner_loser_patterns.json 업데이트
```

---

## 4. 이미지 생성 상세 규칙

### 4-1. 해상도 및 품질
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

### 4-2. 브랜드당 구성 (일 4장)
- 실사 2장 + 일러스트 2장
- 1회 API 호출: n=4 파라미터로 4장 동시 요청

### 4-3. 프롬프트 필수 규칙
- "NO text, NO watermarks, NO logos" 반드시 포함
- "Leave {X}% bottom space for copywriting" 여백 지정
- 브랜드 컬러 헥스코드 명시
- 타겟 감성 명시 (프리미엄/감성/기능성 등)

### 4-4. 재생성 로직
```python
MAX_RETRY = 2
retry_count = {}  # {image_id: count}

def request_regeneration(image_id, feedback):
    if retry_count.get(image_id, 0) >= MAX_RETRY:
        status = "보류"
        return None
    retry_count[image_id] = retry_count.get(image_id, 0) + 1
    new_prompt = apply_feedback(original_prompt, feedback)
    return generate_image(new_prompt)
```

---

## 5. 파일 명명 규칙

```
형식: {브랜드}_{YYYYMMDD}_{유형}_{키워드1}-{키워드2}-{키워드3}_{품질}.png

예시:
someud_20260512_실사_어버이날-부부-황토침대_high.png
kinda_20260512_일러스트_극손상-비포애프터-핑크_medium.png
melliance_20260512_실사_봄-컬렉션-모델_high.png
```

---

## 6. 저장소 구조

### 6-1. 구글 드라이브
```
AIPR_소재관리/
├── someud/
│   ├── 2026-05-12/
│   │   ├── winner/
│   │   │   └── someud_20260512_실사_어버이날-부부-황토침대_high.png
│   │   └── loser/
│   │       └── someud_20260512_일러스트_미니멀-흰배경_medium.png
│   └── 2026-05-13/
├── kinda/
└── ...
```

### 6-2. GitHub (history/)
```
history/
├── daily/
│   ├── 2026-05-12.json        ← 일별 실행 이력
│   └── 2026-05-13.json
├── weekly/
│   └── 2026-W19.json
└── winner_loser_patterns.json  ← 누적 패턴 데이터
```

### 6-3. daily/{날짜}.json 구조
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

### 6-4. GitHub 자동 커밋 메시지 형식
```
📊 [2026-05-12] 소머드 W:2 L:1 P:1 | 킨다 W:3 L:0 P:1 | 총비용 $2.92
```

---

## 7. 위너/루저 판단 기준

```python
WINNER_CRITERIA = {
    "ctr_min": 2.0,      # CTR >= 2.0% (AND)
    "roas_min": 250,     # ROAS >= 250% (AND)
    "cpa_max_ratio": 1.2 # CPA <= 목표CPA × 1.2 (AND)
}

LOSER_CRITERIA = {
    "ctr_max": 0.8,      # CTR < 0.8% (OR)
    "roas_min": 120,     # ROAS < 120% (OR)
    "cpa_max_ratio": 2.0 # CPA > 목표CPA × 2.0 (OR)
}

PENDING_CRITERIA = {
    "min_days": 3,        # 집행 3일 미만
    "min_impressions": 1000  # 노출 1,000회 미만
}
```

---

## 8. 브랜드별 설정 (brands/{브랜드}/config.toml)

```toml
# 소머드 예시
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
real_photo_count = 2    # 실사 장수/일
illustration_count = 2  # 일러스트 장수/일
copy_area_bottom_pct = 25  # 하단 여백 % (카피 삽입용)
```

---

## 9. GitHub Actions 스케줄러

```yaml
# .github/workflows/daily_run.yml
name: AIPR 매일 이미지 생성

on:
  schedule:
    - cron: '0 17 * * 1-5'  # 평일 02:00 KST (UTC+9 = UTC 17:00 전날)
  workflow_dispatch:          # 수동 실행 버튼

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Python 설치
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 패키지 설치
        run: pip install -r requirements.txt

      - name: 팀원 A+B 병렬 수집
        run: |
          python agents/data_collector.py &
          python agents/trend_collector.py &
          wait
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          META_ACCESS_TOKEN: ${{ secrets.META_ACCESS_TOKEN }}
          NAVER_SA_API_KEY: ${{ secrets.NAVER_SA_API_KEY }}

      - name: 팀장 분석
        run: python agents/manager.py --step analyze
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: 팀원 C 프롬프트 제작
        run: python agents/prompt_engineer.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: 팀원 D 이미지 생성
        run: python agents/image_designer.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: 팀장 품질 검수
        run: python agents/manager.py --step review
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: 구글 드라이브 저장
        run: python utils/gdrive_upload.py
        env:
          GOOGLE_SERVICE_ACCOUNT: ${{ secrets.GOOGLE_SERVICE_ACCOUNT }}

      - name: GitHub 이력 커밋
        run: python utils/github_history.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 10. .env 키 목록

```bash
# OpenAI
OPENAI_API_KEY=

# Meta
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=

# 네이버
NAVER_SA_API_KEY=
NAVER_SA_SECRET_KEY=
NAVER_SA_CUSTOMER_ID=
NAVER_NEWS_CLIENT_ID=
NAVER_NEWS_CLIENT_SECRET=

# 카카오
KAKAO_MOMENT_ACCESS_TOKEN=

# 구글
GOOGLE_SERVICE_ACCOUNT_JSON=  # base64 인코딩된 서비스 계정 JSON

# 슬랙 (오류 알림용)
SLACK_WEBHOOK_URL=

# 비용 한도
DAILY_COST_LIMIT_USD=5.00
MONTHLY_COST_LIMIT_USD=79.00
```

---

## 11. 월 비용 목표

| 구성요소 | 월 비용 |
|---|---|
| 팀장 (gpt-5.5 high) | $7 |
| 팀원 A (gpt-5.5 medium) | $2 |
| 팀원 B (gpt-5.5 low) | $1 |
| 팀원 C (gpt-5.5 high) | $5 |
| 팀원 D (gpt-image-2 Batch) | $61 |
| 이력 분석 | $3 |
| **합계** | **$79** |

---

## 12. Phase별 개발 순서

```
PHASE 1: 프로젝트 기반 세팅
  → 폴더 구조 / AGENTS.md / .env.example / requirements.txt

PHASE 2: 팀원 A·B 데이터 수집
  → Meta / 네이버SA / 카카오 / 트렌드 API 연동

PHASE 3: 팀장 분석 엔진
  → 수집 데이터 분석 + 브랜드별 소재 방향 생성

PHASE 4: 팀원 C 프롬프트 엔지니어
  → 텍스트 스토리보드 + 이미지 프롬프트 생성

PHASE 5: 팀원 D 이미지 생성
  → gpt-image-2 Batch API + 파일 라벨링

PHASE 6: 팀장 품질검수 + 위너/루저
  → 검수 로직 + 재생성 루프 + 분류

PHASE 7: 저장소 연동
  → 구글 드라이브 + GitHub 이력

PHASE 8: 대시보드 API 연동
  → FastAPI 서버 + AIPR_Dashboard.html 실시간화

PHASE 9: GitHub Actions 스케줄러
  → 평일 02:00 자동 실행 + 슬랙 알림

PHASE 10: 안정화
  → 예외처리 + 비용 모니터링 + 브랜드 추가 편의성
```

---

## 13. Codex 첫 번째 실행 명령어

```bash
# D:\AIPR 폴더에서 실행
cd D:\AIPR
codex "AGENTS.md와 PROJECT4_작업지시서.md를 읽고
PHASE 1을 시작해줘.
폴더 구조 전체 생성, .env.example, requirements.txt,
각 에이전트 파일 빈 껍데기(주석+함수 시그니처만)를 만들어줘.
Windows 환경이고 Python 3.11 기준."
```

---

*이 문서는 Codex에게 직접 전달하는 작업지시서입니다.*
*각 Phase 완료 후 피드백을 반영하며 다음 Phase를 진행하세요.*
