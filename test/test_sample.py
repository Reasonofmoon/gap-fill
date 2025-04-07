import sys
import os
import json
import tempfile

# 상위 디렉토리 추가하여 다른 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient
from analysis.text_analyzer import TextAnalyzer
from generator.gapfill_generator import GapfillGenerator

def test_gapfill_system():
    """
    샘플 텍스트로 갭필 시스템 테스트
    """
    print("===== 수능영어 지문 갭필 시스템 테스트 =====")
    
    # 샘플 텍스트
    sample_text = """
    Improving your gestural communication involves more than just knowing when to nod or shake hands. 
    It's about using gestures to complement your spoken messages, adding layers of meaning to your words. 
    Open­handed gestures, for example, can indicate honesty, creating an atmosphere of trust. 
    You invite openness and collaboration when you speak with your palms facing up. 
    This simple yet powerful gesture can make others feel more comfortable and willing to engage in conversation. 
    But be careful of the trap of over­gesturing. Too many hand movements can distract from your message, 
    drawing attention away from your words. Imagine a speaker whose hands move quickly like birds, 
    their message lost in the chaos of their gestures. Balance is key. 
    Your gestures should highlight your words, not overshadow them.
    """
    
    print(f"\n[1/4] 샘플 텍스트 준비 완료 (길이: {len(sample_text)} 자)")
    
    try:
        # Gemini API 키 확인
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("\n[오류] Gemini API 키가 설정되지 않았습니다.")
            print("환경 변수 GEMINI_API_KEY를 설정해주세요.")
            return False
        
        # 인스턴스 생성
        print("\n[2/4] 모듈 초기화 중...")
        gemini_client = GeminiClient(api_key)
        text_analyzer = TextAnalyzer(gemini_client)
        gapfill_generator = GapfillGenerator(gemini_client, text_analyzer)
        print("모듈 초기화 완료")
        
        # 텍스트 분석
        print("\n[3/4] 텍스트 분석 중...")
        analysis_result = text_analyzer.analyze(sample_text)
        print("텍스트 분석 완료")
        
        # 분석 결과 확인
        if not analysis_result:
            print("\n[오류] 텍스트 분석 결과가 없습니다.")
            return False
        
        print(f"기본 통계: {json.dumps(analysis_result.get('basic_stats', {}), ensure_ascii=False, indent=2)}")
        
        # 갭필 문제 생성
        print("\n[4/4] 갭필 문제 생성 중...")
        result = gapfill_generator.generate(sample_text)
        print("갭필 문제 생성 완료")
        
        # 결과 확인
        if not result or 'html' not in result:
            print("\n[오류] 갭필 문제 생성 결과가 없습니다.")
            return False
        
        # HTML 파일 저장
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "gapfill_test_output.html")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['html'])
        
        print(f"\n테스트 결과 HTML 파일이 저장되었습니다: {output_path}")
        print("\n===== 테스트 성공적으로 완료 =====")
        return True
    
    except Exception as e:
        print(f"\n[오류] 테스트 중 예외가 발생했습니다: {str(e)}")
        return False

if __name__ == "__main__":
    # 테스트 실행
    success = test_gapfill_system()
    sys.exit(0 if success else 1)
