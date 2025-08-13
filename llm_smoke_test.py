from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv(override=True)

print("Model:", os.getenv("OPENAI_MODEL"))
print("API key present:", bool(os.getenv("OPENAI_API_KEY")))
print("Key snippet:", os.getenv("OPENAI_API_KEY")[:10])  # Debug

llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5"), temperature=0.0)
resp = llm.invoke("Reply with 'pong' only.")
print("LLM OK:", resp.content)
