import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

MODEL_NAME = "llama-3.1-8b-instant"

SINGLE_PROMPT = """You are an expert educator. Produce highly accurate educational content for the topic: {topic}.

Return ONLY valid JSON (no markdown wrapping) matching exactly this format:
{{"article": "A highly informative 2 paragraph summary of the topic.",
 "flashcards": {{"flashcards": [{{"concept": "Key Term 1", "description": "Definition"}}, {{"concept": "Key Term 2", "description": "Definition"}}]}},
 "quiz": {{"questions": [
     {{"question": "A specific question about the topic?", "options": ["Real Option 1", "Real Option 2", "Real Option 3", "Real Option 4"], "correct_answer": "Real Option 2", "explanation": "Why Option 2 is correct"}},
     {{"question": "Another specific question?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option C", "explanation": "Why Option C is correct"}},
     {{"question": "A third question?", "options": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"], "correct_answer": "Choice 1", "explanation": "Why Choice 1 is correct"}}
 ]}}
}}"""

class Orchestrator:
    def __init__(self):
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY not found.")
        self.llm = ChatGroq(model=MODEL_NAME, temperature=0.5).bind(
            response_format={"type": "json_object"}
        )
        
    def run(self, topic: str):
        print(f"--- [ORCHESTRATOR] Single structured call for: {topic} ---")
        prompt = ChatPromptTemplate.from_template(SINGLE_PROMPT)
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            result = chain.invoke({"topic": topic})
        except Exception as e:
            print(f"Parsing error: {e}")
            # Absolute fallback
            result = {
                "article": f"Here is a summary on {topic}. (Error generating full dynamic content: {e})",
                "flashcards": {"flashcards": [{"concept": "Error", "description": str(e)}]},
                "quiz": None
            }
            
        return {
            "article": result.get("article", ""),
            "research": "",
            "videos": [],
            "flashcards": result.get("flashcards"),
            "quiz": result.get("quiz")
        }
