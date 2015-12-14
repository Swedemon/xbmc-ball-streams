import xbmc, xbmcplugin, xbmcaddon, xbmcgui
import streams, utils
import os, datetime, threading, random, time, json, uuid, glob, tempfile, traceback
try:
  from PIL import Image, ImageDraw, ImageFont
except ImportError:
  pilSupport = False
  pass
else:
  pilSupport = True

# author: craig mcnicholas, swedemon
# contact: craig@designdotworks.co.uk, zergcollision@gmail.com

# deals with a bug where errors are thrown 
# if data directory does not exist.
addonId = 'plugin.video.xbmc-ball-streams-frodo'
dataPath = 'special://profile/addon_data/' + addonId
if not os.path.exists: os.makedirs(dataPath)
addon = xbmcaddon.Addon(id = addonId)
addonPath = addon.getAddonInfo('path')
teamsJsonPath = os.path.join(addonPath, 'resources', 'data', 'teams.json')
f = open(teamsJsonPath, 'rb')
teamsContent = f.read()
f.close()
teams = json.loads(teamsContent)

class Icon():
    def feedTypeLogo(self,feedType,homeTeam,awayTeam):
      if feedType is None:
        return None
      elif feedType == 'Home Feed' and 'logo' in homeTeam:
        return Image.open(os.path.join(addonPath,homeTeam['logo']).replace('.png','48x48.png'))
      elif feedType == 'Away Feed' and 'logo' in awayTeam:
        return Image.open(os.path.join(addonPath,awayTeam['logo']).replace('.png','48x48.png'))
      else:
        return None

    def __init__(self, homeTeam, awayTeam, header, feedType = None, homeScore = None, awayScore = None):
        if pilSupport is False:
          raise ValueError('No PIL support.')
        # some fonts we'll be using
        headerFont = ImageFont.truetype(os.path.join(addonPath,'resources','data','fonts','Open_Sans','OpenSans-Regular.ttf'), 18)
        abbFont    = ImageFont.truetype(os.path.join(addonPath,'resources','data','fonts','Open_Sans','OpenSans-Bold.ttf'), 22)
        scoresFont = ImageFont.truetype(os.path.join(addonPath,'resources','data','fonts','Open_Sans','OpenSans-Bold.ttf'), 48)
        emptyIcon  = os.path.join(addonPath,'empty_icon.png')

        icon = Image.open(emptyIcon)
        draw = ImageDraw.Draw(icon)
        
        awayTeam = teams[awayTeam.lower()] if awayTeam.lower() in teams else awayTeam
        homeTeam = teams[homeTeam.lower()] if homeTeam.lower() in teams else homeTeam
        awayTeamText = awayTeam['abbreviation'] if 'abbreviation' in awayTeam else awayTeam['shortName'][:14] if 'shortName' in awayTeam else awayTeam[:14]
        homeTeamText = homeTeam['abbreviation'] if 'abbreviation' in homeTeam else homeTeam['shortName'][:14] if 'shortName' in homeTeam else homeTeam[:14]
        
        if 'logo' in awayTeam:
            awayTeamLogo = Image.open(os.path.join(addonPath,awayTeam['logo']))
            icon.paste(awayTeamLogo, (10,60+1), awayTeamLogo)
            draw.text((115,60+35), awayTeamText, font = abbFont, fill="black")
        else:
            draw.text((10,60+35), awayTeamText, font = abbFont, fill="black")
        if 'logo' in homeTeam:
            homeTeamLogo = Image.open(os.path.join(addonPath,homeTeam['logo']))
            icon.paste(homeTeamLogo, (10,60+98+1), homeTeamLogo)
            draw.text((115,60+98+35), homeTeamText, font = abbFont, fill="black")
        else:
            draw.text((10,60+98+35), homeTeamText, font = abbFont, fill="black")
        ftLogo = self.feedTypeLogo(feedType,homeTeam,awayTeam)
        if ftLogo is not None:
          icon.paste(ftLogo, (10,6,10+48,6+48), ftLogo)
          draw.text((65, 16), header.replace(' - ',' ').replace('   ',' ').replace('  ',' ').replace('[','').replace(']',''), font = headerFont, fill="black")
        else:
          draw.text((10, 16), header.replace(' - ',' ').replace('   ',' ').replace('  ',' ').replace('[','').replace(']','') + (' - {0}'.format(feedType) if feedType is not None and feedType != '' else ''), font = headerFont, fill="black")
        if (homeScore is not None and awayScore is not None):
          xScore = 200
          if int(awayScore) > 99:
            xScore = 170
          elif int(awayScore) > 9:
            xScore = 190
          draw.text((xScore, 60+15), awayScore, font = scoresFont, fill="black")
          xScore = 200
          if int(homeScore) > 99:
            xScore = 170
          elif int(homeScore) > 9:
            xScore = 190
          draw.text((xScore, 60+98+15), homeScore, font = scoresFont, fill="black")
        self.image = icon

    def filename(self):
        return os.path.join(addonPath,'resources','data','hs_logo' + str(uuid.uuid4())[:8] + '.png')

    def save(self):
        try:
          saveLocation = self.filename()
          self.image.save(saveLocation, 'PNG', compress_level = 1)
        except:
          e = sys.exc_info()[0]
          print 'Could not save icon: %s' % e
          saveLocation = 'special://home/addons/' + addonId + '/Main_icon.png'
        return saveLocation

def createIcon(homeTeam, awayTeam, header, feedType = None, homeScore = None, awayScore = None):
    if (showicons and pilSupport):
        return Icon(homeTeam,awayTeam,header,feedType,homeScore if (showscores) else None,awayScore if (showscores) else None)
    else:
        return None

def iconCleanup():
    try:
      tempdir = tempfile.gettempdir()
      for png in glob.glob(os.path.join(addonPath,'resources','data','hs_logo*.png')):
        os.remove(png)
    except:
      e = sys.exc_info()[0]
      print 'iconCleanup failed: %s' % e
      pass

# Method to get the short team name of a team
# @param teamName the team name to get the shortened version for
# @param root the root file path to append the resource file path to
# @return a short team name or the original team name if not found
def shortTeamName(teamName):
    # Get lower case key name and check it exists
    teamNameLower = teamName.lower()
    if teamNameLower in teams and "shortName" in teams[teamNameLower]:
        return teams[teamNameLower]["shortName"] # It does so get name
    else:
        return teamName # It doesn't return original


# Method to draw the home screen
def HOME():
    print 'HOME()'
    utils.addDir(addon.getLocalizedString(100005), utils.Mode.ONDEMAND, '', None, 2, showfanart)
    if showaltlive:
        # utils.addDir(addon.getLocalizedString(100006), utils.Mode.LIVEEVENT, '', None, 2, showfanart)
        LIVEEVENT(session)
    else:
        # utils.addDir(addon.getLocalizedString(100006), utils.Mode.LIVE, '', None, 2, showfanart)
        LIVE(session)

        updateListing = refresh
        cacheToDisc = False

    setViewMode()

# Method to draw the archives screen
def ONDEMAND():
    print 'ONDEMAND()'
    utils.addDir(addon.getLocalizedString(100007), utils.Mode.ONDEMAND_BYDATE, '', None, 2, showfanart)
    utils.addDir(addon.getLocalizedString(100008), utils.Mode.ONDEMAND_BYTEAM, '', None, 2, showfanart)
    
    # Append Recent day events
    ONDEMAND_RECENT(session)

    setViewMode()

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of months/years for archives
def ONDEMAND_BYDATE(session):
    print 'ONDEMAND_BYDATE(session)'

    # Retrieve the available dates
    dates = streams.onDemandDates(session)

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

    # Add custom date directory
    utils.addDir('[ Custom Date ]', utils.Mode.ONDEMAND_BYDATE_CUSTOM, '', None, 2, showfanart)

    setViewMode()

# Method to draw the on-demand by date screen
# which scrapes the external source and presents
# a list of days for a given year and month of archives
def ONDEMAND_BYDATE_YEARMONTH(session, year, month):
    print 'ONDEMAND_BYDATE_YEARMONTH(session, year, month)'
    print 'Year: ' + str(year)
    print 'Month: ' + str(month)

    # Retrieve the available dates
    dates = streams.onDemandDates(session)

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

    setViewMode()

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
        events = streams.dateOnDemandEvents(session, date, showScoresOnDemand)
    except Exception as e:
        print 'Warning:  No events found for date: ' + str(date) + ' Msg: ' + str(e)
        return

    totalItems = len(events)
    
    buildOnDemandEvents(session, events, totalItems, 1) # favorite
    buildOnDemandEvents(session, events, totalItems, 2) # non-favorites

    setViewMode()

# Method to build on-demand events
# @param filter 0 = ALL, 1 = favorite, 2 = non favorites
def buildOnDemandEvents(session, events, totalItems, filter):
    for event in events:
        # skip condition 1
        if filter == 1 and not (event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue
        # skip condition 2
        if filter == 2 and (event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue

        # Check global league filter
        if enableleaguefilter and leagueFilter.count(event.event) == 0:
			continue

        # Create datetime for string formatting
        parts = event.date.split('/')
        day = int(parts[1])
        month = int(parts[0])
        year = int(parts[2])
        dateStr = ' - ' + datetime.date(year, month, day).strftime('%d %b \'%y')

        # Build matchup
        homeTeam = event.homeTeam if not shortNames else shortTeamName(event.homeTeam)
        awayTeam = event.awayTeam if not shortNames else shortTeamName(event.awayTeam)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if event.feedType == 'Home Feed':
            matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
        elif event.feedType == 'Away Feed':
            matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
        # Build score
        homeScore = event.homeScore if event.homeScore != None and len(event.homeScore)>0 else '0'
        awayScore = event.awayScore if event.awayScore != None and len(event.awayScore)>0 else '0'
        scoreStr = ' - ' + awayScore + '-' + homeScore if showScoresOnDemand else ''
        # Build feedStr
        feedStr = ''
        if event.feedType == 'Home Feed' or event.feedType == 'Away Feed':
            feedStr = ''
        elif event.feedType == None or event.feedType == '':
            feedStr = ' - ' + 'N/A'
        elif event.feedType.endswith(' Feed'):
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType[:len(event.feedType)-5] + '[/COLOR]'
        else:
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType + '[/COLOR]'
        # Build title
        title = event.event + ': ' + matchupStr + scoreStr + dateStr + feedStr
        if event.homeTeam == session.favteam or event.awayTeam == session.favteam:
            title = '[COLOR red][B]' + title + '[/B][/COLOR]'

        params = {
            'eventId': event.eventId,
            'feedType': event.feedType,
            'dateStr': dateStr
        }
        icon = createIcon(event.homeTeam,event.awayTeam,event.date,event.feedType,homeScore = event.homeScore,awayScore = event.awayScore)
        utils.addDir(title, utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT, '', params, totalItems, showfanart, icon)

# Method to draw the archives by date screen
# which scrapes the external source and presents
# a list of on-demand streams for a given event
def ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, eventId, feedType, dateStr):
    print 'ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, eventId, feedType, dateStr)'
    print 'eventId: ' + eventId
    print 'feedType: ' + str(feedType)
    print 'dateStr: ' + dateStr

    # Build streams
    onDemandStream = streams.onDemandEventStreams(session, eventId, location)

    totalItems = 10 # max possible

    if onDemandStream == None or onDemandStream.streamSet == None:
        return None

    # Build matchup
    homeTeam = onDemandStream.homeTeam if not shortNames else shortTeamName(onDemandStream.homeTeam)
    awayTeam = onDemandStream.awayTeam if not shortNames else shortTeamName(onDemandStream.awayTeam)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if awayTeam == '' or homeTeam == '': # Indicates special event
        matchupStr = awayTeam + homeTeam
    if feedType == 'Home Feed':
        matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
    elif feedType == 'Away Feed':
        matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
    # Build feedStr
    feedStr = ''
    if feedType == 'Home Feed' or feedType == 'Away Feed':
        feedStr = ''
    elif feedType == None or feedType == '':
        feedStr = ' - ' + 'N/A'
    elif feedType.endswith(' Feed'):
        feedStr = ' - ' + '[COLOR lightgreen]' + feedType[:len(feedType)-5] + '[/COLOR]'
    else:
        feedStr = ' - ' + '[COLOR lightgreen]' + feedType + '[/COLOR]'
    # Build title
    title = onDemandStream.event + ': ' + matchupStr + dateStr
    def icon(suffix):
        return createIcon(onDemandStream.homeTeam,onDemandStream.awayTeam,suffix,feedType)
    if istream and ondemandresolution != 'SD Only' and onDemandStream.streamSet['istream.hd'] != None:
        suffix = ' [iStream HD]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.hd'], '', totalItems, showfanart,icon(' [iStream HD]'))
    if istream and ondemandresolution != 'HD Only' and onDemandStream.streamSet['istream.sd'] != None:
        suffix = ' [iStream SD]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [iStream SD]'))
    if istream and ondemandresolution == 'All' and onDemandStream.streamSet['istream'] != None and onDemandStream.streamSet['istream'] != onDemandStream.streamSet['istream.hd']:
        suffix = ' [iStream]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['istream'], '', totalItems, showfanart, icon(' [iStream]'))
    if hls and onDemandStream.streamSet['hls'] != None:
        if 'HD.' in onDemandStream.streamSet['hls'] and ondemandresolution != 'SD Only':
            suffix = ' [HLS HD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['hls'], '', totalItems, showfanart, icon(' [HLS HD]'))
        elif 'SD.' in onDemandStream.streamSet['hls'] and ondemandresolution != 'HD Only':
            suffix = ' [HLS SD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['hls'], '', totalItems, showfanart, icon(' [HLS SD]'))
        else:
            suffix = ' [HLS]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['hls'], '', totalItems, showfanart, icon(' [HLS]'))
    if hls and onDemandStream.streamSet['hls.sd'] != None and ondemandresolution != 'HD Only':
        suffix = ' [HLS SD]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['hls.sd'], '', totalItems, showfanart, icon(' [HLS SD]'))
    if flash and onDemandStream.streamSet['flash'] != None:
        if 'HD.' in onDemandStream.streamSet['flash']and ondemandresolution != 'SD Only':
            suffix = ' [Flash HD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [Flash HD]'))
        elif 'SD.' in onDemandStream.streamSet['flash'] and ondemandresolution != 'HD Only':
            suffix = ' [Flash SD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [Flash SD]'))
        else:
            suffix = ' [Flash]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [Flash]'))
    if wmv and onDemandStream.streamSet['wmv'] != None:
        suffix = ' [WMV]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['wmv'], '', totalItems, showfanart, icon(' [WMV]'))

    try:
        if feedType == 'Away Feed':
          team = onDemandStream.awayTeam
        else:
          team = onDemandStream.homeTeam
        try:
          dStr = datetime.datetime.strptime(dateStr, ' - %d %b \'%y')
        except TypeError:
          dStr = datetime.datetime(*(time.strptime(dateStr, ' - %d %b \'%y')[0:6]))
        HIGHLIGHTSANDCONDENSED_BYTEAM_TEAMDATE(session, team, dStr)
    except Exception as e:
        print 'Error initializing on-demand event streams: ' + str(e)
        traceback.print_exc()

    setViewMode()

# Method to draw a list of recent month/years
# to custom search on-demand archives
def ONDEMAND_BYDATE_CUSTOM(session):
    print 'ONDEMAND_BYDATE_CUSTOM(session)'

    a = datetime.datetime.today()
    daysBack = 800 # Could be an addon setting
    dateStrList = []
    for x in range (0, daysBack):
        nextDate = a - datetime.timedelta(days = x)
        monthYear = nextDate.strftime('%B %Y')
        if (dateStrList.count(monthYear)==0):
            dateStrList.append(monthYear)
            params = {
                'year': str(nextDate.year),
                'month': str(nextDate.month)
            }
            utils.addDir(monthYear, utils.Mode.ONDEMAND_BYDATE_CUSTOM_YEARMONTH, '', params, 17, showfanart)

    setViewMode()

# Method to draw a list of days for a given month/year
# to custom search on-demand archives
def ONDEMAND_BYDATE_CUSTOM_YEARMONTH(session, year, month):
    print 'ONDEMAND_BYDATE_CUSTOM_YEARMONTH(session, year, month)'
    print 'Year: ' + str(year)
    print 'Month: ' + str(month)

    currentDay = datetime.date.today()
    nextMonthDay = datetime.date(year, month, 1) + datetime.timedelta(days = 31)
    lastMonthDay = datetime.date(nextMonthDay.year, nextMonthDay.month, 1) - datetime.timedelta(days = 1)
    daysBack = int(lastMonthDay.day)

    # COMMENTED THIS OUT - CRASHES XBMC TOO OFTEN EXECUTING TOO MANY API REQUESTS SO QUICKLY
    # if lastMonthDay < currentDay or currentDay.day > 16:
        # params = {
            # 'year': str(year),
            # 'month': str(month),
            # 'day': str(16),
            # 'numberOfDays': str(16)
        # }
        # if str(lastMonthDay.day) == '31':
            # title = '[ Deep Search ' + lastMonthDay.strftime('%B') + ' 16th to ' + str(lastMonthDay.day) + 'st ]'
        # else:
            # title = '[ Deep Search ' + lastMonthDay.strftime('%B') + ' 16th to ' + str(lastMonthDay.day) + 'th ]'
        # utils.addDir(title, utils.Mode.ONDEMAND_BYDATE_CUSTOM_YEARMONTH_RANGE, '', params, 33, showfanart)
    # if lastMonthDay < currentDay or currentDay.day > 1:
        # params = {
            # 'year': str(year),
            # 'month': str(month),
            # 'day': str(1),
            # 'numberOfDays': str(15)
        # }
        # title = '[ Deep Search ' + lastMonthDay.strftime('%B') + ' 1st to 15th ]'
        # utils.addDir(title, utils.Mode.ONDEMAND_BYDATE_CUSTOM_YEARMONTH_RANGE, '', params, 33, showfanart)

    for x in range (0, daysBack):
        nextDate = lastMonthDay - datetime.timedelta(days = x)
        if nextDate <= currentDay:
            params = {
                'year': str(nextDate.year),
                'month': str(nextDate.month),
                'day': str(nextDate.day)
            }
            utils.addDir(nextDate.strftime('%A %d %B %Y'), utils.Mode.ONDEMAND_BYDATE_YEARMONTH_DAY, '', params, 33, showfanart)
    
    setViewMode()

# Method to populate a date range of events
# which scrapes the external source and presents
# a list of events within a date range
def ONDEMAND_BYDATE_CUSTOM_YEARMONTH_RANGE(session, year, month, day, numberOfDays):
    print 'ONDEMAND_RECENT(session)'
    print 'year: ' + str(year)
    print 'month: ' + str(month)
    print 'day: ' + str(day)
    print 'numberOfDays: ' + str(numberOfDays)

    startDate = datetime.date(year, month, day)

    # Loop daysback to Build event list
    i = abs(numberOfDays)-1
    while i >= 0:
        # get current date
        nextDate = startDate + datetime.timedelta(i)
        
        # exit on new month
        if nextDate.month != month:
            continue

        # Build events for day
        ONDEMAND_BYDATE_YEARMONTH_DAY(session, nextDate.year, nextDate.month, nextDate.day)

        # Increment loop to avoid TO INFINITY AND BEYOND!!
        i -= 1

    setViewMode()

# Method to draw the archives by team screen
# which scrapes the external source and presents
# a list of team names (or potentially events)
def ONDEMAND_BYTEAM(session):
    print 'ONDEMAND_BYTEAM(session)'

    # Retrieve the teams
    teams = streams.teams(session)

    # Count total number of items for ui
    totalItems = len(teams)
    
    utils.addDir('[ All Teams ]', utils.Mode.ONDEMAND_BYTEAM_LEAGUE, '', None, totalItems, showfanart)

    # Add directories for teams
    league = []
    for team in teams:
        if (league.count(team.league) == 0):
            league.append(team.league)
            params = {
                'league': team.league
            }
            title = team.league
            # Check global league filter
            if enableleaguefilter and leagueFilter.count(team.league) > 0:
                title = '[COLOR red][B]' + title + '[/B][/COLOR]'
            utils.addDir(title, utils.Mode.ONDEMAND_BYTEAM_LEAGUE, '', params, totalItems, showfanart)

    setViewMode()

# Method to draw the archives by league screen
# which scrapes the external source and presents
# a list of team names
def ONDEMAND_BYTEAM_LEAGUE(session, league):
    print 'ONDEMAND_BYTEAM_LEAGUE(session, league)'
    print 'League: ' + str(league)

    # Retrieve the teams
    teams = streams.teams(session, league)

    # Count total number of items for ui
    totalItems = len(teams)

    # Add directories for teams
    for team in teams:
        params = {
            'league': team.league,
            'team': team.name
        }
        title = team.name
        if league == None and team.league != None:
            title = team.league + ': ' + team.name
        if team.name == session.favteam:
            title = '[COLOR red][B]' + title + '[/B][/COLOR]'
        utils.addDir(title, utils.Mode.ONDEMAND_BYTEAM_LEAGUE_TEAM, '', params, totalItems, showfanart)

    setViewMode()

# Method to draw the archives by team screen
# which scrapes the external source and presents
# a list of events for a given team
def ONDEMAND_BYTEAM_LEAGUE_TEAM(session, league, team):
    print 'ONDEMAND_BYTEAM_LEAGUE_TEAM(session, league, team)'
    print 'League: ' + league
    print 'Team: ' + team

    # Retrieve the team events
    events = streams.teamOnDemandEvents(session, streams.Team(team))

    totalItems = len(events)
    for event in events:
        # Check league filter
        if league != None and len(league) > 0 and event.event != None and len(event.event) > 0:
            if not event.event.startswith(league):
                continue # skip to next event

        # Create datetime for string formatting
        parts = event.date.split('/')
        day = int(parts[1])
        month = int(parts[0])
        year = int(parts[2])
        dateStr = ' - ' + datetime.date(year, month, day).strftime('%d %b \'%y')

        homeTeam = event.homeTeam if not shortNames else shortTeamName(event.homeTeam)
        awayTeam = event.awayTeam if not shortNames else shortTeamName(event.awayTeam)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if event.feedType == 'Home Feed':
            matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
        elif event.feedType == 'Away Feed':
            matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
        # Build feedStr
        feedStr = ''
        if event.feedType == 'Home Feed' or event.feedType == 'Away Feed':
            feedStr = ''
        elif event.feedType == None or event.feedType == '':
            feedStr = ' - ' + 'N/A'
        elif event.feedType.endswith(' Feed'):
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType[:len(event.feedType)-5] + '[/COLOR]'
        else:
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType + '[/COLOR]'
        # Build title
        title = event.event + ': ' + matchupStr + dateStr + feedStr

        params = {
            'eventId': event.eventId,
            'feedType': event.feedType,
            'dateStr': dateStr
        }
        icon = createIcon(event.homeTeam,event.awayTeam, event.date, event.feedType)
        utils.addDir(title, utils.Mode.ONDEMAND_BYTEAM_LEAGUE_TEAM_EVENT, '', params, totalItems, showfanart, icon)

    setViewMode()

# Method to draw the highlights screen
# which scrapes the external source and presents
# a list of highlights for a given team and/or date
def HIGHLIGHTSANDCONDENSED_BYTEAM_TEAMDATE(session, team, date):
    print 'HIGHLIGHTSANDCONDENSED_BYTEAM_TEAMDATE(session, team, date)'
    print 'Team: ' + str(team)
    print 'Date: ' + str(date)
    highlights = []
    if showhighlight:
        highlights = streams.dateOnDemandHighlights(session, date, team)
    condensedGames = []
    if showcondensed:
        condensedGames = streams.dateOnDemandCondensed(session, date, team)

    allMedia = highlights + condensedGames
    totalItems = len(allMedia)
    sourceDefs = [('highQualitySrc','HD'), ('medQualitySrc','MD'), ('lowQualitySrc','SD')]
    src = []
    for media in allMedia:
        def feedType(url):
          if '_h_' in url:
            return 'Home Feed'
          elif '_a_' in url:
            return 'Away Feed'
          else:
            return definition

        # Check global league filter
        if enableleaguefilter and leagueFilter.count(media.event) == 0:
            continue
        if team == None or (team == media.homeTeam or team == media.awayTeam):
            # Create datetime for string formatting
            parts = media.date.split('/')
            day = int(parts[1])
            month = int(parts[0])
            year = int(parts[2])
            dateStr = ' - ' + datetime.date(year, month, day).strftime('%d %b \'%y')
            # Build matchup
            homeTeam = media.homeTeam if not shortNames else shortTeamName(media.homeTeam)
            awayTeam = media.awayTeam if not shortNames else shortTeamName(media.awayTeam)
            matchupStr = awayTeam + ' @ ' + homeTeam
            if awayTeam == '' or homeTeam == '': # Indicates special event
                matchupStr = awayTeam + homeTeam
            # Build title
            prefix = 'Highlights' if isinstance(media, streams.Highlight) else 'Condensed'
            title = '[' + prefix + '] ' + media.event + ': ' + matchupStr + dateStr

            def icon(url,suffix):
                return createIcon(media.homeTeam,media.awayTeam, prefix + ' ' + suffix, feedType(url))

            for acc, definition in sourceDefs:
              url = eval('media.' + acc)
              if definition == 'HD' and not utils.urlExists(url):
                url = url.replace('4500','5000')
              if url != None and 'check_back_shortly' not in url and utils.urlExists(url) and src.count(url) == 0:
                utils.addLink((title + ' [' + definition + ']') , url, '', totalItems, showfanart, icon(url,definition))
                src.append(url)


# Method to draw the archive streams by event screen
# which scrapes the external source and presents
# a list of streams for a given stream id
def ONDEMAND_BYTEAM_LEAGUE_TEAM_EVENT(session, eventId, feedType, dateStr):
    print 'ONDEMAND_BYTEAM_LEAGUE_TEAM_EVENT(session, eventId, feedType, dateStr)'
    print 'eventId: ' + eventId
    print 'feedType: ' + str(feedType)
    print 'dateStr: ' + str(dateStr)

    # Build streams
    onDemandStream = streams.onDemandEventStreams(session, eventId, location)

    totalItems = 6 # max possible

    if onDemandStream == None or onDemandStream.streamSet == None:
        return None

    # Build matchup
    homeTeam = onDemandStream.homeTeam if not shortNames else shortTeamName(onDemandStream.homeTeam)
    awayTeam = onDemandStream.awayTeam if not shortNames else shortTeamName(onDemandStream.awayTeam)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if awayTeam == '' or homeTeam == '': # Indicates special event
        matchupStr = awayTeam + homeTeam
    if feedType == 'Home Feed':
        matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
    elif feedType == 'Away Feed':
        matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
    # Build feedStr
    feedStr = ''
    if feedType == 'Home Feed' or feedType == 'Away Feed':
        feedStr = ''
    elif feedType == None or feedType == '':
        feedStr = ' - ' + 'N/A'
    elif feedType.endswith(' Feed'):
        feedStr = ' - ' + '[COLOR lightgreen]' + feedType[:len(feedType)-5] + '[/COLOR]'
    else:
        feedStr = ' - ' + '[COLOR lightgreen]' + feedType + '[/COLOR]'
    # Build title
    title = onDemandStream.event + ': ' + matchupStr + str(dateStr)
    def icon(suffix):
        header = suffix
        return createIcon(onDemandStream.homeTeam,onDemandStream.awayTeam, header, feedType)

    if istream and ondemandresolution != 'SD Only' and onDemandStream.streamSet['istream.hd'] != None:
        suffix = ' [iStream HD]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.hd'], '', totalItems, showfanart, icon(' [iStream HD]'))
    if istream and ondemandresolution != 'HD Only' and onDemandStream.streamSet['istream.sd'] != None:
        suffix = ' [iStream SD]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [iStream SD]'))
    if istream and ondemandresolution == 'All' and onDemandStream.streamSet['istream'] != None and onDemandStream.streamSet['istream'] != onDemandStream.streamSet['istream.hd']:
        suffix = ' [iStream]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['istream'], '', totalItems, showfanart, icon(' [iStream]'))
    if hls and onDemandStream.streamSet['hls'] != None:
        if 'HD.' in onDemandStream.streamSet['hls'] and ondemandresolution != 'SD Only':
            suffix = ' [HLS HD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['hls'], '', totalItems, showfanart, icon(' [HLS HD]'))
        elif 'SD.' in onDemandStream.streamSet['hls'] and ondemandresolution != 'HD Only':
            suffix = ' [HLS SD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['hls'], '', totalItems, showfanart, icon(' [HLS SD]'))
        else:
            suffix = ' [HLS]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['hls'], '', totalItems, showfanart, icon(' [HLS]'))
    if hls and onDemandStream.streamSet['hls.sd'] != None and ondemandresolution != 'HD Only':
        suffix = ' [HLS SD]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['hls.sd'], '', totalItems, showfanart, icon(' [HLS SD]'))
    if flash and onDemandStream.streamSet['flash'] != None:
        if 'HD.' in onDemandStream.streamSet['flash'] and ondemandresolution != 'SD Only':
            suffix = ' [Flash HD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [Flash HD]'))
        elif 'SD.' in onDemandStream.streamSet['flash'] and ondemandresolution != 'HD Only':
            suffix = ' [Flash SD]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [Flash SD]'))
        else:
            suffix = ' [Flash]' + feedStr
            utils.addLink(title + suffix, onDemandStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(' [Flash]'))
    if wmv and onDemandStream.streamSet['wmv'] != None:
        suffix = ' [WMV]' + feedStr
        utils.addLink(title + suffix, onDemandStream.streamSet['wmv'], '', totalItems, showfanart, icon(' [WMV]'))

    try:
        if feedType == 'Away Feed':
          team = onDemandStream.awayTeam
        else:
          team = onDemandStream.homeTeam
        try:
          dStr = datetime.datetime.strptime(dateStr, ' - %d %b \'%y')
        except TypeError:
          dStr = datetime.datetime(*(time.strptime(dateStr, ' - %d %b \'%y')[0:6]))
        HIGHLIGHTSANDCONDENSED_BYTEAM_TEAMDATE(session, team, dStr)
    except Exception as e:
        print 'Error initializing onDemand by team/league: ' + str(e)

    setViewMode()

# Method to draw the live screen
# which scrapes the external source and presents
# a list of current day events
def LIVE(session):
    print 'LIVE(session)'

    # Find live events
    events = streams.liveEvents(session)

    totalItems = len(events) + 2

    if totalItems > 13:
        # Add refresh button
        refreshParams = {
            'refresh': 'True'
        }
        utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    buildLiveEvents(session, events, totalItems, 1) # favorite team
    buildLiveEvents(session, events, totalItems, 2) # live/coming soon
    buildLiveEvents(session, events, totalItems, 3) # final

    # Add refresh button
    refreshParams = {
        'refresh': 'True'
    }
    utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    setViewMode()

# Method to build live events
# @param filter 0 = ALL, 1 = favorite only, 2 = live/comingSoon only, 3 = final only
def buildLiveEvents(session, events, totalItems, filter):
    for event in events:
        # skip condition 1
        if filter == 1 and not (event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue
        # skip condition 2
        if filter == 2 and (event.isFinal or event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue
        # skip condition 3
        elif filter == 3 and (not event.isFinal or event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue

        # Check global league filter
        if enableleaguefilter and leagueFilter.count(event.event) == 0:
            continue

        # Build prefix
        prefix = '[COLOR blue][B][LIVE][/B][/COLOR] '
        if event.isFuture:
            prefix = '[COLOR lightblue][Coming Soon][/COLOR] '
        elif event.isFinal:
            prefix = '[Final] '
        # Build matchup
        homeTeam = event.homeTeam if not shortNames else shortTeamName(event.homeTeam)
        awayTeam = event.awayTeam if not shortNames else shortTeamName(event.awayTeam)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if event.feedType == 'Home Feed':
            matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
        elif event.feedType == 'Away Feed':
            matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
        # Build feedStr
        feedStr = ''
        if event.feedType == 'Home Feed' or event.feedType == 'Away Feed':
            feedStr = ''
        elif event.feedType == None or event.feedType == '':
            feedStr = ' - ' + 'N/A'
        elif event.feedType.endswith(' Feed'):
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType[:len(event.feedType)-5] + '[/COLOR]'
        else:
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType + '[/COLOR]'
        # Build period
        periodStr = ''
        if event.period == 'HALF - ':
            periodStr = ' - HALF'
        elif event.period != '':
            periodStr = ' - ' + event.period if event.period != None else ''
        # Build score
        homeScore = event.homeScore if event.homeScore != None and len(event.homeScore)>0 else '0'
        awayScore = event.awayScore if event.awayScore != None and len(event.awayScore)>0 else '0'
        scoreStr = ' - ' + awayScore + '-' + homeScore if showscores and not event.isFuture else ''
        # Build start time
        startTimeStr = ''
        if periodStr == '':
            startTimeStr = ' - ' + event.startTime
        # Build title
        title = prefix + event.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr + feedStr
        if event.homeTeam == session.favteam or event.awayTeam == session.favteam:
            title = prefix + '[COLOR red][B]' + event.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr + feedStr + '[/B][/COLOR]'

        if event.isFinal:
            now = streams.adjustedDateTime()
            team = event.homeTeam if event.homeTeam != None and event.homeTeam != '' else event.awayTeam
            params = {
                'year': str(now.year),
                'month': str(now.month),
                'day': str(now.day),
                'team': str(team),
                'feedType': str(event.feedType)
            }
            icon = createIcon(event.homeTeam,event.awayTeam, "Final", event.feedType, homeScore, awayScore)
            utils.addDir(title, utils.Mode.LIVE_FINALEVENT, '', params, totalItems, showfanart, icon)
        elif event.isFuture:
            refreshParams = {
                'refresh': 'True'
            }
            icon = createIcon(event.homeTeam,event.awayTeam, event.startTime, event.feedType, homeScore, awayScore)
            utils.addDir(title, mode, '', refreshParams, totalItems, showfanart, icon)
        else:
            params = {
                'eventId': event.eventId
            }
            icon = createIcon(event.homeTeam,event.awayTeam, event.period, event.feedType, homeScore, awayScore)
            utils.addDir(title, utils.Mode.LIVE_EVENT, '', params, totalItems, showfanart, icon)

# Method to draw the live streams screen
# which scrapes the external source and presents
# a list of current day event streams for an event id
def LIVE_EVENT(session, eventId):
    print 'LIVE_EVENT(session, eventId)'
    print 'eventId: ' + eventId

    # Build streams
    liveStream = streams.liveEventStreams(session, eventId, location)

    totalItems = 15 # max possible

    if liveStream == None or liveStream.streamSet == None:
        return None

    # Build prefix
    prefix = '[COLOR blue][B][LIVE][/B][/COLOR] '
    # Build matchup
    homeTeam = liveStream.homeTeam if not shortNames else shortTeamName(liveStream.homeTeam)
    awayTeam = liveStream.awayTeam if not shortNames else shortTeamName(liveStream.awayTeam)
    matchupStr = awayTeam + ' @ ' + homeTeam
    if awayTeam == '' or homeTeam == '': #indicates special event
        matchupStr = awayTeam + homeTeam
    if liveStream.feedType == 'Home Feed':
        matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
    elif liveStream.feedType == 'Away Feed':
        matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
    # Build feedStr
    feedStr = ''
    if liveStream.feedType == 'Home Feed' or liveStream.feedType == 'Away Feed':
        feedStr = ''
    elif liveStream.feedType == None or liveStream.feedType == '':
        feedStr = ' - ' + 'N/A'
    elif liveStream.feedType.endswith(' Feed'):
        feedStr = ' - ' + '[COLOR lightgreen]' + liveStream.feedType[:len(liveStream.feedType)-5] + '[/COLOR]'
    else:
        feedStr = ' - ' + '[COLOR lightgreen]' + liveStream.feedType + '[/COLOR]'
    # Build period
    periodStr = ''
    if liveStream.period == 'HALF - ':
        periodStr = ' - HALF'
    elif liveStream.period != '':
        periodStr = ' - ' + liveStream.period if liveStream.period != None else ''
    # Build score
    homeScore = liveStream.homeScore if liveStream.homeScore != None and len(liveStream.homeScore)>0 else '0'
    awayScore = liveStream.awayScore if liveStream.awayScore != None and len(liveStream.awayScore)>0 else '0'
    scoreStr = ' - ' + awayScore + '-' + homeScore if showscores else ''
    # Build start time
    startTimeStr = ''
    if periodStr == '':
        startTimeStr = ' - ' + liveStream.startTime
    # Build title
    title = prefix + liveStream.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr
    # Add links
    def icon(suffix):
        return createIcon(liveStream.homeTeam,liveStream.awayTeam, suffix, liveStream.feedType, homeScore, awayScore)
    if truelive and liveresolution != 'SD Only' and liveresolution != 'MD Only' and liveStream.streamSet['truelive.hd'] != None:
        suffix = ' [TrueLive HD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.hd'], '', totalItems, showfanart, icon(suffix))
    if truelive and liveresolution != 'SD Only' and liveresolution != 'HD Only' and liveStream.streamSet['truelive.md'] != None:
        suffix = ' [TrueLive MD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.md'], '', totalItems, showfanart, icon(suffix))
    if truelive and liveresolution != 'MD Only' and liveresolution != 'HD Only' and liveStream.streamSet['truelive.sd'] != None:
        suffix = ' [TrueLive SD]'
        utils.addLink(title + suffix, liveStream.streamSet['truelive.sd'], '', totalItems, showfanart, icon(suffix))
    if istream and liveresolution != 'SD Only' and liveresolution != 'MD Only' and liveStream.streamSet['istream.hd'] != None:
        suffix = ' [iStream HD]'
        utils.addLink(title + suffix, liveStream.streamSet['istream.hd'], '', totalItems, showfanart, icon(suffix))
    if istream and liveresolution != 'SD Only' and liveresolution != 'HD Only' and liveStream.streamSet['istream.md'] != None:
        suffix = ' [iStream MD]'
        utils.addLink(title + suffix, liveStream.streamSet['istream.md'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(suffix))
    if istream and liveresolution != 'HD Only' and liveresolution != 'MD Only' and liveStream.streamSet['istream.sd'] != None:
        suffix = ' [iStream SD]'
        utils.addLink(title + suffix, liveStream.streamSet['istream.sd'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(suffix))
    if istream and liveresolution == 'All' and liveStream.streamSet['istream'] != None and liveStream.streamSet['istream'] != liveStream.streamSet['istream.hd']:
        suffix = ' [iStream]'
        utils.addLink(title + suffix, liveStream.streamSet['istream'], '', totalItems, showfanart, icon(suffix))
    if flash and liveStream.streamSet['flash'] != None:
        if 'HD.' in liveStream.streamSet['flash'] and liveresolution != 'SD Only' and liveresolution != 'MD Only':
            suffix = ' [Flash HD]'
            utils.addLink(title + suffix, liveStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(suffix))
        if 'MD.' in liveStream.streamSet['flash'] and liveresolution != 'SD Only' and liveresolution != 'HD Only':
            suffix = ' [Flash MD]'
            utils.addLink(title + suffix, liveStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(suffix))
        elif 'SD.' in liveStream.streamSet['flash'] and liveresolution != 'MD Only' and liveresolution != 'HD Only':
            suffix = ' [Flash SD]'
            utils.addLink(title + suffix, liveStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(suffix))
        else:
            suffix = ' [Flash]'
            utils.addLink(title + suffix, liveStream.streamSet['flash'].replace('f4m', 'm3u8'), '', totalItems, showfanart, icon(suffix))
    if wmv and liveStream.streamSet['wmv'] != None:
        suffix = ' [WMV]'
        utils.addLink(title + suffix, liveStream.streamSet['wmv'], '', totalItems, showfanart, icon(suffix))
    if dvr and liveresolution != 'SD Only' and liveresolution != 'MD Only' and liveStream.streamSet['nondvrhd'] != None:
        suffix = ' [NonDVR HD]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvrhd'], '', totalItems, showfanart, icon(suffix))
    if dvr and liveresolution != 'SD Only' and liveresolution != 'HD Only' and liveStream.streamSet['nondvrmd'] != None:
        suffix = ' [NonDVR MD]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvrmd'], '', totalItems, showfanart, icon(suffix))
    if dvr and liveresolution != 'MD Only' and liveresolution != 'HD Only' and liveStream.streamSet['nondvrsd'] != None:
        suffix = ' [NonDVR SD]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvrsd'], '', totalItems, showfanart, icon(suffix))
    if dvr and liveresolution == 'All' and liveStream.streamSet['nondvr'] != None:
        suffix = ' [NonDVR]'
        utils.addLink(title + suffix, liveStream.streamSet['nondvr'], '', totalItems, showfanart, icon(suffix))

    # Add refresh button
    refreshParams = {
        'refresh': 'True',
        'eventId': eventId
    }
    utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    setViewMode()

# Method to draw the live streams screen
# which scrapes the external source and presents
# a list of current day event streams for an event id
def LIVE_FINALEVENT(session, year, month, day, team, feedType):
    print 'LIVE_FINALEVENT(session, year, month, day, feedType)'
    print 'Year: ' + str(year)
    print 'Month: ' + str(month)
    print 'Day: ' + str(day)
    print 'Team: ' + team
    print 'FeedType: ' + str(feedType)

    # Retrieve the events
    date = datetime.date(year, month, day)
    try:
        events = streams.dateOnDemandEvents(session, date, showScoresOnDemand)
    except Exception as e:
        print 'Warning:  No events found for date: ' + str(date) + ' Msg: ' + str(e)
        return

    # Search for matching event to display matching on-demand streams
    for event in events:
        print str(event.feedType)
        if (event.homeTeam == team or event.awayTeam == team) and (not(feedType == 'Home Feed' or feedType == 'Away Feed') or feedType == event.feedType):
            # Create datetime for string formatting
            parts = event.date.split('/')
            day = int(parts[1])
            month = int(parts[0])
            year = int(parts[2])
            dateStr = ' - ' + datetime.date(year, month, day).strftime('%d %b \'%y')

            ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT(session, event.eventId, event.feedType, dateStr)

# Method to draw the live screen
# which scrapes the external source and presents
# a list of current day events
def LIVEEVENT(session):
    print 'LIVEEVENT(session)'

    # Find live events
    events = streams.liveEvents(session)

    totalItems = len(events) + 2

    if totalItems > 13:
        # Add refresh button
        refreshParams = {
            'refresh': 'True'
        }
        utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    buildLiveStreams(session, events, totalItems, 1) # favorite team
    buildLiveStreams(session, events, totalItems, 2) # live/coming soon
    buildLiveStreams(session, events, totalItems, 3) # final

    # Add refresh button
    refreshParams = {
        'refresh': 'True'
    }
    utils.addDir(addon.getLocalizedString(100015), mode, '', refreshParams, totalItems, showfanart)

    setViewMode()

# Method to build live event streams
# @param filter 0 = ALL, 1 = favorite only, 2 = live/comingSoon only, 3 = final only
def buildLiveStreams(session, events, totalItems, filter):
    for event in events:
        # skip condition 1
        if filter == 1 and not (event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue
        # skip condition 2
        if filter == 2 and (event.isFinal or event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue
        # skip condition 3
        elif filter == 3 and (not event.isFinal or event.homeTeam == session.favteam or event.awayTeam == session.favteam):
            continue

        # Check global league filter
        if enableleaguefilter and leagueFilter.count(event.event) == 0:
            continue
        
        # Build prefix
        prefix = '[COLOR blue][B][LIVE][/B][/COLOR] '
        if event.isFuture:
            prefix = '[COLOR lightblue][Coming Soon][/COLOR] '
        elif event.isFinal:
            prefix = '[Final] '
        # Build matchup
        homeTeam = event.homeTeam if not shortNames else shortTeamName(event.homeTeam)
        awayTeam = event.awayTeam if not shortNames else shortTeamName(event.awayTeam)
        matchupStr = awayTeam + ' @ ' + homeTeam
        if awayTeam == '' or homeTeam == '': # Indicates special event
            matchupStr = awayTeam + homeTeam
        if event.feedType == 'Home Feed':
            matchupStr = awayTeam + ' @ ' + '[COLOR lightgreen]' + homeTeam + '[/COLOR]*'
        elif event.feedType == 'Away Feed':
            matchupStr = '[COLOR lightgreen]' + awayTeam + '[/COLOR]*' + ' @ ' + homeTeam
        # Build feedStr
        feedStr = ''
        if event.feedType == 'Home Feed' or event.feedType == 'Away Feed':
            feedStr = ''
        elif event.feedType == None or event.feedType == '':
            feedStr = ' - ' + 'N/A'
        elif event.feedType.endswith(' Feed'):
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType[:len(event.feedType)-5] + '[/COLOR]'
        else:
            feedStr = ' - ' + '[COLOR lightgreen]' + event.feedType + '[/COLOR]'
        # Build period
        periodStr = ''
        if event.period == 'HALF - ':
            periodStr = ' - HALF'
        elif event.period != '':
            periodStr = ' - ' + event.period if event.period != None else ''
        # Build score
        homeScore = event.homeScore if event.homeScore != None and len(event.homeScore)>0 else '0'
        awayScore = event.awayScore if event.awayScore != None and len(event.awayScore)>0 else '0'
        scoreStr = ' - ' + awayScore + '-' + homeScore if showscores and not event.isFuture else ''
        # Build start time
        startTimeStr = ''
        if periodStr == '':
            startTimeStr = ' - ' + event.startTime
        # Build title
        title = prefix + event.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr + feedStr
        # Build icon
        if event.homeTeam == session.favteam or event.awayTeam == session.favteam:
            title = prefix + '[COLOR red][B]' + event.event + ': ' + matchupStr + scoreStr + periodStr + startTimeStr + feedStr + '[/B][/COLOR]'

        if event.isFinal:
            now = streams.adjustedDateTime()
            team = event.homeTeam if event.homeTeam != None and event.homeTeam != '' else event.awayTeam
            params = {
                'year': str(now.year),
                'month': str(now.month),
                'day': str(now.day),
                'team': str(team),
                'feedType': str(event.feedType)
            }
            icon = createIcon(event.homeTeam,event.awayTeam, "Final", event.feedType, homeScore, awayScore) 
            utils.addDir(title, utils.Mode.LIVE_FINALEVENT, '', params, totalItems, showfanart, icon)
        elif event.isFuture:
            refreshParams = {
                'refresh': 'True'
            }
            icon = createIcon(event.homeTeam,event.awayTeam, event.startTime, event.feedType, homeScore,awayScore) 
            utils.addDir(title, mode, '', refreshParams, totalItems, showfanart, icon)
        else:
            # Add links
            def icon(suffix):
                header = event.period + ' - ' + suffix
                return createIcon(event.homeTeam,event.awayTeam, header, event.feedType, homeScore, awayScore) 
            if truelive and liveresolution != 'SD Only' and liveresolution != 'MD Only' and event.trueLiveHD != None:
                suffix = ' [TrueLive HD]'
                utils.addLink(title + suffix, event.trueLiveHD, '', totalItems, showfanart, icon(suffix))
            if truelive and liveresolution != 'SD Only' and liveresolution != 'HD Only' and event.trueLiveMD != None:
                suffix = ' [TrueLive MD]'
                utils.addLink(title + suffix, event.trueLiveMD, '', totalItems, showfanart, icon(suffix))
            if truelive and liveresolution != 'MD Only' and liveresolution != 'HD Only' and event.trueLiveSD != None:
                suffix = ' [TrueLive SD]'
                utils.addLink(title + suffix, event.trueLiveSD, '', totalItems, showfanart, icon(suffix))
            if istream and liveresolution != 'SD Only' and liveresolution != 'MD Only' and event.hdUrl != None:
                suffix = ' [iStream HD]'
                utils.addLink(title + suffix, event.hdUrl, '', totalItems, showfanart, icon(suffix))
            if istream and liveresolution != 'SD Only' and liveresolution != 'HD Only' and event.mdUrl != None:
                suffix = ' [iStream MD]'
                utils.addLink(title + suffix, event.mdUrl, '', totalItems, showfanart, icon(suffix))
            if istream and liveresolution != 'HD Only' and liveresolution != 'MD Only' and event.sdUrl != None:
                suffix = ' [iStream SD]'
                utils.addLink(title + suffix, event.sdUrl, '', totalItems, showfanart, icon(suffix))
            if istream and liveresolution == 'All' and event.srcUrl != None:
                suffix = ' [iStream]'
                utils.addLink(title + suffix, event.srcUrl, '', totalItems, showfanart, icon(suffix))

# Method to populate recent events
# which scrapes the external source and presents
# a list of recent days events
def ONDEMAND_RECENT(session):
    print 'ONDEMAND_RECENT(session)'
    print 'daysback: ' + daysback

    # Check disable option
    if daysback == 'Disable':
        return

    # Loop daysback to Build event list
    i = 0
    while i <= int(daysback):
        # get current date
        recentDate = streams.getRecentDateTime(i)

        # Build events for day
        ONDEMAND_BYDATE_YEARMONTH_DAY(session, recentDate.year, recentDate.month, recentDate.day)

        # Increment loop to avoid TO INFINITY AND BEYOND!!
        i += 1

# Set view mode according to addon settings
def setViewMode():
    if viewmode != None:
        try:
            xbmc.executebuiltin('Container.SetViewMode(' + viewmode + ')')
        except Exception as e:
            print 'Warning:  Unable to set view mode:  ' + str(e)

# Load general settings
username = addon.getSetting('username')
password = addon.getSetting('password')
ondemandresolution = addon.getSetting('ondemandresolution')
liveresolution = addon.getSetting('liveresolution')
shortNames = addon.getSetting('shortnames')
shortNames = shortNames != None and shortNames.lower() == 'true'
showicons = addon.getSetting('showicons')
showicons = showicons != None and showicons.lower() == 'true'
showscores = addon.getSetting('showscores')
showscores = showscores != None and showscores.lower() == 'true'
showaltlive = addon.getSetting('showaltlive')
showaltlive = showaltlive != None and showaltlive.lower() == 'true'
showfanart = addon.getSetting('showfanart')
showfanart = showfanart != None and showfanart.lower() == 'true'
showScoresOnDemand = addon.getSetting('showscoresondemand')
showScoresOnDemand = showScoresOnDemand != None and showScoresOnDemand.lower() == 'true'
showhighlight = addon.getSetting('showhighlight')
showhighlight = showhighlight != None and showhighlight.lower() == 'true'
showcondensed = addon.getSetting('showcondensed')
showcondensed = showcondensed != None and showcondensed.lower() == 'true'
viewmode = addon.getSetting('viewmode')
if viewmode != None and viewmode == 'Big List':
    viewmode = '51'
elif viewmode != None and viewmode == 'List':
    viewmode = '50'
elif viewmode != None and viewmode == 'Thumbnail':
    viewmode = '500'
else: # Default
    viewmode = None

# Define league filter
enableleaguefilter = addon.getSetting('enableleaguefilter')
enableleaguefilter = enableleaguefilter != None and enableleaguefilter.lower() == 'true'
leagueFilter = []
print 'League Filter: ' + str(leagueFilter)

# Load stream settings
istream = addon.getSetting('istream')
istream = istream != None and istream.lower() == 'true'
flash = addon.getSetting('flash')
flash = flash != None and flash.lower() == 'true'
wmv = 'True'
truelive = addon.getSetting('truelive')
truelive = truelive != None and truelive.lower() == 'true'
dvr = addon.getSetting('dvr')
dvr = dvr != None and dvr.lower() == 'true'
hls = addon.getSetting('hls')
hls = hls != None and hls.lower() == 'true'
location = addon.getSetting('location')
if location != None and location.lower() == 'auto':
    location = None # Location is special, if it is 'Auto' then it is None
daysback = addon.getSetting('daysback')

# Load the directory params
params = utils.getParams()

# Print directory params for debugging
for k, v in params.iteritems():
    pass # print k + ': ' + v

# Parse mode
mode = utils.parseParamInt(params, 'mode')

# Parse other variables
year = utils.parseParamInt(params, 'year')
month = utils.parseParamInt(params, 'month')
day = utils.parseParamInt(params, 'day')
numberOfDays = utils.parseParamInt(params, 'numberOfDays')
league = utils.parseParamString(params, 'league')
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
    print 'Stream unavailable, please check streams.com for wmv stream availability.'
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
        session = streams.login(username, password)
    except streams.ApiException as e:
        print 'Error logging into streams.com account: ' + str(e)

# Check login status and membership status
if session == None:
    mode = utils.Mode.HOME
    print 'The streams.com session was null, login failed'
    utils.showMessage(addon.getLocalizedString(100011), addon.getLocalizedString(100012))
elif session.isPremium == False:
    mode = utils.Mode.HOME
    print 'The streams.com account membership is non-premium, a paid for account is required'
    utils.showMessage(addon.getLocalizedString(100013), addon.getLocalizedString(100014))
else:
    # Attempt to create IP exception
    try:
        print 'Attempting to generate IP exception'
        ipException = streams.ipException(session)
    except Exception as e:
        print 'Error creating an ip exception: ' + str(e)
        utils.showMessage(addon.getLocalizedString(100018), addon.getLocalizedString(100019))

iconCleanup()

# Invoke mode function
if mode == None or mode == utils.Mode.HOME:
    HOME()
    updateListing = refresh
    cacheToDisc = False
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
elif mode == utils.Mode.ONDEMAND_BYDATE_CUSTOM:
    ONDEMAND_BYDATE_CUSTOM(session)
elif mode == utils.Mode.ONDEMAND_BYDATE_CUSTOM_YEARMONTH:
    ONDEMAND_BYDATE_CUSTOM_YEARMONTH(session, year, month)
elif mode == utils.Mode.ONDEMAND_BYDATE_CUSTOM_YEARMONTH_RANGE:
    ONDEMAND_BYDATE_CUSTOM_YEARMONTH_RANGE(session, year, month, day, numberOfDays)
elif mode == utils.Mode.ONDEMAND_BYTEAM:
    ONDEMAND_BYTEAM(session)
elif mode == utils.Mode.ONDEMAND_BYTEAM_LEAGUE:
    ONDEMAND_BYTEAM_LEAGUE(session,league)
elif mode == utils.Mode.ONDEMAND_BYTEAM_LEAGUE_TEAM:
    ONDEMAND_BYTEAM_LEAGUE_TEAM(session, league, team)
elif mode == utils.Mode.ONDEMAND_BYTEAM_LEAGUE_TEAM_EVENT:
    ONDEMAND_BYTEAM_LEAGUE_TEAM_EVENT(session, eventId, feedType, dateStr)
elif mode == utils.Mode.LIVE:
    LIVE(session)
    updateListing = refresh
    cacheToDisc = False
elif mode == utils.Mode.LIVE_EVENT:
    LIVE_EVENT(session, eventId)
    updateListing = refresh
    cacheToDisc = False
elif mode == utils.Mode.LIVE_FINALEVENT:
    LIVE_FINALEVENT(session, year, month, day, team, feedType)
elif mode == utils.Mode.LIVEEVENT:
    LIVEEVENT(session)
    updateListing = refresh
    cacheToDisc = False

# Signal end of directory
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc = cacheToDisc, updateListing = updateListing)
