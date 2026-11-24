import type {MetadataRoute} from "next";
import {siteOrigin} from "./site-origin";
export const revalidate=86400;
const pages=["/","/ratings","/record","/history","/pricing","/methodology","/faq","/terms","/support","/privacy"];
const sports=["nba","nfl","ncaam","ncaaf","nhl","mlb"];
export default async function sitemap():Promise<MetadataRoute.Sitemap>{
 const origin=siteOrigin();
 const teams=await Promise.all(sports.map(async sport=>{
  try{
   const response=await fetch(origin+"/api/team-ratings?sport="+sport.toUpperCase(),{next:{revalidate:86400},signal:AbortSignal.timeout(15000)});
   if(!response.ok)return [];
   const data=await response.json();
   if(data.ready!==true||!Array.isArray(data.rows))return [];
   const slugs=new Set<string>();
   for(const row of data.rows){if(typeof row?.slug==="string"&&/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(row.slug))slugs.add(row.slug)}
   return [...slugs].map(slug=>({url:origin+"/teams/"+sport+"/"+encodeURIComponent(slug)}));
  }catch{return []}
 }));
 return [...pages.map(path=>({url:origin+path})),...teams.flat()];
}
