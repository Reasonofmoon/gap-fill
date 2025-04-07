import sys
import os
import re
from collections import defaultdict

# 상위 디렉토리 추가하여 다른 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient

class KoreanLearnerOptimization:
    """
    한국 영어학습자를 위한 최적화 모듈
    관계대명사, 수일치, 가정법, 부정사, 동명사, 분사, 시제 등의 문법 요소에 중점
    """
    
    def __init__(self, gemini_client=None):
        """
        KoreanLearnerOptimization 초기화
        
        Args:
            gemini_client (GeminiClient, optional): Gemini API 클라이언트 인스턴스
        """
        self.gemini_client = gemini_client or GeminiClient()
        
        # 한국 영어학습자가 어려워하는 문법 요소
        self.grammar_focus = {
            "relative_pronouns": {
                "patterns": [
                    r'\b(who|whom|whose|which|that)\b(?=\s+\w+)',
                    r'\b\w+\s+(who|whom|whose|which|that)\b'
                ],
                "description": "관계대명사",
                "examples": ["The person who called you is waiting.", "The book that I read was interesting."],
                "korean_note": "관계대명사는 선행사를 수식하는 절을 이끄는 역할을 합니다."
            },
            "subject_verb_agreement": {
                "patterns": [
                    r'\b(is|are|was|were|has|have)\b',
                    r'\b(he|she|it)\s+\w+s\b',
                    r'\b(they|we|you)\s+\w+\b(?!\s+s)'
                ],
                "description": "수일치",
                "examples": ["He walks to school.", "They walk to school."],
                "korean_note": "주어와 동사의 수가 일치해야 합니다."
            },
            "conditionals": {
                "patterns": [
                    r'\bif\s+\w+\s+\w+,\s+\w+\s+would\b',
                    r'\bhad\s+\w+\s+\w+,\s+\w+\s+would\s+have\b',
                    r'\bwere\s+\w+\s+to\b'
                ],
                "description": "가정법",
                "examples": ["If I were you, I would study harder.", "Had I known, I would have told you."],
                "korean_note": "가정법은 현실과 다른 상황을 가정할 때 사용합니다."
            },
            "infinitives": {
                "patterns": [
                    r'\bto\s+\w+\b',
                    r'\b(want|need|try|decide|plan)\s+to\s+\w+\b'
                ],
                "description": "부정사",
                "examples": ["I want to study English.", "To succeed, you must work hard."],
                "korean_note": "부정사는 'to + 동사원형'의 형태로 명사, 형용사, 부사의 역할을 합니다."
            },
            "gerunds": {
                "patterns": [
                    r'\b\w+ing\b(?!\s+\w+ed)',
                    r'\b(enjoy|avoid|consider|finish|practice)\s+\w+ing\b'
                ],
                "description": "동명사",
                "examples": ["I enjoy swimming.", "Reading books is my hobby."],
                "korean_note": "동명사는 '-ing' 형태의 동사로 명사의 역할을 합니다."
            },
            "participles": {
                "patterns": [
                    r'\b\w+ing\s+\w+\b',
                    r'\b\w+ed\s+\w+\b',
                    r'\b\w+,\s+\w+ing\b',
                    r'\b\w+,\s+\w+ed\b'
                ],
                "description": "분사",
                "examples": ["The running water is clean.", "Excited students cheered loudly."],
                "korean_note": "분사는 '-ing'나 '-ed' 형태로 명사를 수식하거나 부수적 상황을 나타냅니다."
            },
            "tenses": {
                "patterns": [
                    r'\b(has|have)\s+\w+ed\b',
                    r'\b(had)\s+\w+ed\b',
                    r'\bwill\s+\w+\b',
                    r'\b(is|are|was|were)\s+\w+ing\b'
                ],
                "description": "시제",
                "examples": ["I have finished my homework.", "She is studying now."],
                "korean_note": "시제는 동작이 일어난 시간을 나타냅니다."
            }
        }
        
        # 템플릿 옵션
        self.templates = {
            "basic": {
                "name": "기본 템플릿",
                "description": "심플한 디자인의 기본 갭필 문제",
                "css": """
                body {
                    font-family: 'Noto Sans KR', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .gapfill-container {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .blank {
                    border-bottom: 1px solid #333;
                    padding: 0 5px;
                    min-width: 80px;
                    display: inline-block;
                    text-align: center;
                }
                .word-bank {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin: 20px 0;
                }
                .word-item {
                    background-color: #e9ecef;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .hint-container {
                    margin-top: 20px;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                }
                .hint {
                    margin-bottom: 10px;
                    display: none;
                }
                .hint-button {
                    background-color: #4263eb;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .answer-key {
                    margin-top: 20px;
                    border-top: 1px solid #ddd;
                    padding-top: 20px;
                    display: none;
                }
                .show-answers {
                    background-color: #38d9a9;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                    margin-top: 20px;
                }
                .tab-container {
                    margin-bottom: 20px;
                }
                .tab {
                    overflow: hidden;
                    border: 1px solid #ccc;
                    background-color: #f1f1f1;
                    border-radius: 5px 5px 0 0;
                }
                .tab button {
                    background-color: inherit;
                    float: left;
                    border: none;
                    outline: none;
                    cursor: pointer;
                    padding: 10px 16px;
                    transition: 0.3s;
                }
                .tab button:hover {
                    background-color: #ddd;
                }
                .tab button.active {
                    background-color: #4263eb;
                    color: white;
                }
                .tabcontent {
                    display: none;
                    padding: 20px;
                    border: 1px solid #ccc;
                    border-top: none;
                    border-radius: 0 0 5px 5px;
                }
                """
            },
            "modern": {
                "name": "모던 템플릿",
                "description": "현대적인 디자인의 갭필 문제",
                "css": """
                body {
                    font-family: 'Noto Sans KR', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }
                .gapfill-container {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 30px;
                    margin-bottom: 30px;
                }
                .blank {
                    border: none;
                    border-bottom: 2px solid #4263eb;
                    padding: 0 5px;
                    min-width: 100px;
                    display: inline-block;
                    text-align: center;
                    color: #4263eb;
                    font-weight: bold;
                }
                .word-bank {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin: 25px 0;
                }
                .word-item {
                    background-color: #e7f5ff;
                    color: #1971c2;
                    padding: 8px 15px;
                    border-radius: 20px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }
                .word-item:hover {
                    background-color: #1971c2;
                    color: white;
                }
                .hint-container {
                    margin-top: 30px;
                    border-top: 1px solid #e9ecef;
                    padding-top: 20px;
                }
                .hint {
                    margin-bottom: 15px;
                    display: none;
                    padding: 10px;
                    background-color: #fff9db;
                    border-left: 4px solid #fcc419;
                    border-radius: 4px;
                }
                .hint-button {
                    background-color: #4263eb;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                .hint-button:hover {
                    background-color: #3b5bdb;
                }
                .answer-key {
                    margin-top: 30px;
                    border-top: 1px solid #e9ecef;
                    padding-top: 20px;
                    display: none;
                }
                .show-answers {
                    background-color: #38d9a9;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 20px;
                    transition: all 0.2s ease;
                }
                .show-answers:hover {
                    background-color: #20c997;
                }
                .tab-container {
                    margin-bottom: 30px;
                }
                .tab {
                    overflow: hidden;
                    border: none;
                    background-color: transparent;
                    display: flex;
                }
                .tab button {
                    background-color: #e9ecef;
                    border: none;
                    outline: none;
                    cursor: pointer;
                    padding: 12px 20px;
                    transition: 0.3s;
                    border-radius: 5px;
                    margin-right: 10px;
                    font-weight: 500;
                }
                .tab button:hover {
                    background-color: #dee2e6;
                }
                .tab button.active {
                    background-color: #4263eb;
                    color: white;
                }
                .tabcontent {
                    display: none;
                    padding: 30px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                """
            },
            "academic": {
                "name": "학습용 템플릿",
                "description": "학습에 최적화된 갭필 문제",
                "css": """
                body {
                    font-family: 'Noto Sans KR', sans-serif;
                    line-height: 1.8;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .gapfill-container {
                    background-color: white;
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 25px;
                    margin-bottom: 25px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }
                .blank {
                    background-color: #f0f4ff;
                    border: 1px dashed #4263eb;
                    padding: 2px 8px;
                    min-width: 100px;
                    display: inline-block;
                    text-align: center;
                    border-radius: 3px;
                }
                .word-bank {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin: 25px 0;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                }
                .word-item {
                    background-color: white;
                    color: #495057;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    border: 1px solid #ced4da;
                    transition: all 0.2s ease;
                }
                .word-item:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                .hint-container {
                    margin-top: 25px;
                    border-top: 1px solid #e9ecef;
                    padding-top: 20px;
                }
                .hint {
                    margin-bottom: 15px;
                    display: none;
                    padding: 12px;
                    background-color: #f8f9fa;
                    border-left: 4px solid #4263eb;
                    border-radius: 4px;
                }
                .hint-button {
                    background-color: #4263eb;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    margin-right: 10px;
                    margin-bottom: 10px;
                }
                .hint-button:hover {
                    background-color: #3b5bdb;
                }
                .grammar-note {
                    background-color: #e7f5ff;
                    border: 1px solid #74c0fc;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }
                .grammar-note h4 {
                    color: #1971c2;
                    margin-top: 0;
                }
                .answer-key {
                    margin-top: 30px;
                    border-top: 1px solid #e9ecef;
                    padding-top: 20px;
                    display: none;
                }
                .show-answers {
                    background-color: #38d9a9;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 20px;
                    transition: all 0.2s ease;
                }
                .show-answers:hover {
                    background-color: #20c997;
                }
                .tab-container {
                    margin-bottom: 25px;
                }
                .tab {
                    overflow: hidden;
                    border: 1px solid #dee2e6;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    display: flex;
                }
                .tab button {
                    background-color: inherit;
                    border: none;
                    outline: none;
                    cursor: pointer;
                    padding: 12px 20px;
                    transition: 0.3s;
                    font-weight: 500;
                    flex: 1;
                    text-align: center;
                }
                .tab button:hover {
                    background-color: #e9ecef;
                }
                .tab button.active {
                    background-color: #4263eb;
                    color: white;
                }
                .tabcontent {
                    display: none;
                    padding: 25px;
                    border: 1px solid #dee2e6;
                    border-top: none;
                    border-radius: 0 0 5px 5px;
                    background-color: white;
                }
                .korean-translation {
                    margin-top: 20px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    border-left: 4px solid #adb5bd;
                }
                """
            }
        }
    
    def optimize_prompt(self, text):
        """
        한국 영어학습자를 위한 프롬프트 최적화
        
        Args:
            text (str): 원본 수능영어 지문
            
        Returns:
            str: 최적화된 프롬프트
        """
        # 문법 요소 분석
        grammar_elements = self._analyze_grammar_elements(text)
        
        # 최적화된 프롬프트 생성
        optimized_prompt = f"""
        다음 수능영어 지문을 한국 영어학습자를 위한 갭필 문제로 변환해주세요:
        
        {text}
        
        다음 문법 요소에 중점을 두어 갭필 문제를 생성해주세요:
        - 관계대명사 (who, whom, whose, which, that)
        - 수일치 (주어-동사 일치)
        - 가정법 (if 조건문, 가정법 과거/과거완료)
        - 부정사 (to + 동사원형)
        - 동명사 (-ing 형태의 동사)
        - 분사 (현재분사, 과거분사)
        - 시제 (현재, 과거, 현재완료, 과거완료, 미래 등)
        
        지문에서 발견된 주요 문법 요소:
        {self._format_grammar_elements(grammar_elements)}
        
        다음 사항을 포함해주세요:
        1. 난이도별 갭필 문제 (기초, 중급, 고급, 전문가)
        2. 각 빈칸에 대한 간단한 힌트
        3. 기본적인 한국어 번역만 제공 (상세한 문법 설명 없이)
        4. 정답 및 해설
        
        결과는 JSON 형식으로 반환해주세요.
        """
        
        return optimized_prompt
    
    def _analyze_grammar_elements(self, text):
        """
        텍스트에서 문법 요소 분석
        
        Args:
            text (str): 분석할 텍스트
            
        Returns:
            dict: 문법 요소 분석 결과
        """
        grammar_elements = defaultdict(list)
        
        # 각 문법 요소별 패턴 검사
        for grammar_type, info in self.grammar_focus.items():
            for pattern in info["patterns"]:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0)
                    if matched_text not in grammar_elements[grammar_type]:
                        grammar_elements[grammar_type].append(matched_text)
        
        return grammar_elements
    
    def _format_grammar_elements(self, grammar_elements):
        """
        문법 요소 분석 결과 포맷팅
        
        Args:
            grammar_elements (dict): 문법 요소 분석 결과
            
        Returns:
            str: 포맷팅된 문법 요소 분석 결과
        """
        formatted_result = ""
        
        for grammar_type, elements in grammar_elements.items():
            if elements:
                description = self.grammar_focus[grammar_type]["description"]
                formatted_result += f"- {description}: {', '.join(elements)}\n"
        
        return formatted_result
    
    def generate_template_selection_html(self):
        """
        템플릿 선택 HTML 생성
        
        Returns:
            str: 템플릿 선택 HTML
        """
        template_html = """
        <div class="template-selection">
            <h3>템플릿 선택</h3>
            <div class="template-options">
        """
        
        for template_id, template in self.templates.items():
            template_html += f"""
                <div class="template-option" data-template="{template_id}">
                    <h4>{template["name"]}</h4>
                    <p>{template["description"]}</p>
                    <button class="select-template" data-template="{template_id}">선택</button>
                </div>
            """
        
        template_html += """
            </div>
        </div>
        <style>
            .template-selection {
                margin: 20px 0;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #dee2e6;
            }
            .template-options {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 15px;
            }
            .template-option {
                flex: 1;
                min-width: 200px;
                padding: 15px;
                background-color: white;
                border-radius: 5px;
                border: 1px solid #dee2e6;
                transition: all 0.2s ease;
            }
            .template-option:hover {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transform: translateY(-2px);
            }
            .template-option h4 {
                margin-top: 0;
                color: #4263eb;
            }
            .select-template {
                background-color: #4263eb;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .select-template:hover {
                background-color: #3b5bdb;
            }
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const templateButtons = document.querySelectorAll('.select-template');
                templateButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const templateId = this.getAttribute('data-template');
                        changeTemplate(templateId);
                    });
                });
                
                function changeTemplate(templateId) {
                    // 현재 스타일 제거
                    const existingStyle = document.getElementById('template-style');
                    if (existingStyle) {
                        existingStyle.remove();
                    }
                    
                    // 새 템플릿 스타일 적용
                    const templates = {
        """
        
        for template_id, template in self.templates.items():
            template_html += f"""
                        '{template_id}': `{template["css"]}`,
            """
        
        template_html += """
                    };
                    
                    const newStyle = document.createElement('style');
                    newStyle.id = 'template-style';
                    newStyle.textContent = templates[templateId];
                    document.head.appendChild(newStyle);
                    
                    // 템플릿 선택 UI 숨기기
                    document.querySelector('.template-selection').style.display = 'none';
                    
                    // 선택된 템플릿 표시
                    const templateName = document.querySelector(`.template-option[data-template="${templateId}"] h4`).textContent;
                    const notification = document.createElement('div');
                    notification.className = 'template-notification';
                    notification.innerHTML = `
                        <p>"${templateName}" 템플릿이 적용되었습니다.</p>
                        <button id="change-template">변경</button>
                    `;
                    document.querySelector('.gapfill-container').insertAdjacentElement('beforebegin', notification);
                    
                    // 템플릿 변경 버튼 이벤트
                    document.getElementById('change-template').addEventListener('click', function() {
                        document.querySelector('.template-selection').style.display = 'block';
                        notification.remove();
                    });
                }
                
                // 기본 템플릿 적용
                changeTemplate('basic');
            });
        </script>
        """
        
        return template_html
    
    def optimize_html_output(self, html_output):
        """
        HTML 출력 최적화
        
        Args:
            html_output (str): 원본 HTML 출력
            
        Returns:
            str: 최적화된 HTML 출력
        """
        # 템플릿 선택 기능 추가
        template_selection_html = self.generate_template_selection_html()
        
        # HTML에 템플릿 선택 기능 삽입
        if "<body>" in html_output:
            # <body> 태그 바로 다음에 삽입
            optimized_html = html_output.replace("<body>", "<body>\n" + template_selection_html)
        elif "<div class=\"container\">" in html_output:
            # 컨테이너 div 바로 다음에 삽입
            optimized_html = html_output.replace("<div class=\"container\">", "<div class=\"container\">\n" + template_selection_html)
        else:
            # HTML 시작 부분에 삽입
            optimized_html = template_selection_html + html_output
        
        # 한국어 학습자를 위한 문법 노트 추가
        for grammar_type, info in self.grammar_focus.items():
            description = info["description"]
            korean_note = info["korean_note"]
            examples = info["examples"]
            
            grammar_note_html = f"""
            <div class="grammar-note">
                <h4>{description}</h4>
                <p>{korean_note}</p>
                <p>예시: {' / '.join(examples)}</p>
            </div>
            """
            
            # 정답 키 섹션 앞에 문법 노트 삽입
            if "<div class=\"answer-key\">" in optimized_html:
                optimized_html = optimized_html.replace("<div class=\"answer-key\">", grammar_note_html + "<div class=\"answer-key\">")
        
        return optimized_html
