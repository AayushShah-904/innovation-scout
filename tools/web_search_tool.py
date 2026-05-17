from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def search_web(query: str, max_results: int = 5) -> list[dict]:
    print(f"Searching the web for: {query}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,
        )

        # Bind Google Search grounding to Gemini so it can actively search the live web for recent developments
        model_with_search = llm.bind_tools([{"google_search": {}}])

        prompt = f"""
        Find information about: "{query}".
        Provide the top {max_results} distinct developments, web articles, or company records.
        Include clear links or references in your analysis summary text.
        """

        response = model_with_search.invoke(prompt)
        response_text = str(response.content) if hasattr(response, "content") else ""
        sanitized_response = []
        res_metadata = getattr(response, "response_metadata", {})
        grounding_meta = res_metadata.get("grounding_metadata", {})
        
        # Parse the live web grounding chunks from Gemini's response metadata to get exact source URLs
        if grounding_meta and "grounding_chunks" in grounding_meta:
            chunks = grounding_meta.get("grounding_chunks", [])
            for chunk in chunks[:max_results]:
                web = chunk.get("web", {})
                if web:
                    sanitized_response.append({
                        "title": web.get("title", "Live Web Intelligence Node").strip(),
                        "summary": response_text[:400].strip() + "...",
                        "url": web.get("uri", ""),
                        "source": "web"
                    })
        
        if not sanitized_response:
            sanitized_response.append({
                "title": f"Web Grounding Target: {query[:30]}",
                "summary": response_text[:500].strip() + "...",
                "url": "https://www.google.com/search?q=" + query.replace(" ", "+"),
                "source": "web"
            })
        
        print("Successfully retrieved web grounding targets.")
        return sanitized_response   

    except Exception as e:
        print(f"Error during web search: {e}")
        return [{
            "title": f"Web Fallback Reference: {query[:25]}",
            "summary": f"Live data retrieval execution defaulted. Status: {e}",
            "url": "https://www.google.com/search?q=" + query.replace(" ", "+"),
            "source": "web"
        }]

if __name__ == "__main__":
    test_query = "AI-powered innovation discovery platforms"
    results = search_web(test_query, max_results=2)
    
    print("\n--- GEMINI GROUNDING TEST OUTPUT ---")
    for idx, item in enumerate(results, 1):
        print(f"\n[{idx}] Title: {item['title']}")
        print(f"    URL: {item['url']}")
        print(f"    Context: {item['summary'][:200]}")