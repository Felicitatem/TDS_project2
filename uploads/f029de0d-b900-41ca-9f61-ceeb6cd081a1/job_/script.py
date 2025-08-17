import duckdb
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json
import numpy as np

def execute_query(query):
    """Connects to DuckDB and executes a query, returning a DataFrame."""
    con = duckdb.connect(database=':memory:', read_only=False)
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL parquet; LOAD parquet;")
    con.execute("SET s3_region='ap-south-1';")
    return con.execute(query).fetchdf()

# --- Step 1: Find the high court that disposed the most cases from 2019 - 2022 ---
query1 = """
    SELECT court, COUNT(*) as case_count
    FROM read_parquet('s3://indian-high-court-judgments/metadata/parquet/year=*/court=*/bench=*/metadata.parquet')
    WHERE year BETWEEN 2019 AND 2022
    GROUP BY court
    ORDER BY case_count DESC
    LIMIT 1;
"""
df_q1 = execute_query(query1)
most_active_court = df_q1['court'].iloc[0]

with open('uploads/f029de0d-b900-41ca-9f61-ceeb6cd081a1/metadata.txt', 'w') as f:
    f.write(f"Question 1 Result: The high court that disposed the most cases from 2019-2022 is {most_active_court}\n\n")

# --- Step 2 & 3: Regression analysis and plotting for court='33_10' ---
query2 = """
    SELECT year, decision_date, date_of_registration 
    FROM read_parquet('s3://indian-high-court-judgments/metadata/parquet/year=*/court=*/bench=*/metadata.parquet') 
    WHERE court = '33_10';
"""
df_q2 = execute_query(query2)

# --- Data Cleaning and Preparation ---
df_q2['decision_date'] = pd.to_datetime(df_q2['decision_date'], errors='coerce')
df_q2['date_of_registration'] = pd.to_datetime(df_q2['date_of_registration'], format='%d-%m-%Y', errors='coerce')
df_q2.dropna(subset=['decision_date', 'date_of_registration'], inplace=True)
df_q2['delay_days'] = (df_q2['decision_date'] - df_q2['date_of_registration']).dt.days

# Remove illogical data points
df_q2 = df_q2[df_q2['delay_days'] >= 0]

with open('uploads/f029de0d-b900-41ca-9f61-ceeb6cd081a1/metadata.txt', 'a') as f:
    f.write(f"Data for court 33_10 after cleaning:\n{df_q2.head().to_string()}\n\n")

# --- Calculate Regression Slope ---
slope, intercept, r_value, p_value, std_err = stats.linregress(df_q2['year'], df_q2['delay_days'])
regression_slope = slope

with open('uploads/f029de0d-b900-41ca-9f61-ceeb6cd081a1/metadata.txt', 'a') as f:
    f.write(f"Question 2 Result: The regression slope is {regression_slope}\n\n")

# --- Generate Plot ---
plt.figure(figsize=(8, 5))
sns.regplot(data=df_q2, x='year', y='delay_days', \
            scatter_kws={'alpha':0.1, 's':10}, \
            line_kws={'color':'red'})
plt.title('Delay from Registration to Decision by Year (Court 33_10)')
plt.xlabel('Year')
plt.ylabel('Delay (Days)')
plt.tight_layout()

# Save plot to buffer and encode
buf = io.BytesIO()
plt.savefig(buf, format='webp')
plt.close()
buf.seek(0)
img_base64 = base64.b64encode(buf.read()).decode('utf-8')
img_uri = f"data:image/webp;base64,{img_base64}"


# --- Final Assembly and Output ---
final_answer = {
  "Which high court disposed the most cases from 2019 - 2022?": most_active_court,
  "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": regression_slope,
  "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters": img_uri
}

with open('uploads/f029de0d-b900-41ca-9f61-ceeb6cd081a1/result.json', 'w') as f:
    json.dump(final_answer, f, indent=2)

print("Processing complete. Final answer saved to result.json")