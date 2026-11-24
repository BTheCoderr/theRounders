import test from "node:test";
import assert from "node:assert/strict";
import {createHmac} from "node:crypto";
import {PLANS,entitledPlan,hasFeature,planForPrice} from "../lib/billing/plans.ts";
import {formEncode,stripeKey,subscriptionRow,verifyStripeSignature} from "../lib/billing/stripe.ts";
import {gatePrediction} from "../lib/billing/gating.ts";
import {toCsv} from "../lib/billing/csv.ts";

const now=new Date("2026-11-23T12:00:00Z");
const future="2026-12-23T12:00:00.000Z",past="2026-11-01T00:00:00.000Z";

test("plans: proposed prices and feature ladder",()=>{
 assert.equal(PLANS.pro.monthlyUsd,19.99);assert.equal(PLANS.edge.monthlyUsd,39.99);
 assert.ok(hasFeature("free","predictions.winner"));
 assert.ok(!hasFeature("free","predictions.lines"));
 assert.ok(hasFeature("pro","predictions.lines")&&!hasFeature("pro","predictions.market"));
 for(const f of PLANS.pro.features)assert.ok(hasFeature("edge",f),"edge includes everything in pro: "+f);
});

test("entitlements follow subscription status and the paid period",()=>{
 const s=(plan,status,end=future,cancel=false)=>({plan,status,current_period_end:end,cancel_at_period_end:cancel});
 assert.equal(entitledPlan([],now),"free");
 assert.equal(entitledPlan([s("pro","active")],now),"pro");
 assert.equal(entitledPlan([s("pro","active",future,true)],now),"pro","cancellation keeps access to period end");
 assert.equal(entitledPlan([s("pro","active",past,true)],now),"free","access ends with the period");
 assert.equal(entitledPlan([s("edge","trialing")],now),"edge");
 assert.equal(entitledPlan([s("edge","past_due")],now),"edge");
 assert.equal(entitledPlan([s("edge","past_due",past)],now),"free");
 for(const status of ["canceled","unpaid","incomplete","incomplete_expired","paused"])assert.equal(entitledPlan([s("edge",status)],now),"free",status);
 assert.equal(entitledPlan([s("pro","active"),s("edge","active")],now),"edge");
 assert.equal(entitledPlan([s(null,"active")],now),"free","unknown price grants nothing");
});

test("price IDs map to plans only through configuration",()=>{
 const env={STRIPE_PRICE_PRO:"price_pro1",STRIPE_PRICE_EDGE:"price_edge1"};
 assert.equal(planForPrice("price_pro1",env),"pro");
 assert.equal(planForPrice("price_edge1",env),"edge");
 assert.equal(planForPrice("price_other",env),null);
 assert.equal(planForPrice(null,env),null);
});

test("only Stripe test keys are accepted",()=>{
 assert.equal(stripeKey({STRIPE_SECRET_KEY:"sk_test_abc123"}),"sk_test_abc123");
 assert.equal(stripeKey({STRIPE_SECRET_KEY:"rk_test_abc123"}),"rk_test_abc123");
 assert.throws(()=>stripeKey({STRIPE_SECRET_KEY:"sk_live_abc123"}),/non-test/);
 assert.throws(()=>stripeKey({STRIPE_SECRET_KEY:"rk_live_abc123"}),/non-test/);
 assert.throws(()=>stripeKey({}),/not configured/);
});

test("form encoding matches Stripe's nested syntax",()=>{
 const s=formEncode({mode:"subscription",line_items:[{price:"price_1",quantity:1}],metadata:{user_id:"u"},skip:undefined});
 assert.equal(decodeURIComponent(s),"mode=subscription&line_items[0][price]=price_1&line_items[0][quantity]=1&metadata[user_id]=u");
});

test("webhook signatures: valid, tampered, stale and rotated secrets",()=>{
 const secret="whsec_test",payload='{"id":"evt_1"}',t=1764000000;
 const sig=createHmac("sha256",secret).update(`${t}.${payload}`).digest("hex");
 assert.ok(verifyStripeSignature(payload,`t=${t},v1=${sig}`,secret,t));
 assert.ok(verifyStripeSignature(payload,`t=${t},v1=${"0".repeat(64)},v1=${sig}`,secret,t),"any matching v1 passes");
 assert.ok(!verifyStripeSignature(payload+" ",`t=${t},v1=${sig}`,secret,t));
 assert.ok(!verifyStripeSignature(payload,`t=${t},v1=${sig}`,"whsec_other",t));
 assert.ok(!verifyStripeSignature(payload,`t=${t},v1=${sig}`,secret,t+301),"replay outside tolerance");
 assert.ok(!verifyStripeSignature(payload,null,secret,t));
 assert.ok(!verifyStripeSignature(payload,`t=${t},v0=${sig}`,secret,t));
});

test("subscription rows read period end from the item on newer API versions",()=>{
 const env={STRIPE_PRICE_PRO:"price_pro1"};
 const row=subscriptionRow({id:"sub_1",customer:"cus_1",status:"active",cancel_at_period_end:true,livemode:false,
  items:{data:[{price:{id:"price_pro1"},current_period_end:1767000000}]}},"00000000-0000-0000-0000-000000000001",env);
 assert.equal(row.plan,"pro");assert.equal(row.cancel_at_period_end,true);
 assert.equal(row.current_period_end,new Date(1767000000*1000).toISOString());
 assert.equal(row.stripe_customer_id,"cus_1");
 assert.equal(subscriptionRow({id:"sub_2",customer:{id:"cus_2"},status:"canceled",current_period_end:1767000000,items:{data:[{price:{id:"price_x"}}]}},"u",env).plan,null);
});

test("server-side gating removes paid fields for free users",()=>{
 const p={eventId:"1",projectedWinner:"A",homeWinProbability:0.6,projectedHome:110,projectedAway:104,projectedSpreadHome:-6,projectedTotal:214,market:{spreadHome:-4,total:216}};
 const free=gatePrediction(p,"free");
 assert.equal(free.projectedSpreadHome,null);assert.equal(free.projectedTotal,null);assert.equal(free.market,null);
 assert.equal(free.homeWinProbability,0.6);assert.equal(free.projectedWinner,"A");
 assert.deepEqual(free.locked,["spread","total","score","market"]);
 const pro=gatePrediction(p,"pro");
 assert.equal(pro.projectedTotal,214);assert.equal(pro.market,null);assert.deepEqual(pro.locked,["market"]);
 const edge=gatePrediction(p,"edge");
 assert.deepEqual(edge.market,{spreadHome:-4,total:216});assert.deepEqual(edge.locked,[]);
 assert.equal(p.projectedTotal,214,"input is not mutated");
});

test("CSV quoting and formula-injection protection",()=>{
 assert.equal(toCsv(["a","b"],[["x,y",'say "hi"'],["=SUM(A1)",-3.5],[null,true]]),'a,b\r\n"x,y","say ""hi"""\r\n\'=SUM(A1),-3.5\r\n,true\r\n');
});
