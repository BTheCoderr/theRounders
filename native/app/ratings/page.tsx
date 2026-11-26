import {redirect} from "next/navigation";
/** Ratings live at one address per sport (/ratings/nba, /ratings/ncaam, ...). */
export default function Ratings(){redirect("/ratings/nba");}
