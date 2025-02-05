confidence_factors = {
    "NBA": {
        "Spread": {
            "min_confidence": 70,
            "factors": [
                "Home team advantage",
                "Recent team performance",
                "Head-to-head record",
                "Key player availability",
                "Rest days between games"
            ]
        },
        "Total": {
            "min_confidence": 65,
            "factors": [
                "Team scoring averages",
                "Defensive ratings",
                "Pace of play",
                "Previous matchup totals"
            ]
        }
    },
    "NHL": {
        "Puck Line": {
            "min_confidence": 65,
            "factors": [
                "Goalie matchup",
                "Special teams performance",
                "Back-to-back games",
                "Home/Away records"
            ]
        }
    }
} 