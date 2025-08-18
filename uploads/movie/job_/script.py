import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json

def solve_questions_and_save():
    try:
        # Load the dataset from the specified path
        file_path = 'uploads/f93b4f21-13c3-4143-8e0f-03c55c27bcfd/highest_grossing_films.csv'
        df = pd.read_csv(file_path)

        # Clean the 'Worldwide gross' column by removing non-digit characters and converting to a numeric type
        df['Worldwide gross'] = df['Worldwide gross'].astype(str).str.replace(r'[^\d]', '', regex=True)
        df['Worldwide gross'] = pd.to_numeric(df['Worldwide gross'], errors='coerce')
        df.dropna(subset=['Worldwide gross'], inplace=True)

        # Ensure required columns are of a numeric type, coercing errors to NaN
        for col in ['Year', 'Rank', 'Peak']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Year', 'Rank', 'Peak'], inplace=True)

        # Question 1: How many $2 bn movies were released before 2000?
        movies_2bn_before_2000 = df[(df['Worldwide gross'] >= 2_000_000_000) & (df['Year'] < 2000)]
        answer1 = len(movies_2bn_before_2000)

        # Question 2: Which is the earliest film that grossed over $1.5 bn?
        movies_1_5bn = df[df['Worldwide gross'] >= 1_500_000_000]
        earliest_film = movies_1_5bn.loc[movies_1_5bn['Year'].idxmin()]
        answer2 = earliest_film['Title']

        # Question 3: What's the correlation between the Rank and Peak?
        correlation = df['Rank'].corr(df['Peak'])
        answer3 = correlation

        # Question 4: Draw a scatterplot of Rank and Peak with a regression line
        plt.figure(figsize=(10, 6))
        sns.regplot(x='Rank', y='Peak', data=df, scatter_kws={'alpha': 0.6}, line_kws={'color': 'red', 'linestyle': '--'})
        plt.title('Rank vs. Peak of Highest-Grossing Films')
        plt.xlabel('Rank')
        plt.ylabel('Peak')
        plt.grid(True)
        
        # Save the plot to a memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        buf.seek(0)
        
        # Encode the image in base64 to create a data URI
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        answer4 = f"data:image/png;base64,{image_base64}"

        # Consolidate answers and save to the final result file
        final_answers = [answer1, answer2, answer3, answer4]
        result_path = 'uploads/f93b4f21-13c3-4143-8e0f-03c55c27bcfd/result.json'
        with open(result_path, 'w') as f:
            json.dump(final_answers, f)
            
        print(f"Successfully generated answers and saved to {result_path}")

    except Exception as e:
        # Print a descriptive error message if the process fails
        print(f"An error occurred during analysis: {e}")

solve_questions_and_save()
