import test from "node:test";
import assert from "node:assert/strict";
import { mockProvider } from "../lib/providers/mock.ts";
import { findLineShopGaps } from "../lib/signals.ts";

const sports = ["NBA", "NFL", "NHL", "MLB"];
const expectedTotals = { NBA: 220.5, NFL: 45.5, NHL: 6.5, MLB: 8.5 };

for (const sport of sports) {
  test(`${sport} demo contains both sides of all markets with realistic lines`, async () => {
    const quotes = await mockProvider.getMarkets(sport);
    assert.equal(quotes.length, 54); // 3 fixtures × 3 markets × 2 sides × 3 books
    assert.ok(quotes.every(q => q.sport === sport && q.state === "simulated"));
    assert.ok(quotes.every(q => q.away.includes(" ") && q.home.includes(" ")));
    assert.ok(quotes.every(q => Number.isFinite(q.price) && Math.abs(q.price) >= 100));
    assert.equal(new Set(quotes.map(q => q.eventId)).size, 3);
    for (const eventId of new Set(quotes.map(q => q.eventId))) {
      const fixture = quotes.filter(q => q.eventId === eventId);
      assert.equal(fixture.length, 18);
      for (const book of ["Northstar", "Metro", "Prime"]) {
        const bookRows = fixture.filter(q => q.book === book);
        assert.equal(bookRows.length, 6);
        const home = fixture[0].home, away = fixture[0].away;
        const money = bookRows.filter(q => q.market === "moneyline");
        const spreads = bookRows.filter(q => q.market === "spread");
        const totals = bookRows.filter(q => q.market === "total");
        assert.deepEqual(new Set(money.map(q => q.selection)), new Set([home, away]));
        assert.deepEqual(new Set(spreads.map(q => q.selection)), new Set([home, away]));
        assert.equal(spreads[0].line + spreads[1].line, 0);
        assert.deepEqual(new Set(totals.map(q => q.selection)), new Set(["Over", "Under"]));
        assert.equal(totals[0].line, totals[1].line);
        assert.ok(totals[0].line >= expectedTotals[sport]);
      }
    }
    const gaps = findLineShopGaps(quotes);
    assert.ok(gaps.length > 0);
    assert.ok(gaps.every(g => g.state === "simulated"));
  });
}
