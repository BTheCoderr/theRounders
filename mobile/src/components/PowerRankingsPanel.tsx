import React,{useEffect,useState} from "react";
import {ActivityIndicator,Pressable,StyleSheet,Text,View} from "react-native";
import {fetchPowerRankings,type PowerRankings} from "../api";
import type {Sport} from "../markets";
import {theme} from "../theme";

/** The component intentionally does not infer that a computed rating is verified game data. */
export function PowerRankingsPanel({sport,demo}:{sport:Sport;demo:boolean}){
 const [data,setData]=useState<PowerRankings|null>(null);
 const [error,setError]=useState("");
 const [loading,setLoading]=useState(false);
 const [revision,setRevision]=useState(0);
 useEffect(()=>{
  let active=true;
  setData(null);setError("");
  if(demo){setLoading(false);return()=>{active=false}}
  setLoading(true);
  void fetchPowerRankings(sport).then(result=>{if(active)setData(result)})
   .catch(err=>{if(active)setError(err instanceof Error?err.message:"Unable to load rankings")})
   .finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[sport,demo,revision]);
 const f=(x:number)=>x>0?"+"+x.toFixed(2):x.toFixed(2);
 return <View style={styles.stack}>
  <Text style={styles.title}>Rounders Power Index</Text>
  <Text style={styles.muted}>Massey-inspired opponent-adjusted point ratings. Preview model, not an official Massey ranking.</Text>
  {demo?<Text style={styles.warning}>Switch to API mode to fetch labeled external or controlled-simulation rankings. No rankings are generated from demo fixtures on the phone.</Text>:
    <Pressable accessibilityRole="button" style={styles.refresh} onPress={()=>setRevision(x=>x+1)} disabled={loading}>
     <Text style={styles.action}>Refresh rankings ↻</Text>
    </Pressable>}
  {loading?<ActivityIndicator size="large" color={theme.accent}/>:null}
  {error?<Text style={styles.warning}>{error}</Text>:null}
  {data?<View style={styles.stack}>
   <View style={styles.panel}>
    <Text style={styles.eyebrow}>{data.dataState==="simulated"?"SIMULATED HISTORY":"EXTERNAL GAME RESULTS"} · {data.coverage.toUpperCase()} COVERAGE</Text>
    <Text style={styles.muted}>{data.provider} · {data.games} completed games · Median {data.medianGames} games per team</Text>
    {data.notes.map((n,i)=><Text key={i} style={styles.warning}>{n}</Text>)}
   </View>
   <View style={styles.panel}>
    <Text style={styles.eyebrow}>CHRONOLOGICAL HOLDOUT CHECK</Text>
    {data.evaluation.evaluatedGames>0?
    <Text style={styles.muted}>Evaluated {data.evaluation.evaluatedGames} held-out games · Rating MAE {data.evaluation.modelMAE?.toFixed(2)} · Home-only baseline MAE {data.evaluation.homeBaselineMAE?.toFixed(2)}. {data.evaluation.beatsBaseline?"Lower error than baseline on this split.":"Did not outperform baseline on this split."}</Text>:
    <Text style={styles.muted}>Not enough eligible history for a holdout comparison.</Text>}
    <Text style={styles.warning}>{data.evaluation.warning}</Text>
   </View>
   {data.rankings.length===0?<Text style={styles.muted}>No eligible games to rank.</Text>:
    data.rankings.map(team=><View key={team.team} style={styles.team}>
     <View style={styles.row}>
      <Text style={styles.position}>{team.rank}.</Text>
      <Text style={styles.teamName}>{team.team}</Text>
      <Text style={styles.rating}>{f(team.rating)}</Text>
     </View>
     <Text style={styles.muted}>W-L-T {team.record.wins}-{team.record.losses}-{team.record.ties} · {team.games} games</Text>
     <Text style={styles.muted}>Opp. rating {f(team.averageOpponentRating)} · Avg. margin {f(team.adjustedMargin)} · Last 5 margin {f(team.recentForm)}</Text>
    </View>)}
  </View>:null}
 </View>;
}
const styles=StyleSheet.create({
 stack:{gap:12},
 title:{color:theme.text,fontSize:24,fontWeight:"800"},
 panel:{backgroundColor:theme.surface,borderRadius:15,padding:14,gap:8,borderWidth:1,borderColor:theme.border},
 team:{backgroundColor:theme.surface,padding:13,borderRadius:12,gap:5,borderWidth:1,borderColor:theme.border},
 row:{flexDirection:"row",alignItems:"center",gap:8},
 position:{color:theme.muted,fontSize:17,fontWeight:"800",width:31},
 teamName:{color:theme.text,fontSize:15,fontWeight:"700",flex:1},
 rating:{color:theme.accent,fontSize:19,fontWeight:"900"},
 muted:{color:theme.muted,fontSize:12,lineHeight:18},
 warning:{color:theme.danger,fontSize:12,lineHeight:18},
 eyebrow:{color:theme.accent,fontWeight:"800",fontSize:11,letterSpacing:1},
 refresh:{paddingVertical:9,paddingHorizontal:12,alignSelf:"flex-start",backgroundColor:theme.surface2,borderRadius:10},
 action:{color:theme.accent,fontWeight:"800",fontSize:13}
});
