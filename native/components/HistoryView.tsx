import Link from "next/link";
import RatingsTable,{type RatingsTableData} from "./RatingsTable";
import type {HistoryPayload,NotReady} from "../lib/persistence/pageData";
import {seasonText,sportTitle} from "../lib/seoSports";
import type {Sport} from "../lib/sports";

/** Server-rendered body shared by /history/<sport> and /history/<sport>/<season>. */
export default function HistoryView({sport,data}:{sport:Sport;data:HistoryPayload|NotReady}){
 const name=sportTitle(sport);
 const champ=data.ready?data.rows[0]:null;
 return <main className="home">
  <section className="hero compact">
   <p className="eyebrow">THE ARCHIVE</p>
   <h1>{name} final ratings{data.ready?` ${seasonText(sport,data.season)}`:""}</h1>
   <p className="heroSub">Final regular-season Power Index ratings, computed the same way as today&apos;s, from that season&apos;s results only.</p>
   {champ?<p className="fine">Top-rated team that season: {champ.team} ({champ.wins}-{champ.losses}{champ.ties?"-"+champ.ties:""}). <Link href={`/ratings/${sport.toLowerCase()}`}>This season&apos;s ratings</Link></p>:null}
  </section>
  <RatingsTable sport={sport} initial={data.ready?data as unknown as RatingsTableData:null} historical/>
 </main>;
}
