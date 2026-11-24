import TeamPage from "../../../../components/TeamPage";
export const metadata={title:"Team · The Rounders"};
export default async function Page({params}:{params:Promise<{sport:string;slug:string}>}){
 const {sport,slug}=await params;
 return <TeamPage sport={sport.toUpperCase()} slug={slug}/>;
}
