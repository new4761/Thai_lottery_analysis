import pandas as pd

# 📥 Load the raw data
df = pd.read_csv("lottery_results.csv")

# 🎯 Columns to extract
prize_columns = ["first", "second", "third", "fourth", "fifth", "last2", "last3f", "last3b", "near1"]

# 🔁 Flatten into long format
records = []

for idx, row in df.iterrows():
    for prize in prize_columns:
        values = str(row[prize]).strip()
        if values.lower() != 'nan' and values:
            for val in values.split(","):
                clean_number = val.strip().zfill(6)
                if clean_number:
                    records.append({
                        "date": row["date"],
                        "prize_type": prize,
                        "number": clean_number
                    })

# 📊 Final Looker-friendly format
df_looker = pd.DataFrame(records)

# 💾 Save to CSV
df_looker.to_csv("lottery_results_looker_ready.csv", index=False)
print("✅ Looker-ready dataset saved as 'lottery_results_looker_ready.csv'")
