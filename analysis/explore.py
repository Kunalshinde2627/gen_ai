import pandas as pd

from app.records import load_records

df = pd.DataFrame(load_records())

# Fact 1: how many records we have
print("Fact 1: total records =", len(df))

# Fact 2: how many records for each regime
print("\nFact 2: records per regime")
print(df["regime"].value_counts())

# Fact 3: which record has the longest summary
df["summary_words"] = df["summary"].str.split().str.len()
longest = df.loc[df["summary_words"].idxmax()]
print("\nFact 3: longest summary is", longest["id"], "-", longest["topic"],
      f"({longest['summary_words']} words)")
print("Average summary length =", round(df["summary_words"].mean(), 1), "words")