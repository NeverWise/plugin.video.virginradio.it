#!/usr/bin/python
# -*- coding: utf-8 -*-
# Version 1.0.0 (18/08/2013)
# Virgin Radio (Style Rock Television)
# <description>
# By NeverWise
# <email>
# <web>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#######################################################################
import sys, os, re, xbmcgui, xbmcplugin, tools#, datetime


def getVirginResponse(link):
  return tools.getResponseUrl('http://www.virginradio.it' + link)


def getStreamParam(quality):
  response = tools.getResponseUrl('http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml')
  serverParam = re.compile('<serverPath value="auto\|(.+?)\|(.+?)"/>').findall(response)
  stream = re.compile('<rate n="' + str(quality) + '" streamName="(.+?)" bitrate="').findall(response)
  return [serverParam[0][0], serverParam[0][1], stream[0]]


def isExtensionNumber(extension):
  result = False
  try:
    int(extension)
    result = True
  except:
    pass
  return result


def normalizeImageUrl(img):
  extension = img[-3:]
  if extension[0] == '.':
    isNumber = isExtensionNumber(extension[-2:])
  else:
    isNumber = isExtensionNumber(extension)

  if isNumber:
    img = img.replace(extension, '.jpg')

  return img


def showNextPageDir(inputString, pattern, idParams):
  nextPage = re.compile(pattern).findall(inputString)
  if len(nextPage) > 0:
    title = tools.getTranslation(idPlugin, 30005) + ' ' + tools.normalizeText(nextPage[0][1]) + ' >' # Pagina.
    tools.addDir(handle, title, '', '', 'video', { 'title' : title, 'plot' : '', 'duration' : -1, 'director' : '' }, { 'id' : idParams, 'page' : nextPage[0][0] })


def getWebRadio(url):
  response = getVirginResponse(url)
  rList = re.compile('<img width="70" height="70" src="(.+?)".+?/> <a href="(.+?)">(.+?)</a> <p><p>(.+?)</p>').findall(response)
  for img, link, title, descr in rList:
    img = img.replace('-70x70', '')
    title = tools.normalizeText(title)
    tools.addDir(handle, title, img, '', 'music', { 'title' : title, 'plot' : tools.normalizeText(descr), 'duration' : -1, 'director' : '' }, { 'id' : 'r', 'page' : link.replace('http://www.virginradio.it', '') })
  showNextPageDir(response, "<span class='page-numbers current'>.+?</span><a class='page-numbers' href='(.+?)'>(.+?)</a>", 't')
  xbmcplugin.endOfDirectory(handle)


# Entry point.
#startTime = datetime.datetime.now()

handle = int(sys.argv[1])
params = tools.urlParametersToDict(sys.argv[2])
idPlugin = 'plugin.virginradio'

if params.get('content_type') is None: # Visualizzo i video della sezione.
  response = getVirginResponse(params['page'])
  if params['id'] == 's': # Video di una categoria.
    videos = re.compile('<figure> <a href="(.+?)" title=".+?">.+?<img src="(.+?)".+?> </a> </figure> <header> <a href=".+?" title=".+?"> <h3>(.+?)</h3> </a> </header> <div.+?>(.+?)</div>').findall(response)
    for link, img, title, descr in videos:
      img = normalizeImageUrl(img)
      descr = tools.normalizeText(descr)
      title = tools.normalizeText(title)
      tools.addDir(handle, title, img, '', 'video', { 'title' : title, 'plot' : descr, 'duration' : -1, 'director' : '' }, { 'id' : 'v', 'page' : link })
    showNextPageDir(response, '[0-9]+ <a rel="nofollow" href="(.+?)">(.+?)</a>', 's')
    xbmcplugin.endOfDirectory(handle)
  elif params['id'] == 'v': # Riproduzione di un video.
    if response.find('<title>Virgin Radio Tv</title>') == -1: # Per evitare i video non funzionanti.
      title = tools.normalizeText(re.compile('<meta property="og:title" content="(.+?)"').findall(response)[0])
      img = normalizeImageUrl(re.compile('<meta property="og:image" content="(.+?)"').findall(response)[0])
      descr = re.compile('<meta property="og:description" content="(.+?)"').findall(response)[0]
      play = re.compile('clip:\{"url":"(.+?):(.+?)"').findall(response)
      server = re.compile('"hddn":\{"url":"(.+?)","netConnectionUrl":"rtmp:\\\/\\\/(.+?)\\\/(.+?)"\},"').findall(response)
      playBS = play[0][1].replace('\\', '')
      li = tools.createListItem(title, img, '', 'video', { 'title' : title, 'plot' : tools.normalizeText(descr), 'duration' : -1, 'director' : '' })
      xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream('rtmp://' + server[0][1] + ':1935/' + server[0][2] + '/' + playBS + ' app=' + server[0][2] + ' playpath=' + play[0][0] + ':' + playBS + ' swfUrl=' + server[0][0].replace('\\', '') + ' pageURL=http://www.virginradio.it swfVfy=true live=false flashVer=LNX 10,1,82,76', li)
    else: # Messaggio d'errore "Video non disponibile".
      xbmcgui.Dialog().ok('Virgin Radio', tools.getTranslation(idPlugin, 30006))
  elif params['id'] == 't':
    getWebRadio(params['page'])
  elif params['id'] == 'r': # Riproduzione di una radio.
    title = tools.normalizeText(re.compile('<div class="seo-strip clearfix"> <header> <h1>(.+?)</h1>').findall(response)[0])
    img = re.compile("<meta property='og:image' content='(.+?)'").findall(response)[0]
    descr = re.compile("<meta property='og:description' content='(.+?)'").findall(response)[0]
    streamParam = getStreamParam(1)
    params = re.compile('<param name="movie" value="http://www\.virginradio\.it/wp-content/themes/wirgin/corePlayerStreamingVisible2013_counter_VIRGIN\.swf\?streamRadio=(.+?)&amp;radioName=(.+?)&amp;autoPlay=1&amp;bufferTime=2\.5&amp;rateServer=37\.247\.51\.47">(.+?)<p>(.+?)</div>').findall(response)
    li = tools.createListItem(title, img, '', 'music', { 'title' : title, 'plot' : tools.normalizeText(descr), 'duration' : -1, 'director' : '' })
    xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).playStream('rtmp://' + streamParam[0] + ':1935/' + streamParam[1] + '/' + params[0][0] + ' app=' + streamParam[1] + ' playpath=' + params[0][0] + ' swfUrl=http://www.virginradio.it/wp-content/themes/wirgin/corePlayerStreamingVisible2013_counter_VIRGIN.swf?streamRadio=' + params[0][0] + '&radioName=' + params[0][1].replace(' ', '%20') + '&autoPlay=1&bufferTime=2.5&rateServer=37.247.51.47 pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297', li)
elif params['content_type'] == 'video': # Diretta e categorie video.
  categs = []
  categs.append(['Virgin Radio TV', 'Guarda i migliori videoclip del canale Virgin Radio TV', '/video-canale/channel/1'])
  categs.append(['Garage Revolver', 'Guarda i migliori videoclip del canale Garage Revolver', '/video-canale/channel/2'])
  categs.append(['Video Community', 'Guarda i migliori videoclip del canale Video Community', '/video-canale/channel/4'])
  categs.append(['Musica', 'Guarda i migliori videoclip del canale Musica', '/video-canale/channel/5'])
  categs.append(['Wikipaola', 'Guarda i migliori videoclip del canale Wikipaola', '/video-canale/channel/7'])
  categs.append(['Heineken Jammin\' Festival', 'Guarda i migliori videoclip del canale Heineken Jammin\' Festival', '/video-canale/channel/9'])
  categs.append(['Virgin on Tour', 'Guarda i migliori videoclip del canale Virgin on Tour', '/video-canale/channel/12'])
  categs.append(['Virgin Radio VideoNews', 'Guarda i migliori videoclip del canale Virgin Radio VideoNews', '/video-canale/channel/13'])
  categs.append(['Virgin Rock 20', 'Guarda i migliori videoclip del canale Virgin Rock 20', '/video-canale/channel/14'])
  categs.append(['Giulia Sessions', 'Guarda i migliori videoclip del canale Giulia Sessions', '/video-canale/channel/15'])
  categs.append(['Elio Fiorucci\'s Stories', 'Guarda i migliori videoclip del canale Elio Fiorucci\'s Stories', '/video-canale/channel/17'])
  categs.append(['Virgin Rock Live', 'Guarda i migliori videoclip del canale Virgin Rock Live', '/video-canale/channel/18'])
  categs.append(['The Photograph', 'Guarda i migliori videoclip del canale The Photograph', '/video-canale/channel/19'])
  categs.append(['Litfiba Contest', 'Guarda i migliori videoclip del canale Litfiba Contest', '/video-canale/channel/20'])
  qlty = int(xbmcplugin.getSetting(handle, 'vid_quality')) + 1
  streamParam = getStreamParam(qlty)
  response = tools.getResponseUrl('http://www.virginradio.it/video')
  descr = tools.normalizeText(tools.stripTags(re.compile('<aside> <p>(.+?)</p> </aside>').findall(response)[0]))
  title = tools.normalizeText(re.compile('<span class="h2Wrapper" style="font-size: 36px;">(.+?)</span>').findall(response)[0])
  img = os.path.dirname(os.path.abspath(__file__)) + '/resources/images/VirginRadioTV.png'
  tools.addLink(handle, tools.getTranslation(idPlugin, 30004), img, '', 'video', { 'title' : title, 'plot' : descr, 'duration' : -1, 'director' : '' }, 'rtmp://' + streamParam[0] + ':1935/' + streamParam[1] + '/' + streamParam[2] + ' app=' + streamParam[1] + ' playpath=' + streamParam[2] + ' swfUrl=http://video.virginradioitaly.it/com/universalmind/swf/video_player_102.swf?xmlPath=http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml&advXML=http://video.virginradioitaly.it/com/universalmind/adsWizzConfig/1.xml pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297') # Diretta.
  for nameCat, descr, link in categs:
    tools.addDir(handle, nameCat, '', '', 'video', { 'title' : nameCat, 'plot' : descr, 'duration' : -1, 'director' : '' }, { 'id' : 's', 'page' : link })
  xbmcplugin.endOfDirectory(handle)
elif params['content_type'] == 'audio': # Web radio.
  getWebRadio('/webradio/')

#print 'Virgin radio azione ' + str(datetime.datetime.now() - startTime)
