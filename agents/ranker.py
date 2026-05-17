from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class RankerInput(BaseModel):
    title:str
    url:str
    source: str=Field(description="The source of the result")
    relevance_score: float=Field(description="Score from 0 to 1 indicating relevance to the R&D query")
    credibility_score: float=Field(description="Score from 0 to 1 indicating research methodology,publication authority or market validity")
    reason: str=Field(description="A brief explanation for the assigned scores")
    
    
class RankedResultSchema(BaseModel):
    results: list[RankerInput]

def rank_results_node(state:dict)->dict:

    raw_docs=state.get("raw_results",[])
    user_query=state.get("query","")

    print(f"-----------Agent Ranker: Evaluating {len(raw_docs)} results for query: {user_query} -----------   ")

    if not raw_docs:
        print("No raw results to rank.")
        return {"ranked_results": []}
    
    llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.2)

    structured_llm=llm.with_structured_output(RankedResultSchema)

    docs_payload = ""
    for idx, doc in enumerate(raw_docs):
        docs_payload += f"\n[Document ID: {idx}]\nTitle: {doc['title']}\nSummary: {doc['summary']}\nURL: {doc['url']}\nSource: {doc['source']}\n---"

    
    prompt = f"""
    You are an expert R&D Director and Technology Scout. Evaluate the following gathered research and market results based on how effectively they resolve this core technical prompt.
    
    Core Prompt: {user_query}
    
    Instructions:
    1. Review each item thoroughly.
    2. Rate its relevance and scientific/market credibility from 0.0 to 1.0.
    3. Provide a precise, engineering-focused rationale for the scores applied.
    4. Return your response strictly formatted as the structured results layout.
    
    Items to Evaluate:
    {docs_payload}
    """

    try:
        score_output=structured_llm.invoke(prompt)
        sorted_results=sorted(
            [item.model_dump() for item in score_output.results],
            key=lambda x: (x["relevance_score"], x["credibility_score"]),
            reverse=True
        )

        print(f"Sucessfully ranked {len(sorted_results)} results.")

        return {"ranked_results": sorted_results}
    
    except Exception as e:
        print(f"Error during ranking: {e}")
        fallback_results=[
            {
                "title":doc["title"],
                "url":doc["url"],
                "relevance_score": 0.5,
                "credibility_score": 0.5,
                "reason": "Fallback score due to ranking error"
            }
            for doc in raw_docs
        ]
        return {"ranked_results": fallback_results}
    

if __name__ == "__main__":
    print("\n--- Testing Ranker Agent Standalone Module ---")
    
    mock_state = {
        "query": "biodegradable polymers packaging",
        "raw_results": [
            {
                "title": "Self-attractive semiflexible polymers under an external force",
                "summary": "An abstract mathematical paper evaluating the physics and kinetic tension of polymer strands under mechanical stress fields.",
                "url": "https://arxiv.org/abs/test.physics",
                "source": "arxiv"
            },
            {
                "title": "Developments in Bio-based Materials for Sustainable Commercial Packaging Solutions",
                "summary": "A detailed market and engineering breakdown analyzing PHA and PLA biodegradable plastic replacements for modern industrial shipping bags.",
                "url": "https://mdpi.com/abs/test.packaging",
                "source": "web"
            }
        ]
    }
    
    output = rank_results_node(mock_state)
    
    print("\n--- RANKER OUTPUT RESULTS ---")
    for idx, paper in enumerate(output["ranked_results"], 1):
        print(f"\n[{idx}] Title: {paper['title']}")
        print(f"    Relevance: {paper['relevance_score']} | Credibility: {paper['credibility_score']}")
        print(f"    Reasoning: {paper['reason']}")