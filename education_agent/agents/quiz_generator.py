from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Define Data Structure for Quiz
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 formatted options (e.g. ['A) ...', 'B) ...'])")
    correct_answer: str = Field(description="The correct answer text exactly matching one of the options")
    explanation: str = Field(description="Brief explanation of why it is correct")

class Quiz(BaseModel):
    questions: List[QuizQuestion]

# Define Prompt
QUIZ_PROMPT = """
You are the QUIZ AGENT.
Your goal is to generate an interactive quiz based on the provided topic and content.

Topic: {topic}
Content Summary: {content}

STRICT INSTRUCTIONS:
1. Generate exactly 3 multiple-choice questions based on the content.
2. Ensure options are distinct.
3. Output strictly in valid JSON format matching the schema.
4. Do NOT add any conversational text, only the JSON.

"""

def get_quiz_chain(llm=None):
    if llm is None:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
    
    parser = JsonOutputParser(pydantic_object=Quiz)
    
    prompt = ChatPromptTemplate.from_template(
        template=QUIZ_PROMPT + "\n\n{format_instructions}",
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    return chain
