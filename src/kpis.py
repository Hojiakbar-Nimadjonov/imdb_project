# kpis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import Counter

sns.set(style='whitegrid')

def load_clean(path="../data/imdb_top250_clean.csv"):
    return pd.read_csv(path, dtype=str)

def explode_list_column(df, col):
    df2 = df.copy()
    df2[col] = df2[col].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else x)
    return df2.explode(col)

def top_genres(df, topn=10):
    df2 = explode_list_column(df, 'Genres')
    counts = df2['Genres'].value_counts().head(topn)
    return counts

def top_actors(df, topn=15):
    df2 = explode_list_column(df, 'TopCast')
    return df2['TopCast'].value_counts().head(topn)

def plot_bar(series, title, outpath=None):
    plt.figure(figsize=(8,5))
    sns.barplot(x=series.values, y=series.index)
    plt.title(title)
    plt.tight_layout()
    if outpath:
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        plt.savefig(outpath)
    plt.show()

if __name__ == "__main__":
    df = load_clean()
    tg = top_genres(df)
    print("Top genres:\n", tg.head(15))
    plot_bar(tg, "Top genres (count)", outpath="../outputs/figures/top_genres.png")
    ta = top_actors(df)
    print("Top actors:\n", ta.head(15))
    plot_bar(ta, "Top actors (count)", outpath="../outputs/figures/top_actors.png")
