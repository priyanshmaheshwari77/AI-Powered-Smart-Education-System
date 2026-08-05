import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

MODEL_NAME = "llama-3.1-8b-instant"

SINGLE_PROMPT = """You are an expert educator. Produce highly accurate and extremely concise educational content for the topic: {topic}.

Return ONLY valid JSON (no markdown wrapping) matching exactly this format:
{{"article": "An extremely brief 3-4 sentence summary of the topic.",
 "flashcards": {{"flashcards": [{{"concept": "Key Term 1", "description": "A very brief 1-sentence definition"}}, {{"concept": "Key Term 2", "description": "A very brief 1-sentence definition"}}]}},
 "quiz": {{"questions": [
     {{"question": "Question 1 about the topic?", "options": ["Choice A", "Choice B", "Choice C", "Choice D"], "correct_answer": "Choice B", "explanation": "Why B is correct"}},
     {{"question": "Question 2 about the topic?", "options": ["Choice A", "Choice B", "Choice C", "Choice D"], "correct_answer": "Choice C", "explanation": "Why C is correct"}},
     {{"question": "Question 3 about the topic?", "options": ["Choice A", "Choice B", "Choice C", "Choice D"], "correct_answer": "Choice D", "explanation": "Why D is correct"}},
     {{"question": "Question 4 about the topic?", "options": ["Choice A", "Choice B", "Choice C", "Choice D"], "correct_answer": "Choice A", "explanation": "Why A is correct"}},
     {{"question": "Question 5 about the topic?", "options": ["Choice A", "Choice B", "Choice C", "Choice D"], "correct_answer": "Choice B", "explanation": "Why B is correct"}}
 ]}}
}}"""

class Orchestrator:
    def __init__(self):
        # Gracefully handle missing API key in Streamlit Cloud environment
        if not os.getenv("GROQ_API_KEY"):
            # No API key; set LLM to None and log a warning (will be handled in run)
            self.llm = None
        else:
            self.llm = ChatGroq(model=MODEL_NAME, temperature=0.5).bind(
                response_format={"type": "json_object"}
            )
        
    def run(self, topic: str):
        print(f"--- [ORCHESTRATOR] Single structured call for: {topic} ---")
        prompt = ChatPromptTemplate.from_template(SINGLE_PROMPT)
        
        if self.llm is None:
            # No LLM available; inform the user about missing API key.
            result = {
                "article": "GROQ_API_KEY is not configured. Please set the secret in Streamlit Cloud settings.",
                "flashcards": {"flashcards": []},
                "quiz": None,
            }
        else:
            try:
                chain = prompt | self.llm | JsonOutputParser()
                result = chain.invoke({"topic": topic})
            except Exception as e:
                print(f"Parsing error: {e}")
                # Absolute fallback
                result = {
                    "article": f"Here is a summary on {topic}. (Error generating full dynamic content: {e})",
                    "flashcards": {"flashcards": [{"concept": "Error", "description": str(e)}]},
                    "quiz": None,
                }
            
        return {
            "article": result.get("article", ""),
            "research": "",
            "videos": [],
            "flashcards": result.get("flashcards"),
            "quiz": result.get("quiz")
        }
