import streamlit as st
import pandas as pd
from GoogleNews import GoogleNews
import datetime

# -----------------------------
# Category and timeframe setup
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

# -----------------------------
# News fetching function
# -----------------------------
def fetch_news(keyword, days_back=7):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_back)
    googlenews = GoogleNews(lang='en', region='IN')
    googlenews.set_time_range(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'))
    googlenews.search(keyword)
    results = googlenews.result()
    if not results:
        return pd.DataFrame()
    df = pd.DataFrame(results)
    df['keyword'] = keyword
    return df


# -----------------------------
# Streamlit UI
# -----------------------------
def main():
    st.title("📈 Stock Market News Dashboard")
    st.markdown("View stock-related news categorized by company type and time window, sourced from Google News.")

    category = st.selectbox("Select Stock Category", list(STOCK_CATEGORIES.keys()))
    timeframe = st.selectbox("Select Time Window", list(TIME_WINDOWS.keys()))
    fetch_button = st.button("Fetch News")

    if fetch_button:
        st.info(f"Fetching news for **{category}** stocks from the past **{timeframe}**...")

        days_back = TIME_WINDOWS[timeframe]
        keywords = STOCK_CATEGORIES[category]

        all_news = pd.DataFrame()
        for kw in keywords:
            st.write(f"🔎 Searching for: {kw}")
            df = fetch_news(kw, days_back=days_back)
            all_news = pd.concat([all_news, df], ignore_index=True)

        if all_news.empty:
            st.warning("No news found for this selection.")
        else:
            # Clean up and format
            all_news = all_news.drop_duplicates(subset=['title'])
            all_news = all_news[['date', 'title', 'media', 'link', 'keyword']]
            all_news['date'] = pd.to_datetime(all_news['date'], errors='coerce')
            all_news = all_news.sort_values(by='date', ascending=False)

            st.success(f"✅ Found {len(all_news)} news articles.")
            st.dataframe(all_news)

            # Clickable table
            def make_clickable(url):
                return f'<a href="{url}" target="_blank">Read Article</a>'
            all_news['Read'] = all_news['link'].apply(make_clickable)
            st.markdown(
                all_news[['date', 'title', 'media', 'keyword', 'Read']].to_html(escape=False, index=False),
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
