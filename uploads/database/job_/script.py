import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json

# --- Configuration ---
DB_FILE = 'uploads/ca056cee-a218-4272-8594-ef5c1a80f305/retail.db'
RESULT_FILE = 'uploads/ca056cee-a218-4272-8594-ef5c1a80f305/result.json'
METADATA_FILE = 'uploads/ca056cee-a218-4272-8594-ef5c1a80f305/metadata.txt'

def solve_questions():
    """Connects to the database, solves all three questions, and saves the result."""
    results = []
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)

        # --- Question 1: Total sales quantity for each product ---
        query1 = """
            SELECT p.name, SUM(s.quantity)
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.name
            ORDER BY p.name;
        """
        df1 = pd.read_sql_query(query1, conn)
        product_sales = df1.set_index('name').to_dict()['SUM(s.quantity)']
        results.append(product_sales)
        with open(METADATA_FILE, 'a') as f:
            f.write('\n--- Question 1: Product Sales Quantity ---\n')
            f.write(json.dumps(product_sales, indent=2))

        # --- Question 2: Top 3 categories by total revenue ---
        query2 = """
            SELECT p.category, SUM(s.quantity * p.price) as total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY p.category
            ORDER BY total_revenue DESC
            LIMIT 3;
        """
        df2 = pd.read_sql_query(query2, conn)
        top_categories = df2['category'].tolist()
        results.append(top_categories)
        with open(METADATA_FILE, 'a') as f:
            f.write('\n\n--- Question 2: Top 3 Categories by Revenue ---\n')
            f.write(json.dumps(top_categories, indent=2))


        # --- Question 3: Monthly total sales bar chart (base64) ---
        query3 = """
            SELECT strftime('%Y-%m', sale_date) as month,
                   SUM(s.quantity * p.price) as total_sales
            FROM sales s
            JOIN products p ON s.product_id = p.id
            GROUP BY month
            ORDER BY month;
        """
        df3 = pd.read_sql_query(query3, conn)
        
        plt.figure(figsize=(10, 6))
        plt.bar(df3['month'], df3['total_sales'], color='skyblue')
        plt.title('Monthly Total Sales')
        plt.xlabel('Month')
        plt.ylabel('Total Sales')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        results.append(image_base64)
        with open(METADATA_FILE, 'a') as f:
            f.write('\n\n--- Question 3: Monthly Sales Chart ---\n')
            f.write('Base64 chart generated.')

        # --- Save Final Result ---
        with open(RESULT_FILE, 'w') as f:
            json.dump(results, f)
        
        print(f"Results saved to {RESULT_FILE}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# --- Execute the function ---
solve_questions()