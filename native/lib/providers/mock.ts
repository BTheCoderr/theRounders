import type { OddsProvider } from "./types";
import type { MarketQuote, MarketName } from "../contracts";

const fixtures: Record<string, [string, string][]> = {
  NBA: [["Boston Celtics", "New York Knicks"], ["Los Angeles Lakers", "Golden State Warriors"], ["Milwaukee Bucks", "Cleveland Cavaliers"]],
  NFL: [["Buffalo Bills", "New York Jets"], ["Dallas Cowboys", "Philadelphia Eagles"], ["Kansas City Chiefs", "Denver Broncos"]],
  NHL: [["Boston Bruins", "New York Rangers"], ["Toronto Maple Leafs", "Montreal Canadiens"], ["Vegas Golden Knights", "Edmonton Oilers"]],
  MLB: [["Boston Red Sox", "New York Yankees"], ["Los Angeles Dodgers", "San Diego Padres"], ["Chicago Cubs", "St. Louis Cardinals"]]
};
const baseline: Record<string, { spread: number; total: number }> = {
  NBA: { spread: -4.5, total: 220.5 },
  NFL: { spread: -3.5, total: 45.5 },
  NHL: { spread: -1.5, total: 6.5 },
  MLB: { spread: -1.5, total: 8.5 }
};
const books = [["Northstar", -9], ["Metro", 0], ["Prime", 9]] as const;

function choices(sport: string, away: string, home: string, game: number, market: MarketName): { selection: string; line?: number; price: number }[] {
  const shape = baseline[sport] ?? baseline.NBA;
  if (market === "moneyline") {
    return [{ selection: home, price: -128 }, { selection: away, price: 113 }];
  }
  if (market === "spread") {
    // Run and puck lines stay at 1.5; basketball/football spreads vary by fixture.
    const homeLine = sport === "NHL" || sport === "MLB" ? -1.5 : shape.spread + game;
    return [{ selection: home, line: homeLine, price: -110 }, { selection: away, line: -homeLine, price: -110 }];
  }
  const step = sport === "NHL" || sport === "MLB" ? 0.5 : sport === "NFL" ? 1.5 : 2;
  const line = shape.total + game * step;
  return [{ selection: "Over", line, price: -112 }, { selection: "Under", line, price: -108 }];
}

export const mockProvider: OddsProvider = {
  name: "controlled-demo",
  mode: "simulated",
  async health() {
    return { name: this.name, mode: this.mode, healthy: true, checkedAt: new Date().toISOString(), message: "Controlled development feed: simulated prices only" };
  },
  async getMarkets(sport) {
    const now = new Date();
    const games = fixtures[sport] ?? fixtures.NBA;
    const quotes: MarketQuote[] = [];
    games.forEach(([away, home], game) => {
      const eventId = sport.toLowerCase() + "-" + (game + 1);
      const startTime = new Date(now.getTime() + (game + 1) * 3600000).toISOString();
      for (const market of ["moneyline", "spread", "total"] as MarketName[]) {
        for (const choice of choices(sport, away, home, game, market)) {
          for (const [book, offset] of books) {
            quotes.push({
              eventId, sport, market, selection: choice.selection, line: choice.line,
              price: choice.price + offset, book,
              updatedAt: now.toISOString(), state: "simulated", away, home, startTime
            });
          }
        }
      }
    });
    return quotes;
  }
};
