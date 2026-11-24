import RatingsTable from "../../components/RatingsTable";
export const metadata={title:"History · The Rounders",description:"Final Power Index ratings for past NBA, NFL, college, NHL and MLB seasons."};
export default function History(){
 return <main className="home">
  <section className="hero compact">
   <p className="eyebrow">THE ARCHIVE</p>
   <h1>Every season, rated.</h1>
   <p className="heroSub">Final regular-season ratings for past seasons, computed the same way as today's.</p>
  </section>
  <RatingsTable historical/>
 </main>;
}
