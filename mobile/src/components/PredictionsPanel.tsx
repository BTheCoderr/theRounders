import React,{useEffect,useState} from "react";
import {ActivityIndicator,Pressable,StyleSheet,Text,View} from "react-native";
import {fetchPredictions,type PredictionView,type Predictions} from "../api";
import type {Sport} from "../markets";
import {theme} from "../theme";

const pct=(x:number)=>(x*100).toFixed(1)+"%";
const signed=(x:number)=>(x>0?"+":"")+x.toFixed(1);
const when=(iso:string)=>new Date(iso).toLocaleString([],{weekday:"short",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});
function PickCard({p,onAsk}:{p:PredictionView;onAsk:(p:PredictionView)=>void}){
 const fav=p.projectedWinner===p.home?p.homeWinProbability:1-p.homeWinProbability;
 const lock=(field:string)=>p.locked?.includes(field)?"Pro":"—";
 return <View style={styles.card}>
  <View style={styles.row}><Text style={styles.time}>{when(p.startsAt)}</Text>
   <Text style={[styles.badge,p.status==="graded"?styles.final:styles.model]}>{p.status==="graded"&&p.final?`FINAL ${p.final.away}-${p.final.home}`:p.status==="void"?"VOID":"MODEL"}</Text></View>
  <Text style={styles.matchup}>{p.away} @ {p.home}</Text>
  <Text style={styles.winner}>{p.projectedWinner} · {pct(fav)}</Text>
  <View style={styles.bar}><View style={[styles.fill,{width:`${(p.homeWinProbability*100).toFixed(1)}%` as `${number}%`}]}/></View>
  <View style={styles.stats}>
   <View style={styles.stat}><Text style={styles.label}>SPREAD ({p.home.split(" ").pop()})</Text><Text style={styles.value}>{p.projectedSpreadHome===null?lock("spread"):signed(p.projectedSpreadHome)}</Text></View>
   <View style={styles.stat}><Text style={styles.label}>TOTAL</Text><Text style={styles.value}>{p.projectedTotal===null?lock("total"):p.projectedTotal.toFixed(1)}</Text></View>
   <View style={styles.stat}><Text style={styles.label}>SCORE</Text><Text style={styles.value}>{p.projectedAway===null||p.projectedHome===null?lock("score"):`${p.projectedAway.toFixed(0)}-${p.projectedHome.toFixed(0)}`}</Text></View>
  </View>
  <Text style={styles.caption}>{p.modelVersion} · frozen {new Date(p.predictedAt).toLocaleString()} · {p.trainingGames} games</Text>
  {p.locked?.length?<Text style={styles.caption}>Spreads, totals and scores are part of Rounders Pro on the website.</Text>:null}
  {p.status==="pending"?<Pressable accessibilityRole="button" onPress={()=>onAsk(p)}><Text style={styles.action}>Explain this pick →</Text></Pressable>:null}
 </View>;
}
export function PredictionsPanel({sport,demo,onAsk}:{sport:Sport;demo:boolean;onAsk:(p:PredictionView)=>void}){
 const [data,setData]=useState<Predictions|null>(null),[error,setError]=useState(""),[loading,setLoading]=useState(false),[rev,setRev]=useState(0);
 useEffect(()=>{
  let active=true;setData(null);setError("");
  if(demo){setLoading(false);return()=>{active=false}}
  setLoading(true);
  void fetchPredictions(sport).then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(e instanceof Error?e.message:"Predictions unavailable")}).finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[sport,demo,rev]);
 return <View style={styles.stack}>
  <Text style={styles.eyebrow}>{sport} PREDICTIONS</Text>
  <Text style={styles.title}>{sport==="NBA"?"Today's projections.":"This week's projections."}</Text>
  <Text style={styles.caption}>Frozen before each game and graded after it. {data?.modelLabel?`Model: ${data.modelLabel}.`:""}</Text>
  {demo?<Text style={styles.warning}>Predictions need the live Rounders API. Switch off demo mode.</Text>:<Pressable onPress={()=>setRev(x=>x+1)} disabled={loading}><Text style={styles.action}>Refresh ↻</Text></Pressable>}
  {loading?<ActivityIndicator color={theme.accent} size="large"/>:null}
  {error?<Text style={styles.warning}>{error}</Text>:null}
  {data&&!data.ready?<Text style={styles.empty}>{data.reason||"Predictions are not available yet."}</Text>:null}
  {data?.ready&&data.predictions.length===0?<Text style={styles.empty}>No {sport} games in the current window yet.</Text>:null}
  {data?.predictions.map(p=><PickCard key={p.eventId} p={p} onAsk={onAsk}/>)}
 </View>;
}
const styles=StyleSheet.create({
 stack:{gap:12},eyebrow:{fontSize:10,color:theme.accent,fontWeight:"900",letterSpacing:1.8},title:{fontSize:24,fontWeight:"800",color:theme.text},
 card:{backgroundColor:theme.surface,borderWidth:1,borderColor:theme.border,borderRadius:15,padding:15,gap:9},
 row:{flexDirection:"row",justifyContent:"space-between",alignItems:"center"},time:{color:theme.muted,fontSize:12},
 badge:{fontSize:10,fontWeight:"800",paddingHorizontal:7,paddingVertical:4,borderRadius:7,overflow:"hidden"},
 model:{backgroundColor:"#1A3358",color:theme.accent},final:{backgroundColor:theme.surface2,color:theme.text},
 matchup:{fontSize:16,fontWeight:"800",color:theme.text},winner:{fontSize:20,fontWeight:"900",color:theme.text},
 bar:{height:6,borderRadius:99,backgroundColor:"#24395E",overflow:"hidden"},fill:{height:6,backgroundColor:theme.accent},
 stats:{flexDirection:"row",gap:7},stat:{flex:1,backgroundColor:theme.surface2,borderRadius:10,padding:9,gap:3},
 label:{color:theme.muted,fontSize:9,fontWeight:"700",letterSpacing:0.8},value:{color:theme.text,fontSize:16,fontWeight:"800"},
 caption:{color:theme.muted,fontSize:11,lineHeight:17},action:{color:theme.accent,fontWeight:"700",fontSize:13},
 warning:{color:theme.danger,fontSize:12,lineHeight:18},empty:{color:theme.muted,padding:18,backgroundColor:theme.surface,borderRadius:12,textAlign:"center"}
});
