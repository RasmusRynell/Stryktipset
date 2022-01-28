from web import oddsPortal
from web import ss
from web import stl
from helper import helpers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import subprocess
import sys
import time
from datetime import datetime

if __name__ == '__main__':
    # Read config file
    with open('config.cfg') as json_data_file:
        config = json.load(json_data_file)

    args = sys.argv[1:]
    print('\033[93m' + 'Ran with commands: ' + str(args) + '\033[0m')
    if len(args) == 1 and args[0] == '--forever':
        print("\033[93mCheck if games are open...\033[0m", flush=True)
        while(not ss.games_are_open()):
            print(f'{datetime.now().strftime("%H:%M:%S")}: \033[91mNo data available yet, sleeping for {config["sleep_time"]}s\033[0m', flush=True)
            time.sleep(config['sleep_time'])
        print('\033[92m' + 'Data found, running' + '\033[0m', flush=True)

    OUT_FILE = 'out.txt'

    options = Options()
    options.headless = config['headless']
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Get games
    games = ss.get_games()

    # Request odds for all games
    oddsPortal.fill_with_odds(games, driver, config['login_op']['username'], config['login_op']['password'])

    with open(OUT_FILE, 'w') as f:
        for i, game in enumerate(games):
            f.write(str(4) + '\n') # Write number of inputs for this game
            f.write(str(i+1) + '\n') # Write game id
            f.write(str(game['odds_info']['avr_odds']['one']) + '\n')
            f.write(str(game['odds_info']['avr_odds']['x']) + '\n')
            f.write(str(game['odds_info']['avr_odds']['two']) + '\n')


    proc = subprocess.Popen(["./a.exe"])
    proc.wait()

    # Read out.txt
    with open(OUT_FILE, 'r') as f:  
        bets = f.readlines()

    result = {}
    for bet in [bet.replace('\n', '') for bet in bets]:
        key, value = bet.split(':')
        result[key] = value

    old = stl.write_bets(result, driver, config['login_stl']['email'], config['login_stl']['password'])

    helpers.print_diff(old, result)
    driver.quit()