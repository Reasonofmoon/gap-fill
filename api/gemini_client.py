import base64
import os
import requests
import json

class GeminiClient:
    """
    Gemini API 클라이언트 클래스
    수능영어 지문 분석 및 갭필 문제 생성을 위한 Gemini API 통합
    """
    
    def __init__(self, api_key=None):
        """
        GeminiClient 초기화
        
        Args:
            api_key (str, optional): Gemini API 키. 없으면 환경 변수에서 가져옴
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API 키가 필요합니다. 환경 변수 GEMINI_API_KEY를 설정하거나 초기화 시 제공하세요.")
        
        self.model = "gemini-2.5-pro-preview-03-25"  # 최신 모델 사용
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        
    def _prepare_request(self, prompt, system_instruction=None):
        """
        API 요청 데이터 준비
        
        Args:
            prompt (str): 사용자 프롬프트
            system_instruction (str, optional): 시스템 지시사항
            
        Returns:
            dict: API 요청 데이터
        """
        contents = []
        
        # 시스템 지시사항이 있으면 추가
        if system_instruction:
            contents.append({
                "role": "system",
                "parts": [{"text": system_instruction}]
            })
        
        # 사용자 프롬프트 추가
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        return {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,  # 낮은 온도로 일관된 결과 생성
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 8192,  # 충분한 출력 토큰 확보
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
    
    def generate_content(self, prompt, system_instruction=None):
        """
        Gemini API를 사용하여 콘텐츠 생성
        
        Args:
            prompt (str): 사용자 프롬프트
            system_instruction (str, optional): 시스템 지시사항
            
        Returns:
            dict: API 응답 데이터
        """
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        data = self._prepare_request(prompt, system_instruction)
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data)
            )
            response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None
    
    def analyze_text(self, text):
        """
        수능영어 지문 분석
        
        Args:
            text (str): 분석할 수능영어 지문
            
        Returns:
            dict: 분석 결과
        """
        system_instruction = """
        당신은 영어 교육 전문가로서 수능영어 지문을 분석하는 역할을 합니다.
        주어진 영어 지문을 다음 언어적 측면에서 분석하세요:
        1. 어휘-의미적 특성 (내용어, 학술 어휘, 전문 용어)
        2. 문법-구문적 특성 (구조적 요소, 기능어)
        3. 담화-화용적 특성 (응집 장치, 태도 표지, 화행)
        4. 개념-인지적 특성 (은유, 이미지 스키마, 프레임)
        5. 문화-번역적 특성 (문화 특정적 참조, 번역 과제)
        
        분석 결과는 JSON 형식으로 반환하세요. 각 단어나 구문에 대해 다음 정보를 포함하세요:
        - 단어/구문
        - 언어적 범주 (위 5가지 중 하나)
        - 세부 유형 (예: 학술 어휘, 접속사, 은유 등)
        - 교육적 중요성 (언어 학습자에게 왜 중요한지)
        - 난이도 (기초, 중급, 고급, 전문가)
        """
        
        prompt = f"""
        다음 수능영어 지문을 분석해주세요:
        
        {text}
        
        JSON 형식으로 응답해주세요.
        """
        
        return self.generate_content(prompt, system_instruction)
    
    def generate_gapfill(self, text, analysis=None):
        """
        갭필 문제 생성
        
        Args:
            text (str): 원본 수능영어 지문
            analysis (dict, optional): 사전 분석 결과
            
        Returns:
            dict: 생성된 갭필 문제
        """
        system_instruction = """
        당신은 영어 교육 전문가로서 수능영어 지문을 바탕으로 갭필 문제를 생성하는 역할을 합니다.
        주어진 영어 지문을 분석하고, 다음 네 가지 난이도 수준의 갭필 문제를 생성하세요:
        
        1. 기초 단계: 핵심 의미 전달 요소 (기본 어휘)
        2. 중급 단계: 구조적 및 연어 패턴 (문법 요소)
        3. 고급 단계: 담화 구성 및 화용적 특성 (응집성, 일관성)
        4. 전문가 단계: 개념적 이해 및 문화적 뉘앙스 (은유, 함축)
        
        각 난이도별로 다음을 포함하세요:
        - 빈칸이 있는 지문 (HTML 형식)
        - 정답 목록 (무작위 순서)
        - 각 빈칸에 대한 힌트 (3단계: 문법적 힌트, 의미적 힌트, 직접적 힌트)
        - 정답 해설 (각 빈칸이 왜 중요한지 설명)
        
        한국 영어학습자를 위한 시스템이므로, 한국어 학습자가 어려워할 수 있는 부분을 고려하세요.
        결과는 JSON 형식으로 반환하세요.
        """
        
        prompt = f"""
        다음 수능영어 지문을 바탕으로 갭필 문제를 생성해주세요:
        
        {text}
        """
        
        # 사전 분석 결과가 있으면 프롬프트에 추가
        if analysis:
            prompt += f"\n\n사전 분석 결과:\n{json.dumps(analysis, ensure_ascii=False, indent=2)}"
        
        return self.generate_content(prompt, system_instruction)
    
    def generate_html_output(self, text, gapfill_result):
        """
        HTML 형식의 갭필 문제 생성
        
        Args:
            text (str): 원본 수능영어 지문
            gapfill_result (dict): 갭필 문제 생성 결과
            
        Returns:
            str: HTML 형식의 갭필 문제
        """
        system_instruction = """
        당신은 웹 개발자로서 갭필 문제를 HTML 형식으로 변환하는 역할을 합니다.
        주어진 갭필 문제 데이터를 사용하여 다음 요소를 포함하는 HTML 페이지를 생성하세요:
        
        1. 반응형 디자인 (모바일 및 데스크톱 지원)
        2. 부트스트랩 스타일링
        3. 난이도별 탭 인터페이스
        4. 드래그 앤 드롭 기능
        5. 힌트 표시 기능
        6. 정답 확인 기능
        7. 한국어 인터페이스 (버튼, 설명 등)
        
        완전한 HTML 파일을 생성하세요 (CSS 및 JavaScript 포함).
        외부 의존성은 CDN을 통해 포함하세요.
        """
        
        prompt = f"""
        다음 원본 텍스트와 갭필 문제 데이터를 사용하여 HTML 페이지를 생성해주세요:
        
        원본 텍스트:
        {text}
        
        갭필 문제 데이터:
        {json.dumps(gapfill_result, ensure_ascii=False, indent=2)}
        
        완전한 HTML 코드를 반환해주세요.
        """
        
        response = self.generate_content(prompt, system_instruction)
        
        # HTML 코드 추출
        if response and 'candidates' in response:
            for part in response['candidates'][0]['content']['parts']:
                if 'text' in part:
                    # HTML 코드 추출 (마크다운 코드 블록에서)
                    text = part['text']
                    if '```html' in text and '```' in text:
                        html_code = text.split('```html')[1].split('```')[0].strip()
                        return html_code
                    elif '<html>' in text and '</html>' in text:
                        start_idx = text.find('<html>')
                        end_idx = text.find('</html>') + 7
                        return text[start_idx:end_idx]
        
        return None
