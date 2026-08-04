from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

class Flashcard(BaseModel):
    concept: str = Field(description="The key concept or term")
    description: str = Field(description="A brief educational description or explanation")
    image_prompt: str = Field(description="A detailed prompt for generating a high-fidelity educational visual representing this concept")

class FlashcardsList(BaseModel):
    flashcards: List[Flashcard]

def get_flashcard_chain(llm):
    parser = JsonOutputParser(pydantic_object=FlashcardsList)
    
    prompt = ChatPromptTemplate.from_template("""
    You are an expert Educational Content Creator. 
    Based on the TOPIC and CONTENT provided, create 3-5 high-quality educational flashcards.
    
    Each flashcard MUST include:
    - 'concept': A short title/term.
    - 'description': A simple explanation (1-2 sentences).
    - 'image_prompt': A descriptive prompt for AI image generation (e.g., 'A detailed scientific 3D illustration of...').

    {format_instructions}

    TOPIC: {topic}
    CONTENT: {content}
    """)

    # Injecting format instructions automatically from the parser
    chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser
    return chain
