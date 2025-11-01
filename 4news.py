import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
import datetime

# -----------------------------------------
# Stock categories and example keywords
# -----------------------------------------
STOCK_CATEGORIES = {
    "F&O": ["NIFTY 50", "BANKNIFTY", "stock futures India", "derivatives India"],
    "Large Cap": ["Reliance Industries", "Tata Consultancy Services", "Infosys", "HDFC Bank"],
    "Mid Cap": ["Bharat Forge", "Voltas", "Crompton Greaves", "Castrol India"],
    "Small Cap": ["Vaibhav Global", "NGL Fine Chem", "RattanIndia Power"],
    "Bluechip": ["Hindustan Unilever", "ITC", "State Bank of India", "Bharti Airtel"]
}

TIME_WINDOWS = {
    "1 Week": 7,
    "4 Weeks": 28,
    "3 Months": 90,
    "6 Months": 180
}

# -----------------------------------------
# Function to fetch news from Google News RSS
# -----------------------------------------
def fetch_news(query, max_items=20):
    """Fetch news from Google News RSS for a keyword."""
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}+when:6m&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return pd.DataFrame()
    data = []
    for entry in feed.entries[:max_items]:
        data.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published if "published" in entry else "",
            "source": entry.source.title if "source" in entry else "",
            "keyword": query
        })
    return pd.DataFrame(data)


# -----------------------------------------
# Streamlit UI
# -----------------------------------------
def main():
    st.title("📈 Stock Market News Dashboard (Google News RSS)")
    st.markdown("View categorized stock-related news from Google News, filtered by time range.")

    category = st.selectbox("Select Stock Category", list(STOCK_CATEGORIES.keys()))
    timeframe = st.selectbox("Select Time Window", list(TIME_WINDOWS.keys()))

    if st.button("Fetch News"):
        st.info(f"Fetching latest news for **{category}** stocks ({timeframe})...")

        keywords = STOCK_CATEGORIES[category]
        all_news = pd.DataFrame()

        for kw in keywords:
            st.write(f"🔎 Searching for: {kw}")
            df = fetch_news(kw)
            all_news = pd.concat([all_news, df], ignore_index=True)

        if all_news.empty:
            st.warning("No news found for this selection.")
        else:
            all_news.drop_duplicates(subset=['title'], inplace=True)
            st.success(f"✅ Found {len(all_news)} news articles.")
            all_news = all_news[['published', 'title', 'source', 'keyword', 'link']]
            st.dataframe(all_news)

            def make_clickable(url):
                return f'<a href="{url}" target="_blank">Read Article</a>'

            all_news['Read'] = all_news['link'].apply(make_clickable)
            st.markdown(
                all_news[['published', 'title', 'source', 'keyword', 'Read']].to_html(escape=False, index=False),
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
