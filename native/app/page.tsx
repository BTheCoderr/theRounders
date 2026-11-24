import Dashboard from "../components/Dashboard";

export default function Home(){
 return <main className="home">
  <section className="hero">
   <p className="eyebrow">NBA · NFL · COLLEGE · NHL · MLB</p>
   <h1>Every pick on the record.</h1>
   <p className="heroSub">Winners, win probabilities, spreads and totals, locked before tip-off and graded after the final.</p>
  </section>
  <Dashboard/>
 </main>;
}
