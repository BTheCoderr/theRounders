import type {Metadata} from "next";
import {notFound} from "next/navigation";
import Link from "next/link";
import RatingsTable,{type RatingsTableData} from "../../../components/RatingsTable";
import {loadRatings} from "../../../lib/persistence/pageData";
import {SPORT_SLUGS,seasonText,sportFromSlug,sportTitle} from "../../../lib/seoSports";

// Server-rendered from the same data as /api/team-ratings, regenerated at most every 15 minutes.
export const dynamic="force-static";
export const revalidate=900;
export const dynamicParams=false;
export function generateStaticParams(){return SPORT_SLUGS.map(sport=>({sport}));}

export async function generateMetadata({params}:{params:Promise<{sport:string}>}):Promise<Metadata>{
 const sport=sportFromSlug((await params).sport);if(!sport)return {};
 const data=await loadRatings(sport);
 const name=sportTitle(sport),season=data.ready?" "+seasonText(sport,data.season):"";
 const top=data.ready?data.rows.slice(0,3).map(r=>r.team).join(", "):"";
 const title=`${name}${season} team ratings · The Rounders`;
 const description=`${name} power ratings for every team: overall rating, offense, defense, strength of schedule${data.ready&&data.projected?" and projected final record":""}.${top?` Top teams: ${top}.`:""}`;
 const path=`/ratings/${sport.toLowerCase()}`;
 return {title,description,alternates:{canonical:path},openGraph:{title,description,url:path},twitter:{title,description}};
}

export default async function SportRatings({params}:{params:Promise<{sport:string}>}){
 const sport=sportFromSlug((await params).sport);if(!sport)notFound();
 const data=await loadRatings(sport);
 const initial=data.ready?data as unknown as RatingsTableData:null;
 const name=sportTitle(sport);
 return <main className="home">
  <section className="hero compact">
   <p className="eyebrow">POWER INDEX</p>
   <h1>{name} team ratings{data.ready?` ${seasonText(sport,data.season)}`:""}</h1>
   <p className="heroSub">Every {name} team rated from regular-season scores, adjusted for opponents and weighted toward recent games. Tap a column to sort, or a team to see its season.</p>
   {data.ready?<p className="fine">Top of the board: {data.rows.slice(0,3).map((r,i)=><span key={r.slug}>{i?", ":""}<Link href={`/teams/${sport.toLowerCase()}/${r.slug}`}>{r.team}</Link></span>)}. <Link href={`/history/${sport.toLowerCase()}`}>Past seasons</Link></p>:null}
  </section>
  <RatingsTable sport={sport} initial={initial}/>
 </main>;
}
