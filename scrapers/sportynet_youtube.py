import feedparser

CHANNEL_ID = "UCMcc9elPZGpg6eU4i3YaCpA"  # @SportyNetBrasil (verificato)

def get_schedule():
    """
    Recupera i titoli dei video dal feed RSS del canale YouTube di SportyNet.
    """
    pages = []
    try:
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            text = entry.title + " " + entry.get("summary", "")
            pages.append(text)
    except Exception as e:
        print(f"  [SportyNet YouTube] {e}")
    return pages