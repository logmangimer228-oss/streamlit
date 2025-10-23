import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Аналіз Telegram-каналу", layout="wide")

st.title("📊 Аналіз Telegram-каналу")

# --- Завантаження даних ---
def load_data(uploaded_file):
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, parse_dates=['datetime'])
        else:
            df = pd.read_csv("sample_posts.csv", parse_dates=['datetime'])
    except Exception as e:
        st.error(f"❌ Помилка при зчитуванні файлу: {e}")
        return None

    # Перевірка структури CSV
    required_cols = {'datetime', 'views', 'reactions'}
    if not required_cols.issubset(df.columns):
        st.error("❌ Невірна структура CSV! Має бути: datetime, views, reactions")
        return None

    # Обробка даних
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    days_uk = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота', 'Неділя']
    df['weekday'] = df['datetime'].dt.weekday.map(lambda x: days_uk[x])
    df['engagement'] = df['reactions'] / df['views']

    return df


# --- Завантаження файлу ---
uploaded = st.file_uploader("📥 Завантаж CSV-файл з постами", type=["csv"], key="file_uploader")

if uploaded is not None:
    st.success(f"✅ Файл **{uploaded.name}** завантажено!")
else:
    st.info("ℹ️ Використовується вбудований приклад sample_posts.csv")

df = load_data(uploaded)

if df is not None:
    st.write("### Дані:")
    st.dataframe(df.head())

    # --- Графік активності ---
    st.write("### 📅 Графік активності")
    activity = df.groupby('date').agg({'views': 'mean', 'reactions': 'sum'}).reset_index()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(activity['date'], activity['views'], marker='o', linewidth=1.5, label='Середні перегляди')
    ax.set_xlabel('Дата', fontsize=9)
    ax.set_ylabel('Перегляди', fontsize=9)
    ax.legend(fontsize=8)
    ax.tick_params(axis='both', labelsize=8)
    st.pyplot(fig, clear_figure=True, key="activity_plot")

    # --- Коефіцієнти залучення ---
    st.write("### 💬 Коефіцієнт залучення")
    er_mean = df['engagement'].mean()
    er_max = df['engagement'].max()
    er_min = df['engagement'].min()

    col1, col2, col3 = st.columns(3)
    col1.metric("Середній ER", f"{er_mean:.2%}", key="er_mean")
    col2.metric("Максимальний ER", f"{er_max:.2%}", key="er_max")
    col3.metric("Мінімальний ER", f"{er_min:.2%}", key="er_min")

    # --- Найефективніший час ---
    st.write("### ⏰ Найефективніший час для публікацій")
    time_eff = df.groupby('hour').agg({'views': 'mean', 'engagement': 'mean'}).reset_index()
    best_hour_views = time_eff.loc[time_eff['views'].idxmax(), 'hour']
    best_hour_er = time_eff.loc[time_eff['engagement'].idxmax(), 'hour']

    st.info(f"Найкраща година за переглядами: **{best_hour_views}:00**", icon="🕒")
    st.info(f"Найкраща година за залученням: **{best_hour_er}:00**", icon="🔥")

    st.success("✅ Аналіз завершено. Дані успішно оброблено!")
else:
    st.warning("⚠️ Дані не завантажені або мають помилковий формат.")
