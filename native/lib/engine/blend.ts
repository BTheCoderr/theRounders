import {normalCdf} from "./metrics.ts";
import type {Sport} from "../sports.ts";

/**
 * Rounders Market Blend v1: our rating combined with the sportsbook line.
 *   margin = w * model + (1 - w) * market      (spread sports; market margin = -home spread)
 *   p      = logistic(w * logit(p_model) + (1 - w) * logit(p_market))   (NHL/MLB, moneyline)
 * The model weight w is learned from our own graded games against the line captured before
 * start, by grid search on squared margin error (spread sports) or Brier (NHL/MLB), and shrunk
 * toward a documented prior until enough games exist. Nothing is tuned on the game being predicted.
 */
export const BLEND_MODEL="blend-v1";
export const BLEND_PRIOR_WEIGHT=0.35;   // markets are usually the stronger input; the data moves this
export const BLEND_PRIOR_GAMES=150;
export const PROB_SPORTS=new Set<Sport>(["NHL","MLB"]);

export type BlendTraining={modelMargin:number;modelProb:number;marketSpreadHome:number|null;marketProb:number|null;finalMargin:number};
const logit=(p:number)=>Math.log(p/(1-p));
const clampP=(p:number)=>Math.min(0.995,Math.max(0.005,p));
export const blendProb=(pm:number,pk:number,w:number)=>clampP(1/(1+Math.exp(-(w*logit(clampP(pm))+(1-w)*logit(clampP(pk))))));

/** Learned model weight and the evidence behind it. */
export function learnWeight(sport:Sport,rows:readonly BlendTraining[]):{weight:number;games:number;raw:number|null}{
 const prob=PROB_SPORTS.has(sport);
 const use=rows.filter(r=>Number.isFinite(r.finalMargin)&&(prob?(r.marketProb!==null&&r.finalMargin!==0):r.marketSpreadHome!==null));
 if(!use.length)return {weight:BLEND_PRIOR_WEIGHT,games:0,raw:null};
 let best=0,bestLoss=Infinity;
 for(let i=0;i<=20;i++){
  const w=i/20;let loss=0;
  for(const r of use){
   if(prob){const y=r.finalMargin>0?1:0;loss+=(blendProb(r.modelProb,r.marketProb!,w)-y)**2;}
   else{const m=w*r.modelMargin+(1-w)*(-r.marketSpreadHome!);loss+=(m-r.finalMargin)**2;}
  }
  if(loss<bestLoss-1e-12){bestLoss=loss;best=w;}
 }
 const n=use.length;
 const weight=(n*best+BLEND_PRIOR_GAMES*BLEND_PRIOR_WEIGHT)/(n+BLEND_PRIOR_GAMES);
 return {weight:Number(weight.toFixed(3)),games:n,raw:best};
}

/** Inverse standard normal (Acklam's approximation), for turning a probability back into a margin. */
export function probit(p:number):number{
 const a=[-39.69683028665376,220.9460984245205,-275.9285104469687,138.357751867269,-30.66479806614716,2.506628277459239];
 const b=[-54.47609879822406,161.5858368580409,-155.6989798598866,66.80131188771972,-13.28068155288572];
 const c=[-0.007784894002430293,-0.3223964580411365,-2.400758277161838,-2.549732539343734,4.374664141464968,2.938163982698783];
 const d=[0.007784695709041462,0.3224671290700398,2.445134137142996,3.754408661907416];
 const q0=Math.min(1-1e-9,Math.max(1e-9,p)),lo=0.02425;
 if(q0<lo){const q=Math.sqrt(-2*Math.log(q0));return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
 if(q0>1-lo){const q=Math.sqrt(-2*Math.log(1-q0));return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
 const q=q0-0.5,r=q*q;
 return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
}

/** Blended margin, total and home win probability for one game, or null without a usable line. */
export function blendGame(sport:Sport,base:{margin:number;total:number;prob:number},line:{spreadHome:number|null;total:number|null;homeProb:number|null},w:number,sigma:number){
 if(PROB_SPORTS.has(sport)){
  if(line.homeProb===null||!Number.isFinite(line.homeProb))return null;
  const p=blendProb(base.prob,line.homeProb,w);
  return {margin:sigma*probit(p),total:base.total,prob:p};
 }
 if(line.spreadHome===null||!Number.isFinite(line.spreadHome))return null;
 const margin=w*base.margin+(1-w)*(-line.spreadHome);
 const total=line.total!==null&&Number.isFinite(line.total)?w*base.total+(1-w)*line.total:base.total;
 return {margin,total,prob:clampP(normalCdf(margin/sigma))};
}
