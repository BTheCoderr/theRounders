"use client";
/** Supabase access token from the magic-link sign-in, sent so the server can apply the visitor's plan. */
export function authHeaders():Record<string,string>{
 try{const t=sessionStorage.getItem("rounders_access_token");return t?{Authorization:"Bearer "+t}:{};}catch{return {};}
}
