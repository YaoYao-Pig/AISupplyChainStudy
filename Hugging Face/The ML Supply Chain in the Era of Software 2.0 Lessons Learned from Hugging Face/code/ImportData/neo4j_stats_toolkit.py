
import pandas as pd
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import os

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "xxx"  # ← Replace with your password

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
out_dir = "neo4j_stats_output"
os.makedirs(out_dir, exist_ok=True)

def run_query(session, query):
    return pd.DataFrame([r.data() for r in session.run(query)])

def save_plot_bar(df, x, y, title, filename, xlabel="", ylabel="", horizontal=False):
    if df.empty:
        print(f"⚠️  Skipping plot: {filename} (no data)")
        return
    plt.figure(figsize=(10, 6))
    if horizontal:
        bars = plt.barh(df[x], df[y], color="#4C9F70")
        plt.xlabel(xlabel); plt.ylabel(ylabel)
        plt.gca().invert_yaxis()
    else:
        bars = plt.bar(df[x], df[y], color="#4C9F70")
        plt.xlabel(xlabel); plt.ylabel(ylabel)
    # Add value labels
    for bar in bars:
        if horizontal:
            plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                     f"{bar.get_width():.1f}", va='center', fontsize=9)
        else:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f"{bar.get_height():.1f}", ha='center', fontsize=9)
    plt.title(title, fontsize=14)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, filename))
    plt.close()

with driver.session() as session:
    print("📊 License distribution...")
    df1 = run_query(session, '''
        MATCH (m:Model)-[:HAS_LICENSE]->(l:License)
        RETURN l.name AS license, COUNT(m) AS count
        ORDER BY count DESC
    ''')
    df1.to_csv(f"{out_dir}/license_distribution.csv", index=False)
    save_plot_bar(df1, "license", "count", "License Distribution", "license_distribution.png", "License", "Model Count")

    print("📊 Longest inheritance chains...")
    df2 = run_query(session, '''
        MATCH path = (m:Model)-[:DERIVED_FROM*]->(:Model)
        RETURN m.name AS model, LENGTH(path) AS depth
        ORDER BY depth DESC
        LIMIT 10
    ''')
    df2.to_csv(f"{out_dir}/longest_chain.csv", index=False)
    save_plot_bar(df2, "model", "depth", "Top 10 Model Inheritance Depth", "longest_chain.png", "Model", "Depth", horizontal=True)

    print("📊 Avg inheritance depth by license type...")
    df3 = run_query(session, '''
        MATCH path = (m:Model)-[:DERIVED_FROM*]->(:Model),
              (m)-[:HAS_LICENSE]->(l:License)
        WHERE l.type IS NOT NULL
        RETURN l.type AS type, avg(length(path)) AS avg_depth
    ''')
    df3.to_csv(f"{out_dir}/license_type_avg_depth.csv", index=False)
    
    if not df3.empty:
        plt.figure(figsize=(10, 6))
        bars = plt.bar(df3["type"], df3["avg_depth"], color="#4C9F70")
        plt.xlabel("License Type")
        plt.ylabel("Avg Inheritance Depth")
        plt.title("Avg Inheritance Depth per License Type", fontsize=14)
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f"{bar.get_height():.1f}", ha='center', fontsize=9)
        max_val = int(df3["avg_depth"].max()) + 1
        plt.yticks(range(0, max_val + 1))
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, "license_type_avg_depth.png"))
        plt.close()
    else:
        print("⚠️  Skipping license type depth plot: no data")
    

    print("📊 Top 5 organizations by model count...")
    df4 = run_query(session, '''
        MATCH (m:Model)-[:OWNED_BY]->(o:Org)
        RETURN o.name AS org, COUNT(m) AS models
        ORDER BY models DESC
        LIMIT 5
    ''')
    df4.to_csv(f"{out_dir}/top_orgs_by_model_count.csv", index=False)
    save_plot_bar(df4, "org", "models", "Top 5 Organizations by Model Count", "top_orgs_by_model_count.png", "Organization", "Model Count")

print("✅ All stats completed. Charts and CSVs saved to neo4j_stats_output/")
