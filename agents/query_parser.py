from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class QueryAnalysis(BaseModel):
    keywords: List[str] = Field(description="5-8 specific technical keywords for vector search.")
    refined_query: str = Field(description="A clean, optimized version of the user's request for API searching.")
    reasoning: str = Field(description="Brief explanation of why these keywords were chosen.")

def parse_query_node(state: dict) -> dict:
    """
    LLM-powered node that transforms a raw user query into structured search terms.
    """
    print(f"\n--- Analyzing user query: {state['query']} ---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    
    structured_llm = llm.with_structured_output(QueryAnalysis)
    
    prompt = f"""
    You are an R&D Technology Scout. Your job is to take a business problem 
    and turn it into technical search terms for scientific databases.
    
    User Problem: {state['query']}
    
    Identify core technologies, methodologies, and specific technical domains.
    """
    
    try:
        analysis = structured_llm.invoke(prompt)
        
        return {
            "keywords": analysis.keywords,
            "query": analysis.refined_query 
        }
        
    except Exception as e:
        print(f"Error in Query Parser: {e}")
        return {"keywords": state["query"].split()}

if __name__ == "__main__":
    mock_state = {"query": "I want to find new ways to use AI for discovering chemicals in plastic recycling"}
    result = parse_query_node(mock_state)
    
    print("\n--- LLM ANALYSIS RESULTS ---")
    print(f"\nKeywords: {result['keywords']}")
    print(f"\n Refined Query: {result['query']}")