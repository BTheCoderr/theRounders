import type {OddsProvider} from "./types";
export const mockProvider:OddsProvider={name:"controlled-demo",async getMarkets(sport){const now=new Date().toISOString();return [{eventId:"demo-1",sport,market:"moneyline",selection:"Home",price:-110,book:"Demo Book",updatedAt:now,state:"simulated"}]}};
