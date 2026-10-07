import type {ProjectionSnapshot} from "./performance";

const KEY="rounders_projection_snapshots_v1";
export function loadSnapshots():ProjectionSnapshot[]{if(typeof window==="undefined")return[];try{return JSON.parse(localStorage.getItem(KEY)||"[]")}catch{return[]}}
export function saveSnapshot(snapshot:ProjectionSnapshot){if(typeof window==="undefined")return;const all=loadSnapshots();if(all.some(x=>x.id===snapshot.id))return;localStorage.setItem(KEY,JSON.stringify([snapshot,...all].slice(0,2000)))}
export function updateSnapshot(id:string,patch:Partial<ProjectionSnapshot>){if(typeof window==="undefined")return;const all=loadSnapshots().map(x=>x.id===id?{...x,...patch}:x);localStorage.setItem(KEY,JSON.stringify(all))}
