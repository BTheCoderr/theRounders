"use client";
import {useSport} from "./useSport";
import SportBar from "./SportBar";
import Predictions from "./Predictions";
import PowerRankings from "./PowerRankings";
import Performance from "./Performance";
import MarketBoard from "./MarketBoard";

/** Sport switch shared by every section; remembered per browser and in the URL. */
export default function Dashboard(){
 const [sport,choose]=useSport();
 return <>
  <SportBar sport={sport} onChange={choose}/>
  <Predictions sport={sport}/>
  <Performance sport={sport}/>
  <PowerRankings sport={sport}/>
  <MarketBoard sport={sport}/>
 </>;
}
