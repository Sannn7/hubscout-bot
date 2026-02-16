"""
Evaluation metrics for RAG system performance.
Tracks precision, recall, time-to-answer, and answer quality.
"""

import time
from typing import List, Dict, Tuple
from datetime import datetime
import json
from pathlib import Path
import pandas as pd

class RAGEvaluator:
    """
    Evaluates RAG system performance with multiple metrics.
    """
    
    def __init__(self, results_path: str = "evaluation_results"):
        self.results_path = Path(results_path)
        self.results_path.mkdir(parents=True, exist_ok=True)
        self.evaluation_log = []
        
    def evaluate_query(
        self,
        query: str,
        retrieved_docs: List[str],
        answer: str,
        ground_truth_docs: List[str] = None,
        start_time: float = None
    ) -> Dict:
        """
        Evaluate a single query.
        
        Metrics:
        - Retrieval precision @ K
        - Time to answer
        - Answer length
        - Number of sources used
        """
        end_time = time.time()
        
        metrics = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "num_retrieved": len(retrieved_docs),
            "answer_length": len(answer),
            "time_to_answer": end_time - start_time if start_time else None,
        }
        
        # Calculate precision if ground truth available
        if ground_truth_docs:
            relevant_retrieved = sum(
                1 for doc in retrieved_docs if doc in ground_truth_docs
            )
            metrics["precision_at_k"] = relevant_retrieved / len(retrieved_docs) if retrieved_docs else 0
            metrics["recall"] = relevant_retrieved / len(ground_truth_docs) if ground_truth_docs else 0
        
        self.evaluation_log.append(metrics)
        return metrics
    
    def compute_aggregate_metrics(self) -> Dict:
        """
        Compute aggregate metrics across all evaluations.
        """
        if not self.evaluation_log:
            return {}
        
        df = pd.DataFrame(self.evaluation_log)
        
        aggregates = {
            "total_queries": len(df),
            "avg_time_to_answer": df["time_to_answer"].mean(),
            "median_time_to_answer": df["time_to_answer"].median(),
            "avg_precision": df["precision_at_k"].mean() if "precision_at_k" in df else None,
            "avg_recall": df["recall"].mean() if "recall" in df else None,
            "avg_answer_length": df["answer_length"].mean(),
        }
        
        return aggregates
    
    def save_results(self):
        """Save evaluation results to JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            "evaluation_date": datetime.now().isoformat(),
            "total_queries": len(self.evaluation_log),
            "aggregate_metrics": self.compute_aggregate_metrics(),
            "detailed_results": self.evaluation_log
        }
        
        output_file = self.results_path / f"evaluation_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Evaluation results saved to: {output_file}")
        return output_file
    
    def generate_report(self) -> str:
        """Generate human-readable evaluation report."""
        metrics = self.compute_aggregate_metrics()
        
        report = f"""
RAG System Evaluation Report
============================
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Queries Evaluated: {metrics.get('total_queries', 0)}

Performance Metrics:
-------------------
Average Time to Answer: {metrics.get('avg_time_to_answer', 0):.3f}s
Median Time to Answer: {metrics.get('median_time_to_answer', 0):.3f}s
Average Precision@K: {metrics.get('avg_precision', 0):.3f}
Average Recall: {metrics.get('avg_recall', 0):.3f}

Answer Quality:
--------------
Average Answer Length: {metrics.get('avg_answer_length', 0):.0f} characters
"""
        
        return report