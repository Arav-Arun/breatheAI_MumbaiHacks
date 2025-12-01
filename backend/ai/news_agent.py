import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

def get_pollution_news(city: str, limit: int = 5) -> list:
    """
    Fetches latest air pollution news for a specific city using Google News RSS.
    Returns a list of dictionaries with title, link, source, and date.
    """
    try:
        if not city:
            return []
            
        # Construct RSS URL
        query = quote(f"{city} air pollution air quality")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        news_items = []
        # Iterate over items (limit to specified number)
        for item in root.findall('./channel/item')[:limit]:
            title = item.find('title').text if item.find('title') is not None else "No Title"
            link = item.find('link').text if item.find('link') is not None else "#"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            source = item.find('source').text if item.find('source') is not None else "Google News"
            
            # Clean up title (Google News often has "Title - Source")
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
                
            news_items.append({
                "title": title,
                "link": link,
                "source": source,
                "date": pub_date
            })
            
        return news_items
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
