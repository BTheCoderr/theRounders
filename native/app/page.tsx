import Dashboard from "../components/Dashboard";
import PaperBankroll from "../components/PaperBankroll";
import SharpSignals from "../components/SharpSignals";
import AccountAccess from "../components/AccountAccess";

export default function Home(){
 return <main>
  <header><div><p className="eyebrow">THE ROUNDERS · NBA & NFL</p><h1>Predictions with a public record.</h1>
   <p className="muted">Daily NBA and weekly NFL projections: winners, win probabilities, spreads and totals. Every prediction is frozen before the game and graded after it, and the full track record is free to inspect.</p></div>
   <div className="headerActions"><span className="pill">RESEARCH · NO WAGERING</span><a className="navAction" href="/pricing">Plans</a></div></header>
  <AccountAccess/>
  <section className="status"><span>Data labels: <b className="state model">MODEL</b> projection · <b className="state live">LIVE</b> provider price · <b className="state simulated">SIMULATED</b> demo data</span></section>
  <Dashboard/>
  <SharpSignals/>
  <PaperBankroll/>
 </main>;
}
