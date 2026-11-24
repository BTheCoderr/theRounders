import {siteOrigin} from "./site-origin";
export default function StructuredData(){
 const url=siteOrigin();
 const description="Sports ratings and pregame predictions for NBA, NFL, college basketball, college football, NHL and MLB.";
 const data={"@context":"https://schema.org","@graph":[{"@type":"Organization",name:"The Rounders",url,description},{"@type":"WebSite",name:"The Rounders",url,description}]};
 return <script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify(data).replace(/</g,"\\u003c")}}/>;
}
