from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Define the Researcher Agent Prompt
RESEARCHER_PROMPT = """
You are the RESEARCHER AGENT.
Your goal is to gather accurate, relevant, and up-to-date information on the user's topic.

STRICT RULES:
- Do NOT format like final notes.
- Do NOT add introduction or conclusion.
- Do NOT simplify excessively.
- Do NOT add decorative formatting.
- Do NOT invent references.
- Focus only on data gathering.

Research Output Format:
- Core Definitions
- Key Concepts
- Technical Explanation
- Real-world Applications
- Study Resources / References

User Topic: {topic}
Web Search Results: {search_results}
"""

def get_researcher_chain(llm=None):
    if llm is None:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0) # Using Llama 3.3 70B on Groq
    
    def get_search_results(inputs):
        topic = inputs["topic"]
        print(f"--- [RESEARCHER] Searching for: {topic} ---")
        try:
            # Custom implementation to bypass LangChain import issue
            from duckduckgo_search import DDGS
            import warnings
            warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(topic, max_results=3))
                if results:
                    return "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in results])
                return "No results found."
        except Exception as e:
            print(f"Search failed: {e}")
            return f"Search failed: {e}"

    prompt = ChatPromptTemplate.from_template(RESEARCHER_PROMPT)
    
    # Chain: (Topic) -> (Search Results + Topic) -> Prompt -> LLM -> Output
    chain = (
        {"topic": RunnablePassthrough(), "search_results": get_search_results}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
