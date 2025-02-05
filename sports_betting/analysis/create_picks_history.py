import json

def create_picks_history():
    picks = []
    
    # NCAAF Games
    ncaaf_games = [
        {
            "game": "Kansas Jayhawks @ Baylor Bears",
            "spread": {"pick": "Baylor Bears", "confidence": 73, "line": -1.0},
            "total": {"pick": "UNDER 62.5", "confidence": 55},
            "moneyline": {"pick": "Kansas Jayhawks", "confidence": 65}
        },
        {
            "game": "South Carolina Gamecocks @ Clemson Tigers",
            "spread": {"pick": "Clemson Tigers", "confidence": 73, "line": -2.5},
            "total": {"pick": "OVER 49.5", "confidence": 55},
            "moneyline": {"pick": "South Carolina Gamecocks", "confidence": 65}
        },
        {
            "game": "Duke Blue Devils @ Wake Forest Demon Deacons",
            "spread": {"pick": "Wake Forest Demon Deacons", "confidence": 73, "line": -3.5},
            "total": {"pick": "OVER 53.5", "confidence": 55},
            "moneyline": {"pick": "Duke Blue Devils", "confidence": 65}
        },
        {
            "game": "Florida Gators @ Florida State Seminoles",
            "spread": {"pick": "Florida State Seminoles", "confidence": 53, "line": -16.5},
            "total": {"pick": "OVER 45.5", "confidence": 55},
            "moneyline": {"pick": "Florida Gators", "confidence": 45}
        },
        {
            "game": "Louisville Cardinals @ Kentucky Wildcats",
            "spread": {"pick": "Louisville Cardinals", "confidence": 70, "line": 4.0},
            "total": {"pick": "OVER 49.5", "confidence": 55},
            "moneyline": {"pick": "Kentucky Wildcats", "confidence": 68}
        },
        {
            "game": "Michigan Wolverines @ Ohio State Buckeyes",
            "spread": {"pick": "Michigan Wolverines", "confidence": 50, "line": 20.5},
            "total": {"pick": "OVER 41.5", "confidence": 65},
            "moneyline": {"pick": "Ohio State Buckeyes", "confidence": 48}
        },
        {
            "game": "Washington Huskies @ Oregon Ducks",
            "spread": {"pick": "Oregon Ducks", "confidence": 53, "line": -18.0},
            "total": {"pick": "OVER 51.0", "confidence": 55},
            "moneyline": {"pick": "Washington Huskies", "confidence": 45}
        },
        {
            "game": "Tennessee Volunteers @ Vanderbilt Commodores",
            "spread": {"pick": "Vanderbilt Commodores", "confidence": 63, "line": -10.5},
            "total": {"pick": "OVER 46.5", "confidence": 55},
            "moneyline": {"pick": "Tennessee Volunteers", "confidence": 55}
        },
        {
            "game": "West Virginia Mountaineers @ Texas Tech Red Raiders",
            "spread": {"pick": "Texas Tech Red Raiders", "confidence": 73, "line": -3.0},
            "total": {"pick": "UNDER 63.5", "confidence": 55},
            "moneyline": {"pick": "West Virginia Mountaineers", "confidence": 65}
        },
        {
            "game": "UTSA Roadrunners @ Army Black Knights",
            "spread": {"pick": "Army Black Knights", "confidence": 73, "line": -5.5},
            "total": {"pick": "OVER 52.5", "confidence": 55},
            "moneyline": {"pick": "UTSA Roadrunners", "confidence": 65}
        },
        {
            "game": "Illinois Fighting Illini @ Northwestern Wildcats",
            "spread": {"pick": "Northwestern Wildcats", "confidence": 63, "line": -8.5},
            "total": {"pick": "OVER 43.5", "confidence": 65},
            "moneyline": {"pick": "Illinois Fighting Illini", "confidence": 55}
        },
        {
            "game": "Louisiana Ragin Cajuns @ UL Monroe Warhawks",
            "spread": {"pick": "UL Monroe Warhawks", "confidence": 63, "line": -9.5},
            "total": {"pick": "OVER 50.0", "confidence": 55},
            "moneyline": {"pick": "Louisiana Ragin Cajuns", "confidence": 55}
        },
        {
            "game": "North Texas Mean Green @ Temple Owls",
            "spread": {"pick": "Temple Owls", "confidence": 63, "line": -10.5},
            "total": {"pick": "UNDER 63.5", "confidence": 55},
            "moneyline": {"pick": "North Texas Mean Green", "confidence": 55}
        },
        {
            "game": "UConn Huskies @ UMass Minutemen",
            "spread": {"pick": "UMass Minutemen", "confidence": 63, "line": -10.5},
            "total": {"pick": "OVER 49.5", "confidence": 55},
            "moneyline": {"pick": "UConn Huskies", "confidence": 55}
        },
        {
            "game": "Eastern Michigan Eagles @ Western Michigan Broncos",
            "spread": {"pick": "Eastern Michigan Eagles", "confidence": 70, "line": 6.5},
            "total": {"pick": "UNDER 55.5", "confidence": 55},
            "moneyline": {"pick": "Western Michigan Broncos", "confidence": 68}
        },
        {
            "game": "Coastal Carolina Chanticleers @ Georgia State Panthers",
            "spread": {"pick": "Coastal Carolina Chanticleers", "confidence": 70, "line": 1.0},
            "total": {"pick": "OVER 54.0", "confidence": 55},
            "moneyline": {"pick": "Georgia State Panthers", "confidence": 68}
        },
        {
            "game": "Middle Tennessee Blue Raiders @ Florida International Panthers",
            "spread": {"pick": "Florida International Panthers", "confidence": 63, "line": -9.0},
            "total": {"pick": "OVER 51.0", "confidence": 55},
            "moneyline": {"pick": "Middle Tennessee Blue Raiders", "confidence": 55}
        },
        {
            "game": "South Florida Bulls @ Rice Owls",
            "spread": {"pick": "South Florida Bulls", "confidence": 70, "line": 5.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Rice Owls", "confidence": 68}
        },
        {
            "game": "Southern Mississippi Golden Eagles @ Troy Trojans",
            "spread": {"pick": "Southern Mississippi Golden Eagles", "confidence": 50, "line": 17.5},
            "total": {"pick": "OVER 49.0", "confidence": 55},
            "moneyline": {"pick": "Troy Trojans", "confidence": 48}
        },
        {
            "game": "Old Dominion Monarchs @ Arkansas State Red Wolves",
            "spread": {"pick": "Old Dominion Monarchs", "confidence": 70, "line": 4.5},
            "total": {"pick": "UNDER 59.0", "confidence": 55},
            "moneyline": {"pick": "Arkansas State Red Wolves", "confidence": 68}
        },
        {
            "game": "Pittsburgh Panthers @ Boston College Eagles",
            "spread": {"pick": "Boston College Eagles", "confidence": 73, "line": -3.5},
            "total": {"pick": "OVER 50.5", "confidence": 55},
            "moneyline": {"pick": "Pittsburgh Panthers", "confidence": 65}
        },
        {
            "game": "Auburn Tigers @ Alabama Crimson Tide",
            "spread": {"pick": "Alabama Crimson Tide", "confidence": 63, "line": -10.5},
            "total": {"pick": "OVER 52.5", "confidence": 55},
            "moneyline": {"pick": "Auburn Tigers", "confidence": 55}
        },
        {
            "game": "Arizona State Sun Devils @ Arizona Wildcats",
            "spread": {"pick": "Arizona Wildcats", "confidence": 63, "line": -7.5},
            "total": {"pick": "OVER 54.0", "confidence": 55},
            "moneyline": {"pick": "Arizona State Sun Devils", "confidence": 55}
        },
        {
            "game": "Arkansas Razorbacks @ Missouri Tigers",
            "spread": {"pick": "Arkansas Razorbacks", "confidence": 70, "line": 3.0},
            "total": {"pick": "OVER 51.5", "confidence": 55},
            "moneyline": {"pick": "Missouri Tigers", "confidence": 68}
        },
        {
            "game": "California Golden Bears @ SMU Mustangs",
            "spread": {"pick": "California Golden Bears", "confidence": 60, "line": 12.5},
            "total": {"pick": "UNDER 55.0", "confidence": 55},
            "moneyline": {"pick": "SMU Mustangs", "confidence": 58}
        },
        {
            "game": "Central Michigan Chippewas @ Northern Illinois Huskies",
            "spread": {"pick": "Central Michigan Chippewas", "confidence": 63, "line": 7.5},
            "total": {"pick": "OVER 54.0", "confidence": 55},
            "moneyline": {"pick": "Northern Illinois Huskies", "confidence": 55}
        },
        {
            "game": "Charlotte 49ers @ Marshall Thundering Herd",
            "spread": {"pick": "Marshall Thundering Herd", "confidence": 63, "line": -10.5},
            "total": {"pick": "UNDER 55.5", "confidence": 55},
            "moneyline": {"pick": "Charlotte 49ers", "confidence": 55}
        },
        {
            "game": "Cincinnati Bearcats @ Memphis Tigers",
            "spread": {"pick": "Memphis Tigers", "confidence": 63, "line": -6.5},
            "total": {"pick": "OVER 57.5", "confidence": 55},
            "moneyline": {"pick": "Cincinnati Bearcats", "confidence": 55}
        },
        {
            "game": "Colorado Buffaloes @ Utah Utes",
            "spread": {"pick": "Utah Utes", "confidence": 63, "line": -14.5},
            "total": {"pick": "UNDER 48.5", "confidence": 55},
            "moneyline": {"pick": "Colorado Buffaloes", "confidence": 55}
        },
        {
            "game": "Connecticut Huskies @ UMass Minutemen",
            "spread": {"pick": "UMass Minutemen", "confidence": 63, "line": -10.5},
            "total": {"pick": "OVER 49.5", "confidence": 55},
            "moneyline": {"pick": "Connecticut Huskies", "confidence": 55}
        },
        {
            "game": "East Carolina Pirates @ Tulsa Golden Hurricane",
            "spread": {"pick": "Tulsa Golden Hurricane", "confidence": 63, "line": -5.5},
            "total": {"pick": "OVER 61.5", "confidence": 55},
            "moneyline": {"pick": "East Carolina Pirates", "confidence": 55}
        },
        {
            "game": "Florida Atlantic Owls @ Middle Tennessee Blue Raiders",
            "spread": {"pick": "Middle Tennessee Blue Raiders", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Florida Atlantic Owls", "confidence": 55}
        },
        {
            "game": "Florida International Panthers @ Southern Miss Golden Eagles",
            "spread": {"pick": "Southern Miss Golden Eagles", "confidence": 63, "line": -7.5},
            "total": {"pick": "OVER 50.5", "confidence": 55},
            "moneyline": {"pick": "Florida International Panthers", "confidence": 55}
        },
        {
            "game": "Georgia Southern Eagles @ Appalachian State Mountaineers",
            "spread": {"pick": "Appalachian State Mountaineers", "confidence": 63, "line": -9.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Georgia Southern Eagles", "confidence": 55}
        },
        {
            "game": "Georgia Tech Yellow Jackets @ Georgia Bulldogs",
            "spread": {"pick": "Georgia Bulldogs", "confidence": 63, "line": -28.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Georgia Tech Yellow Jackets", "confidence": 55}
        },
        {
            "game": "Hawaii Rainbow Warriors @ San Diego State Aztecs",
            "spread": {"pick": "San Diego State Aztecs", "confidence": 63, "line": -10.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Hawaii Rainbow Warriors", "confidence": 55}
        },
        {
            "game": "Houston Cougars @ Navy Midshipmen",
            "spread": {"pick": "Navy Midshipmen", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Houston Cougars", "confidence": 55}
        },
        {
            "game": "Indiana Hoosiers @ Purdue Boilermakers",
            "spread": {"pick": "Purdue Boilermakers", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Indiana Hoosiers", "confidence": 55}
        },
        {
            "game": "Iowa Hawkeyes @ Nebraska Cornhuskers",
            "spread": {"pick": "Iowa Hawkeyes", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Nebraska Cornhuskers", "confidence": 55}
        },
        {
            "game": "Iowa State Cyclones @ Kansas State Wildcats",
            "spread": {"pick": "Kansas State Wildcats", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Iowa State Cyclones", "confidence": 55}
        },
        {
            "game": "Kent State Golden Flashes @ Akron Zips",
            "spread": {"pick": "Akron Zips", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Kent State Golden Flashes", "confidence": 55}
        },
        {
            "game": "Liberty Flames @ New Mexico State Aggies",
            "spread": {"pick": "Liberty Flames", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "New Mexico State Aggies", "confidence": 55}
        },
        {
            "game": "Louisiana Tech Bulldogs @ UAB Blazers",
            "spread": {"pick": "UAB Blazers", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Louisiana Tech Bulldogs", "confidence": 55}
        },
        {
            "game": "LSU Tigers @ Texas A&M Aggies",
            "spread": {"pick": "LSU Tigers", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Texas A&M Aggies", "confidence": 55}
        },
        {
            "game": "Maryland Terrapins @ Rutgers Scarlet Knights",
            "spread": {"pick": "Rutgers Scarlet Knights", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Maryland Terrapins", "confidence": 55}
        },
        {
            "game": "Miami Hurricanes @ Duke Blue Devils",
            "spread": {"pick": "Duke Blue Devils", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Miami Hurricanes", "confidence": 55}
        },
        {
            "game": "Michigan State Spartans @ Penn State Nittany Lions",
            "spread": {"pick": "Penn State Nittany Lions", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Michigan State Spartans", "confidence": 55}
        },
        {
            "game": "Minnesota Golden Gophers @ Wisconsin Badgers",
            "spread": {"pick": "Wisconsin Badgers", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Minnesota Golden Gophers", "confidence": 55}
        },
        {
            "game": "Mississippi State Bulldogs @ Ole Miss Rebels",
            "spread": {"pick": "Ole Miss Rebels", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Mississippi State Bulldogs", "confidence": 55}
        },
        {
            "game": "Missouri Tigers @ Arkansas Razorbacks",
            "spread": {"pick": "Arkansas Razorbacks", "confidence": 63, "line": -7.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Missouri Tigers", "confidence": 55}
        },
        {
            "game": "NC State Wolfpack @ North Carolina Tar Heels",
            "spread": {"pick": "North Carolina Tar Heels", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "NC State Wolfpack", "confidence": 55}
        },
        {
            "game": "Nebraska Cornhuskers @ Iowa Hawkeyes",
            "spread": {"pick": "Iowa Hawkeyes", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Nebraska Cornhuskers", "confidence": 55}
        },
        {
            "game": "Nevada Wolf Pack @ UNLV Rebels",
            "spread": {"pick": "UNLV Rebels", "confidence": 63, "line": -7.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Nevada Wolf Pack", "confidence": 55}
        },
        {
            "game": "New Mexico Lobos @ Colorado State Rams",
            "spread": {"pick": "Colorado State Rams", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "New Mexico Lobos", "confidence": 55}
        },
        {
            "game": "North Carolina Tar Heels @ NC State Wolfpack",
            "spread": {"pick": "NC State Wolfpack", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "North Carolina Tar Heels", "confidence": 55}
        },
        {
            "game": "North Texas Mean Green @ UTEP Miners",
            "spread": {"pick": "UTEP Miners", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "North Texas Mean Green", "confidence": 55}
        },
        {
            "game": "Northern Illinois Huskies @ Central Michigan Chippewas",
            "spread": {"pick": "Central Michigan Chippewas", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Northern Illinois Huskies", "confidence": 55}
        },
        {
            "game": "Northwestern Wildcats @ Illinois Fighting Illini",
            "spread": {"pick": "Illinois Fighting Illini", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Northwestern Wildcats", "confidence": 55}
        },
        {
            "game": "Notre Dame Fighting Irish @ Stanford Cardinal",
            "spread": {"pick": "Stanford Cardinal", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Notre Dame Fighting Irish", "confidence": 55}
        },
        {
            "game": "Ohio Bobcats @ Bowling Green Falcons",
            "spread": {"pick": "Bowling Green Falcons", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Ohio Bobcats", "confidence": 55}
        },
        {
            "game": "Oklahoma Sooners @ Oklahoma State Cowboys",
            "spread": {"pick": "Oklahoma State Cowboys", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Oklahoma Sooners", "confidence": 55}
        },
        {
            "game": "Oregon Ducks @ Oregon State Beavers",
            "spread": {"pick": "Oregon State Beavers", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Oregon Ducks", "confidence": 55}
        },
        {
            "game": "Pittsburgh Panthers @ Syracuse Orange",
            "spread": {"pick": "Syracuse Orange", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Pittsburgh Panthers", "confidence": 55}
        },
        {
            "game": "Purdue Boilermakers @ Indiana Hoosiers",
            "spread": {"pick": "Indiana Hoosiers", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Purdue Boilermakers", "confidence": 55}
        },
        {
            "game": "Rice Owls @ North Texas Mean Green",
            "spread": {"pick": "North Texas Mean Green", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Rice Owls", "confidence": 55}
        },
        {
            "game": "Rutgers Scarlet Knights @ Maryland Terrapins",
            "spread": {"pick": "Maryland Terrapins", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Rutgers Scarlet Knights", "confidence": 55}
        },
        {
            "game": "San Diego State Aztecs @ Hawaii Rainbow Warriors",
            "spread": {"pick": "Hawaii Rainbow Warriors", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "San Diego State Aztecs", "confidence": 55}
        },
        {
            "game": "San Jose State Spartans @ Fresno State Bulldogs",
            "spread": {"pick": "Fresno State Bulldogs", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "San Jose State Spartans", "confidence": 55}
        },
        {
            "game": "SMU Mustangs @ California Golden Bears",
            "spread": {"pick": "California Golden Bears", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "SMU Mustangs", "confidence": 55}
        },
        {
            "game": "South Alabama Jaguars @ Arkansas State Red Wolves",
            "spread": {"pick": "Arkansas State Red Wolves", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "South Alabama Jaguars", "confidence": 55}
        },
        {
            "game": "Southern Miss Golden Eagles @ Florida International Panthers",
            "spread": {"pick": "Florida International Panthers", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Southern Miss Golden Eagles", "confidence": 55}
        },
        {
            "game": "Stanford Cardinal @ Notre Dame Fighting Irish",
            "spread": {"pick": "Notre Dame Fighting Irish", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Stanford Cardinal", "confidence": 55}
        },
        {
            "game": "Syracuse Orange @ Pittsburgh Panthers",
            "spread": {"pick": "Pittsburgh Panthers", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Syracuse Orange", "confidence": 55}
        },
        {
            "game": "TCU Horned Frogs @ Texas Longhorns",
            "spread": {"pick": "Texas Longhorns", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "TCU Horned Frogs", "confidence": 55}
        },
        {
            "game": "Temple Owls @ North Texas Mean Green",
            "spread": {"pick": "North Texas Mean Green", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Temple Owls", "confidence": 55}
        },
        {
            "game": "Tennessee Volunteers @ Vanderbilt Commodores",
            "spread": {"pick": "Vanderbilt Commodores", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Tennessee Volunteers", "confidence": 55}
        },
        {
            "game": "Texas A&M Aggies @ LSU Tigers",
            "spread": {"pick": "LSU Tigers", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Texas A&M Aggies", "confidence": 55}
        },
        {
            "game": "Texas Longhorns @ TCU Horned Frogs",
            "spread": {"pick": "TCU Horned Frogs", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Texas Longhorns", "confidence": 55}
        },
        {
            "game": "Texas State Bobcats @ Louisiana Ragin Cajuns",
            "spread": {"pick": "Louisiana Ragin Cajuns", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Texas State Bobcats", "confidence": 55}
        },
        {
            "game": "Toledo Rockets @ Ball State Cardinals",
            "spread": {"pick": "Ball State Cardinals", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Toledo Rockets", "confidence": 55}
        },
        {
            "game": "Troy Trojans @ South Alabama Jaguars",
            "spread": {"pick": "South Alabama Jaguars", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Troy Trojans", "confidence": 55}
        },
        {
            "game": "Tulane Green Wave @ Memphis Tigers",
            "spread": {"pick": "Memphis Tigers", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Tulane Green Wave", "confidence": 55}
        },
        {
            "game": "Tulsa Golden Hurricane @ East Carolina Pirates",
            "spread": {"pick": "East Carolina Pirates", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Tulsa Golden Hurricane", "confidence": 55}
        },
        {
            "game": "UAB Blazers @ Louisiana Tech Bulldogs",
            "spread": {"pick": "Louisiana Tech Bulldogs", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "UAB Blazers", "confidence": 55}
        },
        {
            "game": "UCF Knights @ South Florida Bulls",
            "spread": {"pick": "South Florida Bulls", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "UCF Knights", "confidence": 55}
        },
        {
            "game": "UCLA Bruins @ USC Trojans",
            "spread": {"pick": "USC Trojans", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "UCLA Bruins", "confidence": 55}
        },
        {
            "game": "UMass Minutemen @ Connecticut Huskies",
            "spread": {"pick": "Connecticut Huskies", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "UMass Minutemen", "confidence": 55}
        },
        {
            "game": "UNLV Rebels @ Nevada Wolf Pack",
            "spread": {"pick": "Nevada Wolf Pack", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "UNLV Rebels", "confidence": 55}
        },
        {
            "game": "USC Trojans @ UCLA Bruins",
            "spread": {"pick": "UCLA Bruins", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "USC Trojans", "confidence": 55}
        },
        {
            "game": "UTEP Miners @ North Texas Mean Green",
            "spread": {"pick": "North Texas Mean Green", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "UTEP Miners", "confidence": 55}
        },
        {
            "game": "UTSA Roadrunners @ Army Black Knights",
            "spread": {"pick": "Army Black Knights", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "UTSA Roadrunners", "confidence": 55}
        },
        {
            "game": "Vanderbilt Commodores @ Tennessee Volunteers",
            "spread": {"pick": "Tennessee Volunteers", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Vanderbilt Commodores", "confidence": 55}
        },
        {
            "game": "Virginia Cavaliers @ Virginia Tech Hokies",
            "spread": {"pick": "Virginia Tech Hokies", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Virginia Cavaliers", "confidence": 55}
        },
        {
            "game": "Wake Forest Demon Deacons @ Duke Blue Devils",
            "spread": {"pick": "Duke Blue Devils", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Wake Forest Demon Deacons", "confidence": 55}
        },
        {
            "game": "Washington Huskies @ Washington State Cougars",
            "spread": {"pick": "Washington State Cougars", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Washington Huskies", "confidence": 55}
        },
        {
            "game": "West Virginia Mountaineers @ Texas Tech Red Raiders",
            "spread": {"pick": "Texas Tech Red Raiders", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "West Virginia Mountaineers", "confidence": 55}
        },
        {
            "game": "Western Kentucky Hilltoppers @ Marshall Thundering Herd",
            "spread": {"pick": "Marshall Thundering Herd", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Western Kentucky Hilltoppers", "confidence": 55}
        },
        {
            "game": "Western Michigan Broncos @ Eastern Michigan Eagles",
            "spread": {"pick": "Eastern Michigan Eagles", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Western Michigan Broncos", "confidence": 55}
        },
        {
            "game": "Wisconsin Badgers @ Minnesota Golden Gophers",
            "spread": {"pick": "Minnesota Golden Gophers", "confidence": 63, "line": -3.5},
            "total": {"pick": "OVER 54.5", "confidence": 55},
            "moneyline": {"pick": "Wisconsin Badgers", "confidence": 55}
        },
        {
            "game": "Wyoming Cowboys @ Boise State Broncos",
            "spread": {"pick": "Boise State Broncos", "confidence": 63, "line": -3.5},
            "total": {"pick": "UNDER 54.5", "confidence": 55},
            "moneyline": {"pick": "Wyoming Cowboys", "confidence": 55}
        }
    ]

    # NCAAB Games
    ncaab_games = [
        {
            "game": "UC Riverside Highlanders @ Idaho Vandals",
            "spread": {"pick": "UC Riverside Highlanders", "confidence": 65, "line": -5.0},
            "total": {"pick": "UNDER 152.0", "confidence": 55},
            "moneyline": {"pick": "Idaho Vandals", "confidence": 65}
        },
        {
            "game": "Bellarmine Knights @ Northern Kentucky Norse",
            "spread": {"pick": "Bellarmine Knights", "confidence": 55, "line": 3.5},
            "total": {"pick": "OVER 135.5", "confidence": 55},
            "moneyline": {"pick": "Northern Kentucky Norse", "confidence": 55}
        },
        {
            "game": "Bucknell Bison @ Siena Saints",
            "spread": {"pick": "Siena Saints", "confidence": 80, "line": -3.5},
            "total": {"pick": "OVER 133.5", "confidence": 55},
            "moneyline": {"pick": "Bucknell Bison", "confidence": 70}
        },
        {
            "game": "Georgia Southern Eagles @ Drake Bulldogs",
            "spread": {"pick": "Drake Bulldogs", "confidence": 60, "line": -13.5},
            "total": {"pick": "UNDER 145.5", "confidence": 55},
            "moneyline": {"pick": "Georgia Southern Eagles", "confidence": 50}
        },
        {
            "game": "Florida Gulf Coast Eagles @ Florida Atlantic Owls",
            "spread": {"pick": "Florida Atlantic Owls", "confidence": 60, "line": -14.0},
            "total": {"pick": "UNDER 144.5", "confidence": 55},
            "moneyline": {"pick": "Florida Gulf Coast Eagles", "confidence": 50}
        },
        {
            "game": "Furman Paladins @ Kansas Jayhawks",
            "spread": {"pick": "Furman Paladins", "confidence": 55, "line": 21.5},
            "total": {"pick": "UNDER 147.5", "confidence": 55},
            "moneyline": {"pick": "Kansas Jayhawks", "confidence": 55}
        },
        {
            "game": "Air Force Falcons @ Wright St Raiders",
            "spread": {"pick": "Air Force Falcons", "confidence": 55, "line": 9.0},
            "total": {"pick": "OVER 137.5", "confidence": 55},
            "moneyline": {"pick": "Wright St Raiders", "confidence": 55}
        },
        {
            "game": "Rice Owls @ Arkansas St Red Wolves",
            "spread": {"pick": "Arkansas St Red Wolves", "confidence": 60, "line": -8.5},
            "total": {"pick": "OVER 141.0", "confidence": 55},
            "moneyline": {"pick": "Rice Owls", "confidence": 50}
        },
        {
            "game": "Detroit Mercy Titans @ Eastern Michigan Eagles",
            "spread": {"pick": "Detroit Mercy Titans", "confidence": 65, "line": 6.5},
            "total": {"pick": "OVER 134.0", "confidence": 55},
            "moneyline": {"pick": "Eastern Michigan Eagles", "confidence": 65}
        },
        {
            "game": "Jacksonville Dolphins @ Georgia Bulldogs",
            "spread": {"pick": "Georgia Bulldogs", "confidence": 60, "line": -16.5},
            "total": {"pick": "UNDER 143.5", "confidence": 55},
            "moneyline": {"pick": "Jacksonville Dolphins", "confidence": 50}
        },
        {
            "game": "San Diego St Aztecs @ Houston Cougars",
            "spread": {"pick": "Houston Cougars", "confidence": 60, "line": -12.5},
            "total": {"pick": "OVER 126.5", "confidence": 65},
            "moneyline": {"pick": "San Diego St Aztecs", "confidence": 50}
        },
        {
            "game": "Marist Red Foxes @ Lehigh Mountain Hawks",
            "spread": {"pick": "Lehigh Mountain Hawks", "confidence": 80, "line": -1.5},
            "total": {"pick": "OVER 139.5", "confidence": 55},
            "moneyline": {"pick": "Marist Red Foxes", "confidence": 70}
        },
        {
            "game": "Maryland-Eastern Shore Hawks @ UConn Huskies",
            "spread": {"pick": "Maryland-Eastern Shore Hawks", "confidence": 55, "line": 41.5},
            "total": {"pick": "UNDER 143.5", "confidence": 55},
            "moneyline": {"pick": "UConn Huskies", "confidence": 55}
        },
        {
            "game": "Oakland Golden Grizzlies @ Toledo Rockets",
            "spread": {"pick": "Oakland Golden Grizzlies", "confidence": 65, "line": 7.5},
            "total": {"pick": "UNDER 148.5", "confidence": 55},
            "moneyline": {"pick": "Toledo Rockets", "confidence": 65}
        },
        {
            "game": "CSU Fullerton Titans @ Pacific Tigers",
            "spread": {"pick": "CSU Fullerton Titans", "confidence": 65, "line": 4.5},
            "total": {"pick": "OVER 138.5", "confidence": 55},
            "moneyline": {"pick": "Pacific Tigers", "confidence": 65}
        },
        {
            "game": "Kennesaw St Owls @ Kent State Golden Flashes",
            "spread": {"pick": "Kennesaw St Owls", "confidence": 65, "line": 5.5},
            "total": {"pick": "OVER 140.0", "confidence": 55},
            "moneyline": {"pick": "Kent State Golden Flashes", "confidence": 65}
        },
        {
            "game": "Lipscomb Bisons @ Alabama A&M Bulldogs",
            "spread": {"pick": "Lipscomb Bisons", "confidence": 55, "line": 11.5},
            "total": {"pick": "UNDER 150.5", "confidence": 55},
            "moneyline": {"pick": "Alabama A&M Bulldogs", "confidence": 55}
        },
        {
            "game": "Marshall Thundering Herd @ Western Kentucky Hilltoppers",
            "spread": {"pick": "Marshall Thundering Herd", "confidence": 65, "line": 8.0},
            "total": {"pick": "UNDER 153.0", "confidence": 55},
            "moneyline": {"pick": "Western Kentucky Hilltoppers", "confidence": 65}
        },
        {
            "game": "Utah Tech Trailblazers @ Portland St Vikings",
            "spread": {"pick": "Portland St Vikings", "confidence": 70, "line": -6.5},
            "total": {"pick": "UNDER 153.5", "confidence": 55},
            "moneyline": {"pick": "Utah Tech Trailblazers", "confidence": 60}
        },
        {
            "game": "Abilene Christian Wildcats @ Omaha Mavericks",
            "spread": {"pick": "Omaha Mavericks", "confidence": 80, "line": -2.5},
            "total": {"pick": "UNDER 142.5", "confidence": 55},
            "moneyline": {"pick": "Abilene Christian Wildcats", "confidence": 70}
        },
        {
            "game": "CSU Bakersfield Roadrunners @ Southern Utah Thunderbirds",
            "spread": {"pick": "CSU Bakersfield Roadrunners", "confidence": 65, "line": 4.5},
            "total": {"pick": "OVER 139.5", "confidence": 55},
            "moneyline": {"pick": "Southern Utah Thunderbirds", "confidence": 65}
        },
        {
            "game": "UMKC Kangaroos @ SE Missouri St Redhawks",
            "spread": {"pick": "UMKC Kangaroos", "confidence": 75, "line": 2.5},
            "total": {"pick": "OVER 136.5", "confidence": 55},
            "moneyline": {"pick": "SE Missouri St Redhawks", "confidence": 75}
        },
        {
            "game": "Oregon Ducks @ Alabama Crimson Tide",
            "spread": {"pick": "Alabama Crimson Tide", "confidence": 70, "line": -6.5},
            "total": {"pick": "UNDER 164.5", "confidence": 65},
            "moneyline": {"pick": "Oregon Ducks", "confidence": 60}
        },
        {
            "game": "Towson Tigers @ UC Irvine Anteaters",
            "spread": {"pick": "Towson Tigers", "confidence": 55, "line": 9.5},
            "total": {"pick": "OVER 129.5", "confidence": 65},
            "moneyline": {"pick": "UC Irvine Anteaters", "confidence": 55}
        },
        {
            "game": "Cal Poly Mustangs @ Stanford Cardinal",
            "spread": {"pick": "Cal Poly Mustangs", "confidence": 55, "line": 14.5},
            "total": {"pick": "UNDER 152.5", "confidence": 55},
            "moneyline": {"pick": "Stanford Cardinal", "confidence": 55}
        },
        {
            "game": "Mercyhurst Lakers @ Sacramento St Hornets",
            "spread": {"pick": "Mercyhurst Lakers", "confidence": 55, "line": 8.5},
            "total": {"pick": "OVER 129.5", "confidence": 65},
            "moneyline": {"pick": "Sacramento St Hornets", "confidence": 55}
        },
        {
            "game": "UC Davis Aggies @ Oregon St Beavers",
            "spread": {"pick": "Oregon St Beavers", "confidence": 60, "line": -10.0},
            "total": {"pick": "OVER 140.0", "confidence": 55},
            "moneyline": {"pick": "UC Davis Aggies", "confidence": 50}
        }
    ]

    # NHL Games
    nhl_games = [
        {
            "game": "Canadiens @ Rangers",
            "puck_line": {"pick": "Canadiens", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 6.5", "confidence": 55},
            "moneyline": {"pick": "Rangers", "confidence": 60}
        },
        {
            "game": "Hurricanes @ Panthers",
            "puck_line": {"pick": "Panthers", "confidence": 65, "line": -1.5},
            "total": {"pick": "UNDER 6.5", "confidence": 55},
            "moneyline": {"pick": "Hurricanes", "confidence": 60}
        },
        {
            "game": "Maple Leafs @ Lightning",
            "puck_line": {"pick": "Maple Leafs", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 6.5", "confidence": 55},
            "moneyline": {"pick": "Lightning", "confidence": 60}
        },
        {
            "game": "Capitals @ Devils",
            "puck_line": {"pick": "Devils", "confidence": 65, "line": -1.5},
            "total": {"pick": "UNDER 6.5", "confidence": 55},
            "moneyline": {"pick": "Capitals", "confidence": 60}
        },
        {
            "game": "Flames @ Penguins",
            "puck_line": {"pick": "Flames", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 6.0", "confidence": 55},
            "moneyline": {"pick": "Penguins", "confidence": 60}
        },
        {
            "game": "Flyers @ Blues",
            "puck_line": {"pick": "Flyers", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 5.5", "confidence": 55},
            "moneyline": {"pick": "Blues", "confidence": 60}
        },
        {
            "game": "Senators @ Kings",
            "puck_line": {"pick": "Kings", "confidence": 65, "line": -1.5},
            "total": {"pick": "UNDER 5.5", "confidence": 55},
            "moneyline": {"pick": "Senators", "confidence": 60}
        },
        {
            "game": "Sabres @ Islanders",
            "puck_line": {"pick": "Sabres", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 5.5", "confidence": 55},
            "moneyline": {"pick": "Islanders", "confidence": 60}
        },
        {
            "game": "Predators @ Wild",
            "puck_line": {"pick": "Wild", "confidence": 65, "line": -1.5},
            "total": {"pick": "UNDER 5.5", "confidence": 55},
            "moneyline": {"pick": "Predators", "confidence": 60}
        },
        {
            "game": "Oilers @ Avalanche",
            "puck_line": {"pick": "Avalanche", "confidence": 65, "line": -1.5},
            "total": {"pick": "UNDER 6.5", "confidence": 55},
            "moneyline": {"pick": "Oilers", "confidence": 60}
        },
        {
            "game": "Utah Hockey Club @ Golden Knights",
            "puck_line": {"pick": "Utah Hockey Club", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 6.5", "confidence": 55},
            "moneyline": {"pick": "Golden Knights", "confidence": 60}
        },
        {
            "game": "Sharks @ Kraken",
            "puck_line": {"pick": "Sharks", "confidence": 65, "line": 1.5},
            "total": {"pick": "UNDER 6.0", "confidence": 55},
            "moneyline": {"pick": "Kraken", "confidence": 60}
        }
    ]
    
    # NBA Games
    nba_games = [
        {
            "game": "Atlanta Hawks @ Charlotte Hornets",
            "spread": {"pick": "Charlotte Hornets", "confidence": 75, "line": -4.5},
            "total": {"pick": "UNDER 225.5", "confidence": 55},
            "moneyline": {"pick": "Atlanta Hawks", "confidence": 70}
        },
        {
            "game": "Philadelphia 76ers @ Detroit Pistons",
            "spread": {"pick": "Detroit Pistons", "confidence": 75, "line": -1.5},
            "total": {"pick": "OVER 215.0", "confidence": 55},
            "moneyline": {"pick": "Philadelphia 76ers", "confidence": 70}
        },
        {
            "game": "Washington Wizards @ Milwaukee Bucks",
            "spread": {"pick": "Milwaukee Bucks", "confidence": 55, "line": -15.5},
            "total": {"pick": "UNDER 229.0", "confidence": 55},
            "moneyline": {"pick": "Washington Wizards", "confidence": 50}
        },
        {
            "game": "Golden State Warriors @ Phoenix Suns",
            "spread": {"pick": "Golden State Warriors", "confidence": 70, "line": 2.5},
            "total": {"pick": "UNDER 232.5", "confidence": 65},
            "moneyline": {"pick": "Phoenix Suns", "confidence": 70}
        },
        {
            "game": "Dallas Mavericks @ Utah Jazz",
            "spread": {"pick": "Utah Jazz", "confidence": 65, "line": -6.5},
            "total": {"pick": "UNDER 231.5", "confidence": 65},
            "moneyline": {"pick": "Dallas Mavericks", "confidence": 60}
        },
        {
            "game": "San Antonio Spurs @ New York Knicks",
            "spread": {"pick": "New York Knicks", "confidence": 65, "line": -9.5},
            "total": {"pick": "UNDER 225.5", "confidence": 55},
            "moneyline": {"pick": "San Antonio Spurs", "confidence": 60}
        },
        {
            "game": "Minnesota Timberwolves @ Dallas Mavericks",
            "spread": {"pick": "Dallas Mavericks", "confidence": 75, "line": -3.5},
            "total": {"pick": "UNDER 228.5", "confidence": 55},
            "moneyline": {"pick": "Minnesota Timberwolves", "confidence": 70}
        },
        {
            "game": "Philadelphia 76ers @ Boston Celtics",
            "spread": {"pick": "Boston Celtics", "confidence": 65, "line": -8.5},
            "total": {"pick": "UNDER 228.0", "confidence": 55},
            "moneyline": {"pick": "Philadelphia 76ers", "confidence": 60}
        },
        {
            "game": "Los Angeles Lakers @ Golden State Warriors",
            "spread": {"pick": "Golden State Warriors", "confidence": 75, "line": -3.5},
            "total": {"pick": "UNDER 234.0", "confidence": 65},
            "moneyline": {"pick": "Los Angeles Lakers", "confidence": 70}
        },
        {
            "game": "Denver Nuggets @ Phoenix Suns",
            "spread": {"pick": "Denver Nuggets", "confidence": 70, "line": 2.5},
            "total": {"pick": "UNDER 225.5", "confidence": 55},
            "moneyline": {"pick": "Phoenix Suns", "confidence": 70}
        }
    ]
    
    # NFL Games
    nfl_games = [
        {
            "game": "Arizona Cardinals @ Minnesota Vikings",
            "spread": {"pick": "Minnesota Vikings", "confidence": 70, "line": -3.0},
            "total": {"pick": "UNDER 45.0", "confidence": 55},
            "moneyline": {"pick": "Minnesota Vikings", "confidence": 65}
        },
        {
            "game": "Los Angeles Chargers @ Atlanta Falcons",
            "spread": {"pick": "Atlanta Falcons", "confidence": 70, "line": -1.0},
            "total": {"pick": "UNDER 48.0", "confidence": 65},
            "moneyline": {"pick": "Atlanta Falcons", "confidence": 65}
        },
        {
            "game": "Pittsburgh Steelers @ Cincinnati Bengals",
            "spread": {"pick": "Pittsburgh Steelers", "confidence": 70, "line": 3.0},
            "total": {"pick": "UNDER 47.0", "confidence": 55},
            "moneyline": {"pick": "Pittsburgh Steelers", "confidence": 65}
        },
        {
            "game": "Houston Texans @ Jacksonville Jaguars",
            "spread": {"pick": "Houston Texans", "confidence": 60, "line": 3.5},
            "total": {"pick": "OVER 44.0", "confidence": 55},
            "moneyline": {"pick": "Houston Texans", "confidence": 55}
        },
        {
            "game": "Indianapolis Colts @ New England Patriots",
            "spread": {"pick": "Indianapolis Colts", "confidence": 70, "line": 2.5},
            "total": {"pick": "OVER 42.5", "confidence": 55},
            "moneyline": {"pick": "Indianapolis Colts", "confidence": 65}
        },
        {
            "game": "Seattle Seahawks @ New York Jets",
            "spread": {"pick": "New York Jets", "confidence": 70, "line": -1.0},
            "total": {"pick": "OVER 41.5", "confidence": 65},
            "moneyline": {"pick": "New York Jets", "confidence": 65}
        },
        {
            "game": "Tennessee Titans @ Washington Commanders",
            "spread": {"pick": "Washington Commanders", "confidence": 60, "line": 6.0},
            "total": {"pick": "UNDER 44.5", "confidence": 55},
            "moneyline": {"pick": "Washington Commanders", "confidence": 55}
        },
        {
            "game": "Tampa Bay Buccaneers @ Carolina Panthers",
            "spread": {"pick": "Carolina Panthers", "confidence": 60, "line": 6.0},
            "total": {"pick": "UNDER 46.5", "confidence": 55},
            "moneyline": {"pick": "Carolina Panthers", "confidence": 55}
        },
        {
            "game": "Los Angeles Rams @ New Orleans Saints",
            "spread": {"pick": "Los Angeles Rams", "confidence": 70, "line": 2.5},
            "total": {"pick": "UNDER 49.5", "confidence": 65},
            "moneyline": {"pick": "Los Angeles Rams", "confidence": 65}
        },
        {
            "game": "Philadelphia Eagles @ Baltimore Ravens",
            "spread": {"pick": "Philadelphia Eagles", "confidence": 70, "line": 2.5},
            "total": {"pick": "UNDER 50.5", "confidence": 65},
            "moneyline": {"pick": "Philadelphia Eagles", "confidence": 65}
        },
        {
            "game": "San Francisco 49ers @ Buffalo Bills",
            "spread": {"pick": "San Francisco 49ers", "confidence": 60, "line": 6.0},
            "total": {"pick": "UNDER 44.5", "confidence": 55},
            "moneyline": {"pick": "San Francisco 49ers", "confidence": 55}
        },
        {
            "game": "Cleveland Browns @ Denver Broncos",
            "spread": {"pick": "Denver Broncos", "confidence": 60, "line": 5.5},
            "total": {"pick": "OVER 42.0", "confidence": 55},
            "moneyline": {"pick": "Denver Broncos", "confidence": 55}
        },
        {
            "game": "Green Bay Packers @ Detroit Lions",
            "spread": {"pick": "Green Bay Packers", "confidence": 60, "line": 5.5},
            "total": {"pick": "UNDER 51.5", "confidence": 65},
            "moneyline": {"pick": "Green Bay Packers", "confidence": 55}
        },
        {
            "game": "Atlanta Falcons @ Minnesota Vikings",
            "spread": {"pick": "Minnesota Vikings", "confidence": 60, "line": 5.5},
            "total": {"pick": "UNDER 46.5", "confidence": 55},
            "moneyline": {"pick": "Minnesota Vikings", "confidence": 55}
        },
        {
            "game": "Carolina Panthers @ Philadelphia Eagles",
            "spread": {"pick": "Philadelphia Eagles", "confidence": 50, "line": 13.0},
            "total": {"pick": "UNDER 45.5", "confidence": 55},
            "moneyline": {"pick": "Philadelphia Eagles", "confidence": 45}
        },
        {
            "game": "Cleveland Browns @ Pittsburgh Steelers",
            "spread": {"pick": "Pittsburgh Steelers", "confidence": 60, "line": 6.0},
            "total": {"pick": "OVER 40.5", "confidence": 65},
            "moneyline": {"pick": "Pittsburgh Steelers", "confidence": 55}
        },
        {
            "game": "Jacksonville Jaguars @ Tennessee Titans",
            "spread": {"pick": "Tennessee Titans", "confidence": 70, "line": 2.5},
            "total": {"pick": "OVER 43.5", "confidence": 55},
            "moneyline": {"pick": "Tennessee Titans", "confidence": 65}
        },
        {
            "game": "Las Vegas Raiders @ Tampa Bay Buccaneers",
            "spread": {"pick": "Tampa Bay Buccaneers", "confidence": 50, "line": 8.0},
            "total": {"pick": "UNDER 45.5", "confidence": 55},
            "moneyline": {"pick": "Tampa Bay Buccaneers", "confidence": 45}
        },
        {
            "game": "New York Jets @ Miami Dolphins",
            "spread": {"pick": "New York Jets", "confidence": 60, "line": 6.0},
            "total": {"pick": "UNDER 44.5", "confidence": 55},
            "moneyline": {"pick": "New York Jets", "confidence": 55}
        },
        {
            "game": "New Orleans Saints @ New York Giants",
            "spread": {"pick": "New Orleans Saints", "confidence": 60, "line": 4.0},
            "total": {"pick": "OVER 40.0", "confidence": 65},
            "moneyline": {"pick": "New Orleans Saints", "confidence": 55}
        },
        {
            "game": "Seattle Seahawks @ Arizona Cardinals",
            "spread": {"pick": "Seattle Seahawks", "confidence": 70, "line": 2.0},
            "total": {"pick": "UNDER 45.5", "confidence": 55},
            "moneyline": {"pick": "Seattle Seahawks", "confidence": 65}
        },
        {
            "game": "Buffalo Bills @ Los Angeles Rams",
            "spread": {"pick": "Buffalo Bills", "confidence": 60, "line": 3.5},
            "total": {"pick": "UNDER 49.0", "confidence": 65},
            "moneyline": {"pick": "Buffalo Bills", "confidence": 55}
        },
        {
            "game": "Chicago Bears @ San Francisco 49ers",
            "spread": {"pick": "San Francisco 49ers", "confidence": 60, "line": 6.0},
            "total": {"pick": "UNDER 44.5", "confidence": 55},
            "moneyline": {"pick": "San Francisco 49ers", "confidence": 55}
        },
        {
            "game": "Los Angeles Chargers @ Kansas City Chiefs",
            "spread": {"pick": "Los Angeles Chargers", "confidence": 60, "line": 4.5},
            "total": {"pick": "UNDER 44.5", "confidence": 55},
            "moneyline": {"pick": "Los Angeles Chargers", "confidence": 55}
        },
        {
            "game": "Cincinnati Bengals @ Dallas Cowboys",
            "spread": {"pick": "Cincinnati Bengals", "confidence": 60, "line": 6.0},
            "total": {"pick": "UNDER 45.5", "confidence": 55},
            "moneyline": {"pick": "Cincinnati Bengals", "confidence": 55}
        }
    ]

    # Add all games to picks list
    for sport, games, pick_type in [
        ("NCAAF", ncaaf_games, "Spread"),
        ("NCAAB", ncaab_games, "Spread"),
        ("NHL", nhl_games, "Puck Line"),
        ("NBA", nba_games, "Spread"),
        ("NFL", nfl_games, "Spread")
    ]:
        for game in games:
            picks.extend([
                {
                    "date": "2023-11-25",
                    "sport": sport,
                    "game": game["game"],
                    "pick_type": pick_type,
                    "pick": game[pick_type.lower().replace(" ", "_")]["pick"],
                    "confidence": game[pick_type.lower().replace(" ", "_")]["confidence"],
                    "line": game[pick_type.lower().replace(" ", "_")]["line"],
                    "result": "Pending"
                },
                {
                    "date": "2023-11-25",
                    "sport": sport,
                    "game": game["game"],
                    "pick_type": "Total",
                    "pick": game["total"]["pick"],
                    "confidence": game["total"]["confidence"],
                    "result": "Pending"
                },
                {
                    "date": "2023-11-25",
                    "sport": sport,
                    "game": game["game"],
                    "pick_type": "Moneyline",
                    "pick": game["moneyline"]["pick"],
                    "confidence": game["moneyline"]["confidence"],
                    "result": "Pending"
                }
            ])
    
    # Save to JSON file
    with open('picks_history.json', 'w') as f:
        json.dump(picks, f, indent=4)

if __name__ == "__main__":
    create_picks_history() 