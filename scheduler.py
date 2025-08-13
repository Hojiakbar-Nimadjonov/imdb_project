import schedule, time
from scrape import scrape_top250
from clean import clean_raw

def job():
    print("Start scheduled job...")
    scrape_top250(save_path="../data/imdb_top250_raw.csv")
    clean_raw(input_csv="../data/imdb_top250_raw.csv", output_csv="../data/imdb_top250_clean.csv")
    print("Done.")

schedule.every().monday.at("03:00").do(job)
while True:
    schedule.run_pending()
    time.sleep(60)
