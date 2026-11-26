import type {Metadata} from "next";
import {notFound} from "next/navigation";
import HistoryView from "../../../components/HistoryView";
import {loadHistory} from "../../../lib/persistence/pageData";
import {seasonText,sportFromSlug,sportTitle} from "../../../lib/seoSports";

// Latest completed season for the sport; past seasons do not change, so regenerate daily.
export const dynamic="force-static";
export const revalidate=86400;
export const dynamicParams=true;
export function generateStaticParams(){return [];}

export async function generateMetadata({params}:{params:Promise<{sport:string}>}):Promise<Metadata>{
 const sport=sportFromSlug((await params).sport);if(!sport)return {};
 const data=await loadHistory(sport,null);
 const name=sportTitle(sport),season=data.ready?seasonText(sport,data.season):"";
 const title=`${name} ${season} final team ratings · The Rounders`.replace("  "," ");
 const description=`Final regular-season ${name} power ratings${season?" for "+season:""}, plus every archived season.`;
 const canonical=data.ready?`/history/${sport.toLowerCase()}/${data.season}`:`/history/${sport.toLowerCase()}`;
 return {title,description,alternates:{canonical},openGraph:{title,description,url:canonical},twitter:{title,description}};
}
export default async function SportHistory({params}:{params:Promise<{sport:string}>}){
 const sport=sportFromSlug((await params).sport);if(!sport)notFound();
 return <HistoryView sport={sport} data={await loadHistory(sport,null)}/>;
}
