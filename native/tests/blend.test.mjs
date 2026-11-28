import test from "node:test";
import assert from "node:assert/strict";
import {learnWeight,blendGame,probit,blendProb,BLEND_PRIOR_WEIGHT} from "../lib/engine/blend.ts";
import {normalCdf} from "../lib/engine/metrics.ts";

test("probit inverts the normal CDF",()=>{for(const p of [0.01,0.2,0.5,0.73,0.99])assert.ok(Math.abs(normalCdf(probit(p))-p)<1e-6,String(p));});
test("weight starts at the prior and learns toward the better input",()=>{
 assert.equal(learnWeight("NBA",[]).weight,BLEND_PRIOR_WEIGHT);
 let seed=9;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
 const mk=(modelNoise,marketNoise)=>Array.from({length:3000},()=>{const truth=(rnd()-0.5)*20;
  return {modelMargin:truth+(rnd()-0.5)*modelNoise,modelProb:0.5,marketSpreadHome:-(truth+(rnd()-0.5)*marketNoise),marketProb:null,finalMargin:truth+(rnd()-0.5)*10};});
 const marketBetter=learnWeight("NBA",mk(20,4)),modelBetter=learnWeight("NBA",mk(4,20));
 assert.ok(marketBetter.weight<0.25,String(marketBetter.weight));assert.ok(modelBetter.weight>0.7,String(modelBetter.weight));
 assert.equal(marketBetter.games,3000);
});
test("blendGame: spread sports average margins; NHL/MLB blend probabilities; no line, no pick",()=>{
 const g=blendGame("NBA",{margin:8,total:220,prob:0.75},{spreadHome:-4,total:224,homeProb:0.62},0.25,12);
 assert.equal(g.margin,5);assert.equal(g.total,223);assert.ok(g.prob>0.6&&g.prob<0.7);
 assert.equal(blendGame("NBA",{margin:8,total:220,prob:0.75},{spreadHome:null,total:null,homeProb:0.6},0.25,12),null);
 const h=blendGame("NHL",{margin:0.6,total:6,prob:0.6},{spreadHome:-1.5,total:6,homeProb:0.5},0.5,2.3);
 assert.ok(h.prob>0.5&&h.prob<0.6&&h.margin>0);
 assert.equal(blendGame("NHL",{margin:0.6,total:6,prob:0.6},{spreadHome:-1.5,total:6,homeProb:null},0.5,2.3),null);
 assert.ok(Math.abs(blendProb(0.7,0.7,0.3)-0.7)<1e-9);
});
