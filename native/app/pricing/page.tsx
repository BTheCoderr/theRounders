import Link from "next/link";
import {PLANS,type PlanId} from "../../lib/billing/plans";
import PlanButton from "../../components/PlanButton";

export const metadata={title:"Plans · The Rounders",description:"Free, Rounders Pro and Rounders Edge"};
const order:PlanId[]=["free","pro","edge"];
export default function Pricing(){
 return <main className="pricingPage">
  <Link className="policyBack" href="/">← Back to predictions</Link>
  <p className="eyebrow">PLANS</p><h1>Pay for depth, not for the record.</h1>
  <p className="muted">The track record, rankings, projected winners and model explanations are free for everyone. Paid plans add projections and tools built for people who model games themselves. No plan includes betting advice, guaranteed results or real-money wagering.</p>
  <div className="testBanner" role="note">Billing runs in Stripe test mode. No real card is charged; use Stripe's test card numbers.</div>
  <div className="planGrid">{order.map(id=>{const p=PLANS[id];return <article key={id} className={"planCard"+(id==="pro"?" featured":"")}>
   <p className="tag">{p.name.toUpperCase()}</p>
   <h2>{p.monthlyUsd?`$${p.monthlyUsd.toFixed(2)}`:"$0"}<small>{p.monthlyUsd?" / month":""}</small></h2>
   <ul>{p.pitch.map(x=><li key={x}>{x}</li>)}</ul>
   {id==="free"?<Link className="navAction" href="/">Use for free</Link>:<PlanButton plan={id} label={"Choose "+p.name}/>}
  </article>})}</div>
  <p className="muted small">Live market comparisons need live odds; until the odds provider is connected, Edge shows "not captured" for market lines. Cancel any time from your account: access continues to the end of the paid period. Prices are proposals in test mode.</p>
 </main>;
}
