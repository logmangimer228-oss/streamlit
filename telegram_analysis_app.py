import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO

st.set_page_config(page_title="Аналіз Telegram-каналу", layout="wide")

st.title("📊 Аналіз Telegram-каналу")

# --- Завантаження даних ---
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, parse_dates=['datetime'])
    else:
        df = pd.read_csv("sample_posts.csv", parse_dates=['datetime'])

    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['weekday'] = df['datetime'].dt.day_name()

    ukrainian_days = {
        'Monday': 'Понеділок',
        'Tuesday': 'Вівторок',
        'Wednesday': 'Середа',
        'Thursday': 'Четвер',
        'Friday': 'П’ятниця',
        'Saturday': 'Субота',
        'Sunday': 'Неділя'
    }
    df['weekday'] = df['weekday'].map(ukrainian_days)

    df['engagement'] = df['reactions'] / df['views']
    return df

uploaded = st.file_uploader("📥 Завантаж CSV-файл з постами", type=["csv"])
df = load_data(uploaded)

st.write("### Дані:")
st.dataframe(df.head())

# --- Графік активності ---
activity = df.groupby('date').agg({'views': 'mean', 'reactions': 'sum'}).reset_index()
st.write("### 📅 Графік активності")
fig, ax = plt.subplots()
ax.plot(activity['date'], activity['views'], label='Середні перегляди')
ax.set_xlabel('Дата')
ax.set_ylabel('Перегляди')
ax.legend()
st.pyplot(fig)

# --- Коефіцієнти залучення ---
er_mean = df['engagement'].mean()
er_max = df['engagement'].max()
er_min = df['engagement'].min()

st.write("### 💬 Коефіцієнт залучення")
st.metric("Середній ER", f"{er_mean:.2%}")
st.metric("Максимальний ER", f"{er_max:.2%}")
st.metric("Мінімальний ER", f"{er_min:.2%}")

# --- Найефективніший час ---
time_eff = df.groupby('hour').agg({'views': 'mean', 'engagement': 'mean'}).reset_index()
best_hour_views = time_eff.loc[time_eff['views'].idxmax(), 'hour']
best_hour_er = time_eff.loc[time_eff['engagement'].idxmax(), 'hour']

st.write("### ⏰ Найефективніший час для публікацій")
st.info(f"Найкраща година за переглядами: **{best_hour_views}:00**")
st.info(f"Найкраща година за залученням: **{best_hour_er}:00**")

# --- Теплова карта ---
st.write("### 🔥 Теплова карта активності")
pivot = df.pivot_table(values='views', index='weekday', columns='hour', aggfunc='mean')
fig, ax = plt.subplots(figsize=(10,5))
sns.heatmap(pivot, cmap='YlGnBu', ax=ax)
st.pyplot(fig)

st.success("✅ Аналіз завершено. Дані успішно оброблено!")