import urllib, urllib2, datetime, json, os

# xbmc-ball-streams
# author: craig mcnicholas
# contact: craig@designdotworks.co.uk

# Represents a session class which contains a users login
# session information from ballstreams
class Session():

    # Creates a new session instance
    # @param userId the users id
    # @param username the users supplied username
    # @param membership the users membership status, either REGULAR or PREMIUM
    # @param token the users session token
    def __init__(self, userId, username, membership, token):
        self.userId = userId
        self.username = username
        self.membership = membership
        self.isPremium = membership.lower() == 'premium'
        self.token = token

    # Overrides this classes string value
    def __str__(self):
        return repr('Username: ' + self.username + ', Membership: ' + self.membership + ', Token: ' + self.token)

# Represents an api exception class which is thrown if there
# is an issue parsing an api response
class ApiException(Exception):

    # Creates a new instance of the api exception
    # @param value a message
    def __init__(self, value):
        self.value = value

    # Overrides this classes string value
    def __str__(self):
        return repr(self.value)

# Represents an event between two teams
class Event():

    # Creates a new event instance
    # @param streamId the stream id
    # @param event the event name (usually a league)
    # @param homeTeam the home team name
    # @param awayTeam the away team name
    # @param isLive [optional] a flag indicating if the stream is live, defaults to false
    # @param isFuture [optional] a flag indicating if the stream is in the future, defaults to false
    # @param isOnDemand [optional] a flag indicating if the stream is on demand, defaults to false
    # @param time [optional] the time of the event, defaults to None
    def __init__(self, streamId, event, homeTeam, awayTeam, feedType = None, homeScore = None, awayScore = None, period = None, isLive = False, isFuture = False, isOnDemand = False, time = None):
        self.streamId = streamId
        self.event = event
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.feedType = feedType
        self.homeScore = homeScore
        self.awayScore = awayScore
        self.period = period
        self.isLive = isLive
        self.isFuture = isFuture
        self.isOnDemand = isOnDemand
        self.time = time

    # Overrides this classes string value
    def __str__(self):
        if self.isOnDemand:
            return repr('On Demand Event: ' + self.homeTeam + ' vs ' + self.awayTeam + ' @ ' + self.streamId)
        elif self.isLive:
            return repr('Live Event: ' + self.homeTeam + ' vs ' + self.awayTeam + ' @ ' + self.time + ' @ ' + self.streamId)
        else:
            return repr('Future Event: ' + self.homeTeam + ' vs ' + self.awayTeam + ' @ ' + self.time)

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
    return Session(userId, username, membership, token)

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
def availableDates(session):
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
def teams(session):
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
        league = team['league']

        # Check team name
        if teamName == None:
            raise ApiException('API Error: The team name was null');

        # Check team league
        if league == None:
            raise ApiException('API Error: The league was null');
        
        results.append(Team(teamName, league))

    return results

# Method to get the events for a given date
# @param session the session details to login with
# @param date a date instance to return the events for
# @return a list of events
def eventsForDate(session, date):
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
    return __parseEvents(url)

# Method to get the events for a given team
# @param session the session details to login with
# @param team a team instance to return the events for
# @return a list of events
def eventsForTeam(session, team):
    # Setup events for team data
    data = urllib.urlencode({
        'token': session.token,
        'team': team.name
    })

    url = 'https://api.ballstreams.com/GetOnDemand?' + data
    return __parseEvents(url)

# Method to parse an on demand events request
# @param url the url to get the json response from and parse
# @return a list of events
def __parseEvents(url):
    # Get response for events
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the events response
    js = json.loads(page)
    
    # Check the api request was successful
    # TODO Change this once Billy has fixed the response,
    # it currently does not set the status flag properly
    # __checkStatus(js)

    # Get the ondemand array
    onDemand = js['ondemand']

    # Check on demand
    if onDemand == None:
        raise ApiException('API Error: The ondemand was null');

    events = []
    for item in onDemand:
        # Get the on demand variables
        streamId = item['id']
        event = item['event']
        homeTeam = item['homeTeam']
        awayTeam = item['awayTeam']
        feedType = item['feedType']

        # Check on demand item id
        if streamId == None:
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
        
        events.append(Event(streamId, event, homeTeam, awayTeam, feedType, homeScore = None, awayScore = None, period = None, isOnDemand = True))

    return events

# Method to get the direct stream url for an event
# @param session the session details to login with
# @param event the event instance to find the direct stream url for
# @param location the optional location to return the stream from
# @return a map of urls with keys wmv, istream, flash, istream.hd,
# istream.sd, truelive.sd, truelive.hd or None if not found
def eventStream(session, event, location=None):
    # Check event is live or archived
    if event.isFuture:
        return None

    # Setup a url source
    url = None

    # Setup stream data
    data = {
        'token': session.token,
        'id': event.streamId
    }
    # Only add location if necessary
    if location != None:
        data['location'] = location
    data = urllib.urlencode(data)

    # Create url based on event type
    if event.isOnDemand:
        url = 'https://api.ballstreams.com/GetOnDemandStream?' + data
    elif event.isLive:
        url = 'https://api.ballstreams.com/GetLiveStream?' + data
    else:
        raise ApiException('API Error: Event was in an invalid state, cannot find stream url');

    # Get response for events for date
    request = __setupRequest(url)
    response = urllib2.urlopen(request)
    page = response.read()
    response.close()

    # Parse the live stream response
    js = json.loads(page)

    # Check the api request was successful
    __checkStatus(js)

    # Get the streams
    streams = None
    hdStreams = None
    sdStreams = None
    # nondvr = None
    # nondvrsd = None
    # nondvrhd = None
    sdTrueLive = None
    hdTrueLive = None
    if 'streams' in js:
        streams = js['streams']
    else:
        streams = []
    if 'HDstreams' in js:
        hdStreams = js['HDstreams']
    else:
        hdStreams = []
    if 'SDstreams' in js:
        sdStreams = js['SDstreams']
    else:
        sdStreams = []
    # if 'nonDVR' in js:
        # nondvr = js['nonDVR']
    # else:
        # nondvr = []
    # if 'nonDVRSD' in js:
        # nondvrsd = js['nonDVRSD']
    # else:
        # nondvrsd = []
    # if 'nonDVRHD' in js:
        # nondvrhd = js['nonDVRHD']
    # else:
        # nondvrhd = []
    if 'TrueLiveSD' in js:
        sdTrueLive = js['TrueLiveSD']
    else:
        sdTrueLive = []
    if 'TrueLiveHD' in js:
        hdTrueLive = js['TrueLiveHD']
    else:
        hdTrueLive = []

    # Check streams
    if streams == None:
        raise ApiException('API Error: The streams was null');
    if hdStreams == None:
        raise ApiException('API Error: The HDstreams was null');
    if sdStreams == None:
        raise ApiException('API Error: The SDstreams was null');
    # if nondvr == None:
        # raise ApiException('API Error: The nonDVR was null');
    # if nondvrsd == None:
        # raise ApiException('API Error: The nonDVRSD was null');
    # if nondvrhd == None:
        # raise ApiException('API Error: The nonDVRHD was null');
    if sdTrueLive == None:
        raise ApiException('API Error: The TrueLiveSD was null');
    if hdTrueLive == None:
        raise ApiException('API Error: The TrueLiveHD was null');

    # Create map of streams
    found = False
    result = {
        'wmv': None,
        'istream': None,
        'istream.hd': None,
        'istream.sd': None,
        # 'nondvr': None,
        # 'nondvrsd': None,
        # 'nondvrhd': None,
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
                found = True
        elif streamType.lower() == 'istream':
            iStreamSource = stream['src']

            # Only set it if the source url is valid
            if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                result['istream'] = iStreamSource
                found = True
        elif streamType.lower() == 'flash':
            flashSource = stream['src']

            # Only set it if the source url is valid
            if flashSource is not None and len(flashSource) > 0 and flashSource.lower().startswith('http'):
                result['flash'] = flashSource
                found = True

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
                found = True

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
                found = True

    # Find the nondvr streams
    # for stream in nondvr:
        # Get the type
        # streamType = stream['type']
        
        # Check type
        # if streamType == None:
            # raise ApiException('API Error: The type was null');

        # Check if the type is nondvr
        # if streamType.lower() == 'istream':
            # iStreamSource = stream['src']

            # Only set it if the source url is valid
            # if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                # result['nondvr'] = iStreamSource
                # found = True

    # Find the nondvrsd streams
    # for stream in nondvrsd:
        # Get the type
        # streamType = stream['type']
        
        # Check type
        # if streamType == None:
            # raise ApiException('API Error: The type was null');

        # Check if the type is nondvrsd
        # if streamType.lower() == 'istream':
            # iStreamSource = stream['src']

            # Only set it if the source url is valid
            # if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                # result['nondvrsd'] = iStreamSource
                # found = True

    # Find the nondvrhd streams
    # for stream in nondvrhd:
        # Get the type
        # streamType = stream['type']

        # Check type
        # if streamType == None:
            # raise ApiException('API Error: The type was null');

        # Check if the type is nondvrhd
        # if streamType.lower() == 'istream':
            # iStreamSource = stream['src']

            # Only set it if the source url is valid
            # if iStreamSource is not None and len(iStreamSource) > 0 and iStreamSource.lower().startswith('http'):
                # result['nondvrhd'] = iStreamSource
                # found = True

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
                found = True

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
                found = True

    # If nothing found then return None
    if found == False:
        return None
    else:
        return result

# Method to get a list of events that are live or in the future
# @param session the session details to login with
# @return a list of events that are live or in the future
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
        streamId = item['id']
        event = item['event']
        homeTeam = item['homeTeam']
        awayTeam = item['awayTeam']
        homeScore = item['homeScore']
        awayScore = item['awayScore']
        feedType = item['feedType']
        period = item['period']
        startTime = item['startTime']
        isPlaying = item['isPlaying']

        # Check schedule item id
        if streamId == None:
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
        
        events.append(Event(streamId, event, homeTeam, awayTeam, feedType, homeScore, awayScore, period, isFuture = isPlaying == False, isLive = isPlaying, time = startTime))

    return events

# Declare class to hold static reference to team names that we load
# in from an external resource
class ShortTeams():
    NAMES = None

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
