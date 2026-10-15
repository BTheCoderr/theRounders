import test from "node:test";
import assert from "node:assert/strict";
import { SPORTS, demoQuotes, groupQuotes, getPriceGaps } from "../src/markets.ts";

for (const sport of SPORTS) {
 test(`${sport} local demo shows both selections and only simulated prices`, () => {
  const quotes = demoQuotes(sport);
  assert.equal(quotes.length, 24); // 2 games × 3 markets × 2 sides × 2 books
  assert.ok(quotes.every(q => q.state === "simulated" && q.sport === sport));
  assert.equal(new Set(quotes.map(q => q.eventId)).size, 2);
  for (const eventId of new Set(quotes.map(q => q.eventId))) {
   const game = quotes.filter(q => q.eventId === eventId);
   for (const market of ["moneyline", "spread", "total"]) {
    const rows = game.filter(q => q.market === market);
    assert.equal(rows.length, 4);
    assert.equal(new Set(rows.map(q => q.selection)).size, 2);
    if(market === "total") assert.deepEqual(new Set(rows.map(q=>q.selection)),new Set(["Over","Under"]));
    if(market === "spread") {
     const lines=[...new Set(rows.map(q=>q.line))];
     assert.equal(lines.length,2);
     assert.equal(lines[0]+lines[1],0);
     if(sport === "NHL" || sport === "MLB") assert.ok(lines.every(line=>Math.abs(line)===1.5));
    }
   }
  }
  assert.equal(groupQuotes(quotes,"moneyline").length,4);
  assert.equal(groupQuotes(quotes,"spread").length,4);
  assert.equal(groupQuotes(quotes,"total").length,4);
  assert.ok(getPriceGaps(quotes).length>0);
 });
}
