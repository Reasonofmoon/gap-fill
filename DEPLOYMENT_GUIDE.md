# 수능영어 갭필 시스템 배포 가이드

이 가이드는 Flask 기반의 수능영어 갭필 시스템을 Render.com을 통해 배포하는 방법을 설명합니다.

## 1. Render.com을 이용한 배포 (가장 간단한 방법)

### 준비 사항

1. 프로젝트 루트 디렉토리에 아래 파일들을 추가하세요:

   - **requirements.txt**
     ```
     Flask==2.1.2
     gunicorn==20.1.0
     ```
     이 파일은 애플리케이션 실행에 필요한 패키지를 명시합니다.

   - **render_app.py**
     ```python
     from flask import Flask
     app = Flask(__name__)

     @app.route('/')
     def home():
         return "Hello, CSAT Gap-fill System!"

     if __name__ == '__main__':
         app.run(host='0.0.0.0', port=5000)
     ```
     이 파일은 Flask 애플리케이션의 엔트리 포인트입니다.

2. 코드가 GitHub 또는 GitLab과 같은 저장소에 push되어 있어야 합니다.

### Render.com 배포 단계

1. [Render.com](https://render.com/)에 가입 후 로그인합니다.
2. 대시보드에서 **"New +"** 버튼을 클릭한 후 **"Web Service"**를 선택합니다.
3. GitHub 또는 GitLab 계정을 Render와 연결한 후 배포할 저장소를 선택합니다.
4. 아래와 같은 설정을 입력합니다:
   - **Name**: 원하는 서비스 이름 (예: `csat-gapfill-system`)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn render_app:app`
5. **Advanced** 섹션을 열어 환경 변수를 추가합니다. 예를 들어:
   - `GEMINI_API_KEY`: 여러분의 Gemini API 키
6. **Create Web Service** 버튼을 클릭하여 배포를 시작합니다.

배포가 완료되면 Render.com이 제공하는 URL을 통해 애플리케이션에 접근할 수 있습니다.

---

이 가이드를 참고하여 배포를 진행하시고, 진행 중 문제가 발생하면 Render의 문서 또는 지원팀의 도움을 받으시기 바랍니다. 