# AIPR 멀티 AI 에이전트 광고 소재 자동화 시스템

AIPR은 5개 브랜드의 광고 소재를 평일 새벽 02:00 KST에 자동 생성, 검수, 저장하기 위한 Python 기반 멀티 에이전트 프로젝트입니다.

## 현재 Phase

PHASE 1: 프로젝트 기반 세팅과 아키텍처 문서화.

## 핵심 흐름

1. 팀원 A가 광고 성과 데이터를 수집합니다.
2. 팀원 B가 트렌드와 시즌 이슈를 수집합니다.
3. 팀장이 데이터 기반 소재 방향을 결정합니다.
4. 팀원 C가 스토리보드와 이미지 프롬프트를 작성합니다.
5. 팀원 D가 이미지를 생성합니다.
6. 팀장이 품질을 검수하고 재생성을 판단합니다.
7. 결과를 Google Drive, GitHub history, Dashboard에 연결합니다.

## PHASE 1 범위

- 폴더 구조 생성.
- `.env.example`, `requirements.txt`, `state`, `logs` 생성.
- 에이전트와 유틸리티 skeleton 생성.
- 기존 대시보드 HTML 보존 및 `dashboard/` 배치.
- 아키텍처와 대시보드 연동 문서 작성.

## 실행 전 준비

`.env.example`을 참고해 로컬 또는 GitHub Secrets에 실제 API 키를 설정합니다. `.env` 파일은 커밋하지 않습니다.

## 검증

PHASE 1의 최소 검증은 폴더/파일 존재 여부와 Python skeleton import 가능 여부입니다.