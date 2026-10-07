import {NextResponse} from "next/server";
import {listSnapshots,persistenceConfigured} from "../../../lib/persistence/supabase";

export const dynamic="force-dynamic";

export async function GET(){
  if(!persistenceConfigured())return NextResponse.json({configured:false,snapshots:[]});
  try{
    return NextResponse.json({configured:true,snapshots:await listSnapshots()});
  }catch(error){
    return NextResponse.json(
      {configured:true,error:error instanceof Error?error.message:"Persistence failure",snapshots:[]},
      {status:503}
    );
  }
}

// Projection persistence uses the server-side writer only.
// Never expose a service-role-backed public mutation endpoint.
export async function POST(){
  return NextResponse.json({error:"Direct projection writes are disabled"},{status:405,headers:{Allow:"GET"}});
}
