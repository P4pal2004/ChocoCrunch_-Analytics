# app.py
import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

# ----------------------------------------------
# 🍫 ChocoCrunch Analytics Streamlit Dashboard
# ----------------------------------------------
st.set_page_config(page_title="ChocoCrunch Analytics", layout="wide")
st.title("🍫 ChocoCrunch Analytics Dashboard")

# Connect to SQLite database
conn = sqlite3.connect("chocolates.db")

# Sidebar: SQL Query Selector
st.sidebar.header("SQL Query Explorer")
query_options = [
    # Product Info Queries
    "Count products per brand",
    "Count unique products per brand",
    "Top 5 brands by product count",
    "Products with missing product name",
    "Number of unique brands",
    "Products with code starting with '3'",
    # Nutrient Info Queries
    "Top 10 products with highest energy-kcal_value",
    "Average sugars_value per nova-group",
    "Count products with fat_value > 20g",
    "Average carbohydrates_value per product",
    "Products with sodium_value > 1g",
    "Count products with non-zero fruits-vegetables-nuts content",
    "Products with energy-kcal_value > 500",
    # Derived Metrics Queries
    "Count products per calorie_category",
    "Count of High Sugar products",
    "Average sugar_to_carb_ratio for High Calorie products",
    "Products both High Calorie & High Sugar",
    "Number of ultra-processed products",
    "Products with sugar_to_carb_ratio > 0.7",
    "Average sugar_to_carb_ratio per calorie_category",
    # Join Queries
    "Top 5 brands with most High Calorie products",
    "Average energy-kcal_value per calorie_category",
    "Count of ultra-processed products per brand",
    "High Sugar & High Calorie products with brand",
    "Average sugar content per brand for ultra-processed products",
    "Products with fruits/vegetables/nuts by calorie_category",
    "Top 5 products by sugar_to_carb_ratio with calorie & sugar category"
]

selected_query = st.sidebar.selectbox("Select a SQL query", query_options)

# Dictionary: map query names to SQL
queries = {
    # Product Info
    "Count products per brand": "SELECT brand, COUNT(*) AS product_count FROM product_info GROUP BY brand ORDER BY product_count DESC",
    "Count unique products per brand": "SELECT brand, COUNT(DISTINCT product_name) AS unique_products FROM product_info GROUP BY brand ORDER BY unique_products DESC",
    "Top 5 brands by product count": "SELECT brand, COUNT(*) AS product_count FROM product_info GROUP BY brand ORDER BY product_count DESC LIMIT 5",
    "Products with missing product name": "SELECT * FROM product_info WHERE product_name IS NULL OR product_name = ''",
    "Number of unique brands": "SELECT COUNT(DISTINCT brand) AS unique_brands FROM product_info",
    "Products with code starting with '3'": "SELECT * FROM product_info WHERE product_code LIKE '3%'",
    # Nutrient Info
    "Top 10 products with highest energy-kcal_value": "SELECT product_code, energy_kcal_value FROM nutrient_info ORDER BY energy_kcal_value DESC LIMIT 10",
    "Average sugars_value per nova-group": "SELECT nova_group, AVG(sugars_value) AS avg_sugars FROM nutrient_info GROUP BY nova_group",
    "Count products with fat_value > 20g": "SELECT COUNT(*) AS high_fat_products FROM nutrient_info WHERE fat_value > 20",
    "Average carbohydrates_value per product": "SELECT AVG(carbohydrates_value) AS avg_carbohydrates FROM nutrient_info",
    "Products with sodium_value > 1g": "SELECT product_code, sodium_value FROM nutrient_info WHERE sodium_value > 1",
    "Count products with non-zero fruits-vegetables-nuts content": "SELECT COUNT(*) AS products_with_fvn FROM nutrient_info WHERE fruits_vegetables_nuts > 0",
    "Products with energy-kcal_value > 500": "SELECT product_code, energy_kcal_value FROM nutrient_info WHERE energy_kcal_value > 500",
    # Derived Metrics
    "Count products per calorie_category": "SELECT calorie_category, COUNT(*) AS count_products FROM derived_metrics GROUP BY calorie_category",
    "Count of High Sugar products": "SELECT COUNT(*) AS high_sugar_count FROM derived_metrics WHERE sugar_category = 'High Sugar'",
    "Average sugar_to_carb_ratio for High Calorie products": "SELECT AVG(sugar_to_carb_ratio) AS avg_ratio FROM derived_metrics WHERE calorie_category = 'High'",
    "Products both High Calorie & High Sugar": "SELECT product_code, calorie_category, sugar_category FROM derived_metrics WHERE calorie_category = 'High' AND sugar_category = 'High Sugar'",
    "Number of ultra-processed products": "SELECT COUNT(*) AS ultra_processed_count FROM derived_metrics WHERE is_ultra_processed = 'Yes'",
    "Products with sugar_to_carb_ratio > 0.7": "SELECT product_code, sugar_to_carb_ratio FROM derived_metrics WHERE sugar_to_carb_ratio > 0.7",
    "Average sugar_to_carb_ratio per calorie_category": "SELECT calorie_category, AVG(sugar_to_carb_ratio) AS avg_ratio FROM derived_metrics GROUP BY calorie_category",
    # Join Queries
    "Top 5 brands with most High Calorie products": "SELECT p.brand, COUNT(*) AS high_cal_count FROM derived_metrics d JOIN product_info p ON d.product_code = p.product_code WHERE d.calorie_category = 'High' GROUP BY p.brand ORDER BY high_cal_count DESC LIMIT 5",
    "Average energy-kcal_value per calorie_category": "SELECT d.calorie_category, AVG(n.energy_kcal_value) AS avg_energy FROM derived_metrics d JOIN nutrient_info n ON d.product_code = n.product_code GROUP BY d.calorie_category",
    "Count of ultra-processed products per brand": "SELECT p.brand, COUNT(*) AS ultra_count FROM derived_metrics d JOIN product_info p ON d.product_code = p.product_code WHERE d.is_ultra_processed = 'Yes' GROUP BY p.brand ORDER BY ultra_count DESC",
    "High Sugar & High Calorie products with brand": "SELECT p.brand, d.product_code, d.calorie_category, d.sugar_category FROM derived_metrics d JOIN product_info p ON d.product_code = p.product_code WHERE d.calorie_category = 'High' AND d.sugar_category = 'High Sugar'",
    "Average sugar content per brand for ultra-processed products": "SELECT p.brand, AVG(n.sugars_value) AS avg_sugar FROM derived_metrics d JOIN product_info p ON d.product_code = p.product_code JOIN nutrient_info n ON d.product_code = n.product_code WHERE d.is_ultra_processed = 'Yes' GROUP BY p.brand ORDER BY avg_sugar DESC",
    "Products with fruits/vegetables/nuts by calorie_category": "SELECT d.calorie_category, COUNT(*) AS count_fvn FROM derived_metrics d JOIN nutrient_info n ON d.product_code = n.product_code WHERE n.fruits_vegetables_nuts > 0 GROUP BY d.calorie_category",
    "Top 5 products by sugar_to_carb_ratio with calorie & sugar category": "SELECT d.product_code, d.sugar_to_carb_ratio, d.calorie_category, d.sugar_category FROM derived_metrics d ORDER BY d.sugar_to_carb_ratio DESC LIMIT 5"
}

# Run the selected query
df_query = pd.read_sql_query(queries[selected_query], conn)
st.subheader(f"Query: {selected_query}")
st.dataframe(df_query)

# -------------------------------
# Sample EDA Visualizations
# -------------------------------
st.subheader("🍫 Sample EDA Visualizations")

# 1️⃣ Calorie Category Distribution
st.write("**Calorie Category Distribution**")
df_calories = pd.read_sql_query("SELECT calorie_category, COUNT(*) AS count FROM derived_metrics GROUP BY calorie_category", conn)
st.bar_chart(df_calories.set_index('calorie_category'))

# 2️⃣ Nova Group Distribution
st.write("**NOVA Group Distribution**")
df_nova = pd.read_sql_query("SELECT nova_group, COUNT(*) AS count FROM nutrient_info GROUP BY nova_group", conn)
fig, ax = plt.subplots()
sns.barplot(x='nova_group', y='count', data=df_nova, palette="Set2", ax=ax)
st.pyplot(fig)

# 3️⃣ Top 10 Brands by Average Energy
st.write("**Top 10 Brands by Average Energy (kcal)**")
query = """
SELECT p.brand, AVG(n.energy_kcal_value) AS avg_energy
FROM product_info p
JOIN nutrient_info n ON p.product_code = n.product_code
GROUP BY p.brand
ORDER BY avg_energy DESC
LIMIT 10
"""
df_top_brands = pd.read_sql_query(query, conn)
st.bar_chart(df_top_brands.set_index('brand'))

# 4️⃣ Scatter Plot: Calories vs Sugar
st.write("**Calories vs Sugar**")
df_scatter = pd.read_sql_query("SELECT n.energy_kcal_value, n.sugars_value FROM nutrient_info n WHERE n.energy_kcal_value IS NOT NULL AND n.sugars_value IS NOT NULL", conn)
fig, ax = plt.subplots()
sns.scatterplot(x='energy_kcal_value', y='sugars_value', data=df_scatter, color='chocolate')
st.pyplot(fig)

# 5️⃣ Boxplot: Sugar to Carb Ratio by Calorie Category
st.write("**Sugar to Carb Ratio by Calorie Category**")
df_box = pd.read_sql_query("SELECT calorie_category, sugar_to_carb_ratio FROM derived_metrics WHERE sugar_to_carb_ratio IS NOT NULL", conn)
fig, ax = plt.subplots()
sns.boxplot(x='calorie_category', y='sugar_to_carb_ratio', data=df_box, palette="Set3", ax=ax)
st.pyplot(fig)
# -------------------------------------------------
# 🍩 Additional Visualizations for Better Insights
# -------------------------------------------------
st.subheader("🍩 Additional Visualizations & Insights")

# ✅ 1️⃣ Pie Chart - Calorie Category Share
st.write("### Calorie Category Distribution (Pie Chart)")
df_calorie_pie = pd.read_sql_query(
    "SELECT calorie_category, COUNT(*) AS count FROM derived_metrics GROUP BY calorie_category", conn
)
fig1, ax1 = plt.subplots()
ax1.pie(df_calorie_pie['count'], labels=df_calorie_pie['calorie_category'], autopct='%1.1f%%', startangle=90)
ax1.axis('equal')
st.pyplot(fig1)

# ✅ 2️⃣ Heatmap - Correlation between Calories, Sugar, Fat
st.write("### Correlation between Energy, Sugars, and Fat")
df_corr = pd.read_sql_query(
    "SELECT energy_kcal_value, sugars_value, fat_value FROM nutrient_info WHERE energy_kcal_value IS NOT NULL AND sugars_value IS NOT NULL AND fat_value IS NOT NULL",
    conn
)
corr = df_corr.corr()
fig2, ax2 = plt.subplots()
sns.heatmap(corr, annot=True, cmap='YlOrBr', ax=ax2)
st.pyplot(fig2)

# ✅ 3️⃣ KPI Cards - Quick Nutritional Overview
st.write("### 🍫 Key Nutritional Metrics")
col1, col2, col3 = st.columns(3)
df_kpi = pd.read_sql_query("SELECT AVG(energy_kcal_value) as avg_cal, AVG(sugars_value) as avg_sugar, COUNT(*) as total_products FROM nutrient_info", conn)

col1.metric("🔥 Average Calories (kcal)", f"{df_kpi['avg_cal'][0]:.1f}")
col2.metric("🍬 Average Sugar (g)", f"{df_kpi['avg_sugar'][0]:.1f}")
col3.metric("📦 Total Products", f"{int(df_kpi['total_products'][0])}")

# -------------------------------------------------
# 💡 Insight & Findings Summary
# -------------------------------------------------
st.subheader("💡 Insights & Findings Summary")
st.markdown("""
- **High Calorie & High Sugar overlap:** Most products classified as *High Calorie* also have a *High Sugar* ratio, indicating potential health risks.  
- **Brand variation:** Top 5 brands dominate product count, but show wide variation in sugar-to-carb ratio.  
- **Energy vs Sugar correlation:** Strong positive correlation seen between calorie and sugar values, confirming sugar’s major role in calorie contribution.  
- **Ultra-processed alert:** Brands with higher NOVA group values tend to have higher sugar content and more additives.  
- **Healthier options:** A few mid-calorie products with moderate sugar ratios could represent the healthiest segment of the dataset.  
""")
# Close connection
conn.close()
