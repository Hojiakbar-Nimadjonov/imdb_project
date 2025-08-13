# clean.py
import pandas as pd
import numpy as np
import re, json, os

def parse_money(x):
    if pd.isna(x): return np.nan
    s = str(x)
    s = re.sub(r'[^0-9.]', '', s)
    try:
        return float(s)
    except:
        return np.nan

def ensure_list(x):
    if pd.isna(x): return []
    if isinstance(x, list): return x
    if isinstance(x, str) and x.startswith('[') and x.endswith(']'):
        try:
            return json.loads(x.replace("'", '"'))
        except:
            pass
    if isinstance(x, str) and ',' in x:
        return [s.strip() for s in x.split(',') if s.strip()]
    return [x]

def clean_raw(input_csv="../data/imdb_top250_raw.csv", output_csv="../data/imdb_top250_clean.csv"):
    df = pd.read_csv(input_csv, dtype=str)
    # Convert numeric fields
    df['RatingNum'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['YearNum'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
    # Votes: try Votes column or VotesDetail
    def get_votes(row):
        for col in ['Votes', 'VotesDetail']:
            v = row.get(col, None)
            if pd.notna(v):
                s = str(v)
                s = re.sub(r'[^0-9]', '', s)
                if s:
                    return int(s)
        return np.nan
    df['VotesNum'] = df.apply(get_votes, axis=1)
    # Box office numeric
    if 'BoxOffice' in df.columns:
        df['BoxOfficeNum'] = df['BoxOffice'].apply(parse_money)
    else:
        df['BoxOfficeNum'] = np.nan
    # Runtime
    if 'RuntimeMin' in df.columns:
        df['RuntimeMinNum'] = pd.to_numeric(df['RuntimeMin'], errors='coerce').astype('Int64')
    else:
        df['RuntimeMinNum'] = np.nan
    # Lists
    for col in ['Genres', 'Directors', 'TopCast']:
        if col in df.columns:
            df[col] = df[col].apply(ensure_list)
        else:
            df[col] = [[] for _ in range(len(df))]
    # Save cleaned CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print("Saved cleaned CSV:", output_csv)
    return df

if __name__ == "__main__":
    clean_raw()
