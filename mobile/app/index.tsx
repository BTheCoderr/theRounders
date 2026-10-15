import React,{useCallback,useEffect,useMemo,useRef,useState} from "react";
import {
 ActivityIndicator,Alert,Linking,Pressable,RefreshControl,ScrollView,StatusBar,
 StyleSheet,Text,TextInput,View
} from "react-native";
import {SafeAreaView} from "react-native-safe-area-context";
import {apiOrigin,fetchFeed,fetchRating,fetchMatchupInsight,type Feed,type Rating,type MatchupInsight} from "../src/api";
import {
 SPORTS,demoQuotes,displayTeam,fmtPrice,getPriceGaps,groupQuotes,
 type Group,type MarketName,type Quote,type Sport,
} from "../src/markets";
import {loadPaper,profit,validStake,writePaper,type PaperEntry} from "../src/paper";
import {theme} from "../src/theme";
import {PowerRankingsPanel} from "../src/components/PowerRankingsPanel";
import ModelLab from "../src/components/ModelLab";

type Tab="board"|"rankings"|"lab"|"signals"|"ai"|"paper";
const MARKET_NAMES:Record<MarketName,string>={moneyline:"Moneyline",spread:"Spread",total:"Total"};
const usd=(value:number)=>"$"+(Number.isFinite(value)?value:0).toFixed(2);

function Pill({label,active=false,onPress}:{label:string;active?:boolean;onPress:()=>void}){
 return <Pressable accessibilityRole="button" accessibilityState={{selected:active}} onPress={onPress} style={[styles.pill,active&&styles.pillActive]}>
  <Text style={[styles.pillText,active&&styles.pillTextActive]}>{label}</Text>
 </Pressable>;
}
function SectionHeader({eyebrow,title}:{eyebrow:string;title:string}){
 return <View style={styles.sectionHeader}><Text style={styles.eyebrow}>{eyebrow}</Text><Text style={styles.title}>{title}</Text></View>;
}
function GroupRow({group,onChoose,onRating,onAnalyze}:{group:Group;onChoose:(quote:Quote)=>void;onRating:(quote:Quote)=>void;onAnalyze:(quote:Quote)=>void}){
 const q=group.first;
 return <View style={styles.card}>
  <View style={styles.rowBetween}>
   <View style={{flex:1}}><Text style={styles.matchup}>{displayTeam(q.sport,q.away)}  @  {displayTeam(q.sport,q.home)}</Text><Text style={styles.label}>{MARKET_NAMES[q.market]} · {displayTeam(q.sport,q.selection)}{q.line===undefined?"":" "+q.line}</Text></View>
   <Text style={[styles.state,q.state==="live"?styles.live:styles.demo]}>{q.state.toUpperCase()}</Text>
  </View>
  <View style={styles.books}>
   {group.quotes.map((quote,i)=><Pressable key={quote.book+":"+i} onPress={()=>onChoose(quote)} style={[styles.quote,i===0&&styles.bestQuote]}>
    <Text style={styles.label}>{quote.book}</Text><Text style={styles.odds}>{fmtPrice(quote.price)}</Text>
    {i===0?<Text style={styles.best}>BEST SAME-LINE PRICE</Text>:<Text style={styles.hint}>Tap for paper ticket</Text>}
   </Pressable>)}
  </View>
  <View style={styles.filterRow}><Pressable accessibilityRole="button" onPress={()=>onRating(q)} style={styles.textButton}><Text style={styles.actionText}>Show rating →</Text></Pressable><Pressable accessibilityRole="button" onPress={()=>onAnalyze(q)} style={styles.textButton}><Text style={styles.actionText}>Ask Rounders AI →</Text></Pressable></View>
 </View>;
}

export default function Home(){
 const [sport,setSport]=useState<Sport>("NBA");
 const [market,setMarket]=useState<MarketName>("moneyline");
 const [tab,setTab]=useState<Tab>("board");
 const [demo,setDemo]=useState(!apiOrigin);
 const [feed,setFeed]=useState<Feed>({quotes:[],provider:"",live:false,fresh:false,message:""});
 const [loading,setLoading]=useState(false);
 const [feedError,setFeedError]=useState("");
 const [rating,setRating]=useState<Rating|null>(null);
 const [ratingError,setRatingError]=useState("");
 const [ratingLoading,setRatingLoading]=useState(false);
 const [aiSelected,setAiSelected]=useState<Quote|null>(null);
 const [aiQuestion,setAiQuestion]=useState("Explain this matchup and what the model could be missing.");
 const [aiInsight,setAiInsight]=useState<MatchupInsight|null>(null);
 const [aiError,setAiError]=useState("");
 const [aiLoading,setAiLoading]=useState(false);
 const [ticket,setTicket]=useState<Quote|null>(null);
 const [stake,setStake]=useState("25");
 const [bets,setBets]=useState<PaperEntry[]>([]);
 const [paperReady,setPaperReady]=useState(false);
 const requestId=useRef(0);
 const ratingRequestId=useRef(0);
 const aiRequestId=useRef(0);

 const refresh=useCallback(async()=>{
  const id=++requestId.current;
  setLoading(true);setFeedError("");
  if(demo){
   const quotes=demoQuotes(sport);
   setFeed({quotes,provider:"Sample fixtures",live:false,fresh:false,message:"SIMULATED DATA ONLY"});
   setLoading(false);return;
  }
  try{
   const result=await fetchFeed(sport);
   if(id===requestId.current)setFeed(result);
  }catch(error){
   if(id===requestId.current){setFeed({quotes:[],provider:"",live:false,fresh:false,message:""});setFeedError(error instanceof Error?error.message:"Unable to reach feed.");}
  }finally{if(id===requestId.current)setLoading(false)}
 },[sport,demo]);
 useEffect(()=>{void refresh();return()=>{requestId.current++}},[refresh]);
 useEffect(()=>{let active=true;void loadPaper().then(value=>{if(active){setBets(value);setPaperReady(true)}});return()=>{active=false}},[]);
 useEffect(()=>{ratingRequestId.current++;setRating(null);setRatingError("");setRatingLoading(false);setTicket(null)},[sport,demo]);
 useEffect(()=>{aiRequestId.current++;setAiSelected(null);setAiInsight(null);setAiError("");setAiLoading(false)},[sport,demo]);
 const changeSport=(next:Sport)=>{
  if(next===sport)return;
  requestId.current++;ratingRequestId.current++;aiRequestId.current++;
  setFeed({quotes:[],provider:"",live:false,fresh:false,message:""});
  setFeedError("");setRating(null);setRatingError("");setRatingLoading(false);setTicket(null);
  setSport(next);
 };
 const toggleDemo=()=>{
  requestId.current++;ratingRequestId.current++;aiRequestId.current++;
  setFeed({quotes:[],provider:"",live:false,fresh:false,message:""});
  setRating(null);setRatingError("");setRatingLoading(false);setTicket(null);
  setDemo(v=>!v);
 };
 const groups=useMemo(()=>groupQuotes(feed.quotes,market),[feed.quotes,market]);
 const gaps=useMemo(()=>getPriceGaps(feed.quotes),[feed.quotes]);
 const wins=bets.filter(b=>b.status==="won").length;
 const settled=bets.filter(b=>b.status==="won"||b.status==="lost").length;
 const total=bets.reduce((sum,b)=>sum+profit(b),0);
 const exposure=bets.filter(b=>b.status==="pending").reduce((sum,b)=>sum+b.stake,0);

 const showRating=async(quote:Quote)=>{
  const id=++ratingRequestId.current;
  setRating(null);setRatingError("");setRatingLoading(true);
  try{
   if(demo)throw new Error("Model ratings are disabled in demo mode. Connect the live Rounders API.");
   const result=await fetchRating(quote);
   if(id===ratingRequestId.current)setRating(result);
  }catch(error){if(id===ratingRequestId.current)setRatingError(error instanceof Error?error.message:"Ratings unavailable.")}
  finally{if(id===ratingRequestId.current)setRatingLoading(false)}
 };
 const openAi=(quote:Quote)=>{
  aiRequestId.current++;
  setAiSelected(quote);setAiInsight(null);setAiError("");setAiLoading(false);
  setAiQuestion("Explain this matchup and what the model could be missing.");
  setTab("ai");
 };
 const askAi=async()=>{
  if(!aiSelected)return;
  const id=++aiRequestId.current;
  setAiError("");setAiInsight(null);setAiLoading(true);
  try{
   if(!apiOrigin)throw new Error("Rounders API is not configured. AI explanations require backend access.");
   if(aiQuestion.trim().length<3||aiQuestion.length>240)throw new Error("Enter a question between 3 and 240 characters.");
   const answer=await fetchMatchupInsight(aiSelected,aiQuestion);
   if(id===aiRequestId.current)setAiInsight(answer);
  }catch(error){if(id===aiRequestId.current)setAiError(error instanceof Error?error.message:"Could not analyze this matchup.")}
  finally{if(id===aiRequestId.current)setAiLoading(false)}
 };
 const add=async()=>{
  if(!ticket)return;
  if(!paperReady){Alert.alert("Paper tickets loading","Your saved paper tickets are still loading. Try again.");return;}
  const amount=Number(stake);
  if(!validStake(amount)){Alert.alert("Invalid paper stake","Enter an amount between $1 and $100,000.");return}
  const bet:PaperEntry={id:Date.now().toString(36)+"-"+Math.random().toString(36).slice(2),
   quote:ticket,stake:amount,status:"pending",placedAt:new Date().toISOString()};
  try{const all=[bet,...bets];await writePaper(all);setBets(all);setTicket(null);setTab("paper")}
  catch{Alert.alert("Could not save","Your paper ticket could not be saved on this device.")}
 };

 const removePaper=(id:string)=>{
  Alert.alert("Delete paper ticket?","Remove this paper ticket from this device?",[
   {text:"Cancel",style:"cancel"},
   {text:"Delete",style:"destructive",onPress:()=>{void (async()=>{
    try{const remaining=bets.filter(b=>b.id!==id);await writePaper(remaining);setBets(remaining)}
    catch{Alert.alert("Could not delete","Your paper ticket could not be removed.")}
   })()}}
  ]);
 };
 const clearPaper=()=>{
  Alert.alert("Clear all paper tickets?","This permanently removes all paper entries stored on this device.",[
   {text:"Cancel",style:"cancel"},
   {text:"Delete all",style:"destructive",onPress:()=>{void (async()=>{
    try{await writePaper([]);setBets([])}
    catch{Alert.alert("Could not clear","Your paper tickets could not be removed.")}
   })()}}
  ]);
 };
 const grade=async(id:string,status:PaperEntry["status"])=>{
  const all=bets.map(b=>b.id===id?{...b,status}:b);
  try{await writePaper(all);setBets(all)}
  catch{Alert.alert("Could not update","Your paper result could not be saved.")}
 };
 return <SafeAreaView style={styles.safe} edges={["top","bottom"]}>
  <StatusBar barStyle="light-content"/>
  <ScrollView style={styles.scroll} contentContainerStyle={styles.content}
   refreshControl={<RefreshControl refreshing={loading} onRefresh={()=>void refresh()} tintColor={theme.accent}/>}>
   <View style={styles.header}>
    <View><Text style={styles.brand}>therounders</Text><Text style={styles.subtitle}>Sports Research Command Center</Text></View>
    <View style={styles.modeBadge}><Text style={styles.modeText}>PAPER ONLY</Text></View>
   </View>
   <View style={styles.modeCard}>
    <View style={{flex:1}}>
     <Text style={styles.modeTitle}>{demo?"DEMO MODE":"API MODE"}</Text>
     <Text style={styles.hint}>{demo?"Fixtures are simulated, not current games or sportsbook prices.":feed.live?(feed.fresh?"Live provider feed":"Live feed is stale"):"Feed is simulated or unavailable; no live claim."}</Text>
    </View>
    {apiOrigin?<Pressable accessibilityRole="button" onPress={toggleDemo} style={styles.switchMode}><Text style={styles.actionText}>{demo?"Use API":"Use demo"}</Text></Pressable>:null}
   </View>
   {!apiOrigin&&<Text style={styles.warning}>A live API is not configured yet. Add EXPO_PUBLIC_ROUNDERS_API_URL to enable backend access.</Text>}
   <View style={styles.tabs}>
    {(["board","rankings","lab","signals","ai","paper"] as const).map(id=><Pill key={id} label={id==="board"?"Board":id==="rankings"?"Power Index":id==="lab"?"Model Lab":id==="signals"?"Price Gaps":id==="ai"?"Rounders AI":"Paper Bets"} active={tab===id} onPress={()=>setTab(id)}/>)}
   </View>
   {tab!=="paper"&&<View style={styles.filterRow}>{SPORTS.map(name=><Pill key={name} label={name} active={sport===name} onPress={()=>changeSport(name)}/>)}</View>}
   {feedError?<View style={styles.card}><Text style={styles.warning}>{feedError}</Text><Pressable onPress={()=>void refresh()}><Text style={styles.actionText}>Retry →</Text></Pressable></View>:null}
   {tab==="board"&&<>
    <SectionHeader eyebrow="MARKET BOARD" title="Compare every point."/>
    <Text style={styles.caption}>{feed.provider||"Not connected"} · {demo?"SIMULATED":feed.live?"LIVE":"FALLBACK"} · {feed.message}</Text>
    <View style={styles.filterRow}>{(["moneyline","spread","total"] as const).map(id=><Pill key={id} label={MARKET_NAMES[id]} active={market===id} onPress={()=>setMarket(id)}/>)}</View>
    {loading?<ActivityIndicator color={theme.accent} size="large"/>:groups.length===0?<Text style={styles.empty}>No markets available for this sport and selection.</Text>:groups.map(group=><GroupRow key={group.key} group={group} onChoose={setTicket} onRating={q=>void showRating(q)} onAnalyze={openAi}/>)}
    {(ratingLoading||rating||ratingError)&&<View style={styles.card}>
     <Text style={styles.eyebrow}>ROUNDERS MODEL</Text>
     {ratingLoading?<ActivityIndicator color={theme.accent}/>:ratingError?<Text style={styles.warning}>{ratingError}</Text>:rating?.projection?<View>
      <Text style={styles.matchup}>{rating.projection.away} {rating.projection.projectedAway.toFixed(1)} · {rating.projection.home} {rating.projection.projectedHome.toFixed(1)}</Text>
      <Text style={styles.label}>Home win probability {rating.projection.homeWinProbability.toFixed(1)}% · Confidence {rating.projection.confidence.toFixed(0)}%</Text>
      <Text style={styles.caption}>MODEL · Training: {rating.trainingDataState||"unknown"} · {rating.trainingProvider||"unknown"}{rating.fallback?" · Simulated fallback":""}</Text>
     </View>:<Text style={styles.warning}>No verified model result.</Text>}
    </View>}
    {ticket&&<View style={[styles.card,styles.ticket]}>
     <Text style={styles.eyebrow}>SIMULATED PAPER TICKET</Text>
     <Text style={styles.matchup}>{displayTeam(ticket.sport,ticket.selection)} {ticket.line===undefined?"":ticket.line} · {fmtPrice(ticket.price)}</Text>
     <Text style={styles.caption}>{displayTeam(ticket.sport,ticket.away)} @ {displayTeam(ticket.sport,ticket.home)} · {ticket.book} · {ticket.state.toUpperCase()}</Text>
     <TextInput style={styles.input} keyboardType="decimal-pad" value={stake} onChangeText={setStake} placeholder="Stake in USD" placeholderTextColor={theme.muted}/>
     <Pressable style={[styles.submit,!paperReady&&{opacity:0.5}]} disabled={!paperReady} onPress={()=>void add()}><Text style={styles.submitText}>{paperReady?"Save paper ticket":"Loading saved tickets…"}</Text></Pressable>
     <Pressable onPress={()=>setTicket(null)}><Text style={styles.actionText}>Cancel</Text></Pressable>
    </View>}
   </>}
   {tab==="rankings"&&<PowerRankingsPanel sport={sport} demo={demo}/>}
   {tab==="lab"&&<ModelLab sport={sport}/>}
   {tab==="signals"&&<>
    <SectionHeader eyebrow="PRICE GAP SCANNER" title="Evidence, not hype."/>
    <Text style={styles.caption}>These compare distinct books at the same line, event and selection. They do not establish steam or reverse-line movement.</Text>
    {loading?<ActivityIndicator color={theme.accent}/>:gaps.length===0?<Text style={styles.empty}>No qualifying price gaps. Historical movement alerts remain unavailable.</Text>:gaps.slice(0,15).map(g=><View style={styles.card} key={g.key}>
     <Text style={styles.matchup}>{displayTeam(g.first.sport,g.first.away)} @ {displayTeam(g.first.sport,g.first.home)}</Text>
     <Text style={styles.label}>{MARKET_NAMES[g.first.market]} · {displayTeam(g.first.sport,g.first.selection)} {g.first.line===undefined?"":g.first.line} · {g.first.state.toUpperCase()}</Text>
     <Text style={styles.strong}>{g.gap.toFixed(2)} percentage-point difference</Text>
     <Text style={styles.caption}>Best: {g.best.book} {fmtPrice(g.best.price)} · Other: {g.worst.book} {fmtPrice(g.worst.price)}</Text>
    </View>)}
   </>}
   {tab==="ai"&&<>
    <SectionHeader eyebrow="SPORTS INTELLIGENCE" title="Ask Rounders AI."/>
    <Text style={styles.caption}>Select a matchup, then ask about the statistical projection. Generative AI is used only when the server reports it is enabled. No unverified injury, news, or live-market claims.</Text>
    {groupQuotes(feed.quotes,"moneyline").filter((g,i,all)=>all.findIndex(x=>x.first.eventId===g.first.eventId)===i).map(g=><Pressable key={g.first.eventId} accessibilityRole="button" onPress={()=>openAi(g.first)} style={[styles.card,aiSelected?.eventId===g.first.eventId&&{borderColor:theme.accent}]}><Text style={styles.matchup}>{displayTeam(g.first.sport,g.first.away)} @ {displayTeam(g.first.sport,g.first.home)}</Text><Text style={styles.caption}>{g.first.state.toUpperCase()} market · Tap to analyze</Text></Pressable>)}
    {aiSelected?<View style={styles.card}>
     <Text style={styles.eyebrow}>ASK ABOUT THIS MATCHUP</Text>
     <Text style={styles.matchup}>{displayTeam(aiSelected.sport,aiSelected.away)} @ {displayTeam(aiSelected.sport,aiSelected.home)}</Text>
     <TextInput style={[styles.input,{minHeight:80,textAlignVertical:"top"}]} value={aiQuestion} onChangeText={setAiQuestion} multiline maxLength={240} placeholder="What matters most in this matchup?" placeholderTextColor={theme.muted}/>
     <Pressable accessibilityRole="button" style={[styles.submit,aiLoading&&{opacity:0.5}]} disabled={aiLoading} onPress={()=>void askAi()}><Text style={styles.submitText}>{aiLoading?"Analyzing…":"Analyze matchup"}</Text></Pressable>
     {aiError?<Text style={styles.warning}>{aiError}</Text>:null}
     {aiInsight?<View style={{gap:9}}>
      <Text style={styles.eyebrow}>{aiInsight.mode==="ai"?"AI EXPLANATION":"MODEL SUMMARY · GENERATIVE AI OFF"}</Text>
      <Text style={[styles.label,{color:theme.text,fontSize:14,lineHeight:22}]}>{aiInsight.answer}</Text>
      <Text style={styles.caption}>Source: {aiInsight.evidence.trainingProvider} · {aiInsight.evidence.trainingDataState.toUpperCase()}{aiInsight.evidence.fallback?" · SIMULATED FALLBACK":""} · {aiInsight.evidence.sampleGames} completed games</Text>
      <Text style={styles.hint}>{aiInsight.notice}</Text>
     </View>:null}
    </View>:<Text style={styles.empty}>Choose a matchup above, or tap “Ask Rounders AI” from the Board.</Text>}
   </>}
   {tab==="paper"&&<>
    <SectionHeader eyebrow="ON-DEVICE PAPER BANKROLL" title="Track before trading."/>
    <Text style={styles.caption}>No money changes hands. Results are marked manually. This device stores the entries, not your Rounders online account.</Text>
    <View style={styles.statRow}>
     <View style={styles.stat}><Text style={styles.label}>Profit / loss</Text><Text style={styles.strong}>{usd(total)}</Text></View>
     <View style={styles.stat}><Text style={styles.label}>Open stakes</Text><Text style={styles.strong}>{usd(exposure)}</Text></View>
     <View style={styles.stat}><Text style={styles.label}>Settled</Text><Text style={styles.strong}>{settled} · {wins} won</Text></View>
    </View>
    {!paperReady?<ActivityIndicator color={theme.accent}/>:bets.length===0?<Text style={styles.empty}>Your paper entries will appear here. Add a ticket from the Board tab.</Text>:bets.map(b=><View key={b.id} style={styles.card}>
     <Text style={styles.matchup}>{displayTeam(b.quote.sport,b.quote.away)} @ {displayTeam(b.quote.sport,b.quote.home)}</Text>
     <Text style={styles.caption}>{displayTeam(b.quote.sport,b.quote.selection)} {b.quote.line===undefined?"":b.quote.line} · {fmtPrice(b.quote.price)} · {b.quote.state.toUpperCase()}</Text>
     <Text style={styles.strong}>{usd(b.stake)} · {b.status.toUpperCase()} · P/L {usd(profit(b))}</Text>
     <View style={styles.filterRow}>{(["pending","won","lost","push"] as const).map(status=><Pill key={status} label={status.toUpperCase()} active={b.status===status} onPress={()=>void grade(b.id,status)}/>)}</View>
     <Pressable accessibilityRole="button" accessibilityLabel="Delete paper ticket" onPress={()=>removePaper(b.id)}><Text style={styles.warning}>Delete this ticket</Text></Pressable>
    </View>)}
    {paperReady&&bets.length>0&&<Pressable accessibilityRole="button" onPress={clearPaper}><Text style={styles.warning}>Delete all paper tickets from this device</Text></Pressable>}
   </>}
   <Text style={styles.footer}>Research and simulated paper tracking only. Prices and models are not guarantees. No wagering or sportsbook account connection.</Text>
   <View style={styles.filterRow}>
    <Pressable accessibilityRole="link" onPress={()=>void Linking.openURL("https://therounders.netlify.app/support").catch(()=>Alert.alert("Link unavailable","Email Bferrell514@gmail.com for help."))}><Text style={styles.actionText}>Support</Text></Pressable>
    <Pressable accessibilityRole="link" onPress={()=>void Linking.openURL("https://therounders.netlify.app/privacy").catch(()=>Alert.alert("Link unavailable","Privacy policy: therounders.netlify.app/privacy"))}><Text style={styles.actionText}>Privacy Policy</Text></Pressable>
    <Pressable accessibilityRole="link" onPress={()=>void Linking.openURL("mailto:Bferrell514@gmail.com?subject=The%20Rounders%20Support").catch(()=>Alert.alert("Email unavailable","Contact Bferrell514@gmail.com"))}><Text style={styles.actionText}>Email support</Text></Pressable>
   </View>
  </ScrollView>
 </SafeAreaView>;
}
const styles=StyleSheet.create({
 safe:{flex:1,backgroundColor:theme.bg},scroll:{backgroundColor:theme.bg},
 content:{padding:18,paddingBottom:48,gap:16},header:{flexDirection:"row",alignItems:"center",justifyContent:"space-between",gap:10,marginBottom:5},
 brand:{fontSize:30,fontWeight:"900",color:theme.accent,letterSpacing:-1},
 subtitle:{color:theme.muted,fontSize:12},modeBadge:{borderWidth:1,borderColor:theme.accent,padding:8,borderRadius:99},
 modeText:{fontSize:10,fontWeight:"800",color:theme.accent,letterSpacing:1},
 modeCard:{flexDirection:"row",alignItems:"center",backgroundColor:theme.surface2,borderRadius:12,padding:14,gap:8},
 modeTitle:{color:theme.text,fontWeight:"800",marginBottom:4},hint:{fontSize:12,color:theme.muted,lineHeight:18},
 switchMode:{padding:8,borderColor:theme.border,borderWidth:1,borderRadius:9},
 tabs:{flexDirection:"row",flexWrap:"wrap",gap:7,marginTop:3},filterRow:{flexDirection:"row",flexWrap:"wrap",gap:7},
 pill:{borderColor:theme.border,borderWidth:1,borderRadius:99,paddingHorizontal:12,paddingVertical:9,backgroundColor:theme.surface},
 pillActive:{backgroundColor:theme.primary,borderColor:theme.primary},pillText:{fontSize:12,color:theme.muted,fontWeight:"700"},
 pillTextActive:{color:theme.onPrimary},sectionHeader:{gap:3,marginTop:8},eyebrow:{fontSize:10,color:theme.accent,fontWeight:"900",letterSpacing:1.8},
 title:{fontSize:24,fontWeight:"800",color:theme.text},card:{backgroundColor:theme.surface,borderWidth:1,borderColor:theme.border,borderRadius:15,padding:15,gap:11},
 rowBetween:{flexDirection:"row",alignItems:"center",gap:10},matchup:{fontSize:16,fontWeight:"800",color:theme.text},
 label:{color:theme.muted,fontSize:12,lineHeight:19},state:{fontSize:10,fontWeight:"800",padding:6,borderRadius:7,overflow:"hidden"},
 live:{backgroundColor:"#18392a",color:theme.success},demo:{backgroundColor:"#39404e",color:"#f3d59e"},
 books:{flexDirection:"row",flexWrap:"wrap",gap:8},quote:{minWidth:115,flexGrow:1,backgroundColor:theme.surface2,padding:11,borderRadius:10,gap:5},
 bestQuote:{borderColor:theme.accent,borderWidth:1},odds:{fontWeight:"900",fontSize:23,color:theme.text},
 best:{color:theme.accent,fontSize:9,fontWeight:"700"},caption:{color:theme.muted,fontSize:12,lineHeight:19},
 textButton:{paddingVertical:9},actionText:{color:theme.accent,fontWeight:"700",fontSize:13},
 strong:{fontSize:19,fontWeight:"800",color:theme.text},warning:{color:theme.danger,fontSize:12,lineHeight:19},
 empty:{color:theme.muted,padding:20,backgroundColor:theme.surface,borderRadius:12,textAlign:"center"},
 ticket:{borderColor:theme.accent},input:{backgroundColor:theme.surface2,color:theme.text,borderWidth:1,borderColor:theme.border,borderRadius:10,padding:13,fontSize:16},
 submit:{backgroundColor:theme.primary,padding:14,borderRadius:10,alignItems:"center"},submitText:{fontWeight:"900",color:theme.onPrimary},
 statRow:{flexDirection:"row",flexWrap:"wrap",gap:7},stat:{flexGrow:1,backgroundColor:theme.surface2,borderRadius:12,padding:12,gap:5},
 footer:{color:theme.muted,fontSize:11,lineHeight:18,marginTop:20,borderTopWidth:1,borderTopColor:theme.border,paddingTop:15},
});
