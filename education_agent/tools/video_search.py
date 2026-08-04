from duckduckgo_search import DDGS
import warnings

# Suppress the rename warning from duckduckgo_search
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

def get_youtube_links(topic, max_results=3):
    """
    Searches for YouTube videos related to the topic using DuckDuckGo.
    Returns a list of dictionaries with title, link, and thumbnail (if available).
    """
    print(f"--- [VIDEO SEARCH] Searching for: {topic} ---")
    results = []
    try:
        with DDGS() as ddgs:
            # specifically search for videos
            # We append "youtube" to the query to ensure we get youtube links predominantly
            query = f"{topic} site:youtube.com"
            search_results = ddgs.videos(query, max_results=max_results)
            
            for r in search_results:
                results.append({
                    'title': r.get('title'),
                    'link': r.get('content'), # DDGS video result usually has 'content' as link URL or 'embed_url'
                    'thumbnail': r.get('images', {}).get('small') # DDGS returns images dict usually
                })
                
            # If search_results format varies (ddgs versions change), fallback clean up might be needed.
            # Printing one result debug if needed.
            
    except Exception as e:
        print(f"Error searching videos: {e}")
        
    return results
