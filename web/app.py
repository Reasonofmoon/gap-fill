import os
import sys
import json
from flask import Flask, render_template, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
import tempfile

# 상위 디렉토리 추가하여 다른 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.gemini_client import GeminiClient
from analysis.text_analyzer import TextAnalyzer
from generator.gapfill_generator import GapfillGenerator

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

# Gemini API 키 환경 변수 설정
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")

# 인스턴스 생성
gemini_client = GeminiClient()
text_analyzer = TextAnalyzer(gemini_client)
gapfill_generator = GapfillGenerator(gemini_client, text_analyzer)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """갭필 문제 생성"""
    try:
        # 입력 텍스트 가져오기
        text = request.form.get('text', '')
        if not text:
            return jsonify({'error': '텍스트를 입력해주세요.'}), 400
        
        # 갭필 문제 생성
        result = gapfill_generator.generate(text)
        
        # 임시 HTML 파일 생성
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=app.config['UPLOAD_FOLDER'])
        temp_file_path = temp_file.name
        
        # HTML 파일 저장
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(result['html'])
        
        # 결과 반환
        return jsonify({
            'success': True,
            'message': '갭필 문제가 생성되었습니다.',
            'html_path': temp_file_path
        })
    
    except Exception as e:
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download(filename):
    """HTML 파일 다운로드"""
    try:
        # 파일 경로 확인
        if not os.path.exists(filename):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        # 파일 읽기
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 응답 생성
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=gapfill_exercise.html'
        
        return response
    
    except Exception as e:
        return jsonify({'error': f'다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """텍스트 분석 API"""
    try:
        # 입력 텍스트 가져오기
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': '텍스트를 입력해주세요.'}), 400
        
        # 텍스트 분석
        analysis_result = text_analyzer.analyze(text)
        
        # 결과 반환
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
    
    except Exception as e:
        return jsonify({'error': f'분석 중 오류가 발생했습니다: {str(e)}'}), 500

@app.route('/api/gapfill', methods=['POST'])
def gapfill():
    """갭필 문제 생성 API"""
    try:
        # 입력 텍스트 가져오기
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': '텍스트를 입력해주세요.'}), 400
        
        # 갭필 문제 생성
        result = gapfill_generator.generate(text)
        
        # 결과 반환
        return jsonify({
            'success': True,
            'gapfill': result['gapfill'],
            'html': result['html']
        })
    
    except Exception as e:
        return jsonify({'error': f'갭필 문제 생성 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    # templates 디렉토리 생성
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    
    # 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True)
