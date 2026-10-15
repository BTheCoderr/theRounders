import React,{useEffect,useState} from "react";
import {ActivityIndicator,Pressable,StyleSheet,Text,View} from "react-native";
import {apiOrigin} from "../api";
import type {Sport} from "../markets";
import {theme} from "../theme";

type ModelScore={model:string;games:number;mae:number|null;winnerAccuracy:number|null;meanBias:number|null};
type Comparison={ready:boolean;reason?:string;sport:Sport;run_day?:string;data_state?:"external"|"simulated";
 data_source?:string;historical_games?:number;evaluated_games?:number;evaluated_weeks?:number;
 seasons?:number[];metrics?:ModelScore[];best_model?:string|null;beats_baseline?:boolean|null;warning?:string;};
const labels:Record<string,string>={
 "home-baseline":"Home baseline",
 "massey-ridge":"Massey-style ridge",
 "elo-margin":"Elo margin",
 "rounders-power-v2":"Rounders Power v2"
};
export default function ModelLab({sport}:{sport:Sport}){
 const [report,setReport]=useState<Comparison|null>(null);
 const [loading,setLoading]=useState(false);
 const [error,setError]=useState("");
 const [revision,setRevision]=useState(0);
 useEffect(()=>{
  let active=true;const controller=new AbortController();
  setReport(null);setError("");setLoading(true);
  async function load(){
   if(!apiOrigin)throw new Error("Server API is not configured.");
   const response=await fetch(apiOrigin+"/api/model-comparison?sport="+sport,{signal:controller.signal});
   if(!response.ok)throw new Error("Model evaluation unavailable. Try again later.");
   const data=await response.json() as Comparison;
   if(data.sport!==sport||typeof data.ready!=="boolean")throw new Error("Invalid model comparison response");
   if(active)setReport(data);
  }
  void load().catch(err=>{if(active)setError(err instanceof Error?err.message:"Unable to load model scorecard.")})
   .finally(()=>{if(active)setLoading(false)});
  return()=>{active=false;controller.abort()};
 },[sport,revision]);
 return <View style={styles.group}>
  <Text style={styles.title}>Model Lab</Text>
  <Text style={styles.muted}>The same future games are scored against Elo, a basic Massey-style ratings system, and a fixed home baseline. Lower margin error is better. No model is presented as proven superior.</Text>
  <Pressable accessibilityRole="button" style={styles.button} disabled={loading} onPress={()=>setRevision(x=>x+1)}>
   <Text style={styles.action}>Refresh scorecard</Text>
  </Pressable>
  {loading?<ActivityIndicator color={theme.accent}/>:null}
  {error?<Text style={styles.warning}>{error}</Text>:null}
  {report&&!report.ready?<View style={styles.panel}><Text style={styles.warning}>{report.reason||"Awaiting first historical evaluation."}</Text></View>:null}
  {report?.ready?<View style={styles.group}>
   <View style={styles.panel}>
    <Text style={styles.eyebrow}>{report.data_state==="simulated"?"SIMULATED, NOT VERIFIED":"EXTERNAL COMPLETED RESULTS"}</Text>
    <Text style={styles.muted}>Source: {report.data_source||"unknown"} · Run {report.run_day||"unknown"}</Text>
    <Text style={styles.muted}>{report.historical_games??0} historical games · {report.evaluated_games??0} held-out games · {report.evaluated_weeks??0} evaluated weeks</Text>
    <Text style={styles.muted}>Calendar years: {(report.seasons||[]).join(", ")||"Unavailable"}</Text>
    <Text style={styles.warning}>{report.warning||"Preliminary estimates; further validation required."}</Text>
   </View>
   {(report.metrics||[]).map(item=><View key={item.model} style={styles.panel}>
    <Text style={styles.model}>{labels[item.model]||item.model}</Text>
    <Text style={styles.metric}>Margin MAE: {item.mae===null?"Not enough data":item.mae.toFixed(2)}</Text>
    <Text style={styles.muted}>Straight-up winner accuracy: {item.winnerAccuracy===null?"Unavailable":item.winnerAccuracy.toFixed(1)+"%"} · Games: {item.games}</Text>
   </View>)}
   <Text style={styles.warning}>A model's lead on one historical sample does not establish an advantage. No real-money betting claims.</Text>
  </View>:null}
 </View>;
}
const styles=StyleSheet.create({
 group:{gap:12},
 panel:{borderRadius:13,padding:14,backgroundColor:theme.surface,borderWidth:1,borderColor:theme.border,gap:7},
 title:{fontSize:24,color:theme.text,fontWeight:"800"},
 model:{fontSize:16,color:theme.text,fontWeight:"800"},
 metric:{fontSize:18,color:theme.accent,fontWeight:"800"},
 muted:{color:theme.muted,fontSize:12,lineHeight:18},
 warning:{color:theme.danger,fontSize:12,lineHeight:18},
 eyebrow:{color:theme.accent,fontSize:11,fontWeight:"800",letterSpacing:1},
 button:{borderRadius:10,backgroundColor:theme.surface2,padding:11,alignSelf:"flex-start"},
 action:{color:theme.accent,fontSize:13,fontWeight:"800"}
});
