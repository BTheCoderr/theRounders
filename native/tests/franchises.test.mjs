import test from "node:test";
import assert from "node:assert/strict";
import {franchiseTeamIds} from "../lib/results/franchises.ts";

test("exhibition-only teams (All-Star, Rising Stars) are excluded from the archive",()=>{
 const rows=[];
 for(let i=0;i<30;i++)rows.push({home_team_id:"1",away_team_id:"2"},{home_team_id:"2",away_team_id:"3"});
 rows.push({home_team_id:"31",away_team_id:"32"},{home_team_id:"31",away_team_id:"32"});
 const ids=franchiseTeamIds(rows);
 assert.deepEqual([...ids].sort(),["1","2","3"]);
 assert.ok(!ids.has("31")&&!ids.has("32"));
});
