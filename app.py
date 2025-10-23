import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Аналіз Telegram-каналу", layout="wide")
st.title("📊 Аналіз Telegram-каналу")

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, parse_dates=['datetime'])
    else:
        df = pd.read_csv("sample_posts.csv", parse_dates=['datetime'])

    df['views'] = pd.to_numeric(df['views'], errors='coerce')
    df['reactions'] = pd.to_numeric(df['reactions'], errors='coerce')
    df = df.dropna(subset=['datetime', 'views', 'reactions'])

    df['date'] = pd.to_datetime(df['datetime'].dt.date)  # важливо: datetime для сортування
    df['hour'] = df['datetime'].dt.hour

    days_uk = ['Понеділок','Вівторок','Середа','Четвер','П’ятниця','Субота','Неділя']
    df['weekday'] = df['datetime'].dt.weekday.map(lambda x: days_uk[x])
    df['engagement'] = df['reactions'] / df['views']

    return df

uploaded = st.file_uploader("📥 Завантаж CSV-файл з постами", type=["csv"])
df = load_data(uploaded)

if df is not None and not df.empty:
    st.write("### Дані:")
    st.dataframe(df.sort_values('datetime'))

    st.write("### 📅 Графік активності")
    activity = df.groupby('date').agg({'views':'mean','reactions':'sum'}).reset_index()
    activity = activity.sort_values('date')  # щоб дати йшли по порядку

    fig, ax = plt.subplots(figsize=(6,3))  # зменшений розмір
    ax.plot(activity['date'], activity['views'], marker='o', linewidth=1.5, label='Середні перегляди')
    ax.set_xlabel('Дата', fontsize=8)
    ax.set_ylabel('Перегляди', fontsize=8)
    ax.legend(fontsize=7)
    ax.tick_params(axis='both', labelsize=7, rotation=45)
    st.pyplot(fig, clear_figure=True)

    er_mean = df['engagement'].mean()
    er_max = df['engagement'].max()
    er_min = df['engagement'].min()

    st.write("### 💬 Коефіцієнт залучення")
    col1, col2, col3 = st.columns(3)
    col1.metric("Середній ER", f"{er_mean:.2%}")
    col2.metric("Максимальний ER", f"{er_max:.2%}")
    col3.metric("Мінімальний ER", f"{er_min:.2%}")

    time_eff = df.groupby('hour').agg({'views':'mean','engagement':'mean'}).reset_index()
    best_hour_views = int(time_eff.loc[time_eff['views'].idxmax(),'hour'])
    best_hour_er = int(time_eff.loc[time_eff['engagement'].idxmax(),'hour'])

    st.write("### ⏰ Найефективніший час для публікацій")
    st.info(f"Найкраща година за переглядами: **{best_hour_views}:00**")
    st.info(f"Найкраща година за залученням: **{best_hour_er}:00**")

    st.success("✅ Аналіз завершено. Дані успішно оброблено!")
else:
    st.warning("⚠️ Дані відсутні або некоректні.")
