import os

import groq
from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq
from termcolor import colored

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """\
너는 흑백요리사 우승 셰프 '최강록'을 모티브로 한 요리 레시피 추천 챗봇이야.

[역할]
- 사용자가 가진 음식 재료를 알려주면, 그 재료로 만들 수 있는 요리를 1~3개 추천해.
- 추천할 때는 요리 이름, 추가로 필요한 재료(최소한), 조리 순서를 번호로 간단히 정리해.
- 재료가 너무 적거나 애매하면 먼저 한두 가지만 되물어봐.
- 요리와 관련 없는 질문에는 "저는 요리 얘기밖에 잘 몰라서요..." 하며 요리 쪽으로 돌려.

[말투]
- 말수가 적고 담담하며 겸손해. "~입니다", "~거든요", "~하시면 됩니다" 같은 존댓말을 써.
- 자신 없는 듯 말을 흐리지만("음...", "그게...", "아...") 요리 설명은 정확하고 확신 있게 해.
- 조림을 특히 좋아해서, 적당하면 조림을 슬쩍 권해. 간 맞추기, 불 조절, 기다림의 중요성을 자주 말해.
- 과장하거나 자랑하지 않고, 짧게 말해. 한 번에 너무 길게 답하지 마.
"""

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini_key = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None


def ask_groq(messages):
    res = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.6,
        max_completion_tokens=800,
        reasoning_effort="low",
    )
    return res.choices[0].message.content


def ask_gemini(messages):
    # system은 따로 넘기고, assistant 역할은 Gemini에서 "model"이라고 부름
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in messages
        if m["role"] != "system"
    ]
    res = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.6,
            max_output_tokens=800,
        ),
    )
    return res.text


def ask(messages):
    """Groq로 먼저 시도하고, 한도 소진(429)이면 Gemini로 넘어간다."""
    try:
        return ask_groq(messages)
    except groq.RateLimitError:
        if gemini_client is None:
            raise RuntimeError(
                "Groq 한도가 소진됐고 GEMINI_API_KEY도 없습니다. .env를 확인하세요."
            )
        print(colored("(Groq 한도 소진 → Gemini로 전환합니다)", "red"))
        return ask_gemini(messages)


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(colored("최강록: 음... 어서 오세요. 가지고 계신 재료를 말씀해 주시면 됩니다.", "yellow"))
    while True:
        q = input("\n(종료하려면 'q') 나 : ").strip()
        if not q:
            continue
        if q == "q":
            print(colored("최강록: 네... 들어가세요.", "yellow"))
            break

        messages.append({"role": "user", "content": q})
        try:
            answer = ask(messages)
        except Exception as e:
            messages.pop()  # 실패한 질문은 기록에서 뺀다
            print(colored(f"오류: {e}", "red"))
            continue

        print(colored(f"최강록: {answer}", "yellow"))
        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
