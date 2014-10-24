import xbmc, xbmcplugin, xbmcaddon, xbmcgui
import ballstreams, utils
import os, datetime, threading, random, time

# xbmc-ball-streams
# author: craig mcnicholas, andrew wise
# contact: craig@designdotworks.co.uk, zergcollision@gmail.com

# deals with a bug where errors are thrown 
# if data directory does not exist.
addonId = 'plugin.video.xbmc-ball-streams'
dataPath = 'special://profile/addon_data/' + addonId
if not os.path.exists: os.makedirs(dataPath)
addon = xbmcaddon.Addon(id = addonId)
addonPath = addon.getAddonInfo('path')

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
    dates = ballstreams.onDemandDates(session)

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
    dates = ballstreams.onDemandDates(session)

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
        events = ballstreams.dateOnDemandEvents(session, date)
    except:
        return

    totalItems = len(events)

    for event in events:
        # Create datetime for string formatting
        parts = event.date.split('/')
        day = int(parts[1])
        month = int(parts[0])
        year = int(parts[2])
        dateStr = ' - ' + datetime.date(year, month, day).strftime('%b %d')

        # Build matchup
        homeTeam = event.homeTeam if not shortNames else ballstreams.shortTeamName(event.homeTeam, addonPath)
        awayTeam = event.awayTeam if not shortNames else ballstreams.shortTeamName(event.awayTeam, addonPath)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if feedType == 'Home Feed':
            matchupStr = matchupStr + '*'
        elif feedType == 'Away Feed':
            matchupStr = awayTeam + '* @ ' + homeTeam
        # Build title
        title = event.event + ': ' + matchupStr + dateStr

        params = {
            'eventId': event.eventId,
            'feedType': event.feedType,
            'dateStr': dateStr
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
def ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, eventId, feedType, dateStr):
    print 'ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, eventId, feedType, dateStr)'
    print 'eventId: ' + eventId
    print 'feedType: ' + str(feedType)
    print 'dateStr: ' + dateStr

    # Build streams
    onDemandStream = ballstreams.onDemandEventStreams(session, eventId, location)

    totalItems = 6 # max possible

    if onDemandStream == None or onDemandStream.streamSet == None:
        return None

    # Build matchup
    homeTeam = onDemandStream.homeTeam if not shortNames else ballstreams.shortTeamName(onDemandStream.homeTeam, addonPath)
    awayTeam = onDemandStream.awayTeam if not shortNames else ballstreams.shortTeamName(onDemandStream.awayTeam, addonPath)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if awayTeam == '' or homeTeam == '': # Indicates special event
        matchupStr = awayTeam + homeTeam
    if feedType == 'Home Feed':
        matchupStr = matchupStr + '*'
    elif feedType == 'Away Feed':
        matchupStr = awayTeam + '* @ ' + homeTeam
    # Build title
    title = onDemandStream.event + ': ' + matchupStr + dateStr

    if flash and onDemandStream.streamSet['flash'] != None:
        suffix = ' [Flash]'
        utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
    if istream and resolution != 'SD Only' and onDemandStream.streamSet['istream.hd'] != None:
        suffix = ' [iStream HD]'
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.hd'], '', totalItems, showfanart)
    if istream and resolution != 'HD Only' and onDemandStream.streamSet['istream.sd'] != None:
        suffix = ' [iStream SD]'
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
    if istream and resolution == 'All' and onDemandStream.streamSet['istream'] != None:
        suffix = ' [iStream]'
        utils.addLink(title + suffix, onDemandStream.streamSet['istream'], '', totalItems, showfanart)
    if wmv and onDemandStream.streamSet['wmv'] != None:
        suffix = ' [WMV]'
        utils.addLink(title + suffix, onDemandStream.streamSet['wmv'], '', totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

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
    events = ballstreams.teamOnDemandEvents(session, ballstreams.Team(team))

    totalItems = len(events)

    for event in events:
        # Create datetime for string formatting
        parts = event.date.split('/')
        day = int(parts[1])
        month = int(parts[0])
        year = int(parts[2])
        dateStr = ' - ' + datetime.date(year, month, day).strftime('%b %d')

        homeTeam = event.homeTeam if not shortNames else ballstreams.shortTeamName(event.homeTeam, addonPath)
        awayTeam = event.awayTeam if not shortNames else ballstreams.shortTeamName(event.awayTeam, addonPath)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if feedType == 'Home Feed':
            matchupStr = matchupStr + '*'
        elif feedType == 'Away Feed':
            matchupStr = awayTeam + '* @ ' + homeTeam
        # Build title
        title = event.event + ': ' + matchupStr + dateStr

        params = {
            'eventId': event.eventId,
            'feedType': event.feedType,
            'dateStr': dateStr
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
def ONDEMAND_BYTEAM_TEAM_EVENT(session, eventId, feedType, dateStr):
    print 'ONDEMAND_BYTEAM_TEAM_EVENT(session, eventId, feedType, dateStr)'
    print 'eventId: ' + eventId
    print 'feedType: ' + str(feedType)
    print 'dateStr: ' + str(dateStr)

    # Build streams
    onDemandStream = ballstreams.onDemandEventStreams(session, eventId, location)

    totalItems = 6 # max possible

    if onDemandStream == None or onDemandStream.streamSet == None:
        return None

    # Build matchup
    homeTeam = onDemandStream.homeTeam if not shortNames else ballstreams.shortTeamName(onDemandStream.homeTeam, addonPath)
    awayTeam = onDemandStream.awayTeam if not shortNames else ballstreams.shortTeamName(onDemandStream.awayTeam, addonPath)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if awayTeam == '' or homeTeam == '': # Indicates special event
        matchupStr = awayTeam + homeTeam
    if feedType == 'Home Feed':
        matchupStr = matchupStr + '*'
    elif feedType == 'Away Feed':
        matchupStr = awayTeam + '* @ ' + homeTeam
    # Build title
    title = onDemandStream.event + ': ' + matchupStr + str(dateStr)

    if flash and onDemandStream.streamSet['flash'] != None:
        suffix = ' [Flash]'
        utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
    if istream and resolution != 'SD Only' and onDemandStream.streamSet['istream.hd'] != None:
        suffix = ' [iStream HD]'
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.hd'], '', totalItems, showfanart)
    if istream and resolution != 'HD Only' and onDemandStream.streamSet['istream.sd'] != None:
        suffix = ' [iStream SD]'
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart)
    if istream and resolution == 'All' and onDemandStream.streamSet['istream'] != None:
        suffix = ' [iStream]'
        utils.addLink(title + suffix, onDemandStream.streamSet['istream'], '', totalItems, showfanart)
    if wmv and onDemandStream.streamSet['wmv'] != None:
        suffix = ' [WMV]'
        utils.addLink(title + suffix, onDemandStream.streamSet['wmv'], '', totalItems, showfanart)

    # Set view as Big List
    try:
        xbmc.executebuiltin('Container.SetViewMode(51)')
    except Exception as e:
        print 'Warning:  Unable to set view as Big List:  ' + str(e)

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
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if event.feedType == 'Home Feed':
            matchupStr = matchupStr + '*'
        elif event.feedType == 'Away Feed':
            matchupStr = awayTeam + '* @ ' + homeTeam
        # Build period
        periodStr = ''
        if event.period == 'HALF - ':
            periodStr = ' - HALF'
        elif event.period != '':
            periodStr = ' - ' + event.period if event.period != None else ''
        # Build score
        homeScore = event.homeScore if event.homeScore != None and len(event.homeScore)>0 else '0'
        awayScore = event.awayScore if event.awayScore != None and len(event.awayScore)>0 else '0'
        scoreStr = ' - ' + awayScore + '-' + homeScore if showscores and not event.isFuture and periodStr != '' else ''
        # Build start time
        startTimeStr = ''
        if periodStr == '':
            startTimeStr = ' - ' + event.startTime
        # Build title
        title = prefix + event.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr
        if event.isFinal:
            now = ballstreams.adjustedDateTime()
            params = {
                'year': str(now.year),
                'month': str(now.month),
                'day': str(now.day)
            }
            utils.addDir(title, utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY, '', params, totalItems, showfanart)
        elif event.isFuture:
            refreshParams = {
                'refresh': 'True'
            }
            utils.addDir(title, mode, '', refreshParams, totalItems, showfanart)
        else:
            params = {
                'eventId': event.eventId
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
# a list of current day event streams for an event id
def LIVE_EVENT(session, eventId):
    print 'LIVE_EVENT(session, eventId)'
    print 'eventId: ' + eventId

    # Build streams
    liveStream = ballstreams.liveEventStreams(session, eventId, location)

    totalItems = 11 # max possible

    if liveStream == None or liveStream.streamSet == None:
        return None

    # Build prefix
    prefix = '[LIVE] '
    # Build matchup
    homeTeam = liveStream.homeTeam if not shortNames else ballstreams.shortTeamName(liveStream.homeTeam, addonPath)
    awayTeam = liveStream.awayTeam if not shortNames else ballstreams.shortTeamName(liveStream.awayTeam, addonPath)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if awayTeam == '' or homeTeam == '': #indicates special event
        matchupStr = awayTeam + homeTeam
    if liveStream.feedType == 'Home Feed':
        matchupStr = matchupStr + '*'
    elif liveStream.feedType == 'Away Feed':
        matchupStr = awayTeam + '* @ ' + homeTeam
    # Build period
    periodStr = ''
    if liveStream.period == 'HALF - ':
        periodStr = ' - HALF'
    elif liveStream.period != '':
        periodStr = ' - ' + liveStream.period if liveStream.period != None else ''
    # Build score
    homeScore = liveStream.homeScore if liveStream.homeScore != None and len(liveStream.homeScore)>0 else '0'
    awayScore = liveStream.awayScore if liveStream.awayScore != None and len(liveStream.awayScore)>0 else '0'
    scoreStr = ' - ' + awayScore + '-' + homeScore if showscores and periodStr != '' else ''
    # Build start time
    startTimeStr = ''
    if periodStr == '':
        startTimeStr = ' - ' + liveStream.startTime
    # Build title
    title = prefix + liveStream.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr

    # Add links
    if truelive and resolution != 'SD Only' and liveStream.streamSet['truelive.hd'] != None:
        suffix = ' [TrueLive HD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.hd'], '', totalItems, showfanart)
    if truelive and resolution != 'HD Only' and liveStream.streamSet['truelive.sd'] != None:
        suffix = ' [TrueLive SD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.sd'], '', totalItems, showfanart)
    if flash and liveStream.streamSet['flash'] != None:
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
    if wmv and liveStream.streamSet['wmv'] != None:
        suffix = ' [WMV]'
        utils.addLink(title + suffix, liveStream.streamSet['wmv'], '', totalItems, showfanart)

    # Add refresh button
    refreshParams = {
        'refresh': 'True',
        'eventId': eventId
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
shortNames = addon.getSetting('shortnames')
shortNames = shortNames != None and shortNames.lower() == 'true'
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
dvr = dvr != None and dvr.lower() == 'true'
location = addon.getSetting('location')
if location != None and location.lower() == 'auto':
    location = None # Location is special, if it is 'Auto' then it is None

# Load the directory params
params = utils.getParams()

# Print directory params for debugging
for k, v in params.iteritems():
    print k + ': ' + v

# Parse mode
mode = utils.parseParamInt(params, 'mode')

# Parse other variables
year = utils.parseParamInt(params, 'year')
month = utils.parseParamInt(params, 'month')
day = utils.parseParamInt(params, 'day')
team = utils.parseParamString(params, 'team')
eventId = utils.parseParamString(params, 'eventId')
feedType = utils.parseParamString(params, 'feedType')
dateStr = utils.parseParamString(params, 'dateStr')
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

# Invoke mode function
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
elif mode == utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT:
    ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, eventId, feedType, dateStr)
elif mode == utils.Mode.ONDEMAND_BYTEAM:
    ONDEMAND_BYTEAM(session)
elif mode == utils.Mode.ONDEMAND_BYTEAM_TEAM:
    ONDEMAND_BYTEAM_TEAM(session, team)
elif mode == utils.Mode.ONDEMAND_BYTEAM_TEAM_EVENT:
    ONDEMAND_BYTEAM_TEAM_EVENT(session, eventId, feedType, dateStr)
elif mode == utils.Mode.LIVE:
    LIVE(session)
    updateListing = refresh
    cacheToDisc = False
elif mode == utils.Mode.LIVE_EVENT:
    LIVE_EVENT(session, eventId)
    updateListing = refresh
    cacheToDisc = False

# Signal end of directory
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc = cacheToDisc, updateListing = updateListing)
