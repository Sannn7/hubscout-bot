"""
Export evaluation metrics to CSV for Power BI dashboard.
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def export_metrics_for_powerbi():
    """
    Export evaluation data in Power BI compatible format.
    """
    # Load evaluation results
    eval_files = list(Path("evaluation_results").glob("*.json"))
    
    all_queries = []
    
    for file in eval_files:
        with open(file) as f:
            data = json.load(f)
            for result in data["detailed_results"]:
                all_queries.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_queries)
    
    # Export for Power BI
    output_path = Path("powerbi_exports")
    output_path.mkdir(exist_ok=True)
    
    # Query-level metrics
    df.to_csv(output_path / "query_metrics.csv", index=False)
    
    # Daily aggregates
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily = df.groupby('date').agg({
        'time_to_answer': ['mean', 'median', 'count'],
        'precision_at_k': 'mean',
        'answer_length': 'mean'
    }).reset_index()
    daily.columns = ['date', 'avg_time', 'median_time', 'query_count', 'avg_precision', 'avg_answer_length']
    daily.to_csv(output_path / "daily_metrics.csv", index=False)
    
    print(f"Exported to {output_path}")
    print(f"Total queries: {len(df)}")

if __name__ == "__main__":
    export_metrics_for_powerbi()