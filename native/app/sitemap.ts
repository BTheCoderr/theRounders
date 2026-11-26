import type {MetadataRoute} from "next";
import {siteOrigin} from "./site-origin";
export const revalidate=86400;
const pages=["/","/record","/pricing","/methodology","/faq","/terms","/support","/privacy"];
const sports=["nba","nfl","ncaam","ncaaf","nhl","mlb"];
const SLUG=/^[a-z0-9]+(?:-[a-z0-9]+)*$/;
async function json(url:string):Promise<Record<string,unknown>|null>{
 try{
  const response=await fetch(url,{next:{revalidate:86400},signal:AbortSignal.timeout(15000)});
  return response.ok?await response.json() as Record<string,unknown>:null;
 }catch{return null}
}
/**
 * Every public page: static pages, one ratings and one history page per sport, each
 * archived season, and every current team. A sport whose data fails is skipped.
 */
export default async function sitemap():Promise<MetadataRoute.Sitemap>{
 const origin=siteOrigin();
 const perSport=await Promise.all(sports.map(async sport=>{
  const urls:MetadataRoute.Sitemap=[{url:`${origin}/ratings/${sport}`,changeFrequency:"daily"},{url:`${origin}/history/${sport}`}];
  const [ratings,history]=await Promise.all([json(`${origin}/api/team-ratings?sport=${sport.toUpperCase()}`),json(`${origin}/api/history?sport=${sport.toUpperCase()}`)]);
  if(ratings?.ready===true&&Array.isArray(ratings.rows)){
   const slugs=new Set<string>();
   for(const row of ratings.rows as Array<{slug?:unknown}>)if(typeof row?.slug==="string"&&SLUG.test(row.slug))slugs.add(row.slug);
   for(const slug of slugs)urls.push({url:`${origin}/teams/${sport}/${slug}`,changeFrequency:"daily"});
  }
  if(Array.isArray(history?.seasons))
   for(const y of history.seasons as unknown[])if(typeof y==="number"&&Number.isInteger(y)&&y>=1900&&y<=2200)urls.push({url:`${origin}/history/${sport}/${y}`});
  return urls;
 }));
 return [...pages.map(path=>({url:origin+path})),...perSport.flat()];
}
