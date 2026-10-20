# 261020_bucheon_chatbot_jbs

Groq API KEY를 활용하여 챗봇 만들기

가지고 있는 음식 재료를 말하면, 흑백요리사 우승 셰프 최강록 말투로 만들 수 있는 요리와 조리 순서를 추천해 주는 레시피 챗봇입니다.
Groq 한도가 소진되면 Gemini로 자동 전환됩니다.

> 예시: `계란, 김치, 대파` → "음... 김치계란볶음밥 어떠세요. 있는 재료로 제일 무난하거든요. ..."

## 설치 라이브러리

**Python 3.10 이상**이 필요합니다. (`python --version`으로 확인)

```bash
pip install -r requirements.txt
```

| 라이브러리 | 용도 |
|---|---|
| groq | Groq API 호출 (기본 모델) |
| google-genai | Gemini API 호출 (Groq 한도 소진 시 대체) |
| python-dotenv | `.env`에서 API 키 읽기 |
| termcolor | 터미널 글자 색 |
| streamlit | 웹 화면 |

## 실행 방법

### 1. 코드 내려받기
```bash
git clone https://github.com/Jbs1214/261020_bucheon_chatbot_jbs.git
cd 261020_bucheon_chatbot_jbs
```

### 2. API 키 발급받기
- **Groq 키 (필수)**: https://console.groq.com/keys 에서 로그인 후 `Create API Key`
- **Gemini 키 (선택)**: https://aistudio.google.com/apikey 에서 `Create API key`
  Groq 무료 한도가 끝났을 때를 대비한 키입니다. 없어도 Groq만으로 동작합니다.

### 3. `.env` 파일 만들기
`.env.example`을 복사해서 이름을 `.env`로 바꾸고, 발급받은 키를 `=` 뒤에 붙여 넣습니다.

```bash
# Windows (PowerShell / CMD)
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

```
GROQ_API_KEY=gsk_여기에_발급받은_키
GEMINI_API_KEY=여기에_발급받은_키
```

- 따옴표(`"`)나 공백 없이, 키만 그대로 붙여 넣으세요.
- `.env`는 `.gitignore`에 들어 있어 GitHub에 올라가지 않습니다. 키를 다른 사람에게 공유하지 마세요.

### 4. 실행하기

**웹 화면으로 실행 (추천)** : 브라우저가 자동으로 열립니다.
```bash
streamlit run app.py
```
화면의 예시 재료 버튼을 누르거나, 아래 입력창에 재료를 적으면 됩니다. 왼쪽의 `새 대화 시작`으로 처음부터 다시 할 수 있습니다.

**터미널로 실행**
```bash
python 261020_bucheon_chatbot_jbs.py
```
재료를 입력하면 답변이 나옵니다. 종료는 `exit`를 입력하세요.

## 문제가 생겼을 때

| 증상 | 해결 |
|---|---|
| `The api_key client option must be set ...` | `.env` 파일이 없거나 `GROQ_API_KEY` 이름이 틀렸습니다. 파일 이름이 `.env`인지, 실행 위치가 프로젝트 폴더인지 확인하세요. |
| `401 Invalid API Key` | 키를 잘못 붙여 넣었습니다. 앞뒤 공백, 따옴표, 안내 문구가 남아 있지 않은지 확인하세요. |
| `Groq 한도가 소진됐고 GEMINI_API_KEY도 없습니다` | Groq 무료 한도가 끝났습니다. 잠시 후 다시 하거나 `.env`에 Gemini 키를 넣으세요. |
| `No module named ...` | `pip install -r requirements.txt`를 다시 실행하세요. 여러 Python이 설치돼 있으면 `python -m pip install -r requirements.txt`를 쓰세요. |
