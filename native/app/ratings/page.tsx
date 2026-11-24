import RatingsTable from "../../components/RatingsTable";
export const metadata={title:"Ratings · The Rounders",description:"NBA and NFL team ratings: overall, offense, defense and strength of schedule."};
export default function Ratings(){
 return <main className="home">
  <section className="hero compact">
   <p className="eyebrow">POWER INDEX</p>
   <h1>Every team, rated.</h1>
   <p className="heroSub">Schedule-adjusted ratings from every regular-season score. Tap a column to sort, a team to see its season.</p>
  </section>
  <RatingsTable/>
 </main>;
}
