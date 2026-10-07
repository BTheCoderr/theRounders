import type {ProjectionSnapshot} from "../performance";
const url=()=>process.env.SUPABASE_URL||process.env.NEXT_PUBLIC_SUPABASE_URL;
const key=()=>process.env.SUPABASE_SERVICE_ROLE_KEY;
export function persistenceConfigured(){return Boolean(url()&&key())}
async function request(path:string,init?:RequestInit){
 const base=url(),token=key();if(!base||!token)throw new Error("Central persistence is not configured");
 const r=await fetch(base+"/rest/v1/"+path,{...init,headers:{apikey:token,Authorization:"Bearer "+token,"Content-Type":"application/json",Prefer:"return=representation",...(init?.headers||{})},cache:"no-store"});
 if(!r.ok)throw new Error("Persistence request failed: "+r.status);return r;
}
export async function listSnapshots(limit=500):Promise<ProjectionSnapshot[]>{
 const r=await request("model_projections?select=*&order=created_at.desc&limit="+Math.min(limit,2000));
 const rows=await r.json();return rows.map(fromRow);
}
export async function putSnapshot(s:ProjectionSnapshot){
 const row=toRow(s);await request("model_projections?on_conflict=id",{method:"POST",headers:{Prefer:"resolution=ignore-duplicates,return=minimal"},body:JSON.stringify(row)});
}
const toRow=(s:ProjectionSnapshot)=>({id:s.id,event_id:s.eventId,sport:s.sport,away:s.away,home:s.home,created_at:s.createdAt,model_version:s.modelVersion,training_provider:s.trainingProvider,training_data_state:s.trainingDataState,projected_away:s.projectedAway,projected_home:s.projectedHome,fair_spread_home:s.fairSpreadHome,home_win_probability:s.homeWinProbability,confidence:s.confidence,market:s.market||null,closing:s.closing||null,final:s.final||null});
const fromRow=(r:any):ProjectionSnapshot=>({id:r.id,eventId:r.event_id,sport:r.sport,away:r.away,home:r.home,createdAt:r.created_at,modelVersion:r.model_version,trainingProvider:r.training_provider,trainingDataState:r.training_data_state,projectedAway:r.projected_away,projectedHome:r.projected_home,fairSpreadHome:r.fair_spread_home,homeWinProbability:r.home_win_probability,confidence:r.confidence,market:r.market||undefined,closing:r.closing||undefined,final:r.final||undefined});
