import type {Metadata} from "next";
import {notFound} from "next/navigation";
import TeamPage,{type TeamData} from "../../../../components/TeamPage";
import {loadTeam} from "../../../../lib/persistence/pageData";
import {seasonText,sportFromSlug,sportTitle} from "../../../../lib/seoSports";

// Rendered on first visit, then cached and regenerated at most every 15 minutes.
export const dynamic="force-static";
export const revalidate=900;
export const dynamicParams=true;
export function generateStaticParams(){return [];}

type P={params:Promise<{sport:string;slug:string}>};
export async function generateMetadata({params}:P):Promise<Metadata>{
 const {sport:s,slug}=await params;const sport=sportFromSlug(s);if(!sport)return {};
 const data=await loadTeam(sport,slug);
 if(!data.ready)return {title:"Team · The Rounders",robots:data.status===404?{index:false}:undefined};
 const t=data.team,name=sportTitle(sport),season=seasonText(sport,data.season);
 const record=`${t.wins}-${t.losses}${t.ties?"-"+t.ties:""}`;
 const title=`${t.team} ${season} rating, record and picks · The Rounders`;
 const description=`${t.team}: #${t.rank} of ${data.teams} in the ${name} Power Index, ${record} this season${t.projWins!==undefined?`, projected ${Math.round(t.projWins)}-${Math.round(t.projLosses??0)}`:""}. Rating trend, results and every pregame pick.`;
 const path=`/teams/${sport.toLowerCase()}/${slug}`;
 return {title,description,alternates:{canonical:path},openGraph:{title,description,url:path},twitter:{title,description}};
}
export default async function Team({params}:P){
 const {sport:s,slug}=await params;const sport=sportFromSlug(s);if(!sport)notFound();
 const data=await loadTeam(sport,slug);
 if(!data.ready&&(data.status===404||data.status===400))notFound();
 return <TeamPage sport={sport} slug={slug} initial={data.ready?data as unknown as TeamData:null}/>;
}
