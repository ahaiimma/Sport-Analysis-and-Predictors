import numpy as np
import pandas as pd
import random
import time
import logging
from io import StringIO  # Import StringIO for the future-proof read_html
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
logging.basicConfig(
    filename='nba_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define teams and seasons
teams = [
    'atl', 'bos', 'brk', 'cho', 'chi', 'cle', 'dal', 'den', 'det', 'gsw',
    'hou', 'ind', 'lac', 'lal', 'mem', 'mia', 'mil', 'min', 'nop', 'nyk',
    'okc', 'orl', 'phi', 'pho', 'por', 'sac', 'sas', 'tor', 'uta', 'was'
]

seasons = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']

# Define stats and column mappings
stats = [
    'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB',
    'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF'
]

tm_stats_dict = {stat: 'Tm_' + str(stat) for stat in stats}
opp_stats_dict = {stat + '.1': 'Opp_' + str(stat) for stat in stats}

# Initialize an empty list to store DataFrames
all_dfs = []

# Configure Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# --- Start of Driver Initialization (Moved outside the loop) ---
# Initialize the WebDriver once
driver_path = ChromeDriverManager().install()
service = Service(driver_path)
driver = None
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Iterate through seasons and teams
    for season in seasons:
        for team in teams:
            url = f'https://www.basketball-reference.com/teams/{team}/{season}/gamelog/'
            logging.info(f"Scraping: {url}")
            print(f"Scraping: {url}")
            
            try:
                driver.get(url)

                # Wait for the table to load
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located((By.ID, 'team_game_log_reg')))

                # Parse the HTML table
                html_source = driver.page_source
                # Use StringIO to handle the FutureWarning
                team_df = pd.read_html(StringIO(html_source), attrs={'id': 'team_game_log_reg'})[0]

                # Clean the DataFrame
                if 'Rk' in team_df.columns:
                    team_df = team_df[(team_df['Rk'].str != '') & (team_df['Rk'].str.isnumeric())]
                if 'Unnamed: 24' in team_df.columns:
                    team_df = team_df.drop(columns=['Unnamed: 24'])

                # Rename columns
                team_df = team_df.rename(columns={'Unnamed: 3': 'Home', 'Tm': 'Tm_Pts', 'Opp.1': 'Opp_Pts'})
                team_df = team_df.rename(columns=tm_stats_dict)
                team_df = team_df.rename(columns=opp_stats_dict)
                
                # Use .loc to avoid a SettingWithCopyWarning
                team_df.loc[:, 'Home'] = team_df['Home'].apply(lambda x: 0 if x == '@' else 1)

                # Add season and team info
                team_df.insert(loc=0, column='Season', value=season)
                team_df.insert(loc=1, column='Team', value=team.upper())

                # Append to the list
                all_dfs.append(team_df)
                logging.info(f"Successfully scraped {url}")
                
            except Exception as e:
                # Log the error, but continue to the next URL
                logging.error(f"An error occurred while scraping {url}: {e}")
                print(f"An error occurred while scraping {url}: {e}")
            
            # Random delay to avoid rate-limiting
            sleep_time = random.uniform(5, 10)
            logging.info(f"Sleeping for {sleep_time:.2f} seconds...")
            print(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

finally:
    # --- End of Driver Initialization (Moved outside the loop) ---
    # Quit the WebDriver once after all scraping is done
    if driver is not None:
        driver.quit()

# Combine all DataFrames and save to CSV
if all_dfs:
    nba_df = pd.concat(all_dfs, ignore_index=True)
    print("Scraping complete. Saving to CSV...")
    logging.info("Scraping complete. Saving to CSV...")
    nba_df.to_csv('nba-gamelogs-2018-2025.csv', index=False)
else:
    print("No data was scraped. Check the log file for errors.")
    logging.error("No data was scraped.")