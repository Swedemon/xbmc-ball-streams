import xbmc, xbmcplugin, xbmcaddon, xbmcgui
import ballstreams, utils
import os, datetime, threading, random, time

# xbmc-ball-streams2
# author: craig mcnicholas
# contact: craig@designdotworks.co.uk

# deals with a bug where errors are thrown 
# if data directory does not exist.
addonId = 'plugin.video.xbmc-ball-streams2'
dataPath = 'special://profile/addon_data/' + addonId
if not os.path.exists: os.makedirs(dataPath)
addon = xbmcaddon.Addon(id = addonId)
addonPath = addon.getAddonInfo('path')
now = datetime.datetime.utcnow()

# Method to draw the home screen
def HOME():
    print 'HOME()'
    utils.addDir(addon.getLocalizedString(100005), utils.Mode.ONDEMAND, '', None, showfanart)
    utils.addDir(addon.getLocalizedString(100006), utils.Mode.LIVE, '', None, showfanart)

# Method to draw the archives screen
def ONDEMAND():
    print 'ONDEMAND()'
    utils.addDir(addon.getLocalizedString(100007), utils.Mode.ONDEMAND_BYDATE, '', None, showfanart)
    utils.addDir(addon.getLocalizedString(100008), utils.Mode.ONDEMAND_BYTEAM, '', None, showfanart)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of months/years for archives
def ONDEMAND_BYDATE(session):
    print 'ONDEMAND_BYDATE(session)'

    # Retrieve the available dates
    dates = ballstreams.availableDates(session)

    # Find unique months/years
    monthsYears = []
    for date in dates:
        current = str(date.month) + '/' + str(date.year)
        if monthsYears.count(current) < 1:
            monthsYears.append(current)

    # Count total number of items for ui
    totalItems = len(monthsYears)

    # Add directories for months
    for monthYear in monthsYears:
        # Create datetime for string formatting
        index = monthYear.index("/")
        year = monthYear[index+1:]
        month = monthYear[:index]
        date = datetime.date(int(year), int(month), 1)
        params = {
            'year': str(year),
            'month': str(month)
        }
        utils.addDir(date.strftime('%B %Y'), utils.Mode.ONDEMAND_BYDATE_YEARMONTH, '', params, totalItems, showfanart)

# Method to draw the on-demand by date screen
# which scrapes the external source and presents
# a list of days for a given year and month of archives
def ONDEMAND_BYDATE_YEARMONTH(session, year, month):
    print 'ONDEMAND_BYDATE_YEARMONTH(session, year, month)'
    print 'Year: ' + str(year)
    print 'Month: ' + str(month)

    # Retrieve the available dates
    dates = ballstreams.availableDates(session)

    # Find unique days
    days = []
    for date in dates:
        if year == date.year and month == date.month and days.count(date.day) < 1:
            days.append(date.day)

    # Count total number of items for ui
    totalItems = len(days)

    # Add directories for days
    for day in days:
        # Create datetime for string formatting
        date = datetime.date(year, month, day)
        params = {
            'year': str(year),
            'month': str(month),
            'day': str(day)
        }
        utils.addDir(date.strftime('%A %d %B %Y'), utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY, '', params, totalItems, showfanart)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of on-demand events for a given day
def ONDEMAND_BYDATE_YEARMONTH_DAY(session, year, month, day):
    print 'ONDEMAND_BYDATE_YEARMONTH_DAY(session, year, month, day)'
    print 'Year: ' + str(year)
    print 'Month: ' + str(month)
    print 'Day: ' + str(day)

    # Retrieve the events
    date = datetime.date(year, month, day)
    try:
        events = ballstreams.eventsForDate(session, date)
    except:
        return
        
    totalItems = len(events)

    for event in events:
        # Create datetime for string formatting
        parts = event.date.split('/')
        day = int(parts[1])
        month = int(parts[0])
        year = int(parts[2])
        datestr = ' - ' + datetime.date(year, month, day).strftime('%b %d')
        homeTeam = event.homeTeam if not shortNames else ballstreams.shortTeamName(event.homeTeam, addonPath)
        awayTeam = event.awayTeam if not shortNames else ballstreams.shortTeamName(event.awayTeam, addonPath)
        title = ''
        if event.feedType == 'Home Feed':
            title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + '*' + datestr
        elif event.feedType == 'Away Feed':
            title = event.event + ': ' + awayTeam + '* @ ' + homeTeam + datestr
        else:
            title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + datestr
        params = {
            'streamId': event.streamId
        }
        utils.addDir(title, utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT, '', params, totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of on-demand streams for a given event
def ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, streamId):
    print 'ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, streamId)'
    print 'StreamId: ' + streamId
    # TODO.
    pass

# Method to draw the archives by team screen
# which scrapes the external source and presents
# a list of team names (or potentially events)
def ONDEMAND_BYTEAM(session):
    print 'ONDEMAND_BYTEAM(session)'

    # Retrieve the teams
    teams = ballstreams.teams(session)

    # Count total number of items for ui
    totalItems = len(teams)

    # Add directories for teams
    for team in teams:
        params = {
            'team': team.name
        }
        title = team.league + ': ' + team.name if team.league != '' else team.name
        utils.addDir(title, utils.Mode.ONDEMAND_BYTEAM_TEAM, '', params, totalItems, showfanart)

# Method to draw the archives by team screen
# which scrapes the external source and presents
# a list of events for a given team
def ONDEMAND_BYTEAM_TEAM(session, team):
    print 'ONDEMAND_BYTEAM_TEAM(session, team)'
    print 'Team: ' + team

    # Retrieve the team events
    events = ballstreams.eventsForTeam(session, ballstreams.Team(team))

    totalItems = len(events)

    for event in events:
        # Create datetime for string formatting
        parts = event.date.split('/')
        day = int(parts[1])
        month = int(parts[0])
        year = int(parts[2])
        datestr = ' - ' + datetime.date(year, month, day).strftime('%b %d')
        homeTeam = event.homeTeam if not shortNames else ballstreams.shortTeamName(event.homeTeam, addonPath)
        awayTeam = event.awayTeam if not shortNames else ballstreams.shortTeamName(event.awayTeam, addonPath)
        title = ''
        if event.feedType == 'Home Feed':
            title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + '*' + datestr
        elif event.feedType == 'Away Feed':
            title = event.event + ': ' + awayTeam + '* @ ' + homeTeam + datestr
        else:
            title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + datestr
        params = {
            'streamId': event.streamId
        }
        utils.addDir(title, utils.Mode.ONDEMAND_BYTEAM_TEAM_EVENT, '', params, totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

# Method to draw the archive streams by event screen
# which scrapes the external source and presents
# a list of streams for a given stream id
def ONDEMAND_BYTEAM_TEAM_EVENT(session, streamId):
    print 'ONDEMAND_BYTEAM_TEAM_EVENT(session, streamId)'
    print 'StreamId: ' + streamId

# Method to draw the live screen
# which scrapes the external source and presents
# a list of current day events
def LIVE(session):
    print 'LIVE(session)'

    # Find live events
    events = ballstreams.liveEvents(session)

    totalItems = len(events) + 1

    for event in events:
        # Build prefix
        prefix = '[LIVE] '
        if event.isFuture:
            prefix = '[Coming Soon] '
        elif event.isFinal:
            prefix = '[Final] '
        # Build matchup
        homeTeam = event.homeTeam if not shortNames else ballstreams.shortTeamName(event.homeTeam, addonPath)
        awayTeam = event.awayTeam if not shortNames else ballstreams.shortTeamName(event.awayTeam, addonPath)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if event.feedType == 'Home Feed':
            matchupStr = matchupStr + '*'
        elif event.feedType == 'Away Feed':
            matchupStr = awayTeam + '* @ ' + homeTeam
        # Build period
        periodStr = ''
        if event.period == 'HALF - ':
            periodStr = ' - HALF'
        else:
            periodStr = ' - ' + event.period if event.period != None else ''
        # Build score
        homeScore = event.homeScore if event.homeScore != None and len(event.homeScore)>0 else '0'
        awayScore = event.awayScore if event.awayScore != None and len(event.awayScore)>0 else '0'
        scoreStr = ' - ' + awayScore + '-' + homeScore if showscores and not event.isFuture else ''
        # Build title
        title = prefix + event.event + ': ' + matchupStr + scoreStr + periodStr
        if event.isFinal:
            now = getAdjustedDateTime()
            params = {
                'year': str(now.year),
                'month': str(now.month),
                'day': str(now.day)
            }
            utils.addDir(title, utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY, '', params, totalItems, showfanart)
        elif event.isFuture:
            utils.addDir(title, mode, '', refreshParams, totalItems, showfanart)
        else:
            params = {
                'streamId': event.streamId
            }
            utils.addDir(title, utils.Mode.LIVE_EVENT, '', params, totalItems, showfanart)

    # Add refresh button
    refreshParams = {
        'refresh': 'True'
    }
    utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

# Method to draw the live streams screen
# which scrapes the external source and presents
# a list of current day event streams for a stream id
def LIVE_EVENT(session, streamId):
    print 'LIVE_EVENT(session, streamId)'
    print 'StreamId: ' + streamId

    # Build streams
    liveStream = ballstreams.eventLiveStream(session, streamId, location)
    
    totalItems = 11 # max possible

    if liveStream == None or liveStream.streamSet == None:
        return None

    # Build prefix
    prefix = '[LIVE] '
    # Build matchup
    homeTeam = liveStream.homeTeam if not shortNames else ballstreams.shortTeamName(liveStream.homeTeam, addonPath)
    awayTeam = liveStream.awayTeam if not shortNames else ballstreams.shortTeamName(liveStream.awayTeam, addonPath)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if liveStream.feedType == 'Home Feed':
        matchupStr = matchupStr + '*'
    elif liveStream.feedType == 'Away Feed':
        matchupStr = awayTeam + '* @ ' + homeTeam
    # Build period
    periodStr = ''
    if liveStream.period == 'HALF - ':
        periodStr = ' - HALF'
    else:
        periodStr = ' - ' + liveStream.period if liveStream.period != None else ''
    # Build score
    homeScore = liveStream.homeScore if liveStream.homeScore != None and len(liveStream.homeScore)>0 else '0'
    awayScore = liveStream.awayScore if liveStream.awayScore != None and len(liveStream.awayScore)>0 else '0'
    scoreStr = ' - ' + awayScore + '-' + homeScore if showscores else ''
    # Build title
    title = prefix + liveStream.event + ': ' + matchupStr + scoreStr + periodStr
    
    if truelive and resolution != 'SD Only' and liveStream.streamSet['truelive.hd'] != None:
        suffix = ' [TrueLive HD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.hd'], '', totalItems, showfanart)
    if truelive and resolution != 'HD Only' and liveStream.streamSet['truelive.sd'] != None:
        suffix = ' [TrueLive SD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.sd'], '', totalItems, showfanart)
    if flash and resolution != 'SD Only' and liveStream.streamSet['flash'] != None:
        suffix = ' [Flash]'
        utils.addLink(title + suffix, liveStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
    if istream and resolution != 'SD Only' and liveStream.streamSet['istream.hd'] != None:
        suffix = ' [iStream HD]'
        utils.addLink(title + suffix, liveStream.streamSet['istream.hd'], '', totalItems, showfanart)
    if istream and resolution != 'HD Only' and liveStream.streamSet['istream.sd'] != None:
        suffix = ' [iStream SD]'
        utils.addLink(title + suffix, liveStream.streamSet['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
    if istream and resolution == 'All' and liveStream.streamSet['istream'] != None:
        suffix = ' [iStream]'
        utils.addLink(title + suffix, liveStream.streamSet['istream'], '', totalItems, showfanart)
    if dvr and resolution != 'SD Only' and liveStream.streamSet['nondvrhd'] != None:
        suffix = ' [DVR HD]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvrhd'], '', totalItems, showfanart)
    if dvr and resolution != 'HD Only' and liveStream.streamSet['nondvrsd'] != None:
        suffix = ' [DVR SD]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvrsd'], '', totalItems, showfanart)
    if dvr and resolution == 'All' and liveStream.streamSet['nondvr'] != None:
        suffix = ' [DVR]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvr'], '', totalItems, showfanart)
    if wmv and resolution == 'All' and liveStream.streamSet['wmv'] != None:
        suffix = ' [WMV]'
        utils.addLink(title + suffix, liveStream.streamSet['wmv'], '', totalItems, showfanart)

    # Add refresh button
    refreshParams = {
        'refresh': 'True',
        'streamId': streamId
    }
    utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

# Compute the date utilized to determine current day live 
# once a game is final.
def getAdjustedDateTime():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=-8)

# Method to list a series of event streams
def __listEvents(session, events, mode, params, addRefresh = False):
    # Count total number of items for ui, this could potentially be
    # less if the url is invalid
    totalItems = len(events)

    # Increment the item count if we want a refresh button
    if addRefresh:
        totalItems = totalItems + 1

    # Add invalid flag to params
    params['invalid'] = 'True'

    # Add directories for events
    for event in events:
        streams = ballstreams.eventStream(session, event, location)

        # Make sure the streams are valid
        if streams != None:
            # Prepare title variables
            time = event.time if event.time != None else ''
            awayTeam = event.awayTeam
            homeTeam = event.homeTeam
            if shortNames:
                awayTeam = ballstreams.shortTeamName(event.awayTeam, addonPath)
                homeTeam = ballstreams.shortTeamName(event.homeTeam, addonPath)
            # Build score
            awayScore = event.awayScore if event.awayScore != None else ''
            homeScore = event.homeScore if event.homeScore != None else ''
            score = ''
            if showscores and awayScore != '' and not (awayScore == '0' and homeScore == '0'):
                score = ' - ' + awayScore + '-' + homeScore
            # Build period
            period = event.period if event.period != None else ''
            if period == 'HALF - ':
                period = 'HALF'
            elif period == '':
                period = time
            else:
                period = period.strip()
            feedType = event.feedType if event.feedType != None else ''
            # Generate stream title
            if awayScore == '':
                if feedType == 'Home Feed':
                    title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + '*'
                if feedType == 'Away Feed':
                    title = event.event + ': ' + awayTeam + '* @ ' + homeTeam
                if feedType == '':
                    title = event.event + ': ' + awayTeam + ' @ ' + homeTeam
            else:
                if feedType == 'Home Feed':
                    title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + '*' + score + ' - ' + period
                if feedType == 'Away Feed':
                    title = event.event + ': ' + awayTeam + '* @ ' + homeTeam + score + ' - ' + period
                if feedType == '':
                    title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + score + ' - ' + period

            # Add the streams that are enabled
            noStream = True
            if truelive and resolution != 'SD Only' and streams['truelive.hd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [TrueLive HD]'
                utils.addLink(prefix + title + suffix, streams['truelive.hd'], '', totalItems, showfanart)
                noStream = False
            if truelive and resolution != 'HD Only' and streams['truelive.sd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [TrueLive SD]'
                utils.addLink(prefix + title + suffix, streams['truelive.sd'], '', totalItems, showfanart)
                noStream = False

            if wmv and streams['wmv'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [WMV]'
                utils.addLink(prefix + title + suffix, streams['wmv'], '', totalItems, showfanart)
                noStream = False
            if flash and streams['flash'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [Flash]'
                utils.addLink(prefix + title + suffix, streams['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
                noStream = False

            noHdOrSd = True # Flag to indicate if we have hd or sd streams
            if istream and resolution != 'SD Only' and streams['istream.hd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [iStream HD]'
                utils.addLink(prefix + title + suffix, streams['istream.hd'], '', totalItems, showfanart)
                noHdOrSd = False
                noStream = False
            if istream and resolution != 'HD Only' and streams['istream.sd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [iStream SD]'
                utils.addLink(prefix + title + suffix, streams['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
                noHdOrSd = False
                noStream = False

            # Only add normal istream if we dont have SD or HD channels
            if istream and noHdOrSd and streams['istream'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [iStream]'
                utils.addLink(prefix + title + suffix, streams['istream'], '', totalItems, showfanart)
                noStream = False

            # Only add no stream message if we havent added any of the above
            if noStream:
                utils.addDir('[' + addon.getLocalizedString(100009) + '] ' + title, mode, '', params, totalItems, showfanart)

        # Add future stream items
        if streams == None:
            # Generate a title
            time = event.time if event.time != None else ''
            awayTeam = event.awayTeam
            homeTeam = event.homeTeam
            awayScore = event.awayScore if event.awayScore != None else ''
            homeScore = event.homeScore if event.homeScore != None else ''
            if shortNames:
                awayTeam = ballstreams.shortTeamName(event.awayTeam, addonPath)
                homeTeam = ballstreams.shortTeamName(event.homeTeam, addonPath)
            # customize title based on feed type
            feedType = event.feedType
            if feedType == 'Home Feed':
                title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + '* - ' + time
            elif feedType == 'Away Feed':
                title = event.event + ': ' + awayTeam + '* @ ' + homeTeam + ' - ' + time
            elif feedType == None or feedType == '':
                title = event.event + ': ' + awayTeam + ' @ ' + homeTeam + ' - ' + time
            # customize title based on period
            if event.period == None or str(event.period) == '':
                prefix = '[' + addon.getLocalizedString(100029) + '] ' if event.isOnDemand != True else ''
            else:
                if showscores and not(awayScore == '0' and homeScore == '0'):
                    title = title + ' - ' + awayScore + '-' + homeScore
                prefix = '[' + addon.getLocalizedString(100030) + '] ' if event.isOnDemand != True else ''

            suffix = ''
            # utils.addDir(prefix + title + suffix, mode, '', None, totalItems)
            # Create datetime for string formatting
            params = {
                'year': str(now.year),
                'month': str(now.month),
                'day': str(now.day)
            }
            utils.addDir(prefix + title + suffix, utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY, '', params, totalItems, showfanart)
            noStream = False

    # Check if we want a refresh button (only used for live)
    if addRefresh:
        refreshParams = {
            'refresh': 'True'
        }
        utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

# Load general settings
username = addon.getSetting('username')
password = addon.getSetting('password')
resolution = addon.getSetting('resolution')
print 'Setting resolution = ' + str(resolution)
shortNames = addon.getSetting('shortnames')
shortNames = shortNames != None and shortNames.lower() == 'true'
print 'Setting shortNames = ' + str(shortNames)
showscores = addon.getSetting('showscores')
showscores = showscores != None and showscores.lower() == 'true'
showfanart = addon.getSetting('showfanart')
showfanart = showfanart != None and showfanart.lower() == 'true'

# Load stream settings
istream = addon.getSetting('istream')
istream = istream != None and istream.lower() == 'true'
flash = addon.getSetting('flash')
flash = flash != None and flash.lower() == 'true'
wmv = addon.getSetting('wmv')
wmv = wmv != None and wmv.lower() == 'true'
truelive = addon.getSetting('truelive')
truelive = truelive != None and truelive.lower() == 'true'
dvr = addon.getSetting('dvr')
dvr = truelive != None and dvr.lower() == 'true'
location = addon.getSetting('location')
if location != None and location.lower() == 'auto':
    location = None # Location is special, if it is 'Auto' then it is None

# Load the sub-directory params
params = utils.getParams()

# Print sub-directory params for debugging
for k, v in params.iteritems():
    print k + ': ' + v

# Parse mode
mode = utils.parseParamInt(params, 'mode')

# Parse other variables
year = utils.parseParamInt(params, 'year')
month = utils.parseParamInt(params, 'month')
day = utils.parseParamInt(params, 'day')
team = utils.parseParamString(params, 'team')
streamId = utils.parseParamString(params, 'streamId')
invalid = utils.parseParamString(params, 'invalid')
invalid = invalid != None and invalid.lower() == 'true'
refresh = utils.parseParamString(params, 'refresh')
refresh = refresh != None and refresh.lower() == 'true'

# First check invalid stream else find mode and execute
if invalid:
    print 'Stream unavailable, please check ballstreams.com for wmv stream availability.'
    utils.showMessage(addon.getLocalizedString(100003), addon.getLocalizedString(100004))

# Check if username/password has been provided
if username == None or len(username) < 1 or password == None or len(password) < 1:
    addon.openSettings()
    # Reload settings
    username = addon.getSetting('username')
    password = addon.getSetting('password')

# Check if the user has entered valid settings
settingsInvalid = username == None or len(username) < 1 or password == None or len(password) < 1

# Set flags for end of directory
updateListing = invalid
cacheToDisc = True

# Perform a login
session = None
if settingsInvalid == False:
    try:
        session = ballstreams.login(username, password)
    except ballstreams.ApiException as e:
        print 'Error logging into ballstreams.com account: ' + str(e)

# Check login status and membership status
if session == None:
    mode = utils.Mode.HOME
    print 'The ballstreams.com session was null, login failed'
    utils.showMessage(addon.getLocalizedString(100011), addon.getLocalizedString(100012))
elif session.isPremium == False:
    mode = utils.Mode.HOME
    print 'The ballstreams.com account membership is non-premium, a paid for account is required'
    utils.showMessage(addon.getLocalizedString(100013), addon.getLocalizedString(100014))
else:
    # Attempt to create IP exception
    try:
        print 'Attempting to generate IP exception'
        ipException = ballstreams.ipException(session)
    except Exception as e:
        print 'Error creating an ip exception: ' + str(e)
        utils.showMessage(addon.getLocalizedString(100018), addon.getLocalizedString(100019))

if mode == None or mode == utils.Mode.HOME:
    HOME()
elif mode == utils.Mode.ONDEMAND:
    ONDEMAND()
elif mode == utils.Mode.ONDEMAND_BYDATE:
    ONDEMAND_BYDATE(session)
elif mode == utils.Mode.ONDEMAND_BYDATE_YEARMONTH:
    ONDEMAND_BYDATE_YEARMONTH(session, year, month)
elif mode == utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY:
    ONDEMAND_BYDATE_YEARMONTH_DAY(session, year, month, day)
    cacheToDisc = False
elif mode == utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT:
    ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, streamId)
    cacheToDisc = False
elif mode == utils.Mode.ONDEMAND_BYTEAM:
    ONDEMAND_BYTEAM(session)
elif mode == utils.Mode.ONDEMAND_BYTEAM_TEAM:
    ONDEMAND_BYTEAM_TEAM(session, team)
    cacheToDisc = False
elif mode == utils.Mode.ONDEMAND_BYTEAM_TEAM_EVENT:
    ONDEMAND_BYTEAM_TEAM_EVENT(session, streamId)
    cacheToDisc = False
elif mode == utils.Mode.LIVE:
    LIVE(session)
    updateListing = refresh
    cacheToDisc = False
elif mode == utils.Mode.LIVE_EVENT:
    LIVE_EVENT(session, streamId)
    updateListing = refresh
    cacheToDisc = False
    
# Signal end of directory
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc = cacheToDisc, updateListing = updateListing)
