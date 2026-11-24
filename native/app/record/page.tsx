import TrackRecord from "../../components/TrackRecord";
export const metadata={title:"Track record · The Rounders",description:"Every NBA and NFL pick, stored before the game and graded after it."};
export default function Record(){
 return <main className="home">
  <section className="hero compact">
   <p className="eyebrow">PUBLIC LEDGER</p>
   <h1>Every pick, right or wrong.</h1>
   <p className="heroSub">Locked before tip-off or kickoff, graded after the final, never edited.</p>
  </section>
  <TrackRecord/>
 </main>;
}
