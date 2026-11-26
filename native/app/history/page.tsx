import {redirect} from "next/navigation";
/** Past seasons live at /history/<sport> and /history/<sport>/<season>. */
export default function History(){redirect("/history/nba");}
