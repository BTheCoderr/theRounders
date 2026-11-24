"use client";
import {PRODUCT_SPORTS,SPORT_LABEL,SPORT_NAME,type ProductSport} from "../lib/clientTypes";
export default function SportBar({sport,onChange}:{sport:ProductSport;onChange:(s:ProductSport)=>void}){
 return <div className="sportBar" role="tablist" aria-label="Sport">
  {PRODUCT_SPORTS.map(s=><button key={s} role="tab" aria-selected={s===sport} title={SPORT_NAME[s]} className={s===sport?"on":""} onClick={()=>onChange(s)}>{SPORT_LABEL[s]}</button>)}
 </div>;
}
