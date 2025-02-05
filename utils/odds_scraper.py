"""Odds scraper for collecting betting lines from various sportsbooks."""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class OddsScraper:
    """Scraper for collecting odds from various sportsbooks."""
    
    def __init__(self):
        self.ua = UserAgent()
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
    
    def get_draftkings_odds(self, sport: str) -> Dict:
        """Scrape odds from DraftKings."""
        odds = {}
        try:
            # DraftKings uses a React app, need Selenium
            with webdriver.Chrome(options=self.chrome_options) as driver:
                # Example URL for NBA
                url = f'https://sportsbook.draftkings.com/leagues/{sport}'
                driver.get(url)
                
                # Wait for odds to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sportsbook-outcome-cell__label'))
                )
                
                # Extract game data
                games = driver.find_elements(By.CLASS_NAME, 'sportsbook-event-accordion__wrapper')
                
                for game in games:
                    try:
                        teams = game.find_elements(By.CLASS_NAME, 'event-cell__name')
                        odds_elements = game.find_elements(By.CLASS_NAME, 'sportsbook-odds')
                        
                        if len(teams) >= 2 and len(odds_elements) >= 2:
                            game_id = f"{teams[0].text.strip()}_vs_{teams[1].text.strip()}"
                            odds[game_id] = {
                                'home_team': teams[0].text.strip(),
                                'away_team': teams[1].text.strip(),
                                'home_odds': odds_elements[0].text.strip(),
                                'away_odds': odds_elements[1].text.strip(),
                                'timestamp': datetime.now().isoformat()
                            }
                    except Exception as e:
                        logger.error(f"Error parsing game: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping DraftKings: {str(e)}")
        
        return odds
    
    def get_betmgm_odds(self, sport: str) -> Dict:
        """Scrape odds from BetMGM."""
        odds = {}
        try:
            headers = {'User-Agent': self.ua.random}
            # Example URL for NBA
            url = f'https://sports.betmgm.com/en/sports/{sport}'
            
            with webdriver.Chrome(options=self.chrome_options) as driver:
                driver.get(url)
                
                # Wait for odds to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'markets-container'))
                )
                
                # Extract game data
                games = driver.find_elements(By.CLASS_NAME, 'game-row')
                
                for game in games:
                    try:
                        teams = game.find_elements(By.CLASS_NAME, 'participant-name')
                        odds_elements = game.find_elements(By.CLASS_NAME, 'market-price')
                        
                        if len(teams) >= 2 and len(odds_elements) >= 2:
                            game_id = f"{teams[0].text.strip()}_vs_{teams[1].text.strip()}"
                            odds[game_id] = {
                                'home_team': teams[0].text.strip(),
                                'away_team': teams[1].text.strip(),
                                'home_odds': odds_elements[0].text.strip(),
                                'away_odds': odds_elements[1].text.strip(),
                                'timestamp': datetime.now().isoformat()
                            }
                    except Exception as e:
                        logger.error(f"Error parsing game: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping BetMGM: {str(e)}")
        
        return odds
    
    def get_fanduel_odds(self, sport: str) -> Dict:
        """Scrape odds from FanDuel."""
        odds = {}
        try:
            headers = {'User-Agent': self.ua.random}
            # Example URL for NBA
            url = f'https://sportsbook.fanduel.com/sports/{sport}'
            
            with webdriver.Chrome(options=self.chrome_options) as driver:
                driver.get(url)
                
                # Wait for odds to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'event'))
                )
                
                # Extract game data
                games = driver.find_elements(By.CLASS_NAME, 'event')
                
                for game in games:
                    try:
                        teams = game.find_elements(By.CLASS_NAME, 'name')
                        odds_elements = game.find_elements(By.CLASS_NAME, 'price')
                        
                        if len(teams) >= 2 and len(odds_elements) >= 2:
                            game_id = f"{teams[0].text.strip()}_vs_{teams[1].text.strip()}"
                            odds[game_id] = {
                                'home_team': teams[0].text.strip(),
                                'away_team': teams[1].text.strip(),
                                'home_odds': odds_elements[0].text.strip(),
                                'away_odds': odds_elements[1].text.strip(),
                                'timestamp': datetime.now().isoformat()
                            }
                    except Exception as e:
                        logger.error(f"Error parsing game: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping FanDuel: {str(e)}")
        
        return odds
    
    def get_caesars_odds(self, sport: str) -> Dict:
        """Scrape odds from Caesars."""
        odds = {}
        try:
            headers = {'User-Agent': self.ua.random}
            # Example URL for NBA
            url = f'https://www.caesars.com/sportsbook-and-casino/sport/{sport}'
            
            with webdriver.Chrome(options=self.chrome_options) as driver:
                driver.get(url)
                
                # Wait for odds to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'market'))
                )
                
                # Extract game data
                games = driver.find_elements(By.CLASS_NAME, 'market')
                
                for game in games:
                    try:
                        teams = game.find_elements(By.CLASS_NAME, 'team-name')
                        odds_elements = game.find_elements(By.CLASS_NAME, 'odds')
                        
                        if len(teams) >= 2 and len(odds_elements) >= 2:
                            game_id = f"{teams[0].text.strip()}_vs_{teams[1].text.strip()}"
                            odds[game_id] = {
                                'home_team': teams[0].text.strip(),
                                'away_team': teams[1].text.strip(),
                                'home_odds': odds_elements[0].text.strip(),
                                'away_odds': odds_elements[1].text.strip(),
                                'timestamp': datetime.now().isoformat()
                            }
                    except Exception as e:
                        logger.error(f"Error parsing game: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping Caesars: {str(e)}")
        
        return odds
    
    def get_all_odds(self, sport: str) -> Dict:
        """Get odds from all supported sportsbooks."""
        all_odds = {
            'draftkings': self.get_draftkings_odds(sport),
            'betmgm': self.get_betmgm_odds(sport),
            'fanduel': self.get_fanduel_odds(sport),
            'caesars': self.get_caesars_odds(sport)
        }
        
        # Add metadata
        all_odds['metadata'] = {
            'sport': sport,
            'timestamp': datetime.now().isoformat(),
            'success_count': sum(1 for book in all_odds.values() if book)
        }
        
        return all_odds
    
    def _add_random_delay(self):
        """Add random delay between requests to avoid detection."""
        time.sleep(random.uniform(1, 3))

if __name__ == '__main__':
    # Example usage
    scraper = OddsScraper()
    odds = scraper.get_all_odds('nba')
    print(json.dumps(odds, indent=2)) 