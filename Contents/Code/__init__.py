TITLE = 'Rooster Teeth'
ART   = 'art-default.jpg'
ICON  = 'icon-default.png'
BASE_URL = 'http://roosterteeth.com'
HTTP_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1'

CHANNELS = [
    {
        'title': 'Rooster Teeth',
        'url': 'http://roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/699276126644936704/rCkvY0SS_400x400.jpg'
    },
    {
        'title': 'Achievement Hunter',
        'url': 'http://achievementhunter.roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/1834741417/283025_10150250994985698_268895495697_7664630_357027_n_400x400.jpg'
    },
    {
        'title': 'Funhaus',
        'url': 'http://funhaus.roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/563456577076596737/kTHggklU_400x400.png'
    },
    {
        'title': 'ScrewAttack',
        'url': 'http://screwattack.roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/735516290773704704/gJZmqxDZ_400x400.jpg'
    },
    {
        'title': 'Game Attack',
        'url': 'http://gameattack.roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/783404372323475456/A3XK5iD7_400x400.jpg'
    },
    {
        'title': 'The Know',
        'url': 'http://theknow.roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/639837776934891520/WA-rAvdP_400x400.png'
    },
    {
        'title': 'Cow Chop',
        'url': 'http://cowchop.roosterteeth.com/show',
        'image': 'https://pbs.twimg.com/profile_images/671530901734473728/CfowRP9t_400x400.png'
    }
]

##########################################################################################
def Start():
    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1     = TITLE
    ObjectContainer.art        = R(ART)

    HTTP.CacheTime  = CACHE_1HOUR
    HTTP.User_Agent = HTTP_USER_AGENT

##########################################################################################
@handler('/video/roosterteeth', TITLE, thumb = ICON, art = ART)
def MainMenu():

    oc = ObjectContainer()
    
    oc.add(PrefsObject(title = "Preferences"))
    
    for channel in CHANNELS:
        oc.add(
            DirectoryObject(
                key = Callback(Shows, url=channel['url'], title=channel['title']),
                title = channel['title'],
                thumb = channel['image']
            )
        )
        
    return oc
    
##########################################################################################
@route('/video/roosterteeth/Shows', TITLE, thumb = ICON, art = ART)
def Shows(url, title):

    oc = ObjectContainer(title2=title)

    shows       = []
    showNames   = []
        
    # Add shows by parsing the site
    element = HTML.ElementFromURL(url)

    for item in element.xpath("//*[@class = 'square-blocks']//a"):
        show = {}
        try:
            show["url"] = item.xpath("./@href")[0]
            show["img"] = item.xpath(".//img/@src")[0]
            
            if show["img"].startswith("//"):
                show["img"] = 'http:' + show["img"]
                
            show["name"] = item.xpath(".//*[@class='name']/text()")[0]
            show["desc"] = item.xpath(".//*[@class='post-stamp']/text()")[0]
        
            if not show["name"] in showNames:
                showNames.append(show["name"])
                shows.append(show)
        except:
            pass     
    
    sortedShows = sorted(shows, key=lambda show: show["name"])
    for show in sortedShows:

        if show["name"] in ('RT Sponsor Cut'):
            if not (Prefs['login'] and Prefs['username'] and Prefs['password']):
                continue

        oc.add(
            DirectoryObject(
                key = Callback(
                    EpisodeCategories, 
                    title = show["name"],
                    url = show["url"], 
                    thumb = show["img"]
                ), 
                title = show["name"],
                summary = show["desc"],
                thumb = show["img"]
            )
        )
    
    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "No shows found."
                     
    return oc

##########################################################################################
@route("/video/roosterteeth/EpisodeCategories")
def EpisodeCategories(title, url, thumb):

    oc = ObjectContainer(title2=title)

    content = HTTP.Request(url).content
    
    if 'Sponsor Only Content' in content:
        if not (Prefs['login'] and Prefs['username'] and Prefs['password']):
            return ObjectContainer(header="Sponsor Only", message="This show contains sponsor only content.\r\nPlease login to access this show")
    
    element = HTML.ElementFromString(content)
    
    try:
        art = element.xpath("//*[@class='cover-image']/@style")[0].split("(")[1].split(")")[0]
        
        if art.startswith("//"):
            art = 'http:' + art 
    except:
        art = None
    
    '''
    for category in [{'title': 'Recently Added Videos', 'xpath': "//*[@id='tab-content-trending']//*[@class='episodes--recent']//*[@id='recent-carousel-comment']//text()"}, {'title': 'All Time Favorites', 'xpath': "//*[@id='tab-content-trending']//*[@class='episodes--all-time-favs']"}]:
        oc.add(
            DirectoryObject(
                key = Callback(
                    Items, 
                    title = category['title'],
                    url = url,
                    thumb = thumb,
                    xpath_string = category['xpath'],
                    art = art,
                    recent = 'recent' in category['xpath']
                ), 
                title = category['title'],
                thumb = thumb,
                art = art
            )
        )
    '''
    
    # Fetch seasons    
    for item in element.xpath("//*[@id='tab-content-episodes']//*[@class='accordion']//label"):
        id = item.xpath("./@for")[0]
        
        if not id:
            continue
        
        try:
            season = id.split(" ")[1]
        except:
            season = None
        
        title = item.xpath(".//*[@class='title']/text()")[0]
        
        oc.add(
            DirectoryObject(
                key = Callback(
                    Items, 
                    title = title, 
                    url = url, 
                    thumb = thumb,
                    xpath_string = "//*[@id='tab-content-episodes']//*[@class='accordion']",
                    art = art,
                    id = id
                ), 
                title = title,
                thumb = thumb,
                art = art
            )
        )

    if len(oc) > 0:
        title = 'Episodes'
        oc.add(
            DirectoryObject(
                key = Callback(
                    Items, 
                    title = title,
                    url = url,
                    thumb = thumb,
                    xpath_string = "//*[@id='tab-content-episodes']",
                    art = art
                ), 
                title = title,
                thumb = thumb,
                art = art
            )
        )
    
        return oc
        
    else:
        return Items(
            title = title,
            url = url,
            thumb = thumb,
            xpath_string = "//*[@id='tab-content-episodes']",
            art = art
        )

##########################################################################################
@route("/video/roosterteeth/Items",  recent = bool)
def Items(title, url, thumb, xpath_string, art, id=None, recent=False):
    oc = ObjectContainer(title2=title)

    element = HTML.ElementFromURL(url)
    
    episodes = []
    for item in element.xpath(xpath_string):
        if id:
            season_id = item.xpath(".//@id")[0]
             
            if id != season_id:
                continue
                
            try:
                season = int(id.split(" ")[1])
            except:
                season = None
        else:
            season = None
        
        for episode in item.xpath(".//*[@class='grid-blocks']//li"):
            try:
                url = episode.xpath(".//@href")[0]
                
                if not '/episode/' in url:
                    continue
            except:
                continue
            
            try:
                title = episode.xpath(".//*[@class='name']/text()")[0]
            except:
                continue
            
            thumb = episode.xpath(".//img/@src")[0]
            
            if thumb.startswith("//"):
                thumb = 'http:' + thumb
            
            try:
                index = int(title.split(" ")[1])
            except:
                index = None
                
            try:
                duration_string = episode.xpath(".//*[@class='timestamp']/text()")[0].strip()
                duration = ((int(duration_string.split(":")[0])*60) + int(duration_string.split(":")[1])) * 1000
            except:
                duration = None
            
            episodes.append(
                EpisodeObject(
                    url = url,
                    title = title,
                    thumb = thumb,
                    season = season,
                    index = index,
                    duration = duration,
                    art = art
                )
            )

    if Prefs['sort'] == 'Latest First' or recent:
        for episode in episodes:
            oc.add(episode)   
    else:
        for episode in reversed(episodes):
            oc.add(episode)
    
    if len(oc) < 1:
        return ObjectContainer(
            header = "Sorry",
            message = "Couldn't find any videos for this show"
        )
        
    return oc

