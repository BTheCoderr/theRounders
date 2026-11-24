"use client";
import {useSport} from "./useSport";
import SportBar from "./SportBar";
import Predictions from "./Predictions";
import PowerRankings from "./PowerRankings";
import Performance from "./Performance";
import MarketBoard from "./MarketBoard";
import SharpSignals from "./SharpSignals";
import PaperBankroll from "./PaperBankroll";

/** Sport switch shared by every section; remembered per browser and in the URL. */
export default function Dashboard(){
 const [sport,choose]=useSport();
 return <>
  <SportBar sport={sport} onChange={choose}/>
  <Predictions sport={sport}/>
  <Performance sport={sport}/>
  <PowerRankings sport={sport}/>
  <MarketBoard key={sport} sport={sport}/>
  <section className="tools" aria-label="Tools">
   <details><summary><span>Price gaps across books</span><small>Same game, same line, different prices</small></summary><SharpSignals key={sport} sport={sport}/></details>
   <details><summary><span>Paper bankroll</span><small>Track picks without real money · all sports</small></summary><PaperBankroll/></details>
  </section>
 </>;
}
