Implement the following in the backend and database

Backend should fetch youtube video details from a given set of URLs (use bath API), and collect ALL the data returned.

The following data for each video should be added to the supabase database for each video fetched. Along with another field that timestamps the last fetched (and updated) time for each video.

Update the database implementation accordingly, including correct create_table.sql schemas.

{
    "kind": "youtube#video",
    "etag": "69pihEvHGLXBHela9eq-UxFZTtA",
    "id": "dQw4w9WgXcQ",
    "snippet": {
        "publishedAt": "2009-10-25T06:57:33Z",
        "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
        "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
        "description": "The official video for “Never Gonna Give You Up” by Rick Astley. \n\nNever: The Autobiography 📚 OUT NOW! \nFollow this link to get your copy and listen to Rick’s ‘Never’ playlist ...",
        "channelTitle": "Rick Astley",
        "tags": [
            "rick astley",
            "Never Gonna Give You Up",
            "nggyu",
            "never gonna give you up lyrics",
            "rick rolled",
            "Rick Roll",
            "rick astley official",
            "rickrolled",
            "Fortnite song",
            "Fortnite event",
            "Fortnite dance",
            "fortnite never gonna give you up",
            "rick roll",
            "rickrolling",
            "rick rolling",
            "never gonna give you up",
            "80s music",
            "rick astley new",
            "animated video",
            "rickroll",
            "meme songs",
            "never gonna give u up lyrics",
            "Rick Astley 2022",
            "never gonna let you down",
            "animated",
            "rick rolls 2022",
            "never gonna give you up karaoke"
        ],
        "categoryId": "10",
        "liveBroadcastContent": "none",
        "defaultLanguage": "en",
        "localized": {   <---- # Save this ONLY if default language is not en
            "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
            "description": "The official video for “Never Gonna Give You Up” by Rick Astley. \n\nNever: The Autobiography 📚 OUT NOW! \nFollow this link to get your copy and listen to Rick’s ‘Never’ playlist "
        },
        "defaultAudioLanguage": "en"
    },
    "contentDetails": {
        "duration": "PT3M34S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "true",
        "licensedContent": true,
        "contentRating": {},
        "projection": "rectangular"
    },
    "status": {
        "uploadStatus": "processed",
        "privacyStatus": "public",
        "license": "youtube",
        "embeddable": true,
        "publicStatsViewable": true,
        "madeForKids": false
    },
    "statistics": {
        "viewCount": "1701474331",
        "likeCount": "18579779",
        "favoriteCount": "0",
        "commentCount": "2405276"
    }
}