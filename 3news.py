import streamlit as st
import pandas as pd
from gnewsclient import gnewsclient
import datetime

# -----------------------------
# Stock categories
# -----------------------------
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


def fetch_news(keyword, max_results=20):
    """Fetch top news for a keyword using gnewsclient."""
    client = gnewsclient.NewsClient(
        language='english',
        location='India',
        query=keyword,
        max_results=max_results
    )
    news_list = client.get_news()
    if not news_list:
        return pd.DataFrame()
    df = pd.DataFrame(news_list)
    df['keyword'] = keyword
    df.rename(columns={'title': 'headline'}, inplace=True)
    return df


def main():
    st.title("📈 Stock Market News Dashboard")
    st.markdown("Get the latest stock-related news from Google News, categorized by stock type and time window.")

    category = st.selectbox("Select Stock Category", list(STOCK_CATEGORIES.keys()))
    timeframe = st.selectbox("Select Time Window", list(TIME_WINDOWS.keys()))

    if st.button("Fetch News"):
        st.info(f"Fetching news for **{category}** stocks ({timeframe})...")

        keywords = STOCK_CATEGORIES[category]
        all_news = pd.DataFrame()

        for kw in keywords:
            st.write(f"🔎 Searching for: {kw}")
            df = fetch_news(kw)
            all_news = pd.concat([all_news, df], ignore_index=True)

        if all_news.empty:
            st.warning("No news found for this selection.")
        else:
            all_news.drop_duplicates(subset=['headline'], inplace=True)
            all_news = all_news[['headline', 'publisher', 'link', 'keyword']]
            st.success(f"✅ Found {len(all_news)} news articles.")
            st.dataframe(all_news)

            # Clickable links
            def make_clickable(url):
                return f'<a href="{url}" target="_blank">Read Article</a>'

            all_news['Read'] = all_news['link'].apply(make_clickable)
            st.markdown(
                all_news[['headline', 'publisher', 'keyword', 'Read']].to_html(escape=False, index=False),
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
