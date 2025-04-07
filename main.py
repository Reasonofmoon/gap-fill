import sys
import os

# 상위 디렉토리 추가하여 다른 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient
from analysis.text_analyzer import TextAnalyzer
from generator.gapfill_generator import GapfillGenerator
from optimization.korean_learner_optimization import KoreanLearnerOptimization

def main():
    """
    수능영어 지문 갭필 시스템 메인 스크립트
    """
    print("===== 수능영어 지문 갭필 시스템 =====")
    
    # 환경 변수 확인
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[주의] Gemini API 키가 설정되지 않았습니다.")
        print("환경 변수 GEMINI_API_KEY를 설정하거나 아래에 직접 입력해주세요.")
        api_key = input("Gemini API 키 (없으면 Enter): ")
    
    try:
        # 인스턴스 생성
        gemini_client = GeminiClient(api_key) if api_key else None
        text_analyzer = TextAnalyzer(gemini_client)
        gapfill_generator = GapfillGenerator(gemini_client, text_analyzer)
        korean_optimizer = KoreanLearnerOptimization(gemini_client)
        
        # 웹 서버 실행 안내
        print("\n웹 서버를 실행하려면 다음 명령어를 사용하세요:")
        print("cd web && python app.py")
        
        print("\n시스템 사용 방법은 docs/user_manual.md 파일을 참조하세요.")
        print("\n===== 준비 완료 =====")
    
    except Exception as e:
        print(f"\n[오류] 시스템 초기화 중 예외가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()
