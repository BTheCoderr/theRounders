/** One-time deep history toward 1980 for the History pages; stops per sport when the feed runs dry. */
export default async function handler(_request:Request):Promise<Response>{
 const {deepHistoryStep}=await import("../../lib/persistence/history");
 try{
  const result=await deepHistoryStep();
  console.log("rounders deep history",JSON.stringify(result));
  return Response.json({ok:true,...result});
 }catch(error){
  const message=error instanceof Error?error.message:"failed";
  console.error("rounders deep history",message);
  return Response.json({ok:false,error:message},{status:503});
 }
}
export const config={schedule:"*/10 * * * *"};
