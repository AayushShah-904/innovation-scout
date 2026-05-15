import arxiv
from datetime import datetime

def search(query:str,max_results:int=5)->list[dict]:
    print(f"Querying arXvi api for {query}")

    client=arxiv.Client()
    
    search=arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    sanitized_results=[]

    try:
        results=client.results(search)
        for r in results:
            doc = {
                "title": r.title.replace("\n", " ").strip(),
                "summary": r.summary.replace("\n", " ").strip()[:600] + "...",
                "authors": [author.name for author in r.authors[:3]],
                "url": r.entry_id,
                "published": str(r.published.date()),
                "source": "arxiv"
            }

            sanitized_results.append(doc)
            print(f"Successfully retrieved {len(sanitized_results)} papers from arXiv.")
        return sanitized_results

    except Exception as e:
        print(f"Error querying arXiv: {e}")
        return []


if __name__=="__main__":
    print("testing")
    test_query = "AI-powered tools for enterprise technology scouting"
    test_results = search(test_query, max_results=2)

    print("-------OUTPUT---------")
    for i, paper in enumerate(test_results, 1):
        print(f"\n[{i}] Title: {paper['title']}")
        print(f"    URL: {paper['url']}")
        print(f"    Authors: {', '.join(paper['authors'])}")
        print(f"    Summary Snippet: {paper['summary'][:150]}")


