
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Telegram Channel Analysis", layout="wide")

st.title("Аналіз Telegram-каналу — прикладний додаток")

st.markdown("""
Завантажте CSV-файл із колонками **datetime** (наприклад `2025-10-16 14:30`), **views**, **reactions**.
Якщо файл не завантажено, використовується прикладний CSV, що додається з додатком.
""")

uploaded = st.file_uploader("Завантажити CSV", type=["csv"])

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv("sample_posts.csv")
    # try to parse datetime
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    elif 'дата' in df.columns:
        # support Ukrainian column name
        df['datetime'] = pd.to_datetime(df['дата'], errors='coerce')
    else:
        st.error("CSV має містити колонку 'datetime' або 'дата'")
        return None
    # clean numeric columns
    for col in ['views','перегляди']:
        if col in df.columns and 'views' not in df.columns:
            df['views'] = pd.to_numeric(df[col], errors='coerce')
    for col in ['reactions','реакції','реакції_count']:
        if col in df.columns and 'reactions' not in df.columns:
            df['reactions'] = pd.to_numeric(df[col], errors='coerce')
    # ensure columns exist
    if 'views' not in df.columns or 'reactions' not in df.columns:
        st.error("CSV має містити колонки для переглядів та реакцій (views, reactions або українські назви).")
        return None
    df = df.dropna(subset=['datetime','views','reactions']).copy()
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['weekday'] = df['datetime'].dt.day_name(locale='en_US')
    df['engagement_rate'] = df['reactions'] / df['views']
    return df

df = load_data(uploaded)

if df is None:
    st.stop()

st.sidebar.header("Фільтри")
min_date = df['datetime'].min().date()
max_date = df['datetime'].max().date()
date_range = st.sidebar.date_input("Дата (діапазон)", [min_date, max_date])

# filter by date
if len(date_range) == 2:
    start, end = date_range
    df = df[(df['datetime'].dt.date >= start) & (df['datetime'].dt.date <= end)]

# Overview metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Постів", len(df))
col2.metric("Середні перегляди", int(df['views'].mean()))
col3.metric("Середні реакції", int(df['reactions'].mean()))
col4.metric("Середній ER", f"{df['engagement_rate'].mean()*100:.2f}%")

st.markdown("### Графік активності — кількість постів та середні перегляди за датою")
posts_per_day = df.groupby('date').size().reset_index(name='posts')
views_per_day = df.groupby('date')['views'].mean().reset_index(name='avg_views')
merged = posts_per_day.merge(views_per_day, on='date')
merged['date'] = pd.to_datetime(merged['date'])

chart_posts = alt.Chart(merged).mark_bar(opacity=0.6).encode(
    x='date:T',
    y='posts:Q',
    tooltip=['date:T','posts:Q','avg_views:Q']
).properties(height=250, width=700)

chart_views = alt.Chart(merged).mark_line(point=True).encode(
    x='date:T',
    y='avg_views:Q',
    tooltip=['date:T','avg_views:Q']
).properties(height=250, width=700)

st.altair_chart((chart_posts + chart_views).resolve_scale(y='independent'), use_container_width=True)

st.markdown("### Коефіцієнти залучення (Engagement Rate)")
er_stats = df['engagement_rate'].describe()
st.write(er_stats.apply(lambda x: f"{x:.4f}" if isinstance(x, float) else x))

st.markdown("#### Розподіл ER за постами")
hist = alt.Chart(df).mark_bar().encode(
    alt.X('engagement_rate:Q', bin=alt.Bin(maxbins=30)),
    y='count()'
).properties(height=250)
st.altair_chart(hist, use_container_width=True)

st.markdown("### Найефективніший час для публікацій (по середніх переглядах і ER)")

# Heatmap: hour vs weekday with average views
pivot_views = df.pivot_table(index='hour', columns='weekday', values='views', aggfunc='mean').fillna(0)
# Reorder weekdays from Monday to Sunday
weekday_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
# prepare dataframe for heatmap
hm_data = df.groupby(['hour','weekday'])['views'].mean().reset_index()
hm_data['weekday'] = pd.Categorical(hm_data['weekday'], categories=weekday_order, ordered=True)
hm_data = hm_data.sort_values(['hour','weekday'])

heat = alt.Chart(hm_data).mark_rect().encode(
    x=alt.X('weekday:O', sort=weekday_order),
    y=alt.Y('hour:O'),
    color='views:Q',
    tooltip=['hour','weekday','views']
).properties(height=300)
st.altair_chart(heat, use_container_width=True)

# Best hour by avg views and by avg ER
hour_stats = df.groupby('hour').agg(avg_views=('views','mean'), avg_er=('engagement_rate','mean'), posts=('views','size')).reset_index()
best_by_views = hour_stats.sort_values('avg_views', ascending=False).iloc[0]
best_by_er = hour_stats.sort_values('avg_er', ascending=False).iloc[0]

col1, col2 = st.columns(2)
col1.metric("Найкраща година — по середніх переглядах", f"{int(best_by_views['hour'])}:00", f"avg views: {int(best_by_views['avg_views'])}")
col2.metric("Найкраща година — по середньому ER", f"{int(best_by_er['hour'])}:00", f"avg ER: {best_by_er['avg_er']*100:.2f}%")

st.markdown("### Деталі — таблиця постів")
st.dataframe(df.sort_values('datetime', ascending=False).reset_index(drop=True))

st.markdown("### Поради (автоматично згідно з даними)")
advice = []
if best_by_views['hour'] == best_by_er['hour']:
    advice.append(f"Оптимальний час публікацій — приблизно {int(best_by_views['hour'])}:00 (високі перегляди і ER).")
else:
    advice.append(f"Найбільше переглядів — о {int(best_by_views['hour'])}:00, найвищий ER — о {int(best_by_er['hour'])}:00. Розгляньте публікації в обидва інтервали залежно від мети: охоплення vs залучення.")

if hour_stats['posts'].max() < 3:
    advice.append("Даних небагато для деяких годин — корисно мати більше постів у різні години для точнішого визначення патернів.")

for a in advice:
    st.write("- " + a)

st.markdown("---")
st.write("Файл sample_posts.csv додається з цим додатком. Щоб запустити локально:")
st.code("streamlit run app.py", language='bash')
