# 수능영어 지문 갭필 시스템 개발 문서

## 시스템 아키텍처

이 문서는 수능영어 지문 갭필 시스템의 기술적 구조와 구현 세부사항을 설명합니다.

### 주요 컴포넌트

1. **API 모듈** (`api/gemini_client.py`)
   - Gemini API와의 통신을 담당
   - 텍스트 분석, 갭필 생성, HTML 출력 생성 기능 제공

2. **분석 모듈** (`analysis/text_analyzer.py`)
   - 수능영어 지문의 언어적 특성 분석
   - 기본 텍스트 통계 및 언어적 분석 제공

3. **생성 모듈** (`generator/gapfill_generator.py`)
   - 분석 결과를 바탕으로 갭필 문제 생성
   - 결과 구조화 및 HTML 출력 생성

4. **최적화 모듈** (`optimization/korean_learner_optimization.py`)
   - 한국 영어학습자를 위한 최적화
   - 문법 요소 분석 및 템플릿 선택 기능 제공

5. **웹 인터페이스** (`web/app.py`, `web/templates/index.html`)
   - 사용자 인터페이스 및 웹 서버
   - 갭필 문제 생성 및 다운로드 기능 제공

### 데이터 흐름

1. 사용자가 수능영어 지문 입력
2. 웹 서버가 입력 텍스트를 분석 모듈로 전달
3. 분석 모듈이 텍스트 분석 후 결과 반환
4. 생성 모듈이 분석 결과를 바탕으로 갭필 문제 생성
5. 최적화 모듈이 한국 영어학습자를 위한 최적화 적용
6. 웹 서버가 HTML 출력을 사용자에게 제공
7. 사용자가 HTML 파일 다운로드

## 모듈별 세부 설명

### API 모듈 (`api/gemini_client.py`)

GeminiClient 클래스는 Google의 Gemini API와 통신하여 텍스트 분석 및 갭필 생성을 수행합니다.

주요 메서드:
- `generate_content()`: Gemini API를 사용하여 콘텐츠 생성
- `analyze_text()`: 수능영어 지문 분석
- `generate_gapfill()`: 갭필 문제 생성
- `generate_html_output()`: HTML 형식의 갭필 문제 생성

### 분석 모듈 (`analysis/text_analyzer.py`)

TextAnalyzer 클래스는 수능영어 지문을 분석하여 언어적 특성을 파악합니다.

주요 메서드:
- `analyze()`: 수능영어 지문 분석
- `_analyze_basic_stats()`: 기본 텍스트 통계 분석
- `_analyze_linguistic_features()`: 언어적 특성 분석
- `categorize_words()`: 분석 결과를 바탕으로 단어 분류
- `get_difficulty_levels()`: 분석 결과를 바탕으로 난이도별 단어 분류
- `get_korean_english_contrastive_points()`: 한국어-영어 대조적 관점에서 중요한 포인트 추출

### 생성 모듈 (`generator/gapfill_generator.py`)

GapfillGenerator 클래스는 분석 결과를 바탕으로 갭필 문제를 생성합니다.

주요 메서드:
- `generate()`: 갭필 문제 생성
- `_generate_gapfill_with_gemini()`: Gemini API를 통한 갭필 문제 생성
- `_structure_gapfill_result()`: 갭필 결과 구조화
- `_generate_html_output()`: HTML 출력 생성
- `save_html_to_file()`: HTML 출력을 파일로 저장

### 최적화 모듈 (`optimization/korean_learner_optimization.py`)

KoreanLearnerOptimization 클래스는 한국 영어학습자를 위한 최적화를 제공합니다.

주요 메서드:
- `optimize_prompt()`: 한국 영어학습자를 위한 프롬프트 최적화
- `_analyze_grammar_elements()`: 텍스트에서 문법 요소 분석
- `_format_grammar_elements()`: 문법 요소 분석 결과 포맷팅
- `generate_template_selection_html()`: 템플릿 선택 HTML 생성
- `optimize_html_output()`: HTML 출력 최적화

### 웹 인터페이스 (`web/app.py`, `web/templates/index.html`)

Flask 웹 애플리케이션은 사용자 인터페이스와 웹 서버를 제공합니다.

주요 라우트:
- `/`: 메인 페이지
- `/generate`: 갭필 문제 생성
- `/download/<path:filename>`: HTML 파일 다운로드
- `/api/analyze`: 텍스트 분석 API
- `/api/gapfill`: 갭필 문제 생성 API

## 확장 가능성

1. **다양한 언어 지원**: 영어 외 다른 언어로 확장 가능
2. **추가 문제 유형**: 갭필 외에도 다양한 문제 유형(선택형, 짝짓기 등) 지원 가능
3. **사용자 프로필**: 학습자의 수준과 진행 상황을 추적하는 기능 추가 가능
4. **맞춤형 학습 경로**: 학습자의 성과에 따른 맞춤형 학습 경로 제안 기능 추가 가능
5. **오프라인 모드**: API 없이도 기본적인 기능을 사용할 수 있는 오프라인 모드 추가 가능

## 기술 스택

- **백엔드**: Python, Flask
- **프론트엔드**: HTML, CSS, JavaScript, Bootstrap
- **API**: Google Gemini API
- **기타 라이브러리**: requests, json, base64, os

## 개발 환경 설정

1. Python 3.6 이상 설치
2. 필요한 패키지 설치:
```
pip install flask requests
```
3. Gemini API 키 설정:
```
export GEMINI_API_KEY="your_api_key_here"
```
4. 웹 서버 실행:
```
cd web
python app.py
```

## 테스트

테스트 코드는 `test/test_sample.py`에 구현되어 있습니다. 이 코드는 샘플 텍스트를 사용하여 전체 시스템의 흐름을 테스트합니다.

테스트 실행:
```
cd test
python test_sample.py
```

## 알려진 제한사항

1. Gemini API 키가 필요하며, API 호출 한도가 있을 수 있습니다.
2. 대용량 텍스트 처리 시 성능 저하가 발생할 수 있습니다.
3. 인터넷 연결이 필요합니다.
4. 현재 버전은 영어 텍스트만 지원합니다.

## 향후 개선 사항

1. 오프라인 모드 지원
2. 다양한 언어 지원
3. 성능 최적화
4. 사용자 프로필 및 학습 진행 상황 추적
5. 모바일 앱 개발
