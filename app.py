import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Аналіз Telegram-каналу", layout="wide")
st.title("📊 Аналіз Telegram-каналу")

def load_data(uploaded_file):
    # Читання CSV
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_csv("sample_posts.csv")
    except Exception as e:
        st.error(f"❌ Помилка при читанні файлу: {e}")
        return None

    # Перевірка наявності колонок
    required_cols = ['datetime', 'views', 'reactions']
    if not all(col in df.columns for col in required_cols):
        st.error("❌ CSV має містити колонки: datetime, views, reactions")
        return None

    # Примусове перетворення типів
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df['views'] = pd.to_numeric(df['views'], errors='coerce')
    df['reactions'] = pd.to_numeric(df['reactions'], errors='coerce')

    # Видалення рядків з некоректними даними
    df = df.dropna(subset=['datetime', 'views', 'reactions']).copy()

    # Додаткові колонки
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    days_uk = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота', 'Неділя']
    df['weekday'] = df['datetime'].dt.weekday.map(lambda x: days_uk[x])
    df['engagement'] = df['reactions'] / df['views']

    return df

uploaded = st.file_uploader("📥 Завантаж CSV", type=["csv"], key="file_uploader")
if uploaded is not None:
    st.success(f"✅ Файл {uploaded.name} завантажено!")
else:
    st.info("ℹ️ Використовується sample_posts.csv")

df = load_data(uploaded)

if df is not None and not df.empty:
    st.write("### Дані:")
    st.dataframe(df.head())

    # Графік активності
    st.write("### 📅 Графік активності")
    activity = df.groupby('date').agg({'views': 'mean', 'reactions': 'sum'}).reset_index()
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(activity['date'], activity['views'], marker='o', linewidth=1.5, label='Середні перегляди')
    ax.set_xlabel('Дата', fontsize=9)
    ax.set_ylabel('Перегляди', fontsize=9)
    ax.tick_params(axis='both', labelsize=8)
    ax.legend(fontsize=8)
    st.pyplot(fig, clear_figure=True, key="activity_plot")

    # Коефіцієнти залучення
    st.write("### 💬 Коефіцієнт залучення")
    col1, col2, col3 = st.columns(3)
    col1.metric("Середній ER", f"{df['engagement'].mean():.2%}", key="er_mean")
    col2.metric("Максимальний ER", f"{df['engagement'].max():.2%}", key="er_max")
    col3.metric("Мінімальний ER", f"{df['engagement'].min():.2%}", key="er_min")

    # Найефективніший час
    st.write("### ⏰ Найефективніший час для публікацій")
    time_eff = df.groupby('hour').agg({'views':'mean', 'engagement':'mean'}).reset_index()
    best_hour_views = int(time_eff.loc[time_eff['views'].idxmax(), 'hour'])
    best_hour_er = int(time_eff.loc[time_eff['engagement'].idxmax(), 'hour'])
    st.info(f"Найкраща година за переглядами: **{best_hour_views}:00**")
    st.info(f"Найкраща година за залученням: **{best_hour_er}:00**")

    st.success("✅ Аналіз завершено!")
else:
    st.warning("⚠️ Дані відсутні або некоректні.")
