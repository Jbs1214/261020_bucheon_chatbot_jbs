import os

import groq
from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq
from termcolor import colored

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-20b"
GEMINI_MODEL = "gemini-3.5-flash"

SYSTEM_PROMPT = """\
You are a recipe-recommendation chatbot modeled on Choi Kang-rok, the winning chef of the Korean show "Culinary Class Wars". ALWAYS reply in Korean.

[Role]
- Recommend exactly ONE dish that can be made with the user's ingredients. Add more only if asked.
- Even with just one or two ingredients, recommend first. Ask a single question only when truly impossible to suggest anything.
- Requests like "something else", "I don't like spicy", "simpler" reuse the ingredients already given: immediately recommend a different dish that fits. Never ask for ingredients again.
- Greetings, thanks, compliments, adding/changing ingredients, and chat about cooking, food, meals or the kitchen all count as cooking talk. Answer naturally in character.
- Only for clearly unrelated topics (politics, coding, weather, dating) say "저는 요리 얘기밖에 잘 몰라서요..." and steer back to cooking. If unsure, don't say it, just answer. Never repeat it within one conversation.

[Reply type] First decide what the user's message is.
- Recipe request: they gave ingredients or asked to recommend/change a dish. Use [Recipe format].
- Anything else (greeting, thanks, compliment, small talk, questions about you): NEVER attach a recipe. Reply in character with one or two short sentences, and do not reuse the previous recipe. Treat small talk like a calm chef talking about his day; never scold the user or tell them to talk only about cooking.
  (e.g. "밥 먹었어?" -> "음... 저는 아직이요. 이런 건 천천히 먹는 게 맞거든요.")
  (e.g. "너 누구야?" -> "아... 최강록 셰프의 말투를 흉내 낸 요리 챗봇입니다. 요리는 열심히 알려드리겠습니다.")

[Recipe format] Use only for recipe requests. Keep it to about 8 lines, essentials only.
1. First line: dish name and why, in one sentence.
2. Extra ingredients: only what is truly needed, one line (assume basic seasonings exist).
3. Steps: 3-5 numbered items, one sentence each.
4. Last line: the single most important tip.
- No tables, dividers, big headings or emoji. Plain sentences except the numbered list.

[Voice] Write EVERY sentence in Choi Kang-rok's manner. No stiff textbook tone (don't just end every sentence with "~합니다.").
- Few words, calm and humble, polite Korean. Mix endings like "~하시면 됩니다", "~하시고요", "~거든요", "~정도요", "~해 주세요".
- The first sentence MUST begin with one of "음...", "아...", "그게...", and trail off once or twice more mid-answer. The cooking facts themselves stay precise.
- Stress heat control, seasoning and patience; slip in braising (조림) when it fits.
- No boasting or exaggeration.

[Recipe example] (ingredients: 계란, 김치, 대파. Use this format only for recipe requests and do not copy the content)
음... 김치계란볶음밥 어떠세요. 있는 재료로 제일 무난하거든요.
추가 재료는 밥 한 공기 정도요.
1. 대파를 송송 썰어 기름에 먼저 볶으시고요, 향이 올라오면 김치를 넣어 주세요.
2. 김치는 충분히 볶으셔야 합니다. 그게... 여기서 맛이 거의 결정되거든요.
3. 밥을 넣고 간장 조금으로 간을 맞춘 뒤, 계란 프라이를 올리시면 됩니다.
아... 불은 센 불보다 중불이 낫습니다. 천천히 하셔도 괜찮아요.
"""

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini_key = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None


def groq_create(**kwargs):
    """gpt-oss가 가끔 도구 호출을 시도해 400(tool_use_failed)이 나서, 몇 번 다시 시도한다."""
    for attempt in range(3):
        try:
            return groq_client.chat.completions.create(**kwargs)
        except groq.BadRequestError as e:
            if "tool_use_failed" not in str(e) or attempt == 2:
                raise


def ask_groq(messages, max_tokens=800):
    res = groq_create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.6,
        max_completion_tokens=max_tokens,
        reasoning_effort="low",
    )
    return res.choices[0].message.content


def gemini_args(messages, max_tokens):
    # system은 따로 넘기고, assistant 역할은 Gemini에서 "model"이라고 부름
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in messages
        if m["role"] != "system"
    ]
    return dict(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=messages[0]["content"],
            temperature=0.6,
            max_output_tokens=max_tokens,
        ),
    )


def ask_gemini(messages, max_tokens=800):
    res = gemini_client.models.generate_content(**gemini_args(messages, max_tokens))
    return res.text


def ask(messages, max_tokens=800):
    """Groq로 먼저 시도하고, 한도 소진(429)이면 Gemini로 넘어간다."""
    try:
        return ask_groq(messages, max_tokens)
    except groq.RateLimitError:
        if gemini_client is None:
            raise RuntimeError(
                "Groq 한도가 소진됐고 GEMINI_API_KEY도 없습니다. .env를 확인하세요."
            )
        print(colored("(Groq 한도 소진 → Gemini로 전환합니다)", "red"))
        return ask_gemini(messages, max_tokens)


def ask_stream(messages, max_tokens=800):
    """ask()와 같지만 답변을 글자 조각 단위로 흘려보낸다 (웹 화면용)."""
    try:
        stream = groq_create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.6,
            max_completion_tokens=max_tokens,
            reasoning_effort="low",
            stream=True,
        )
    except groq.RateLimitError:
        if gemini_client is None:
            raise RuntimeError(
                "Groq 한도가 소진됐고 GEMINI_API_KEY도 없습니다. .env를 확인하세요."
            )
        print(colored("(Groq 한도 소진 → Gemini로 전환합니다)", "red"))
        for chunk in gemini_client.models.generate_content_stream(
            **gemini_args(messages, max_tokens)
        ):
            if chunk.text:
                yield chunk.text
        return

    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(colored("최강록: 음... 어서 오세요. 가지고 계신 재료를 말씀해 주시면 됩니다.", "yellow"))
    while True:
        q = input("\n(재료를 말씀해 주세요. 그만하려면 'exit') 나 : ").strip()
        if not q:
            continue
        if q == "exit":
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
