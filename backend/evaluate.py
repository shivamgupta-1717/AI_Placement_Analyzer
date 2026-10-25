#!/usr/bin/env python3
"""
RAG Reliability & Evaluation Benchmark Runner.
Executes the deterministic 10-scenario evaluation dataset and outputs formal metrics.
"""
import sys
import os
import json

# Ensure app package is discoverable
sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal, Base, engine
from app.services.evaluation_service import EvaluationService

def main():
    print("=" * 70)
    print("AI Placement Analyzer - RAG Benchmark & Reliability Evaluation")
    print("=" * 70)

    # Initialize tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        evaluator = EvaluationService(db=db)
        print("Executing benchmark across 10 deterministic test scenarios...")
        results = evaluator.run_benchmark()

        print("\n--- MEASURED BENCHMARK METRICS ---")
        print(f"Dataset Version              : v{results['dataset_version']}")
        print(f"Total Test Cases             : {results['total_test_cases']}")
        print(f"Skill Classification Accuracy: {results['classification_accuracy']}%")
        print(f"Evidence Citation Validity   : {results['citation_validity_rate']}%")
        print(f"Abstention on Missing Skills : {results['abstention_rate']}%")
        print(f"Unsupported-Claim Rate       : {results['unsupported_claim_rate']}%  (Target: 0.0%)")
        print(f"Retrieval Precision@K        : {results['precision_at_k']}%")
        print(f"Retrieval Recall@K           : {results['recall_at_k']}%")
        print(f"Schema Validation Rate       : {results['schema_validation_rate']}%")
        print(f"End-to-End Success Rate      : {results['end_to_end_success_rate']}%")

        print("\n--- DETAILED SCENARIO BREAKDOWN ---")
        for r in results["detailed_results"]:
            status_symbol = "PASS" if r["passed"] else "FAIL"
            print(f"[{status_symbol}] {r['scenario_id']} - {r['name']}")
            print(f"       Expected: {r['expected_classification']} | Actual: {r['actual_classification']}")
            print(f"       Reasoning: {r['reasoning'][:90]}...")
            if r.get("injection_prevented"):
                print("       [SECURITY] Prompt injection successfully detected & neutralized.")
            print()

        print("=" * 70)
        print("Evaluation benchmark completed successfully.")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    main()
