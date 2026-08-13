import asyncio
from app.core.groq_client import get_groq_client


async def main():
    client = get_groq_client()
    response = await client.chat([{"role": "user", "content": "Say hello in exactly 5 words."}])
    print("AI replied:", response.text)
    print("Model used:", response.model_used)
    print("Tokens: in =", response.prompt_tokens, " out =", response.completion_tokens)


asyncio.run(main())