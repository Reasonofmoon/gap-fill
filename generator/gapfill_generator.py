import sys
import os
import json
import random
import re
from collections import defaultdict

# 상위 디렉토리 추가하여 다른 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient
from analysis.text_analyzer import TextAnalyzer

class GapfillGenerator:
    """
    갭필 문제 생성 모듈
    분석된 텍스트를 바탕으로 다양한 난이도의 갭필 문제 생성
    """
    
    def __init__(self, gemini_client=None, text_analyzer=None):
        """
        GapfillGenerator 초기화
        
        Args:
            gemini_client (GeminiClient, optional): Gemini API 클라이언트 인스턴스
            text_analyzer (TextAnalyzer, optional): 텍스트 분석기 인스턴스
        """
        self.gemini_client = gemini_client or GeminiClient()
        self.text_analyzer = text_analyzer or TextAnalyzer(self.gemini_client)
    
    def generate(self, text):
        """
        갭필 문제 생성
        
        Args:
            text (str): 원본 수능영어 지문
            
        Returns:
            dict: 생성된 갭필 문제
        """
        # 텍스트 분석
        analysis_result = self.text_analyzer.analyze(text)
        
        # Gemini API를 통한 갭필 문제 생성
        gapfill_result = self._generate_gapfill_with_gemini(text, analysis_result)
        
        # 결과 처리 및 구조화
        structured_result = self._structure_gapfill_result(gapfill_result)
        
        # HTML 출력 생성
        html_output = self._generate_html_output(text, structured_result)
        
        return {
            "original_text": text,
            "analysis": analysis_result,
            "gapfill": structured_result,
            "html": html_output
        }
    
    def _generate_gapfill_with_gemini(self, text, analysis_result):
        """
        Gemini API를 통한 갭필 문제 생성
        
        Args:
            text (str): 원본 수능영어 지문
            analysis_result (dict): 텍스트 분석 결과
            
        Returns:
            dict: 생성된 갭필 문제
        """
        # 분석 결과를 JSON 문자열로 변환
        analysis_json = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        # Gemini API를 통한 갭필 문제 생성
        response = self.gemini_client.generate_gapfill(text, analysis_json)
        
        # 응답 처리
        if response and 'candidates' in response:
            for part in response['candidates'][0]['content']['parts']:
                if 'text' in part:
                    # JSON 형식 데이터 추출
                    text_content = part['text']
                    try:
                        # JSON 형식 문자열 찾기
                        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text_content)
                        if json_match:
                            json_str = json_match.group(1)
                            return json.loads(json_str)
                        
                        # 중괄호로 둘러싸인 JSON 찾기
                        json_match = re.search(r'({[\s\S]*})', text_content)
                        if json_match:
                            json_str = json_match.group(1)
                            return json.loads(json_str)
                        
                        # 전체 텍스트가 JSON인지 확인
                        return json.loads(text_content)
                    except json.JSONDecodeError:
                        # JSON 파싱 실패 시 텍스트 그대로 반환
                        return {"raw_result": text_content}
        
        # 응답이 없거나 처리 실패 시 빈 결과 반환
        return {}
    
    def _structure_gapfill_result(self, gapfill_result):
        """
        갭필 결과 구조화
        
        Args:
            gapfill_result (dict): Gemini API로부터 받은 갭필 결과
            
        Returns:
            dict: 구조화된 갭필 결과
        """
        # 기본 구조 정의
        structured_result = {
            "tiers": {
                "foundation": {
                    "text": "",
                    "blanks": [],
                    "answers": [],
                    "hints": []
                },
                "intermediate": {
                    "text": "",
                    "blanks": [],
                    "answers": [],
                    "hints": []
                },
                "advanced": {
                    "text": "",
                    "blanks": [],
                    "answers": [],
                    "hints": []
                },
                "expert": {
                    "text": "",
                    "blanks": [],
                    "answers": [],
                    "hints": []
                }
            },
            "korean_translation": "",
            "answer_key": [],
            "cultural_notes": []
        }
        
        # 갭필 결과가 있는 경우
        if gapfill_result:
            # 원시 결과만 있는 경우
            if "raw_result" in gapfill_result:
                # 텍스트 파싱 시도
                raw_result = gapfill_result["raw_result"]
                
                # 난이도별 섹션 찾기
                tier_patterns = {
                    "foundation": r"Foundation Tier.*?(?=Intermediate Tier|$)",
                    "intermediate": r"Intermediate Tier.*?(?=Advanced Tier|$)",
                    "advanced": r"Advanced Tier.*?(?=Expert Tier|$)",
                    "expert": r"Expert Tier.*?(?=$)"
                }
                
                for tier, pattern in tier_patterns.items():
                    tier_match = re.search(pattern, raw_result, re.DOTALL)
                    if tier_match:
                        tier_content = tier_match.group(0)
                        
                        # 텍스트 추출
                        text_match = re.search(r"Text:.*?(?=Blanks:|$)", tier_content, re.DOTALL)
                        if text_match:
                            structured_result["tiers"][tier]["text"] = text_match.group(0).replace("Text:", "").strip()
                        
                        # 빈칸 추출
                        blanks_match = re.search(r"Blanks:.*?(?=Answers:|$)", tier_content, re.DOTALL)
                        if blanks_match:
                            blanks_text = blanks_match.group(0).replace("Blanks:", "").strip()
                            structured_result["tiers"][tier]["blanks"] = [b.strip() for b in blanks_text.split("\n") if b.strip()]
                        
                        # 정답 추출
                        answers_match = re.search(r"Answers:.*?(?=Hints:|$)", tier_content, re.DOTALL)
                        if answers_match:
                            answers_text = answers_match.group(0).replace("Answers:", "").strip()
                            structured_result["tiers"][tier]["answers"] = [a.strip() for a in answers_text.split("\n") if a.strip()]
                        
                        # 힌트 추출
                        hints_match = re.search(r"Hints:.*?(?=$)", tier_content, re.DOTALL)
                        if hints_match:
                            hints_text = hints_match.group(0).replace("Hints:", "").strip()
                            structured_result["tiers"][tier]["hints"] = [h.strip() for h in hints_text.split("\n") if h.strip()]
                
                # 한국어 번역 추출
                korean_match = re.search(r"Korean Translation:.*?(?=Answer Key:|$)", raw_result, re.DOTALL)
                if korean_match:
                    structured_result["korean_translation"] = korean_match.group(0).replace("Korean Translation:", "").strip()
                
                # 정답 키 추출
                answer_key_match = re.search(r"Answer Key:.*?(?=Cultural Notes:|$)", raw_result, re.DOTALL)
                if answer_key_match:
                    answer_key_text = answer_key_match.group(0).replace("Answer Key:", "").strip()
                    structured_result["answer_key"] = [line.strip() for line in answer_key_text.split("\n") if line.strip()]
                
                # 문화적 참고사항 추출
                cultural_notes_match = re.search(r"Cultural Notes:.*?(?=$)", raw_result, re.DOTALL)
                if cultural_notes_match:
                    cultural_notes_text = cultural_notes_match.group(0).replace("Cultural Notes:", "").strip()
                    structured_result["cultural_notes"] = [line.strip() for line in cultural_notes_text.split("\n") if line.strip()]
            
            # 구조화된 결과가 있는 경우
            else:
                # 난이도별 데이터 매핑
                tier_mapping = {
                    "foundation": ["foundation", "basic", "beginner"],
                    "intermediate": ["intermediate", "medium"],
                    "advanced": ["advanced", "high"],
                    "expert": ["expert", "very high", "master"]
                }
                
                # 각 난이도별 데이터 추출
                for result_tier, result_data in gapfill_result.items():
                    # 난이도 매핑
                    mapped_tier = None
                    for tier, aliases in tier_mapping.items():
                        if any(alias in result_tier.lower() for alias in aliases):
                            mapped_tier = tier
                            break
                    
                    if mapped_tier:
                        # 텍스트 추출
                        if "text" in result_data:
                            structured_result["tiers"][mapped_tier]["text"] = result_data["text"]
                        
                        # 빈칸 추출
                        if "blanks" in result_data:
                            structured_result["tiers"][mapped_tier]["blanks"] = result_data["blanks"]
                        
                        # 정답 추출
                        if "answers" in result_data:
                            structured_result["tiers"][mapped_tier]["answers"] = result_data["answers"]
                        
                        # 힌트 추출
                        if "hints" in result_data:
                            structured_result["tiers"][mapped_tier]["hints"] = result_data["hints"]
                
                # 한국어 번역 추출
                if "korean_translation" in gapfill_result:
                    structured_result["korean_translation"] = gapfill_result["korean_translation"]
                
                # 정답 키 추출
                if "answer_key" in gapfill_result:
                    structured_result["answer_key"] = gapfill_result["answer_key"]
                
                # 문화적 참고사항 추출
                if "cultural_notes" in gapfill_result:
                    structured_result["cultural_notes"] = gapfill_result["cultural_notes"]
        
        # 정답 무작위 섞기 (Fisher-Yates 알고리즘)
        for tier in structured_result["tiers"].values():
            answers = tier["answers"].copy()
            for i in range(len(answers) - 1, 0, -1):
                j = random.randint(0, i)
                answers[i], answers[j] = answers[j], answers[i]
            tier["shuffled_answers"] = answers
        
        return structured_result
    
    def _generate_html_output(self, text, structured_result):
        """
        HTML 출력 생성
        
        Args:
            text (str): 원본 수능영어 지문
            structured_result (dict): 구조화된 갭필 결과
            
        Returns:
            str: HTML 출력
        """
        # Gemini API를 통한 HTML 생성
        html_output = self.gemini_client.generate_html_output(text, structured_result)
        
        return html_output
    
    def save_html_to_file(self, html_output, output_path):
        """
        HTML 출력을 파일로 저장
        
        Args:
            html_output (str): HTML 출력
            output_path (str): 출력 파일 경로
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_output)
            return True
        except Exception as e:
            print(f"HTML 파일 저장 오류: {e}")
            return False
