import xbmc, xbmcplugin, xbmcaddon, xbmcgui
import ballstreams, utils
import os, datetime, threading, random, time

# xbmc-ball-streams
# author: craig mcnicholas
# contact: craig@designdotworks.co.uk

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
    utils.addDir(addon.getLocalizedString(100005), utils.Mode.ARCHIVES, '', None)
    utils.addDir(addon.getLocalizedString(100006), utils.Mode.LIVE, '', None)

# Method to draw the archives screen
def ARCHIVES():
    print 'ARCHIVES()'
    utils.addDir(addon.getLocalizedString(100007), utils.Mode.ARCHIVES_BY_DATE, '', None)
    utils.addDir(addon.getLocalizedString(100008), utils.Mode.ARCHIVES_BY_TEAM, '', None)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of years for archives
# @param session the user session to make api calls with
def ARCHIVES_BY_DATE(session):
    print 'ARCHIVES_BY_DATE(session)'

    # Retrieve the available dates
    dates = ballstreams.availableDates(session)

    # Find unique years
    years = []
    for date in dates:
        if years.count(date.year) < 1:
            years.append(date.year)

    # Count total number of items for ui
    totalItems = len(years)
    
    # Add directories for years
    for year in years:
        params = {
            'year': str(year)
        }
        utils.addDir(str(year), utils.Mode.ARCHIVES_BY_DATE_YEAR, '', params, totalItems)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of months for a given year of archives
# @param session the user session to make api calls with
# @param year the year to obtain valid months for
def ARCHIVES_BY_DATE_YEAR(session, year):
    print 'ARCHIVES_BY_DATE_YEAR(session, year)'
    print 'Year: ' + str(year)

    # Retrieve the available dates
    dates = ballstreams.availableDates(session)

    # Find unique months
    months = []
    for date in dates:
        if year == date.year and months.count(date.month) < 1:
            months.append(date.month)

    # Count total number of items for ui
    totalItems = len(months)

    # Add directories for months
    for month in months:
        # Create datetime for string formatting
        date = datetime.date(year, month, 1)
        params = {
            'year': str(year),
            'month': str(month)
        }
        utils.addDir(date.strftime('%B %Y'), utils.Mode.ARCHIVES_BY_DATE_MONTH, '', params, totalItems)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of days for a given year and month of archives
# @param session the user session to make api calls with
# @param year the year to obtain valid months for
# @param month the month to obtain valid days for
def ARCHIVES_BY_DATE_MONTH(session, year, month):
    print 'ARCHIVES_BY_DATE_MONTH(session, year, month)'
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
        utils.addDir(date.strftime('%A %d %B %Y'), utils.Mode.ARCHIVES_BY_DATE_DAY, '', params, totalItems)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of archived games for a given day
# @param session the user session to make api calls with
# @param year the year to obtain valid months for
# @param month the month to obtain valid days for
# @param day the day to obtain valid games for
# @param istream whether to enable istreams
# @param flash whether to enable flash
# @param rtmp whether to enable rtmp
# @param wmv whether to enable wmv
# @param shortNames whether to show short team names
# @param location the location to use for streams
def ARCHIVES_BY_DATE_DAY(session, year, month, day, istream, flash, rtmp, wmv, shortNames, location):
    print 'ARCHIVES_BY_DATE_DAY(session, year, month, day)'
    print 'Year: ' + str(year)
    print 'Month: ' + str(month)
    print 'Day: ' + str(day)

    # Retrieve the events
    date = datetime.date(year, month, day)
    events = ballstreams.eventsForDate(session, date)

    params = {
        'year': str(year),
        'month': str(month),
        'day': str(day)
    }
    __listEvents(session, events, utils.Mode.ARCHIVES_BY_DATE_DAY, params, istream = istream, flash = flash, rtmp = rtmp, wmv = wmv, shortNames = shortNames, location = location)

# Method to draw the archives by team screen
# which scrapes the external source and presents
# a list of team names (or potentially events)
# @param session the user session to make api calls with
# @param shortNames whether to show short team names
def ARCHIVES_BY_TEAM(session, shortNames):
    print 'ARCHIVES_BY_TEAM(session)'

    # Retrieve the teams
    teams = ballstreams.teams(session)

    # Count total number of items for ui
    totalItems = len(teams)

    # Add directories for teams
    for team in teams:
        params = {
            'team': team.name
        }
        teamName = team.name
        # if shortNames:
            # teamName = ballstreams.shortTeamName(team.name, addonPath)
        utils.addDir(teamName, utils.Mode.ARCHIVES_BY_TEAM_EVENTS, '', params, totalItems)

# Method to draw the archives by team screen
# which scrapes the external source and presents
# a list of events for a given team
# @param session the user session to make api calls with
# @param team the team to find the events for
# @param istream whether to enable istreams
# @param flash whether to enable flash
# @param rtmp whether to enable rtmp
# @param wmv whether to enable wmv
# @param shortNames whether to show short team names
# @param location the location to use for streams
def ARCHIVES_BY_TEAM_EVENTS(session, team, istream, flash, rtmp, wmv, shortNames, location):
    print 'ARCHIVES_BY_TEAM_EVENTS(session, team)'
    print 'Team: ' + team

    # Retrieve the team events
    events = ballstreams.eventsForTeam(session, ballstreams.Team(team))

    params = {
        'team': team
    }
    __listEvents(session, events, utils.Mode.ARCHIVES_BY_TEAM_EVENTS, params, istream = istream, flash = flash, rtmp = rtmp, wmv = wmv, shortNames = shortNames, location = location)

# Method to list a series of event streams
# @param session the session instance to login with
# @param events the list of events to display
# @param mode the mode to return to if stream is invalid
# @param params the params to pass if stream is invalid
# @param addRefresh whether to add a refresh link to the end
# @param istream whether to enable istreams
# @param flash whether to enable flash streams
# @param rtmp whether to enable rtmp streams
# @param wmv whether to enable wmv streams
# @param shortNames whether to show short team names
# @param location the location to get streams for or None
def __listEvents(session, events, mode, params, addRefresh = False, istream = False, flash = False, rtmp = False, wmv = False, shortNames = True, location = None):
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
            if awayScore != '' and not (awayScore == '0' and homeScore == '0'):
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
            if rtmp and resolution != 'SD Only' and streams['truelive.hd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [TrueLive HD]'
                utils.addLink(prefix + title + suffix, streams['truelive.hd'], '', totalItems)
                noStream = False
            if rtmp and resolution != 'HD Only' and streams['truelive.sd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [TrueLive SD]'
                utils.addLink(prefix + title + suffix, streams['truelive.sd'], '', totalItems)
                noStream = False

            if wmv and streams['wmv'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [WMV]'
                utils.addLink(prefix + title + suffix, streams['wmv'], '', totalItems)
                noStream = False
            if flash and streams['flash'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [Flash]'
                utils.addLink(prefix + title + suffix, streams['flash'].replace('f4m', 'm3u8'), '', totalItems)
                noStream = False

            noHdOrSd = True # Flag to indicate if we have hd or sd streams
            if istream and resolution != 'SD Only' and streams['istream.hd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [iStream HD]'
                utils.addLink(prefix + title + suffix, streams['istream.hd'], '', totalItems)
                noHdOrSd = False
                noStream = False
            if istream and resolution != 'HD Only' and streams['istream.sd'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [iStream SD]'
                utils.addLink(prefix + title + suffix, streams['istream.sd'].replace('f4m', 'm3u8'), '', totalItems)
                noHdOrSd = False
                noStream = False
            
            # if streams['nondvrhd'] != None:
                # prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                # suffix = ' [DVR HD]'
                # utils.addLink(prefix + title + suffix, streams['nondvrhd'], '', totalItems)
                # noStream = False
            # if streams['nondvrsd'] != None:
                # prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                # suffix = ' [DVR SD]'
                # utils.addLink(prefix + title + suffix, streams['nondvrsd'], '', totalItems)
                # noStream = False

            # Only add normal istream if we dont have SD or HD channels
            if istream and noHdOrSd and streams['istream'] != None:
                prefix = '[' + addon.getLocalizedString(100010) + '] ' if event.isOnDemand != True else ''
                suffix = ' [iStream]'
                utils.addLink(prefix + title + suffix, streams['istream'], '', totalItems)
                noStream = False

            # Only add no stream message if we havent added any of the above
            if noStream:
                utils.addDir('[' + addon.getLocalizedString(100009) + '] ' + title, mode, '', params, totalItems)

        # Add future stream items
        if streams == None:
            # Generate a title
            time = event.time if event.time != None else ''
            awayTeam = event.awayTeam
            homeTeam = event.homeTeam
            awayScore = event.awayScore
            homeScore = event.homeScore
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
                title = title + ' - ' + awayScore + '-' + homeScore
                prefix = '[' + addon.getLocalizedString(100030) + '] ' if event.isOnDemand != True else ''

            suffix = ''
            utils.addDir(prefix + title + suffix, mode, '', None, totalItems)
            noStream = False

    # Check if we want a refresh button (only used for live)
    if addRefresh:
        refreshParams = {
            'refresh': 'True'
        }
        utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems)

# Method to draw the live screen
# which scrapes the external source and presents
# a list of live or future events
# @param session the user session to make api calls with
# @param istream whether to enable istreams
# @param flash whether to enable flash
# @param rtmp whether to enable rtmp
# @param wmv whether to enable wmv
# @param shortNames whether to show short team names
# @param location the location to get streams for or None
def LIVE(session, istream, flash, rtmp, wmv, shortNames, location):
    print 'LIVE(session)'

    # Find live events
    events = ballstreams.liveEvents(session)

    params = {}
    __listEvents(session, events, utils.Mode.LIVE, params, addRefresh = True, istream = istream, flash = flash, rtmp = rtmp, wmv = wmv, shortNames = shortNames, location = location)
	
# Load settings
username = addon.getSetting('username')
password = addon.getSetting('password')
istream = addon.getSetting('istream')
istream = istream != None and istream.lower() == 'true'
flash = addon.getSetting('flash')
flash = flash != None and flash.lower() == 'true'
wmv = addon.getSetting('wmv')
wmv = wmv != None and wmv.lower() == 'true'
shortNames = addon.getSetting('shortnames')
shortNames = shortNames != None and shortNames.lower() == 'true'
rtmp = addon.getSetting('rtmp')
rtmp = rtmp != None and rtmp.lower() == 'true'
location = addon.getSetting('location')
if location != None and location.lower() == 'auto':
    location = None # Location is special, if it is 'Auto' then it is None
resolution = addon.getSetting('resolution')
    
# Load the parameters
params = utils.getParams()

# Print params for debugging
for k, v in params.iteritems():
    print k + ': ' + v

# Attempt to parse mode
mode = utils.parseParamInt(params, 'mode')

# Attempt to parse other variables
year = utils.parseParamInt(params, 'year')
month = utils.parseParamInt(params, 'month')
day = utils.parseParamInt(params, 'day')
team = utils.parseParamString(params, 'team')
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
elif mode == utils.Mode.ARCHIVES:
    ARCHIVES()
elif mode == utils.Mode.ARCHIVES_BY_DATE:
    ARCHIVES_BY_DATE(session)
elif mode == utils.Mode.ARCHIVES_BY_DATE_YEAR:
    ARCHIVES_BY_DATE_YEAR(session, year)
elif mode == utils.Mode.ARCHIVES_BY_DATE_MONTH:
    ARCHIVES_BY_DATE_MONTH(session, year, month)
elif mode == utils.Mode.ARCHIVES_BY_DATE_DAY:
    ARCHIVES_BY_DATE_DAY(session, year, month, day, istream, flash, rtmp, wmv, shortNames, location)
elif mode == utils.Mode.ARCHIVES_BY_TEAM:
    ARCHIVES_BY_TEAM(session, shortNames)
elif mode == utils.Mode.ARCHIVES_BY_TEAM_EVENTS:
    ARCHIVES_BY_TEAM_EVENTS(session, team, istream, flash, rtmp, wmv, shortNames, location)
elif mode == utils.Mode.LIVE:
    LIVE(session, istream, flash, rtmp, wmv, shortNames, location)
    cacheToDisc = False # Never cache this view
    updateListing = refresh

# Signal end of directory
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc = cacheToDisc, updateListing = updateListing)
