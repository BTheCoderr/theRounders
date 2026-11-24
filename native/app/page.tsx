import Dashboard from "../components/Dashboard";
import PaperBankroll from "../components/PaperBankroll";
import SharpSignals from "../components/SharpSignals";

export default function Home(){
 return <main className="home">
  <section className="hero">
   <p className="eyebrow">NBA · NFL · COLLEGE · NHL · MLB</p>
   <h1>Every pick on the record.</h1>
   <p className="heroSub">Winners, win probabilities, spreads and totals, locked before tip-off and graded after the final.</p>
  </section>
  <Dashboard/>
  <section className="tools" aria-label="Tools">
   <details><summary><span>Price gaps across books</span><small>Same game, same line, different prices</small></summary><SharpSignals/></details>
   <details><summary><span>Paper bankroll</span><small>Track picks without real money</small></summary><PaperBankroll/></details>
  </section>
 </main>;
}
