import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
import datetime

# ---------------------------------------------------
# STOCK CATEGORIES AND EXAMPLE KEYWORDS
# ---------------------------------------------------
STOCK_CATEGORIES = {
    "F&O": ["NIFTY 50", "BANKNIFTY", "derivatives India", "stock futures India"],
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


# ---------------------------------------------------
# FETCH NEWS USING GOOGLE NEWS RSS
# ---------------------------------------------------
def fetch_news(query, days_back=7, max_items=20):
    """
    Fetch recent Google News RSS results for a given query.
    `days_back` determines how far back to fetch (approx).
    """
    time_filter = f"when:{days_back}d"
    encoded_query = urllib.parse.quote(f"{query} {time_filter}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        return pd.DataFrame()

    articles = []
    for entry in feed.entries[:max_items]:
        articles.append({
            "Date": entry.get("published", ""),
            "Title": entry.get("title", ""),
            "Source": entry.get("source", {}).get("title", "") if "source" in entry else "",
            "Link": entry.get("link", ""),
            "Keyword": query
        })
    return pd.DataFrame(articles)


# ---------------------------------------------------
# STREAMLIT APP
# ---------------------------------------------------
def main():
    st.set_page_config(page_title="Stock News Dashboard", layout="wide")
    st.title("📊 Stock Market News Dashboard")
    st.markdown("### View categorized stock news from Google News — filtered by time window.")

    category = st.selectbox("📁 Select Stock Category", list(STOCK_CATEGORIES.keys()))
    timeframe = st.selectbox("⏱ Select Time Window", list(TIME_WINDOWS.keys()))
    fetch_button = st.button("🔍 Fetch News")

    if fetch_button:
        days_back = TIME_WINDOWS[timeframe]
        keywords = STOCK_CATEGORIES[category]

        st.info(f"Fetching latest news for **{category}** stocks from the past **{timeframe}**...")
        all_news = pd.DataFrame()

        for kw in keywords:
            with st.spinner(f"Searching for '{kw}'..."):
                df = fetch_news(kw, days_back=days_back)
                all_news = pd.concat([all_news, df], ignore_index=True)

        if all_news.empty:
            st.warning("No news found for this selection. Try another category or larger time window.")
        else:
            # Remove duplicates
            all_news.drop_duplicates(subset=["Title"], inplace=True)
            all_news["Date"] = pd.to_datetime(all_news["Date"], errors="coerce")
            all_news.sort_values(by="Date", ascending=False, inplace=True)

            st.success(f"✅ Found {len(all_news)} news articles.")

            # Display in an interactive table
            st.dataframe(all_news, use_container_width=True)

            # Clickable version
            def make_clickable(url):
                return f'<a href="{url}" target="_blank">Read Article</a>'

            all_news["Read"] = all_news["Link"].apply(make_clickable)
            st.markdown(
                all_news[["Date", "Title", "Source", "Keyword", "Read"]]
                .to_html(escape=False, index=False),
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
