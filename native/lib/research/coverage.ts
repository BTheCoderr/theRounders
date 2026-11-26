/** Read-only coverage audit. Never creates or rewrites predictions. */
export type Scheduled={eventId:string;startsAt:string;home:string;away:string};
export type Locked={provider_event_id:string;model_id:string;predicted_at:string;starts_at:string};
export function auditCoverage(schedule:readonly Scheduled[],locked:readonly Locked[],models:readonly string[],knownTeams:ReadonlySet<string>,now:Date){
 const index=new Map<string,Locked[]>();
 for(const row of locked){const key=row.provider_event_id+"|"+row.model_id;const list=index.get(key)??[];list.push(row);index.set(key,list);}
 return schedule.map(game=>{
  const missingTeams=[game.home,game.away].filter(t=>!knownTeams.has(t));
  const missingModels=models.filter(m=>!(index.get(game.eventId+"|"+m)??[]).some(p=>Date.parse(p.predicted_at)<Date.parse(game.startsAt)&&Date.parse(p.starts_at)===Date.parse(game.startsAt)));
  const duplicateModels=models.filter(m=>(index.get(game.eventId+"|"+m)??[]).length>1);
  const reason=missingModels.length===0?"covered":Date.parse(game.startsAt)-now.getTime()<600000?"lock-window-closed":missingTeams.length?"missing-team-history":"missing-model-output";
  return {eventId:game.eventId,missingTeams,missingModels,duplicateModels,reason};
 });
}
