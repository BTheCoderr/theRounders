import type {Metadata} from "next";
import {notFound} from "next/navigation";
import HistoryView from "../../../../components/HistoryView";
import {loadHistory} from "../../../../lib/persistence/pageData";
import {seasonText,sportFromSlug,sportTitle} from "../../../../lib/seoSports";

export const dynamic="force-static";
export const revalidate=86400;
export const dynamicParams=true;
export function generateStaticParams(){return [];}

type P={params:Promise<{sport:string;season:string}>};
const parse=async(params:P["params"])=>{const p=await params;const sport=sportFromSlug(p.sport),season=Number(p.season);
 return sport&&/^(19|20)\d{2}$/.test(p.season)?{sport,season}:null;};
export async function generateMetadata({params}:P):Promise<Metadata>{
 const p=await parse(params);if(!p)return {};
 const data=await loadHistory(p.sport,p.season);
 if(!data.ready||data.season!==p.season)return {title:"Season not found · The Rounders",robots:{index:false}};
 const name=sportTitle(p.sport),season=seasonText(p.sport,p.season),top=data.rows.slice(0,3).map(r=>r.team).join(", ");
 const title=`${name} ${season} final team ratings · The Rounders`;
 const description=`Final regular-season ${name} power ratings for ${season}. Top teams: ${top}.`;
 const path=`/history/${p.sport.toLowerCase()}/${p.season}`;
 return {title,description,alternates:{canonical:path},openGraph:{title,description,url:path},twitter:{title,description}};
}
export default async function SeasonHistory({params}:P){
 const p=await parse(params);if(!p)notFound();
 const data=await loadHistory(p.sport,p.season);
 // An unarchived season would silently fall back to another one: treat it as not found instead.
 if(data.ready&&data.season!==p.season)notFound();
 return <HistoryView sport={p.sport} data={data}/>;
}
