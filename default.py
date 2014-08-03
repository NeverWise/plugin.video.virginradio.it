#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, re, xbmcgui, xbmcplugin#, datetime
from neverwise import Util


class VirginRadio(object):

  _handle = int(sys.argv[1])
  _params = Util.urlParametersToDict(sys.argv[2])

  def __init__(self):

    # Visualizzo i video della sezione.
    if self._params.get('content_type') is None:
      response = self._getVirginResponse(self._params['page'])
      if response != None:

        # Video di una categoria.
        if self._params['id'] == 's':
          videos = re.compile('<figure> <a href="(.+?)" title=".+?">.+?<img src="(.+?)".+?> </a> </figure> <header> <a href=".+?" title=".+?"> <h3>(.+?)</h3> </a> </header> <div.+?>(.+?)</div>').findall(response)
          items = []
          for link, img, title, descr in videos:
            title = Util.normalizeText(title)
            li = Util.createListItem(title, thumbnailImage = self._normalizeImageUrl(img), streamtype = 'video', infolabels = { 'title' : title, 'plot' : Util.normalizeText(descr) }, isPlayable = True)
            items.append([{ 'id' : 'v', 'page' : link }, li, False, True])
          self._showNextPageDir(response, '[0-9]+ <a rel="nofollow" href="(.+?)">(.+?)</a>', 's', items)
          Util.addItems(self._handle, items)

        # Riproduzione di un video.
        elif self._params['id'] == 'v':
          if response.find('<title>Virgin Radio Tv</title>') == -1: # Per evitare i video non funzionanti.
            title = Util.normalizeText(re.compile('<meta property="og:title" content="(.+?)"').findall(response)[0])
            img = self._normalizeImageUrl(re.compile('<meta property="og:image" content="(.+?)"').findall(response)[0])
            descr = re.compile('<meta property="og:description" content="(.+?)"').findall(response)[0]
            play = re.compile('clip: \{"url":"(.+?):(.+?)"').findall(response)
            server = re.compile('"hddn":\{"url":"(.+?)","netConnectionUrl":"rtmp:\\\/\\\/(.+?)\\\/(.+?)"\},"').findall(response)
            playBS = play[0][1].replace('\\', '')
            Util.playStream(self._handle, title, img, 'rtmp://{0}:1935/{1}/{2} app={1} playpath={3}:{2} swfUrl={4} pageURL=http://www.virginradio.it swfVfy=true live=false flashVer=LNX 10,1,82,76'.format(server[0][1], server[0][2], playBS, play[0][0], server[0][0].replace('\\', '')), 'video', { 'title' : title, 'plot' : Util.normalizeText(descr) })
          else:
            Util.showVideoNotAvailableDialog()

        # Pagina successiva radio.
        elif self._params['id'] == 't':
          self._getWebRadio(response)

        # Riproduzione di una radio.
        elif self._params['id'] == 'r':
          streamParam = self._getStreamParam(1)
          if streamParam != None:
            title = Util.normalizeText(re.compile('<div class="seo-strip clearfix"> <header> <h1>(.+?)</h1>').findall(response)[0])
            img = re.compile("<meta property='og:image' content='(.+?)'").findall(response)[0]
            #descr = re.compile("<meta property='og:description' content='(.+?)'").findall(response)[0]
            params = re.compile('<param name="movie" value="/wp-content/themes/wirgin/swf//corePlayerStreamingVisible2014_Virgin\.swf\?streamRadio=(.+?)&radioName=(.+?)&.+?>').findall(response)
            Util.playStream(self._handle, title, img, 'rtmp://{0}:1935/{1}/{2} app={1} playpath={2} swfUrl=http://www.virginradio.it/wp-content/themes/wirgin/corePlayerStreamingVisible2013_counter_VIRGIN.swf?streamRadio={2}&radioName={3}&autoPlay=1&bufferTime=2.5&rateServer=37.247.51.47 pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297'.format(streamParam[0], streamParam[1], params[0][0], params[0][1].replace(' ', '%20')), 'music', { 'title' : title })

      else:
        Util.showConnectionErrorDialog() # Errore connessione internet!

    # Diretta e categorie video.
    elif self._params['content_type'] == 'video':
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
      qlty = int(xbmcplugin.getSetting(self._handle, 'vid_quality')) + 1
      streamParam = self._getStreamParam(qlty)
      items = []
      if streamParam != None:
        response = self._getVirginResponse('/video')
        if response != None:
          descr = Util.normalizeText(Util.trimTags(re.compile('<aside> <p>(.+?)</p> </aside>').findall(response)[0]))
          title = Util.normalizeText(re.compile('<span class="h2Wrapper" style="font-size: 36px;">(.+?)</span>').findall(response)[0])
          img = '{0}/resources/images/VirginRadioTV.png'.format(os.path.dirname(os.path.abspath(__file__)))
          li = Util.createListItem(Util.getTranslation(30003), thumbnailImage = img, streamtype = 'video', infolabels = { 'title' : title, 'plot' : descr }) # Diretta.
          items.append(['rtmp://{0}:1935/{1}/{2} app={1} playpath={2} swfUrl=http://video.virginradioitaly.it/com/universalmind/swf/video_player_102.swf?xmlPath=http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml&advXML=http://video.virginradioitaly.it/com/universalmind/adsWizzConfig/1.xml pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297'.format(streamParam[0], streamParam[1], streamParam[2]), li, False, False])
      for nameCat, descr, link in categs:
        li = Util.createListItem(nameCat, streamtype = 'video', infolabels = { 'title' : nameCat, 'plot' : descr })
        items.append([{ 'id' : 's', 'page' : link }, li, True, True])

      if (streamParam == None or not streamParam) and (response == None or not response): # Se sono vuoti oppure liste vuote.
        xbmcgui.Dialog().ok(Util._addonName, Util.getTranslation(30004)) # Errore recupero stream diretta.

      # Show items.
      Util.addItems(self._handle, items)

    # Web radio.
    elif self._params['content_type'] == 'audio':
      response = self._getVirginResponse('/webradio')
      if response != None:
        self._getWebRadio(response)
      else:
        Util.showConnectionErrorDialog() # Errore connessione internet!


  def _getVirginResponse(self, link):
    return Util('http://www.virginradio.it{0}'.format(link)).getHtml()


  def _getStreamParam(self, quality):
    result = None
    response = Util('http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml').getHtml()
    if response != None:
      serverParam = re.compile('<serverPath value="auto\|(.+?)\|(.+?)"/>').findall(response)
      stream = re.compile('<rate n="{0}" streamName="(.+?)" bitrate="'.format(str(quality))).findall(response)
      result = [serverParam[0][0], serverParam[0][1], stream[0]]
    return result


  def _isExtensionNumber(self, extension):
    result = False
    try:
      int(extension)
      result = True
    except:
      pass
    return result


  def _normalizeImageUrl(self, img):
    extension = img[-3:]
    if extension[0] == '.':
      isNumber = self._isExtensionNumber(extension[-2:])
    else:
      isNumber = self._isExtensionNumber(extension)

    if isNumber:
      img = img.replace(extension, '.jpg')

    return img


  def _showNextPageDir(self, inputString, pattern, idParams, items):
    nextPage = re.compile(pattern).findall(inputString)
    if len(nextPage) > 0:
      items.append([{ 'id' : idParams, 'page' : nextPage[0][0] }, Util.createItemPage(Util.normalizeText(nextPage[0][1])), True, True])


  def _getWebRadio(self, response):
    rList = re.compile('<img width="70" height="70" src="(.+?)".+?/> <a href="(.+?)">(.+?)</a>').findall(response)
    #rList = re.compile('<img width="70" height="70" src="(.+?)".+?/> <a href="(.+?)">(.+?)</a> <p><p>(.+?)</p>').findall(response)
    items = []
    for img, link, title in rList:
      title = Util.normalizeText(title)
      li = Util.createListItem(title, thumbnailImage = img.replace('-70x70', ''), streamtype = 'music', infolabels = { 'title' : title }, isPlayable = True)
      items.append([{ 'id' : 'r', 'page' : link.replace('http://www.virginradio.it', '') }, li, False, True])
    self._showNextPageDir(response, "<span class='page-numbers current'>.+?</span><a class='page-numbers' href='(.+?)'>(.+?)</a>", 't', items)
    Util.addItems(self._handle, items)


# Entry point.
#startTime = datetime.datetime.now()
vr = VirginRadio()
del vr
#print '{0} azione {1}'.format(Util._addonName, str(datetime.datetime.now() - startTime))
