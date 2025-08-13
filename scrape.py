# scrape.py
import requests, time, re, json
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import os

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FilmFlixBot/1.0)"}
BASE = "https://www.imdb.com"
TOP250_URL = "https://www.imdb.com/chart/top/"

def get_soup(url, sleep=0.6, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            r.raise_for_status()
            time.sleep(sleep)
            return BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"Request error ({i+1}/{retries}) for {url}: {e}")
            time.sleep(1 + i)
    raise RuntimeError(f"Failed to fetch {url}")

def parse_movie_page(url):
    soup = get_soup(url)
    # Genres
    genres = [g.text.strip() for g in soup.select("div[data-testid='genres'] a")] or []
    # Runtime
    runtime = None
    rt = soup.find('li', {'data-testid': 'title-techspec_runtime'})
    if rt:
        m = re.search(r'(\d+)\s*min', rt.get_text())
        if m: runtime = int(m.group(1))
    # Directors (fallbacks)
    directors = []
    try:
        # prefer credit summary
        d_nodes = soup.select("li[data-testid='title-pc-principal-credit']:has(a[href^='/name/']) a[href^='/name/']")
        if d_nodes:
            directors = [a.get_text(strip=True) for a in d_nodes]
        else:
            # alternate
            directors = [a.get_text(strip=True) for a in soup.select("a[href*='/name/']")][:3]
    except:
        directors = []
    # Top cast
    top_cast = []
    try:
        cast_nodes = soup.select("div[data-testid='title-cast'] a[href^='/name/']")
        names = []
        for a in cast_nodes:
            txt = a.get_text(strip=True)
            if txt and txt not in names:
                names.append(txt)
            if len(names) >= 5: break
        top_cast = names[:3]
    except:
        top_cast = []
    # Box office (try to find $ amounts near box office labels)
    box_office = None
    try:
        labels = soup.find_all(text=re.compile(r'Box office|Gross worldwide|Cumulative worldwide', re.I))
        for lbl in labels:
            parent = lbl.parent
            txt = parent.get_text(" ", strip=True)
            m = re.search(r'\$\s?[\d,]+', txt)
            if m:
                box_office = m.group(0)
                break
    except:
        box_office = None
    # Votes - fallback
    votes = None
    try:
        # try find element with votes count
        vote_tag = soup.select_one("div[data-testid='score-and-rating'] a[href*='ratings']")
        if vote_tag:
            v = re.sub(r'[^0-9]', '', vote_tag.get_text())
            votes = int(v) if v else None
    except:
        votes = None

    return {
        "Genres": genres,
        "RuntimeMin": runtime,
        "Directors": directors,
        "TopCast": top_cast,
        "BoxOffice": box_office,
        "VotesDetail": votes
    }

def scrape_top250(save_path="../data/imdb_top250_raw.csv"):
    soup = get_soup(TOP250_URL)
    rows = soup.select("tbody.lister-list tr")
    movies = []
    for r in tqdm(rows, desc="Parsing top250"):
        try:
            title_col = r.select_one("td.titleColumn a")
            title = title_col.text.strip()
            rel = title_col['href'].split('?')[0]
            url = BASE + rel
            year_text = r.select_one("td.titleColumn span.secondaryInfo").text.strip()
            year = int(re.sub(r'[^0-9]', '', year_text))
            rating = float(r.select_one("td.imdbRating strong").text.strip())
            # votes sometimes in title attr of <strong>
            votes = None
            try:
                strong = r.select_one("td.imdbRating strong")
                if strong and strong.has_attr('title'):
                    m = re.search(r'based on ([\d,]+) user ratings', strong['title'])
                    if m:
                        votes = int(m.group(1).replace(',', ''))
            except:
                votes = None

            base = {"Title": title, "Year": year, "Rating": rating, "URL": url, "Votes": votes}
            # enrich
            details = parse_movie_page(url)
            base.update(details)
            movies.append(base)
        except Exception as e:
            print("Error parsing row:", e)
    df = pd.DataFrame(movies)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False, encoding="utf-8")
    print("Saved raw CSV:", save_path)
    return df

if __name__ == "__main__":
    scrape_top250(save_path="../data/imdb_top250_raw.csv")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re
import os

# Папка для сохранения CSV
os.makedirs("data", exist_ok=True)

# URL IMDb Top 250
BASE_URL = "https://www.imdb.com"
URL = "https://www.imdb.com/chart/top/"

# Делаем запрос
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

# Находим ссылки на страницы фильмов
movie_links = [
    BASE_URL + a["href"].split("?")[0]
    for a in soup.select("td.titleColumn a")
]

data = []

for link in tqdm(movie_links, desc="Сбор данных с IMDb"):
    r = requests.get(link, headers=headers)
    s = BeautifulSoup(r.text, "lxml")

    # Название
    title_tag = s.select_one("h1")
    title = title_tag.text.strip() if title_tag else None

    # Год
    year_tag = s.select_one("span.sc-8c396aa2-2")
    year = int(year_tag.text.strip()) if year_tag else None

    # Рейтинг
    rating_tag = s.select_one("span.sc-bde20123-1")
    rating = float(rating_tag.text.strip()) if rating_tag else None

    # Количество голосов
    votes_tag = s.select_one("div.sc-7ab21ed2-3.kLojWo")
    votes = int(votes_tag.text.replace(",", "")) if votes_tag else None

    # Жанры
    genres_tag = s.select("div.ipc-chip-list__scroller a.ipc-chip__text")
    genres = ", ".join([g.text for g in genres_tag]) if genres_tag else None

    # Режиссёры
    directors_tag = s.select('li[data-testid="title-pc-principal-credit"]:first-child a')
    directors = ", ".join([d.text for d in directors_tag]) if directors_tag else None

    # Топ-3 актёра
    actors_tag = s.select('li[data-testid="title-pc-principal-credit"]:nth-child(2) a')
    actors = ", ".join([a.text for a in actors_tag[:3]]) if actors_tag else None

    # Сборы (Box Office)
    gross_tag = s.find(text=re.compile("Gross worldwide"))
    gross = None
    if gross_tag:
        parent = gross_tag.find_parent("li")
        if parent:
            value = parent.select_one("span.ipc-metadata-list-item__list-content-item")
            gross = value.text if value else None

    # Длительность
    runtime_tag = s.select_one('li[data-testid="title-techspec_runtime"] span')
    runtime = runtime_tag.text if runtime_tag else None

    data.append({
        "Title": title,
        "Year": year,
        "Rating": rating,
        "Votes": votes,
        "Genres": genres,
        "Directors": directors,
        "Actors": actors,
        "Gross": gross,
        "Runtime": runtime,
        "URL": link
    })

# Сохраняем в CSV
df = pd.DataFrame(data)
df.to_csv("data/imdb_top250_raw.csv", index=False, encoding="utf-8-sig")

print("✅ Парсинг завершён. Файл сохранён в data/imdb_top250_raw.csv")
