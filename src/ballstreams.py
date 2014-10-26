import urllib, urllib2, datetime, json, os

# xbmc-ball-streams
# author: craig mcnicholas, andrew wise (since v2.8.2)
# contact: craig@designdotworks.co.uk, zergcollision@gmail.com

# Represents a session class which contains a users login
# session information from ballstreams
class Session():

    # Creates a new session instance
    # @param userId the users id
    # @param username the users supplied username
    # @param favteam the users favorite team as set on the website account settings
    # @param membership the users membership status, either REGULAR or PREMIUM
    # @param token the users session token
    def __init__(self, userId, username, favteam, membership, token):
        self.userId = userId
        self.username = username
        self.favteam = favteam
        self.membership = membership
        self.isPremium = membership.lower() == 'premium'
        self.token = token

    # Overrides this classes string value
    def __str__(self):
        return repr('Username: ' + self.username + ', Membership: ' + self.membership + ', Token: ' + self.token)

# Represents a live event between two teams
class LiveEvent():

    # Creates a new event instance
    def __init__(self, eventId, event, homeTeam, homeScore, awayTeam, awayScore, startTime, period, isPlaying, feedType):
        self.eventId = eventId
        self.event = event
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.startTime = startTime
        self.period = period if period != None else ''
        self.isPlaying = isPlaying
        self.feedType = feedType
        self.isFuture = self.period == '' and not self.isPlaying
        self.isFinal = len(self.period)>0 and not self.isPlaying

    # Overrides this classes string value
    def __str__(self):
        return repr('Live Event: ' + self.homeTeam + ' vs ' + self.awayTeam + ' id: ' + self.eventId + ' period: ' + self.period + ' isPlaying: ' + str(self.isPlaying))

# Represents an on-demand event between two teams
class OnDemandEvent():

    # Creates a new event instance
    def __init__(self, eventId, date, event, homeTeam, awayTeam, feedType = None):
        self.eventId = eventId
        self.date = date
        self.event = event
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.feedType = feedType

    # Overrides this classes string value
    def __str__(self):
        return repr('OnDemand Event: ' + self.homeTeam + ' vs ' + self.awayTeam + ' @ ' + self.date + ' @ ' + self.eventId)

# Represents an event stream between two teams
class LiveStream():

    # Creates a new streams instance
    def __init__(self, eventId, event, homeTeam, homeScore, awayTeam, awayScore, startTime, period, feedType, streamSet = None):
        self.eventId = eventId
        self.event = event
        self.homeTeam = homeTeam
        self.homeScore = homeScore
        self.awayTeam = awayTeam
        self.awayScore = awayScore
        self.startTime = startTime
        self.period = period
        self.feedType = feedType
        self.streamSet = streamSet

    # Overrides this classes string value
    def __str__(self):
        return repr('Live Event Stream: ' + self.homeTeam + ' vs ' + self.awayTeam + ' @ ' + self.eventId)

# Represents an event stream between two teams
class OnDemandStream():

    # Creates a new streams instance
    def __init__(self, eventId, event, homeTeam, awayTeam, streamSet = None):
        self.eventId = eventId
        self.event = event
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.streamSet = streamSet

    # Overrides this classes string value
    def __str__(self):
        return repr('On Demand Event Stream: ' + self.homeTeam + ' vs ' + self.awayTeam + ' @ ' + self.eventId)

# Represents a highlight
class Highlight():
    # Creates a new highlight instance
    def __init__(self, eventId, date, event, homeTeam, awayTeam, lowQualitySrc, medQualitySrc, highQualitySrc, homeSrc, awaySrc):
        self.eventId = eventId
        self.date = date
        self.event = event
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.lowQualitySrc = lowQualitySrc
        self.medQualitySrc = medQualitySrc
        self.highQualitySrc = highQualitySrc
        self.homeSrc = homeSrc
        self.awaySrc = awaySrc

    # Overrides this classes string value
    def __str__(self):
        return repr('Highlight: ' + self.homeTeam + ' vs ' + self.awayTeam + ' ID ' + self.eventId + ' on ' + self.date)

# Represents a condensed game
class CondensedGame():
    # Creates a new instance
    def __init__(self, eventId, date, event, homeTeam, awayTeam, lowQualitySrc, medQualitySrc, highQualitySrc, homeSrc, awaySrc):
        self.eventId = eventId
        self.date = date
        self.event = event
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.lowQualitySrc = lowQualitySrc
        self.medQualitySrc = medQualitySrc
        self.highQualitySrc = highQualitySrc
        self.homeSrc = homeSrc
        self.awaySrc = awaySrc

    # Overrides this classes string value
    def __str__(self):
        return repr('Condensed Game: ' + self.homeTeam + ' vs ' + self.awayTeam + ' ID ' + self.eventId + ' on ' + self.date)

# Represents a team
class Team():

    # Creates a new team instance
    # @param name the team name
    # @param league the teams league
    def __init__(self, name, league = ''):
        self.name = name
        self.league = league

    # Overrides this classes string value
    def __str__(self):
        return repr(self.name + ' @ ' + self.league)

# Represents a short team name
class ShortTeams():
    NAMES = None

# Represents an API exception
class ApiException(Exception):

    # Creates a new instance of the api exception
    # @param value a message
    def __init__(self, value):
        self.value = value

    # Overrides this classes string value
    def __str__(self):
        return repr(self.value)

# Method to attempt a login to a ballstreams account
# @param username the username to login with
# @param password the password to login with
# @throws ApiException when a login fails due to parsing or an incorrect account
# @return the session instance to use for subsequent requests
def login(username, password):
    # The applications api key, generated @ https://www4.ballstreams.com/api
    API_KEY = 'd4b03595a0691edbf89347a132fb5d28'

    # Setup login request data
    data = urllib.urlencode({
        'username': username,
        'password': password,
        'key': API_KEY
    })

    # Get login response
    request = __setupRequest('https://api.ballstreams.com/Login')
    response = None

    try:
        response = urllib2.urlopen(request, data)
    except urllib2.HTTPError as e:
        if e.code == 400:
            raise ApiException('API Error: Failed to login, CODE = 400');
        else:
            raise e

    page = response.read()
    response.close()

    # Parse the login response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the user session info
    userId = js['uid']
    username = js['username']
    favteam = js['favteam']
    membership = js['membership']
    token = js['token']

    # Check user id
    if userId == None or len(userId) < 1:
        raise ApiException('API Error: The user id was null or empty');

    # Check user name
    if username == None or len(username) < 1:
        raise ApiException('API Error: The username was null or empty');

    # Check membership
    if membership == None or len(membership) < 1:
        raise ApiException('API Error: The membership was null or empty');

    # Check token
    if token == None or len(token) < 1:
        raise ApiException('API Error: The token was null or empty');

    # Create and return session instance
    return Session(userId, username, favteam, membership, token)

# Method to check the ip of a username
# @param username the username to check the ip of
# @return a flag indicating if the ip check was successful
def checkIp(username):
    # Setup check ip data
    data = urllib.urlencode({
        'username': username
    })

    # Get response for ip check
    request = __setupRequest('https://www4.ballstreams.com/scripts/check_ip.php?' + data)
    response = urllib2.urlopen(request, data)
    page = response.read()
    response.close()

    # Check the response, a null or empty response is good to go
    if page == None or page == '':
        return True
    else:
        return False

# Method to generate an ip exception
# @param session the session details to login with
# @return a flag indicating success
def ipException(session):
    # Setup ip exception data
    data = urllib.urlencode({
        'token': session.token
    })

    # Get response for ip exception
    request = __setupRequest('https://api.ballstreams.com/IPException')
    response = urllib2.urlopen(request, data)
    page = response.read()
    response.close()

    # Parse the ip exception response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    return True

# Method to retrieve available archived dates for ball streams
# @param session the session details to login with
# @return a list of available dates
def onDemandDates(session):
    # Setup available dates data
    data = urllib.urlencode({
        'token': session.token
    })

    # Get response for available dates
    request = __setupRequest('https://api.ballstreams.com/GetOnDemandDates?' + data)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the on demand dates response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the dates array
    dates = js['dates']

    # Check dates
    if dates == None:
        raise ApiException('API Error: The dates were null');

    # Parse the available dates from json response,
    # dates in format'mm/dd/yyyy'
    results = []
    for date in dates:
        if date is not None and len(date) > 0:
            parts = date.split('/')
            day = int(parts[1])
            month = int(parts[0])
            year = int(parts[2])
            results.append(datetime.date(year, month, day))

    return results

# Method to retrieve available teams for ball streams
# @param session the session details to login with
# @return a list of teams
def teams(session, league = None):
    # Setup teams data
    data = urllib.urlencode({
        'token': session.token
    })

    # Get response for teams
    request = __setupRequest('https://api.ballstreams.com/ListTeams?' + data)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the teams response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the teams array
    teams = js['teams']

    # Check teams
    if teams == None:
        raise ApiException('API Error: The teams were null');

    # Parse the teams from json response
    results = []
    for team in teams:
        # Get the team variables
        teamName = team['name']
        leagueName = team['league']
        
        # Check team name
        if teamName == None:
            raise ApiException('API Error: The team name was null');

        # Check team leagueName
        if leagueName == None:
            raise ApiException('API Error: The leagueName was null');

        if league == None or league == leagueName:
            results.append(Team(teamName, leagueName))

    return results

# Method to get the events for a given date
# @param session the session details to login with
# @param date a date instance to return the events for
# @return a list of events
def dateOnDemandEvents(session, date):
    # Strip the date into usable strings for formatting
    year = str(date.year)
    month = '%02d' % (date.month,)
    day = '%02d' % (date.day,)

    # Setup events for date data
    data = urllib.urlencode({
        'token': session.token,
        'date': month + '/' + day + '/' + year
    })
    
    url = 'https://api.ballstreams.com/GetOnDemand?' + data

    events = parseOnDemandEvents(url)
    
    return events

# Method to get on-demand highlights for a given date
# @param session the session details to login with
# @param date a date instance to return the highlights for
# @return a list of highlights
def dateOnDemandHighlights(session, date = None, team = None):
    data = ''
    # Strip the date into usable strings for formatting
    if date != None and team != None and len(team) > 0:
        year = str(date.year)
        month = '%02d' % (date.month,)
        day = '%02d' % (date.day,)
        data = urllib.urlencode({
                'token': session.token,
                'team': team,
                'date': month + '/' + day + '/' + year
            })
    elif date != None:
        year = str(date.year)
        month = '%02d' % (date.month,)
        day = '%02d' % (date.day,)
        data = urllib.urlencode({
                'token': session.token,
                'date': month + '/' + day + '/' + year
            })
    elif team != None and len(team) > 0:
        data = urllib.urlencode({
                'token': session.token,
                'team': team
            })
    else:
        data = urllib.urlencode({
                'token': session.token
            })

    url = 'https://api.ballstreams.com/GetHighlights?' + data

    # Get response for events
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    highlights = []
    
    # Parse the events response
    try:
        js = json.loads(page)
    except Exception as e:
        print 'Warning: Unable to retrieve highlights for date: ' + str(date) + ' team: ' + str(team)
        return highlights

    __checkStatus(js)

    # Get the schedule array
    highlightArray = js['highlights']

    # Check schedule
    if highlightArray == None:
        return None;

    highlights = []
    for highlight in highlightArray:
        # Get the schedule variables
        eventId = highlight['id']
        hDate = highlight['date']
        event = highlight['event']
        homeTeam = highlight['homeTeam']
        awayTeam = highlight['awayTeam']
        lowQualitySrc = highlight['lowQualitySrc']
        medQualitySrc = highlight['medQualitySrc']
        highQualitySrc = highlight['highQualitySrc']
        homeSrc = highlight['homeSrc']
        awaySrc = highlight['awaySrc']
        
        highlights.append(Highlight(eventId, hDate, event, homeTeam, awayTeam, lowQualitySrc, medQualitySrc, highQualitySrc, homeSrc, awaySrc))

    return highlights

# Method to get on-demand condensed games for a given date
# @param session the session details to login with
# @param date a date instance to return the condensed games for
# @return a list of condensed games
def dateOnDemandCondensed(session, date = None, team = None):
    data = ''
    # Strip the date into usable strings for formatting
    if date != None and team != None and len(team) > 0:
        year = str(date.year)
        month = '%02d' % (date.month,)
        day = '%02d' % (date.day,)
        data = urllib.urlencode({
                'token': session.token,
                'team': team,
                'date': month + '/' + day + '/' + year
            })
    elif date != None:
        year = str(date.year)
        month = '%02d' % (date.month,)
        day = '%02d' % (date.day,)
        data = urllib.urlencode({
                'token': session.token,
                'date': month + '/' + day + '/' + year
            })
    elif team != None and len(team) > 0:
        data = urllib.urlencode({
                'token': session.token,
                'team': team
            })
    else:
        data = urllib.urlencode({
                'token': session.token
            })

    url = 'https://api.ballstreams.com/GetCondensedGames?' + data

    # Get response for events
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    condenseds = []
    
    # Parse the events response
    try:
        js = json.loads(page)
    except Exception as e:
        print 'Warning: Unable to retrieve condensed games for date: ' + str(date) + ' team: ' + str(team)
        return condenseds

    __checkStatus(js)

    # Get the schedule array
    condensedGames = js['condensed']

    # Check schedule
    if condensedGames == None:
        return None;

    condenseds = []
    for condensed in condensedGames:
        # Get the schedule variables
        eventId = condensed['id']
        hDate = condensed['date']
        event = condensed['event']
        homeTeam = condensed['homeTeam']
        awayTeam = condensed['awayTeam']
        lowQualitySrc = condensed['lowQualitySrc']
        medQualitySrc = condensed['medQualitySrc']
        highQualitySrc = condensed['highQualitySrc']
        homeSrc = condensed['homeSrc']
        awaySrc = condensed['awaySrc']
        
        condenseds.append(CondensedGame(eventId, hDate, event, homeTeam, awayTeam, lowQualitySrc, medQualitySrc, highQualitySrc, homeSrc, awaySrc))

    return condenseds

# Method to get the events for a given team
# @param session the session details to login with
# @param team a team instance to return the events for
# @return a list of events
def teamOnDemandEvents(session, team):
    # Setup events for team data
    data = urllib.urlencode({
        'token': session.token,
        'team': team.name
    })

    url = 'https://api.ballstreams.com/GetOnDemand?' + data

    return parseOnDemandEvents(url)

# Method to parse an on demand events request
# @param url the url to get the json response from and parse
# @return a list of ondemand events for the given api url
def parseOnDemandEvents(url):
    # Get response for events
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the events response
    js = json.loads(page)

    __checkStatus(js)

    # Get the ondemand array
    onDemand = js['ondemand']

    # Check on demand
    if onDemand == None:
        raise ApiException('API Error: The ondemand was null');

    events = []
    for item in onDemand:
        # Get the on demand variables
        eventId = item['id']
        date = item['date']
        event = item['event']
        homeTeam = item['homeTeam']
        awayTeam = item['awayTeam']
        feedType = item['feedType']

        # Check on demand item id
        if eventId == None:
            raise ApiException('API Error: The id was null');

        # Check on demand item event
        if event == None:
            raise ApiException('API Error: The event was null');

        # Check on demand item home team
        if homeTeam == None:
            raise ApiException('API Error: The home team was null');

        # Check on demand item away team
        if awayTeam == None:
            raise ApiException('API Error: The away team was null');

        events.append(OnDemandEvent(eventId, date, event, homeTeam, awayTeam, feedType))

    return events

# Method to get on-demand streams for a given event id
# @param session the session details to login with
# @param eventId unique id of an event
# @param location the optional location to return the stream from
# @return a list of on-demand event streams
def onDemandEventStreams(session, eventId, location=None):
    # Setup stream data
    data = {
        'token': session.token,
        'id': eventId
    }
    # Only add location if necessary
    if location != None:
        data['location'] = location
    data = urllib.urlencode(data)

    # Create url
    url = 'https://api.ballstreams.com/GetOnDemandStream?' + data

    # Get response for events for date
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the live stream response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the on-demand stream variables
    eventId = js['id']
    event = js['event']
    homeTeam = js['homeTeam']
    awayTeam = js['awayTeam']

    # Get the streams
    streams = js['streams'] if 'streams' in js else []
    hdStreams = js['HDstreams'] if 'HDstreams' in js else []
    sdStreams = js['SDstreams'] if 'SDstreams' in js else []

    # Create map of streams
    result = {
        'wmv': None,
        'flash': None,
        'istream': None,
        'istream.hd': None,
        'istream.sd': None
    }

    # Find the streams
    for stream in streams:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is wmv, flash or istream
        if streamType.lower() == 'windows media':
            wmvSource = stream['src']

            # Only set it if the source url is valid
            if wmvSource is not None and len(wmvSource) > 0 and wmvSource.lower().startswith('http'):
                result['wmv'] = wmvSource
        elif streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream'] = iStreamSource
        elif streamType.lower() == 'flash':
            flashSource = stream['src']

            # Only set it if the source url is valid
            if flashSource is not None and len(flashSource) > 0 and flashSource.lower().startswith('http'):
                result['flash'] = flashSource

    # Find the HD streams
    for stream in hdStreams:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is istream
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream.hd'] = iStreamSource

    # Find the SD streams
    for stream in sdStreams:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is istream
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream.sd'] = iStreamSource

    return OnDemandStream(eventId, event, homeTeam, awayTeam, result)

# Method to get a list of events that are live or in the future
# @param session the session details to login with
# @return a list of live events for current day
def liveEvents(session):
    # Setup live events data
    data = urllib.urlencode({
        'token': session.token
    })

    # Get response for events
    request = __setupRequest('https://api.ballstreams.com/GetLive?' + data)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # If the page response isn't available return no events
    if page == None or page == '':
        return []

    # Parse the events response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the schedule array
    schedule = js['schedule']

    # Check schedule
    if schedule == None:
        raise ApiException('API Error: The schedule was null');

    events = []
    for item in schedule:
        # Get the schedule variables
        eventId = item['id']
        event = item['event']
        homeTeam = item['homeTeam']
        homeScore = item['homeScore']
        awayTeam = item['awayTeam']
        awayScore = item['awayScore']
        startTime = item['startTime']
        period = item['period']
        isPlaying = item['isPlaying']
        feedType = item['feedType']

        # Check schedule item id
        if eventId == None:
            raise ApiException('API Error: The id was null');

        # Check schedule item event
        if event == None:
            raise ApiException('API Error: The event was null');

        # Check schedule item home team
        if homeTeam == None:
            raise ApiException('API Error: The home team was null');

        # Check schedule item away team
        if awayTeam == None:
            raise ApiException('API Error: The away team was null');

        # Check schedule item start time
        if startTime == None:
            raise ApiException('API Error: The start time was null');

        # Check schedule item is playing
        if isPlaying == None:
            raise ApiException('API Error: The is playing was null');
        if str(isPlaying) != '0' and str(isPlaying) != '1':
            raise ApiException('API Error: The is playing value was in an incorrect format');
        # Convert the value to a boolean
        isPlaying = str(isPlaying) == '1'

        events.append(LiveEvent(eventId, event, homeTeam, homeScore, awayTeam, awayScore, startTime, period, isPlaying, feedType))

    return events

# Method to get the streams for an event id
# @param session the session details to login with
# @param eventId the event instance to find the direct stream url for
# @param location the optional location to return the stream from
# @return a live event stream for given event id
# istream.sd, truelive.sd, truelive.hd or None if not found
def liveEventStreams(session, eventId, location=None):
    # Setup stream data
    data = {
        'token': session.token,
        'id': eventId
    }
    # Only add location if necessary
    if location != None:
        data['location'] = location
    data = urllib.urlencode(data)

    # Create url
    url = 'https://api.ballstreams.com/GetLiveStream?' + data

    # Get response for events for date
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the live stream response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the live stream variables
    eventId = js['id']
    event = js['event']
    homeTeam = js['homeTeam']
    homeScore = js['homeScore']
    awayTeam = js['awayTeam']
    awayScore = js['awayScore']
    startTime = js['startTime']
    period = js['period']
    feedType = js['feedType']

    # Get the streams
    streams = js['streams'] if 'streams' in js else []
    hdStreams = js['HDstreams'] if 'HDstreams' in js else []
    sdStreams = js['SDstreams'] if 'SDstreams' in js else []
    nondvr = js['nonDVR'] if 'nonDVR' in js else []
    nondvrsd = js['nonDVRSD'] if 'nonDVRSD' in js else []
    nondvrhd = js['nonDVRHD'] if 'nonDVRHD' in js else []
    sdTrueLive = js['TrueLiveSD'] if 'TrueLiveSD' in js else []
    hdTrueLive = js['TrueLiveHD'] if 'TrueLiveHD' in js else []

    # Create map of streams
    result = {
        'wmv': None,
        'istream': None,
        'istream.hd': None,
        'istream.sd': None,
        'nondvr': None,
        'nondvrsd': None,
        'nondvrhd': None,
        'flash': None,
        'truelive.hd': None,
        'truelive.sd': None
    }

    # Find the streams
    for stream in streams:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is wmv, flash or istream
        if streamType.lower() == 'windows media':
            wmvSource = stream['src']

            # Only set it if the source url is valid
            if wmvSource is not None and len(wmvSource) > 0 and wmvSource.lower().startswith('http'):
                result['wmv'] = wmvSource
        elif streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream'] = iStreamSource
        elif streamType.lower() == 'flash':
            flashSource = stream['src']

            # Only set it if the source url is valid
            if flashSource is not None and len(flashSource) > 0 and flashSource.lower().startswith('http'):
                result['flash'] = flashSource

    # Find the HD streams
    for stream in hdStreams:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is istream
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream.hd'] = iStreamSource

    # Find the SD streams
    for stream in sdStreams:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is istream
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream.sd'] = iStreamSource

    # Find the nondvr streams
    for stream in nondvr:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is nondvr
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['nondvr'] = iStreamSource

    # Find the nondvrsd streams
    for stream in nondvrsd:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is nondvrsd
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['nondvrsd'] = iStreamSource

    # Find the nondvrhd streams
    for stream in nondvrhd:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is nondvrhd
        if streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['nondvrhd'] = iStreamSource

    # Find the SD true live streams
    for stream in sdTrueLive:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is flash (usable by rtmp)
        if streamType.lower() == 'flash live':
            flashStreamSource = stream['src']

            # Only set it if the source url is valid
            if flashStreamSource is not None and len(flashStreamSource) > 0 and flashStreamSource.lower().startswith('rtmp'):
                result['truelive.sd'] = flashStreamSource

    # Find the HD true live streams
    for stream in hdTrueLive:
        # Get the type
        streamType = stream['type']

        # Check type
        if streamType == None:
            raise ApiException('API Error: The type was null');

        # Check if the type is flash (usable by rtmp)
        if streamType.lower() == 'flash live':
            flashStreamSource = stream['src']

            # Only set it if the source url is valid
            if flashStreamSource is not None and len(flashStreamSource) > 0 and flashStreamSource.lower().startswith('rtmp'):
                result['truelive.hd'] = flashStreamSource

    return LiveStream(eventId, event, homeTeam, homeScore, awayTeam, awayScore, startTime, period, feedType, result)

# Method to get the short team name of a team
# @param teamName the team name to get the shortened version for
# @param root the root file path to append the resource file path to
# @return a short team name or the original team name if not found
def shortTeamName(teamName, root):
    # Load dictionary of team names on first call
    if ShortTeams.NAMES == None:
        path = os.path.join(root, 'resources', 'data', 'teams.json')
        f = open(path, 'rb')
        content = f.read()
        f.close()
        ShortTeams.NAMES = json.loads(content)

    # Get lower case key name and check it exists
    teamNameLower = teamName.lower()
    if teamNameLower in ShortTeams.NAMES:
        return ShortTeams.NAMES[teamNameLower] # It does so get name
    else:
        return teamName # It doesn't return original

# Compute the date utilized to determine current day live 
# once a game is final.  Used to provide on-demand events
# for the current day.
# @return datetime for any on-demand current day events
def adjustedDateTime():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=-8)

# Compute the current date with number of days back.
# @return datetime today minus number of days back
def getRecentDateTime(daysBack = 0):
    now = datetime.datetime.now()
    return now - datetime.timedelta(daysBack)

# Method to setup a request object to ballstreams
# @param url the url to setup the request to
# @return an urllib2.Request object
def __setupRequest(url):
    request = urllib2.Request(url)
    request.add_header('From', 'xbmc-ball-streams')

    return request

# Method to check an api response and make sure its valid
# @param js the json object to check
# @throws ApiException if there is a problem with the api status
def __checkStatus(js):
    status = js['status']

    # Check the status value exists
    if status == None:
        raise ApiException('API Error: Status not found!')

    # Check the status value is valid
    if status.lower() != 'success':
        message = js['msg']
        if message != None and len(message) > 0:
            raise ApiException('API Error: Status=' + status + ', ' + message)
        else:
            raise ApiException('API Error: Status=' + status + ', Unknown')
