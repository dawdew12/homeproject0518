# AGENTS.md — PROJECT 4: AI 이미지 자동화 팀

## 프로젝트 개요
마케팅 대행사(그로스마케팅) 운영용 AI 이미지 생성 자동화 시스템.
매일 평일 새벽 02:00, 5개 브랜드 광고 소재를 자동으로 생성·검수·저장하는 멀티에이전트 파이프라인.

## 기술 스택
- Language: Python 3.11+
- AI: OpenAI gpt-5.5 API / gpt-image-2 API (Batch)
- Storage: Google Drive API / GitHub API
- Scheduler: GitHub Actions (평일 02:00 KST)
- Ad APIs: Meta Marketing API / 네이버SA API / 카카오모먼트 API
- Trend APIs: 네이버 트렌드 API / pytrends (구글)

## 폴더 구조
```
D:\AIPR\
├── AGENTS.md                  ← 이 파일
├── .env                       ← API 키 (절대 커밋 금지)
├── .env.example               ← 키 슬롯 템플릿
├── requirements.txt
├── agents/
│   ├── manager.py             ← 팀장 (분석·검수·판단)
│   ├── data_collector.py      ← 팀원 A (광고 수집)
│   ├── trend_collector.py     ← 팀원 B (트렌드 수집)
│   ├── prompt_engineer.py     ← 팀원 C (프롬프트 제작)
│   └── image_designer.py      ← 팀원 D (이미지 생성)
├── brands/
│   ├── someud/
│   │   ├── brand_context.md   ← 브랜드 컨텍스트 (캐싱용)
│   │   └── config.toml        ← 브랜드 설정
│   ├── kinda/
│   ├── melliance/
│   ├── paperback/
│   └── baren/
├── utils/
│   ├── gdrive_upload.py
│   ├── github_history.py
│   └── cost_tracker.py
├── outputs/                   ← 생성 이미지 임시 저장
├── history/
│   ├── daily/
│   └── winner_loser_patterns.json
├── dashboard/
│   └── AIPR_Dashboard.html
└── .github/
    └── workflows/
        └── daily_run.yml

```

## 팀 구성 및 모델

| 역할 | 파일 | 모델 | reasoning | 주요 업무 |
|---|---|---|---|---|
| 팀장 | manager.py | gpt-5.5 | high | 분석·개선안·검수·위너/루저 판단 |
| 팀원 A | data_collector.py | gpt-5.5 | medium | Meta/네이버SA/카카오 성과 수집 |
| 팀원 B | trend_collector.py | gpt-5.5 | low | 네이버/구글 트렌드·시즌·경쟁사 |
| 팀원 C | prompt_engineer.py | gpt-5.5 | high | 스토리보드·프롬프트 제작·재생성 |
| 팀원 D | image_designer.py | gpt-image-2 | Batch | 실사 2K high·일러스트 2K medium |

## 브랜드 목록
- someud (소머드): 황토 매트리스, 타겟 40-60대 여성
- kinda (킨다): 극손상 헤어팩, 타겟 35-44 여성
- melliance (멜리언스): 뷰티 브랜드
- paperback (페이퍼백): 라이프스타일 브랜드
- baren (바렌): 기능성 브랜드

## 코딩 규칙
- 모든 API 키는 .env에서만 로드 (하드코딩 절대 금지)
- 각 에이전트 파일 첫 줄에 한국어 주석으로 역할 명시
- API 호출 실패 시 3회 자동 재시도 후 슬랙 알림
- 모든 실행 결과는 outputs/ 또는 history/에 저장
- 금액 단위: USD (소수점 4자리), 원화 KRW
- 함수명은 snake_case, 한국어 docstring 포함
- 에러 로그: history/daily/{날짜}_errors.log

## 이미지 생성 규칙
- 실사(인물·배경·풍경): 2K high Batch = $0.211/장
- 일러스트/3D: 2K medium Batch = $0.053/장
- 초안 이미지 생성 금지 (텍스트 스토리보드로 방향 확인)
- n=4 배칭: 브랜드당 1회 API 호출로 4장 요청
- 프롬프트 캐싱: 브랜드 컨텍스트 75% 할인 적용
- 재생성 제한: 소재당 최대 2회
- 텍스트 삽입 금지: 카피 영역 여백만 확보

## 위너/루저 판단 기준
- Winner (AND 조건): CTR ≥ 2.0%, ROAS ≥ 250%, CPA ≤ 목표×1.2
- Loser (OR 조건): CTR < 0.8%, ROAS < 120%, CPA > 목표×2.0
- Pending: 집행 3일 미만 OR 노출 1,000회 미만

## 파일 명명 규칙
```
{브랜드}_{YYYYMMDD}_{유형}_{키워드1}-{키워드2}-{키워드3}_{품질}.png
예: someud_20260512_실사_어버이날-부부-황토침대_high.png
    kinda_20260512_일러스트_극손상-비포애프터-핑크_medium.png
```

## 운영 일정
- 실행 시간: 평일(월~금) 02:00 KST
- 월 운영일: 21일
- 일 생산량: 20장 (5브랜드 × 4장)
- 월 목표량: 420장

## 월 예산 한도
- 총 $79/월
- 팀원 D 이미지: 최대 $65/월
- 일일 비용 초과($5) 시 슬랙 경고 알림
