import test from "node:test";
import assert from "node:assert/strict";
import {buildRatings,projectMatchup,marketEdge} from "../lib/ratings.ts";
import {completedTeamGames} from "../lib/results/espn.ts";

test("opponent-adjusted power converges on a mirrored two-team schedule",()=>{
 const games=[
  {date:"2026-10-11",team:"Boston Celtics",opponent:"New York Knicks",teamScore:110,opponentScore:100,location:"home"},
  {date:"2026-10-11",team:"New York Knicks",opponent:"Boston Celtics",teamScore:100,opponentScore:110,location:"away"}
 ];
 const ratings=buildRatings(games,24);
 const bos=ratings.get("Boston Celtics"),ny=ratings.get("New York Knicks");
 assert.ok(bos&&ny);
 assert.ok(Math.abs(bos.power-5)<0.01, "winner should be about +5, not 0 or +10");
 assert.ok(Math.abs(ny.power+5)<0.01, "loser should be about -5");
 const projection=projectMatchup(ratings,"New York Knicks","Boston Celtics");
 assert.ok(projection);
 assert.ok(Number.isFinite(projection.homeWinProbability));
 assert.ok(projection.homeWinProbability>50);
});

test("completed ESPN rows use full market-compatible team names",()=>{
 const events=[{date:"2026-10-11T19:00:00Z",status:{type:{completed:true}},competitions:[{competitors:[
  {homeAway:"home",score:"110",team:{displayName:"Boston Celtics",abbreviation:"BOS"}},
  {homeAway:"away",score:"100",team:{displayName:"New York Knicks",abbreviation:"NYK"}}
 ]}]},
 {status:{type:{completed:false}},competitions:[{competitors:[
  {homeAway:"home",score:"0",team:{displayName:"Boston Celtics"}},
  {homeAway:"away",score:"0",team:{displayName:"New York Knicks"}}
 ]}]}];
 const rows=completedTeamGames(events);
 assert.equal(rows.length,2);
 assert.equal(rows[0].team,"Boston Celtics");
 assert.equal(rows[1].team,"New York Knicks");
 assert.equal(rows[0].location,"home");
 assert.equal(rows[1].location,"away");
});

test("missing scores and invalid matchup data are excluded",()=>{
 assert.deepEqual(completedTeamGames([{status:{type:{completed:true}},competitions:[{competitors:[
  {homeAway:"home",team:{displayName:"Boston Celtics"}},
  {homeAway:"away",score:"2",team:{displayName:"New York Knicks"}}
 ]}]}]),[]);
});

test("edge remains model probability minus implied sportsbook probability",()=>{
 const r=marketEdge(60,-110);
 assert.ok(Math.abs(r.implied-52.38095)<0.01);
 assert.ok(Math.abs(r.edge-7.61905)<0.01);
});
