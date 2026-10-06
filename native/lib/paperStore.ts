"use client";
import type {PaperBet} from "./contracts";
const BETS_KEY="rounders.paper-bets.v1";
const BANKROLL_KEY="rounders.paper-bankroll.v1";
export function loadBets():PaperBet[]{try{return JSON.parse(localStorage.getItem(BETS_KEY)||"[]")}catch{return []}}
export function saveBet(bet:PaperBet){const next=[bet,...loadBets()];localStorage.setItem(BETS_KEY,JSON.stringify(next));window.dispatchEvent(new Event("rounders:paper"));return next}
export function updateBet(id:string,status:PaperBet["status"]){const next=loadBets().map(b=>b.id===id?{...b,status}:b);localStorage.setItem(BETS_KEY,JSON.stringify(next));window.dispatchEvent(new Event("rounders:paper"));return next}
export function loadStartingBankroll(){return Number(localStorage.getItem(BANKROLL_KEY)||1000)}
export function saveStartingBankroll(value:number){localStorage.setItem(BANKROLL_KEY,String(value));window.dispatchEvent(new Event("rounders:paper"))}
export function profitFor(bet:PaperBet){if(bet.status==="pending"||bet.status==="push")return 0;if(bet.status==="lost")return -bet.stake;return bet.price>0?bet.stake*(bet.price/100):bet.stake*(100/Math.abs(bet.price))}
