import test from "node:test";
import assert from "node:assert/strict";
import {scoreModel,sameGames} from "../lib/engine/scorecard.ts";
test("scorecard grades straight up, against the close and Brier on the same games",()=>{
 const s=scoreModel([
  {eventId:"1",projectedMargin:6,homeWinProbability:0.7,finalHome:100,finalAway:90,closeSpreadHome:-4},   // SU win, ATS win
  {eventId:"2",projectedMargin:2,homeWinProbability:0.56,finalHome:90,finalAway:95,closeSpreadHome:-4},  // SU loss, model likes away vs -4 -> ATS win
  {eventId:"3",projectedMargin:5,homeWinProbability:0.66,finalHome:94,finalAway:90,closeSpreadHome:-4}]); // push
 assert.deepEqual([s.su.wins,s.su.losses],[2,1]);assert.deepEqual([s.ats.wins,s.ats.losses,s.ats.pushes],[2,0,1]);
 assert.equal(s.games,3);assert.ok(s.brier>0&&s.brier<0.25);
 const same=sameGames({a:[{eventId:"1"},{eventId:"2"}],b:[{eventId:"2"},{eventId:"3"}]});
 assert.deepEqual(same.a.map(x=>x.eventId),["2"]);assert.deepEqual(same.b.map(x=>x.eventId),["2"]);
});
