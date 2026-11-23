import React,{useEffect,useState} from "react";
import {ActivityIndicator,StyleSheet,Text,View} from "react-native";
import {fetchPerformance,type Performance,type Summary} from "../api";
import type {Sport} from "../markets";
import {theme} from "../theme";

const pct=(x:number|null)=>x===null?"—":(x*100).toFixed(1)+"%";
const n=(x:number|null,d=2)=>x===null?"—":x.toFixed(d);
function Tiles({s}:{s:Summary}){
 const t:[string,string][]=[["GAMES",String(s.games)],["ACCURACY",pct(s.winnerAccuracy)],["BRIER",n(s.brierScore,3)],["SPREAD ERR",n(s.marginMAE,1)],["TOTAL ERR",n(s.totalMAE,1)]];
 return <View style={styles.tiles}>{t.map(([a,b])=><View key={a} style={styles.tile}><Text style={styles.label}>{a}</Text><Text style={styles.value}>{b}</Text></View>)}</View>;
}
export function PerformancePanel({sport,demo}:{sport:Sport;demo:boolean}){
 const [d,setD]=useState<Performance|null>(null),[error,setError]=useState(""),[loading,setLoading]=useState(false);
 useEffect(()=>{
  let active=true;setD(null);setError("");
  if(demo){setLoading(false);return()=>{active=false}}
  setLoading(true);
  void fetchPerformance(sport).then(x=>{if(active)setD(x)}).catch(e=>{if(active)setError(e instanceof Error?e.message:"Unavailable")}).finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[sport,demo]);
 const champ=d?.live?.find(x=>x.champion);
 return <View style={styles.stack}>
  <Text style={styles.eyebrow}>TRACK RECORD</Text><Text style={styles.title}>How the model has done.</Text>
  <Text style={styles.caption}>Live results count only predictions stored before the game. Backtests are simulated on past seasons and shown separately.</Text>
  {demo?<Text style={styles.warning}>Switch off demo mode to load the track record.</Text>:null}
  {loading?<ActivityIndicator color={theme.accent} size="large"/>:null}
  {error?<Text style={styles.warning}>{error}</Text>:null}
  {d&&!d.ready?<Text style={styles.caption}>{d.reason}</Text>:null}
  {d?.ready?<>
   <View style={styles.card}><Text style={styles.eyebrow}>LIVE · {d.championLabel?.toUpperCase()}</Text>
    {champ&&champ.summary.games>0?<><Tiles s={champ.summary}/>
     {champ.summary.calibration.filter(b=>b.forecasts>0).map(b=><Text key={b.from} style={styles.caption}>Stated {Math.round(b.from*100)}–{Math.min(100,Math.round(b.to*100))}%: won {pct(b.observedRate)} of {b.forecasts}</Text>)}</>
     :<Text style={styles.caption}>No graded live predictions yet. The record starts with the first stored slate.</Text>}
   </View>
   <View style={styles.card}><Text style={styles.eyebrow}>WALK-FORWARD BACKTEST</Text>
    {d.backtest?<><Text style={styles.caption}>{d.backtest.evaluatedGames} games · {d.backtest.evaluatedWeeks} weeks · seasons {d.backtest.seasons.join(", ")} · run {d.backtest.runDay}</Text>
     {d.backtest.models.map(m=><Text key={m.model} style={[styles.caption,m.model===d.champion&&{color:theme.accent}]}>{m.label}: {pct(m.summary.winnerAccuracy)} · Brier {n(m.summary.brierScore,3)} · spread err {n(m.summary.marginMAE,1)}</Text>)}</>
     :<Text style={styles.caption}>No backtest stored yet.</Text>}
   </View>
   <Text style={styles.caption}>No result here implies future profitability.</Text>
  </>:null}
 </View>;
}
const styles=StyleSheet.create({
 stack:{gap:12},eyebrow:{fontSize:10,color:theme.accent,fontWeight:"900",letterSpacing:1.8},title:{fontSize:24,fontWeight:"800",color:theme.text},
 card:{backgroundColor:theme.surface,borderWidth:1,borderColor:theme.border,borderRadius:15,padding:15,gap:9},
 tiles:{flexDirection:"row",flexWrap:"wrap",gap:7},tile:{flexGrow:1,minWidth:90,backgroundColor:theme.surface2,borderRadius:10,padding:10,gap:3},
 label:{color:theme.muted,fontSize:9,fontWeight:"700",letterSpacing:0.8},value:{color:theme.text,fontSize:17,fontWeight:"800"},
 caption:{color:theme.muted,fontSize:12,lineHeight:18},warning:{color:theme.danger,fontSize:12,lineHeight:18}
});
