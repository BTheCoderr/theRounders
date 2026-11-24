import PlanCards from "../../components/PlanCards";

export const metadata={title:"Plans · The Rounders",description:"Free, Rounders Pro and Rounders Edge"};
export default function Pricing(){
 return <main className="pricingPage">
  <section className="hero compact">
   <p className="eyebrow">PLANS</p>
   <h1>Pay for depth, not for the record.</h1>
   <p className="heroSub">Winners, rankings and the full track record stay free. Paid plans add the numbers serious modelers want.</p>
  </section>
  <div className="testBanner" role="note">Test mode: no real cards are charged. Use card 4242 4242 4242 4242.</div>
  <PlanCards/>
  <p className="fine center">Cancel anytime; access continues to the end of the paid period. No plan includes betting advice or guaranteed results.</p>
 </main>;
}
