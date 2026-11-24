/** RFC 4180 CSV with formula-injection protection for spreadsheet users. */
export function toCsv(header:string[],rows:Array<Array<string|number|boolean|null|undefined>>):string{
 const cell=(v:string|number|boolean|null|undefined)=>{
  if(v===null||v===undefined)return "";
  let s=String(v);
  if(/^[=+\-@\t\r]/.test(s)&&typeof v==="string")s="'"+s;
  return /[",\r\n]/.test(s)?`"${s.replace(/"/g,'""')}"`:s;
 };
 return [header,...rows].map(r=>r.map(cell).join(",")).join("\r\n")+"\r\n";
}
