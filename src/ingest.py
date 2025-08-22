"""
Builds the Chroma vector DB from a CSV dataset of court diversion records.

Usage:
    python src/ingest.py --csv data/diversion_data.csv --persist chroma_data/ALM
"""

import argparse
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

def build_chroma_from_csv(csv_path: str, persist_dir: str):
    # Load CSV
    df = pd.read_csv(csv_path)

    # Sanity check: require ID + RECEIVED DATE at least
    required_cols = ["ID", "RECEIVED DATE"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV must contain column '{col}'")

    # Create documents for embedding
    docs = []
    for _, row in df.iterrows():
        # Turn row into a structured string
        content = []
        for col, val in row.items():
            content.append(f"{col}: {val}")
        text = "\n".join(content)

        # Use ID as metadata for grouping
        metadata = {"ID": str(row["ID"])}
        docs.append(Document(page_content=text, metadata=metadata))

    # Embed + persist in Chroma
    embeddings = OpenAIEmbeddings()
    vs = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    vs.persist()
    print(f"✅ Built Chroma index at {persist_dir} with {len(docs)} records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--persist", required=True, help="Directory to persist Chroma DB")
    args = parser.parse_args()

    build_chroma_from_csv(args.csv, args.persist)
