/** Provider team IDs with at least `minGames` archived games: drops exhibition-only teams. */
export function franchiseTeamIds(rows:Array<{home_team_id:string;away_team_id:string}>,minGames=20):Set<string>{
 const count=new Map<string,number>();
 for(const r of rows)for(const id of [r.home_team_id,r.away_team_id])count.set(id,(count.get(id)||0)+1);
 return new Set([...count].filter(([,n])=>n>=minGames).map(([id])=>id));
}
