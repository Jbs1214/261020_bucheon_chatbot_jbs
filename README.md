# 최강록 레시피 챗봇

가지고 있는 음식 재료를 말하면 만들 수 있는 요리와 조리 순서를 추천해 주는 터미널 챗봇입니다.
말투는 흑백요리사 우승 셰프 최강록을 모티브로 했습니다. (실제 인물이 아닌 AI의 흉내입니다)

- 기본: [Groq](https://console.groq.com) API (`openai/gpt-oss-20b`)
- Groq 한도 소진(429) 시 자동으로 Gemini API (`gemini-2.5-flash`)로 전환

## 사용법

### 1. 설치
```bash
git clone https://github.com/Jbs1214/261020_bucheon_chatbot_jbs.git
cd 261020_bucheon_chatbot_jbs
pip install -r requirements.txt
```

### 2. API 키 설정
`.env.example`을 복사해 `.env`를 만들고 키를 채웁니다.
```
GROQ_API_KEY=발급받은_groq_키
GEMINI_API_KEY=발급받은_gemini_키
```
- Groq 키: https://console.groq.com/keys
- Gemini 키: https://aistudio.google.com/apikey (Groq 소진 시 대비용, 없어도 Groq만으로 동작)
- `.env`는 `.gitignore`에 들어 있어 GitHub에 올라가지 않습니다.

### 3. 실행
```bash
python 261020_bucheon_chatbot_jbs.py
```

### 4. 대화 예시
```
나 : 계란이랑 김치, 대파 있어요
최강록: 음... 그 정도면 김치계란볶음밥이 좋겠습니다. ...
```
`q`를 입력하면 종료됩니다.

## 파일 구성
| 파일 | 설명 |
|---|---|
| `261020_bucheon_chatbot_jbs.py` | 챗봇 본체 (페르소나, Groq 호출, Gemini 폴백) |
| `requirements.txt` | 필요 라이브러리 |
| `.env.example` | 환경변수 양식 |
