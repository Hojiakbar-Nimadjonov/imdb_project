# 🎬 IMDb Top 250 — Python-Powered Movie Performance Insights

## 📌 About the Project
This project automatically scrapes data from [IMDb Top 250](https://www.imdb.com/chart/top/) using Python and analyzes it to generate valuable **KPIs** for streaming platforms like **FilmFlix**.

**What the project does:**
- 📥 Scrapes IMDb (title, year, rating, votes, genres, directors, actors, gross, runtime)
- 🧹 Cleans and normalizes the data
- 📊 Calculates key KPIs
- 📈 Visualizes results
- ⚡ Can be automated for regular updates

---

## 🗂 Project Structure
```bash
imdb_project/
├── data/                       
│   ├── imdb_top250_raw.csv       # Raw scraped data
│   ├── imdb_top250_clean.csv     # Cleaned data
│   ├── kpi_genres.png            # Top genres chart
│   ├── kpi_ratings_by_year.png   # Ratings over time chart
│   ├── kpi_runtime_vs_rating.png # Runtime vs rating chart
│   ├── kpi_top_directors.csv     # Best directors
│   ├── kpi_top_actors.csv        # Top actors
│   ├── kpi_top_gross.csv         # Top box office films
│
├── src/
│   ├── scrape.py                 # IMDb scraping logic
│   ├── clean.py                  # Data cleaning (optional)
│   ├── kpi.py                    # KPI analysis
│
├── notebooks/
│   ├── imdb_analysis.ipynb       # Jupyter Notebook for analysis
│
├── requirements.txt              # Project dependencies
├── README.md                     # Documentation
├── .gitignore                    # Ignored files
