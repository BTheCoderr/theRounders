import test from "node:test";
import assert from "node:assert/strict";
import {buildRatings,projectMatchup} from "../lib/ratings.ts";
import {createEvidence,explainFromModel,readResponseText,ANALYST_INSTRUCTIONS} from "../lib/aiInsights.ts";

const games=[
  {date:"2026-10-11",team:"Boston Celtics",opponent:"New York Knicks",teamScore:110,opponentScore:100,location:"home"},
  {date:"2026-10-11",team:"New York Knicks",opponent:"Boston Celtics",teamScore:100,opponentScore:110,location:"away"}
];
function evidence(fallback=false){
  const p=projectMatchup(buildRatings(games),"New York Knicks","Boston Celtics");
  assert.ok(p);
  return createEvidence("NBA",p,{
    trainingDataState:fallback?"simulated":"external",
    trainingProvider:fallback?"controlled-demo":"ESPN scoreboard",
    fallback,sampleGames:1
  });
}
test("model context is derived from real projection values, not guessed numbers",()=>{
  const e=evidence();
  assert.equal(e.home,"Boston Celtics");
  assert.equal(e.away,"New York Knicks");
  assert.ok(e.homeWinProbability>50);
  assert.equal(e.sampleGames,1);
  assert.equal(e.homeGames,1);
});
test("controlled simulated fallback is unmistakably labeled",()=>{
  const response=explainFromModel(evidence(true),"Who is favored?");
  assert.match(response,/SIMULATED history/);
  assert.match(response,/not a current-game prediction/);
  assert.match(response,/not calibrated or independently backtested/);
});
test("claims about injuries or live market moves are refused without evidence",()=>{
  const response=explainFromModel(evidence(),"What injuries caused the odds to move today?");
  assert.match(response,/do not have verified injury/);
  assert.match(response,/market-movement data/);
});
test("model confidence is disclosed as heuristic rather than measured accuracy",()=>{
  assert.match(explainFromModel(evidence(),"How confident are you?"),/heuristic/);
  assert.match(ANALYST_INSTRUCTIONS,/never outside knowledge/);
});
test("Responses API parser reads only output_text and ignores other parts",()=>{
  const text=readResponseText({output:[{type:"message",content:[{type:"output_text",text:"Model says Boston has the edge."},{type:"refusal",text:"ignore this"}]}]});
  assert.equal(text,"Model says Boston has the edge.");
  assert.equal(readResponseText({output:[]}),null);
});
