from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime

from ..data_collection.odds_collector import OddsCollector
from ..models.predictor import BettingPredictor
from ..utils.bet_tracker import WaltersBetTracker, BetDetails
from ..config.settings import SUPPORTED_SPORTS, WEB_CONFIG

app = FastAPI(title="Sports Betting Analytics Platform")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
odds_collector = OddsCollector()
predictor = BettingPredictor()
bet_tracker = WaltersBetTracker()

# Background task for updating odds
async def update_odds_background():
    while True:
        async with odds_collector as collector:
            await collector.fetch_all_odds()
        await asyncio.sleep(WEB_CONFIG['refresh_interval'])

# Models for request/response
class GamePredictionRequest(BaseModel):
    sport: str
    game_id: str
    home_team: str
    away_team: str
    additional_data: Optional[Dict] = None

class PlayerPropsRequest(BaseModel):
    sport: str
    player_id: str
    prop_type: str
    line: float
    additional_data: Optional[Dict] = None

class BetPlacementRequest(BaseModel):
    sport: str
    game: str
    pick_type: str
    pick: str
    line: float
    odds: float
    bet_amount: float
    book: str
    confidence: int
    notes: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    # Start background odds updating
    background_tasks = BackgroundTasks()
    background_tasks.add_task(update_odds_background)

@app.get("/api/sports")
async def get_supported_sports():
    """Get list of supported sports and their configurations."""
    return SUPPORTED_SPORTS

@app.get("/api/odds/{sport}")
async def get_odds(sport: str):
    """Get current odds for a specific sport."""
    if sport not in SUPPORTED_SPORTS:
        raise HTTPException(status_code=404, detail="Sport not supported")
    
    async with odds_collector as collector:
        odds = await collector.fetch_odds("draftkings", sport)  # Example using DraftKings
        return odds

@app.post("/api/predictions/game")
async def predict_game(request: GamePredictionRequest):
    """Get game prediction."""
    try:
        prediction = predictor.predict_game(request.sport, {
            'home_team': request.home_team,
            'away_team': request.away_team,
            **request.additional_data
        } if request.additional_data else {
            'home_team': request.home_team,
            'away_team': request.away_team
        })
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predictions/props")
async def predict_props(request: PlayerPropsRequest):
    """Get player props prediction."""
    try:
        prediction = predictor.predict_player_props(request.sport, {
            'player_id': request.player_id,
            'prop_type': request.prop_type,
            'prop_line': request.line,
            **request.additional_data
        } if request.additional_data else {
            'player_id': request.player_id,
            'prop_type': request.prop_type,
            'prop_line': request.line
        })
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bets")
async def place_bet(request: BetPlacementRequest):
    """Record a new bet."""
    try:
        new_bet = BetDetails(
            date=datetime.now().strftime("%Y-%m-%d"),
            sport=request.sport,
            game=request.game,
            pick_type=request.pick_type,
            pick=request.pick,
            confidence=request.confidence,
            line=request.line,
            odds=request.odds,
            bet_amount=request.bet_amount,
            book=request.book,
            bet_time=datetime.now().strftime("%H:%M:%S"),
            notes=request.notes if request.notes else ""
        )
        
        bet_tracker.add_bet(new_bet)
        return {"status": "success", "bet_id": len(bet_tracker.bets)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bets/analytics")
async def get_betting_analytics():
    """Get comprehensive betting analytics."""
    try:
        analytics = bet_tracker.get_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/arbitrage/{sport}")
async def get_arbitrage_opportunities(sport: str):
    """Get current arbitrage opportunities for a sport."""
    if sport not in SUPPORTED_SPORTS:
        raise HTTPException(status_code=404, detail="Sport not supported")
    
    async with odds_collector as collector:
        odds = await collector.fetch_all_odds()
        opportunities = []
        
        for event_id in odds.get(f"draftkings_{sport}", {}).keys():
            arb = collector.detect_arbitrage(sport, event_id)
            if arb:
                opportunities.append(arb)
        
        return opportunities

@app.get("/api/line-movement/{sport}/{event_id}")
async def get_line_movement(sport: str, event_id: str, timeframe_minutes: int = 60):
    """Get line movement data for a specific event."""
    if sport not in SUPPORTED_SPORTS:
        raise HTTPException(status_code=404, detail="Sport not supported")
    
    movements = odds_collector.get_line_movement(sport, event_id, timeframe_minutes)
    return movements

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=WEB_CONFIG['host'], port=WEB_CONFIG['port']) 