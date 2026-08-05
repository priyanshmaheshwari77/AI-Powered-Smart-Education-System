import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

SINGLE_PROMPT = """You are a world-class educator and subject matter expert. Your task is to produce DETAILED, ACCURATE, and COMPREHENSIVE educational content about the topic the user searched for: {topic}.

CRITICAL RULES:
- Be FACTUALLY ACCURATE. Do not hallucinate or invent information.
- Cover the topic THOROUGHLY with real facts, dates, formulas, or examples as appropriate.
- Write content that matches EXACTLY what the user typed — do not drift to a different subject.
- Use clear, structured language suitable for a university-level student.

Return ONLY valid JSON (no markdown wrapping, no code fences) matching exactly this structure:

{{
  "article": "Write a DETAILED educational article about the topic. Include:\\n\\n**Introduction:** Define the topic clearly and explain why it matters.\\n\\n**Core Concepts:** Cover 3-5 key ideas, principles, or components in depth. Use real-world examples, formulas, historical context, or step-by-step explanations as appropriate.\\n\\n**Key Details:** Include important facts, figures, dates, names, or technical details that a student would need to know.\\n\\n**Applications:** Explain how this topic is used in practice or its real-world significance.\\n\\n**Summary:** Conclude with a brief recap of the most important takeaways.\\n\\nThe article should be at least 8-10 paragraphs long and use markdown formatting (headers with ##, bold with **, bullet points with -, etc.) for readability.",

  "flashcards": {{"flashcards": [
    {{"concept": "Key Term 1", "description": "A clear, accurate 2-3 sentence explanation of this concept with an example if applicable."}},
    {{"concept": "Key Term 2", "description": "A clear, accurate 2-3 sentence explanation of this concept with an example if applicable."}},
    {{"concept": "Key Term 3", "description": "A clear, accurate 2-3 sentence explanation of this concept with an example if applicable."}},
    {{"concept": "Key Term 4", "description": "A clear, accurate 2-3 sentence explanation of this concept with an example if applicable."}},
    {{"concept": "Key Term 5", "description": "A clear, accurate 2-3 sentence explanation of this concept with an example if applicable."}},
    {{"concept": "Key Term 6", "description": "A clear, accurate 2-3 sentence explanation of this concept with an example if applicable."}}
  ]}},

  "quiz": {{"questions": [
    {{"question": "A challenging factual question about the topic?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option B", "explanation": "A thorough 2-3 sentence explanation of why this answer is correct and why the others are wrong."}},
    {{"question": "A conceptual understanding question?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option C", "explanation": "A thorough 2-3 sentence explanation of why this answer is correct."}},
    {{"question": "An application-based question?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option A", "explanation": "A thorough 2-3 sentence explanation of why this answer is correct."}},
    {{"question": "A question testing deeper knowledge?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option D", "explanation": "A thorough 2-3 sentence explanation of why this answer is correct."}},
    {{"question": "A question connecting concepts?", "options": ["Option A", "Option B", "Option C", "Option D"], "correct_answer": "Option B", "explanation": "A thorough 2-3 sentence explanation of why this answer is correct."}}
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
