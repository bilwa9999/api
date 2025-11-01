import streamlit as st
import pandas as pd
import datetime
from GNews import GNews   # pip install GNews

# mapping for your stock‐categories (you’ll need to decide which tickers/keywords map to each category)
STOCK_CATEGORIES = {
    "F&O": ["NIFTY 50", "BANKNIFTY", "Futures options stocks India"],
    "Large Cap": ["Reliance Industries", "Tata Consultancy Services", "HDFC Bank"],
    "Mid Cap": ["Midcap Company1", "Midcap Company2"],
    "Small Cap": ["Smallcap Company1", "Smallcap Company2"],
    "Blue-chip": ["Bluechip Company1", "Bluechip Company2"]
}

# time windows mapping
TIME_WINDOWS = {
    "1 Week": 7,
    "4 Weeks": 28,
    "3 Months": 90,
    "6 Months": 180
}

def fetch_news(query, days_back=7, max_results=50):
    """Fetch news for query within the past `days_back` days using GNews."""
    gn = GNews(language='en', country='US')  # adjust region/language as needed
    # compute start_date
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days_back)
    gn.set_time_range(start_date.strftime("%m/%d/%Y"), end_date.strftime("%m/%d/%Y"))
    gn.search(query)
    results = gn.result()[:max_results]
    df = pd.DataFrame(results)
    if not df.empty:
        # convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def main():
    st.title("Stock News Aggregator")
    st.markdown("Select category and time window to view relevant news.")

    category = st.selectbox("Stock Category", list(STOCK_CATEGORIES.keys()))
    time_window = st.selectbox("Time Window", list(TIME_WINDOWS.keys()))

    if st.button("Fetch News"):
        days = TIME_WINDOWS[time_window]
        keywords = STOCK_CATEGORIES[category]

        all_news = pd.DataFrame()
        for kw in keywords:
            st.write(f"Fetching for keyword: {kw} …")
            df = fetch_news(kw, days_back=days)
            df['keyword'] = kw
            all_news = pd.concat([all_news, df], ignore_index=True)

        if all_news.empty:
            st.write("No news found for this selection.")
        else:
            # optionally sort, drop duplicates, etc.
            all_news = all_news.drop_duplicates(subset=['title', 'link'])
            all_news = all_news.sort_values(by='date', ascending=False)
            st.write(f"Found {len(all_news)} articles.")
            st.dataframe(all_news[['date','title','publisher','keyword','link']])

            # optionally allow opening link
            def make_clickable(url):
                return f'<a href="{url}" target="_blank">Open article</a>'
            all_news['open'] = all_news['link'].apply(make_clickable)
            st.markdown(all_news[['date','title','publisher','keyword','open']].to_html(escape=False, index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
