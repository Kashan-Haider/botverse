from dotenv import load_dotenv
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini model with default config
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# prompt = ChatPromptTemplate(
#     [
#         (
#             "system",
#             (
#                 "You are a helpful AI that classifies user queries into predefined topics. "
#                 "You will be given a list of topics and a user query. Your task is to identify which topic "
#                 "from the list the query belongs to. If the query doesn’t match any topic, respond with 'default'. "
#                 "Return your answer as a single category like 'cars', 'medical', or 'movies'.\nTopics:\n{chain_names}"
#             ),
#         ),
#         ("human", "{user_input}"),
#     ]
# )