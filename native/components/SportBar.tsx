"use client";
import {PRODUCT_SPORTS,type ProductSport} from "../lib/clientTypes";
export default function SportBar({sport,onChange}:{sport:ProductSport;onChange:(s:ProductSport)=>void}){
 return <div className="sportBar" role="tablist" aria-label="Sport">
  {PRODUCT_SPORTS.map(s=><button key={s} role="tab" aria-selected={s===sport} className={s===sport?"on":""} onClick={()=>onChange(s)}>{s}</button>)}
 </div>;
}
