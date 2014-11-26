import xbmcgui, xbmcplugin
import urllib
import sys

# xbmc-ball-streams
# author: craig mcnicholas, andrew wise
# contact: craig@designdotworks.co.uk, zergcollision@gmail.com

# Represents an enumeration for application modes
class Mode:
    HOME = 1
    ONDEMAND = 2
    ONDEMAND_BYDATE = 3
    ONDEMAND_BYDATE_YEARMONTH = 4
    ONDEMAND_BYDATE_YEARMONTH_DAY = 5
    ONDEMAND_BYDATE_YEARMONTH_DAY_EVENT = 6
    ONDEMAND_BYDATE_CUSTOM = 7
    ONDEMAND_BYDATE_CUSTOM_YEARMONTH = 8
    ONDEMAND_BYDATE_CUSTOM_YEARMONTH_RANGE = 9
    ONDEMAND_BYTEAM = 10
    ONDEMAND_BYTEAM_LEAGUE = 11
    ONDEMAND_BYTEAM_LEAGUE_TEAM = 12
    ONDEMAND_BYTEAM_LEAGUE_TEAM_EVENT = 13
    LIVE = 14
    LIVE_EVENT = 15
    LIVE_FINALEVENT = 16
    LIVEEVENT = 17

# Method to get the parameters for the current view
# @return an array of parameters
def getParams():
    param = {}
    paramString = sys.argv[2]
    if len(paramString) >= 2:
        cleanedParams = paramString.replace('?', '')
        if (paramString[len(paramString) - 1] == '/'):
            paramString = paramString[0 : len(paramString) - 2]
        pairsOfParams = cleanedParams.split('&')
        for i in range(len(pairsOfParams)):
            splitParams = pairsOfParams[i].split('=')
            if (len(splitParams)) == 2:
                param[splitParams[0]] = splitParams[1]
    return param

# Method to parse a parameter as an int
# @param params the parameters to parse
# @key the key name of the parameter to parse
# @return the int value of the parameter or None
def parseParamInt(params, key):
    value = None
    try:
        value = int(params[key])
    except:
        pass
    return value

# Method to parse a parameter as a string
# @param params the parameters to parse
# @key the key name of the parameter to parse
# @return the string value of the parameter or None
def parseParamString(params, key):
    value = None
    try:
        value = urllib.unquote_plus(params[key])
    except:
        pass
    return value

# Method to add a link to the xbmc gui
# @param name the name of the link to show
# @param url the url of the link
# @param image the image to display as the thumbnail
# @param totalItems [optional] the total number of items to add to show progress
# @return a flag indicating success
def addLink(name, url, image, totalItems = None, showfanart = None):
    ok = True
    item = xbmcgui.ListItem(name, iconImage = 'DefaultVideo.png', thumbnailImage = 'special://home/addons/plugin.video.xbmc-ball-streams-frodo/Basketball-Ball-icon.png')
    item.setInfo(type = 'Video', infoLabels = { 'Title': name })
    if showfanart:
        item.setProperty( "Fanart_Image", 'special://home/addons/plugin.video.xbmc-ball-streams-frodo/fanart.jpg' )
    if totalItems == None:
        ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = item)
    else:
        ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = item, totalItems = totalItems)
    return ok

# Method to add a directory to the xbmc gui
# @param name the name of the directory to show
# @param mode the mode number
# @param image the image to display as the thumbnail
# @param params a dictionary of params to append
# @param totalItems [optional] the total number of items to add to show progress
# @return a flag indicating success
def addDir(name, mode, image, params, totalItems = None, showfanart = None):
    url = sys.argv[0] + "?mode=" + str(mode)
    if params != None:
        for k, v in params.iteritems():
            url += '&' + k + '=' + urllib.quote_plus(v)
    ok = True
    item = xbmcgui.ListItem(name, iconImage = 'DefaultFolder.png', thumbnailImage = 'special://home/addons/plugin.video.xbmc-ball-streams-frodo/Basketball-Ball-icon.png')
    item.setInfo(type = 'Video', infoLabels = { 'Title': name })
    if showfanart:
        item.setProperty( "Fanart_Image", 'special://home/addons/plugin.video.xbmc-ball-streams-frodo/fanart.jpg' )
    if totalItems == None:
        ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = item, isFolder = True)
    else:
        ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = item, isFolder = True, totalItems = totalItems)
    return ok

# Method to show a dialog message
# @param title the title of the dialog
# @param message the message of the dialog
def showMessage(title, message):
    dialog = xbmcgui.Dialog()
    ok = dialog.ok(title, message)
