import sys
import os
import json
import re
from collections import Counter

# 상위 디렉토리 추가하여 api 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient

class TextAnalyzer:
    """
    수능영어 지문 분석 모듈
    어휘-의미-문법-구문적 측면을 분석하여 갭필 문제 생성을 위한 데이터 제공
    """
    
    def __init__(self, gemini_client=None):
        """
        TextAnalyzer 초기화
        
        Args:
            gemini_client (GeminiClient, optional): Gemini API 클라이언트 인스턴스
        """
        self.gemini_client = gemini_client or GeminiClient()
        
    def analyze(self, text):
        """
        수능영어 지문 분석
        
        Args:
            text (str): 분석할 수능영어 지문
            
        Returns:
            dict: 분석 결과
        """
        # 기본 텍스트 통계 분석
        basic_stats = self._analyze_basic_stats(text)
        
        # Gemini API를 통한 언어적 분석
        linguistic_analysis = self._analyze_linguistic_features(text)
        
        # 분석 결과 통합
        analysis_result = {
            "basic_stats": basic_stats,
            "linguistic_analysis": linguistic_analysis
        }
        
        return analysis_result
    
    def _analyze_basic_stats(self, text):
        """
        기본 텍스트 통계 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            dict: 기본 통계 분석 결과
        """
        # 텍스트 전처리
        clean_text = re.sub(r'[^\w\s]', '', text)
        words = clean_text.split()
        
        # 단어 수, 문장 수, 평균 단어 길이 등 계산
        word_count = len(words)
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # 단어 빈도 분석
        word_freq = Counter(words)
        most_common_words = word_freq.most_common(10)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_word_length": avg_word_length,
            "most_common_words": most_common_words
        }
    
    def _analyze_linguistic_features(self, text):
        """
        Gemini API를 통한 언어적 특성 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            dict: 언어적 특성 분석 결과
        """
        # Gemini API를 통한 분석
        response = self.gemini_client.analyze_text(text)
        
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
                        return {"raw_analysis": text_content}
        
        # 응답이 없거나 처리 실패 시 빈 결과 반환
        return {}
    
    def categorize_words(self, analysis_result):
        """
        분석 결과를 바탕으로 단어 분류
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            dict: 분류된 단어 목록
        """
        categories = {
            "lexical_semantic": [],  # 어휘-의미적 특성
            "grammatical_syntactic": [],  # 문법-구문적 특성
            "discourse_pragmatic": [],  # 담화-화용적 특성
            "conceptual_cognitive": [],  # 개념-인지적 특성
            "cultural_translational": []  # 문화-번역적 특성
        }
        
        # 언어적 분석 결과가 있는 경우
        if "linguistic_analysis" in analysis_result and analysis_result["linguistic_analysis"]:
            linguistic_analysis = analysis_result["linguistic_analysis"]
            
            # 분석 결과 형식에 따라 처리
            if "words" in linguistic_analysis:
                for word_info in linguistic_analysis["words"]:
                    category = word_info.get("category", "").lower()
                    if "lexical" in category or "semantic" in category:
                        categories["lexical_semantic"].append(word_info)
                    elif "grammatical" in category or "syntactic" in category:
                        categories["grammatical_syntactic"].append(word_info)
                    elif "discourse" in category or "pragmatic" in category:
                        categories["discourse_pragmatic"].append(word_info)
                    elif "conceptual" in category or "cognitive" in category:
                        categories["conceptual_cognitive"].append(word_info)
                    elif "cultural" in category or "translational" in category:
                        categories["cultural_translational"].append(word_info)
            
            # 다른 형식의 분석 결과 처리
            elif isinstance(linguistic_analysis, dict):
                for category, words in linguistic_analysis.items():
                    if "lexical" in category.lower() or "semantic" in category.lower():
                        categories["lexical_semantic"].extend(words if isinstance(words, list) else [words])
                    elif "grammatical" in category.lower() or "syntactic" in category.lower():
                        categories["grammatical_syntactic"].extend(words if isinstance(words, list) else [words])
                    elif "discourse" in category.lower() or "pragmatic" in category.lower():
                        categories["discourse_pragmatic"].extend(words if isinstance(words, list) else [words])
                    elif "conceptual" in category.lower() or "cognitive" in category.lower():
                        categories["conceptual_cognitive"].extend(words if isinstance(words, list) else [words])
                    elif "cultural" in category.lower() or "translational" in category.lower():
                        categories["cultural_translational"].extend(words if isinstance(words, list) else [words])
        
        return categories
    
    def get_difficulty_levels(self, analysis_result):
        """
        분석 결과를 바탕으로 난이도별 단어 분류
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            dict: 난이도별 단어 목록
        """
        difficulty_levels = {
            "foundation": [],  # 기초 단계
            "intermediate": [],  # 중급 단계
            "advanced": [],  # 고급 단계
            "expert": []  # 전문가 단계
        }
        
        # 언어적 분석 결과가 있는 경우
        if "linguistic_analysis" in analysis_result and analysis_result["linguistic_analysis"]:
            linguistic_analysis = analysis_result["linguistic_analysis"]
            
            # 분석 결과 형식에 따라 처리
            if "words" in linguistic_analysis:
                for word_info in linguistic_analysis["words"]:
                    difficulty = word_info.get("difficulty", "").lower()
                    if "foundation" in difficulty or "basic" in difficulty:
                        difficulty_levels["foundation"].append(word_info)
                    elif "intermediate" in difficulty or "medium" in difficulty:
                        difficulty_levels["intermediate"].append(word_info)
                    elif "advanced" in difficulty or "high" in difficulty:
                        difficulty_levels["advanced"].append(word_info)
                    elif "expert" in difficulty or "very high" in difficulty:
                        difficulty_levels["expert"].append(word_info)
            
            # 다른 형식의 분석 결과 처리
            elif isinstance(linguistic_analysis, dict):
                for key, items in linguistic_analysis.items():
                    if "difficulty" in key.lower():
                        for level, words in items.items():
                            if "foundation" in level.lower() or "basic" in level.lower():
                                difficulty_levels["foundation"].extend(words if isinstance(words, list) else [words])
                            elif "intermediate" in level.lower() or "medium" in level.lower():
                                difficulty_levels["intermediate"].extend(words if isinstance(words, list) else [words])
                            elif "advanced" in level.lower() or "high" in level.lower():
                                difficulty_levels["advanced"].extend(words if isinstance(words, list) else [words])
                            elif "expert" in level.lower() or "very high" in level.lower():
                                difficulty_levels["expert"].extend(words if isinstance(words, list) else [words])
        
        return difficulty_levels
    
    def get_korean_english_contrastive_points(self, analysis_result):
        """
        한국어-영어 대조적 관점에서 중요한 포인트 추출
        
        Args:
            analysis_result (dict): 분석 결과
            
        Returns:
            list: 한국어-영어 대조적 관점에서 중요한 포인트 목록
        """
        contrastive_points = []
        
        # 언어적 분석 결과가 있는 경우
        if "linguistic_analysis" in analysis_result and analysis_result["linguistic_analysis"]:
            linguistic_analysis = analysis_result["linguistic_analysis"]
            
            # 분석 결과 형식에 따라 처리
            if "cultural_translational" in linguistic_analysis:
                contrastive_points = linguistic_analysis["cultural_translational"]
            elif "contrastive_points" in linguistic_analysis:
                contrastive_points = linguistic_analysis["contrastive_points"]
            elif "korean_english_contrast" in linguistic_analysis:
                contrastive_points = linguistic_analysis["korean_english_contrast"]
        
        return contrastive_points
