import concurrent.futures
from tools.arxiv_tool import search
from tools.vector_store import search_similar_documents,save_document
from tools.web_search_tool import search_web

def parallel_search_node(state:dict)->dict:
    """Performs parallel searches across multiple sources and combines results."""

    query=state.get("query","")
    keywords=state.get("keywords",[])

    search_item=" ".join(keywords) if keywords else query

    print(f"\n---------Launching 3 Way Parallel Search------Researching: {search_item}")

    arxiv_results = []
    local_results = []
    web_results = []

    # Run arXiv, local vector DB, and Google Web searches simultaneously on separate threads to save time
    with concurrent.futures.ThreadPoolExecutor() as ex:
        future_arxiv=ex.submit(search,search_item,max_results=2)
        future_vector=ex.submit(search_similar_documents,search_item,limit=2)
        future_web=ex.submit(search_web,search_item,max_results=2)

        try:
            arxiv_results = future_arxiv.result()
        except Exception as e:
            print(f"ArXiv fetch failed: {e}")
            
        try:
            local_results = future_vector.result()
        except Exception as e:
            print(f"Local vector DB fetch failed: {e}")
            
        try:
            web_results = future_web.result()
        except Exception as e:
            print(f"Web search fetch failed: {e}")

    seen_urls=set()
    combined_results=[]

    for doc in local_results:
        if doc["url"] not in seen_urls:
            seen_urls.add(doc["url"])
            combined_results.append({
                "title":doc["title"],
                "summary":doc["summary"],
                "url":doc["url"],
                "source":doc["source"]
                })
            
    new_count=0
    for doc in arxiv_results:
        if doc["url"] not in seen_urls:
            seen_urls.add(doc["url"])
            combined_results.append(doc)

            try:
                # Automatically ingest newly discovered arXiv papers into our local vector database for future research
                save_document(doc)
                new_count+=1
            except Exception as e:
                print(f"Failed to auto-ingest document {doc['url']} from Arxiv: {e}")


    for doc in web_results:
        if doc["url"] not in seen_urls:
            seen_urls.add(doc["url"])
            combined_results.append(doc)
            try:
                # Automatically ingest live web articles into the vector database as well
                save_document(doc)
                new_count += 1
            except Exception as e:
                print(f"Failed to auto-ingest web article {doc['url']}: {e}")


    print(f"Search Complete Total item found {len(combined_results)}. New Live Paper auto save to DB: {new_count}")

    return {
        "raw_results":combined_results
    }


if __name__ == "__main__":
    print("\n--- Testing Complete 3-Way Searcher Agent ---")
    mock_state = {
        "query": "biodegradable polymers packaging",
        "keywords": ["biodegradable", "polymers", "packaging"]
    }
    output_state = parallel_search_node(mock_state)
    
    print("\n--- COMBINED RESULTS OVERVIEW ---")
    for idx, item in enumerate(output_state["raw_results"], 1):
        print(f"[{idx}] Source: {item['source']} | Title: {item['title'][:60]}...")