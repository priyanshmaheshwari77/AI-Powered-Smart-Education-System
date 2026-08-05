import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"

SINGLE_PROMPT = """You are a world-class educator and subject matter expert. Your task is to produce a MASSIVE, EXHAUSTIVE, and BOOK-CHAPTER LENGTH educational guide about the topic the user searched for: {topic}.

CRITICAL RULES:
- Be EXTREMELY DETAILED and FACTUALLY ACCURATE. Do not hallucinate.
- The article MUST BE AT LEAST 15-20 paragraphs long (minimum 1500 words). Do not summarize briefly.
- Cover every possible angle: historical background, advanced core concepts, mathematical/scientific principles (if applicable), deep technical details, and massive amounts of real-world examples.
- Write a university-level textbook chapter matching EXACTLY what the user typed.

Return ONLY valid JSON (no markdown wrapping, no code fences) matching exactly this structure:

{{
  "article": "Write a MASSIVE, EXHAUSTIVE educational article. IT MUST BE VERY LONG. Include:\\n\\n**1. Comprehensive Introduction:** Deeply define the topic and its significance.\\n\\n**2. Historical Context & Background:** Detailed history, origins, or evolution.\\n\\n**3. Deep Dive into Core Concepts:** Expand heavily here. Cover at least 5 key principles in extreme detail with formulas or technical breakdowns if relevant.\\n\\n**4. Advanced Principles:** Detailed analysis of advanced mechanics, theories, or systems.\\n\\n**5. Real-World Applications & Case Studies:** Multiple extensive examples of how this is used in practice.\\n\\n**6. Summary & Future Outlook:** A thorough conclusion.\\n\\nUSE EXTENSIVE MARKDOWN (headers, bolding, bullet points). The article string MUST BE AT LEAST 15 PARAGRAPHS long.",

  "flashcards": {{"flashcards": [
    {{"concept": "Key Term 1", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 2", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 3", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 4", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 5", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 6", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 7", "description": "A clear, accurate 3-sentence explanation of this concept."}},
    {{"concept": "Key Term 8", "description": "A clear, accurate 3-sentence explanation of this concept."}}
  ]}},

  "quiz": {{"questions": [
    {{"question": "A challenging factual question?", "options": ["A", "B", "C", "D"], "correct_answer": "B", "explanation": "A thorough explanation of the answer."}},
    {{"question": "A conceptual understanding question?", "options": ["A", "B", "C", "D"], "correct_answer": "C", "explanation": "A thorough explanation."}},
    {{"question": "An application-based question?", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "A thorough explanation."}},
    {{"question": "A question testing deeper knowledge?", "options": ["A", "B", "C", "D"], "correct_answer": "D", "explanation": "A thorough explanation."}},
    {{"question": "A highly advanced technical question?", "options": ["A", "B", "C", "D"], "correct_answer": "B", "explanation": "A thorough explanation."}}
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
