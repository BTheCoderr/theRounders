"use client";
import {useState} from "react";
import type {DataState,MarketName,PaperBet} from "../lib/contracts";
import {saveBet} from "../lib/paperStore";
type Props={eventId:string;sport:string;matchup:string;market:MarketName;selection:string;line?:number;price:number;book:string;stake:number;dataState:DataState};
export default function AddPaperBet(props:Props){const [saved,setSaved]=useState(false);function add(){const bet:PaperBet={id:Date.now().toString(36)+"-"+Math.random().toString(36).slice(2),eventId:props.eventId,sport:props.sport,matchup:props.matchup,market:props.market,selection:props.selection,line:props.line,price:props.price,book:props.book,stake:Math.max(1,props.stake),status:"pending",placedAt:new Date().toISOString(),dataState:props.dataState};saveBet(bet);setSaved(true)}return <><button type="button" onClick={add}>Add to paper card</button>{saved&&<span className="saved">Saved to paper card ✓</span>}</>}