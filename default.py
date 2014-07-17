#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, re, xbmcgui, xbmcplugin#, datetime
from neverwise import Util


class VirginRadio:

  __handle = int(sys.argv[1])
  __params = Util.urlParametersToDict(sys.argv[2])
  __idPlugin = 'plugin.virginradio'
  __namePlugin = 'Virgin Radio'
  __itemsNumber = 0

  def __init__(self):

    # Visualizzo i video della sezione.
    if self.__params.get('content_type') is None:
      response = self.__getVirginResponse(self.__params['page'])
      if response != None:

        # Video di una categoria.
        if self.__params['id'] == 's':
          videos = re.compile('<figure> <a href="(.+?)" title=".+?">.+?<img src="(.+?)".+?> </a> </figure> <header> <a href=".+?" title=".+?"> <h3>(.+?)</h3> </a> </header> <div.+?>(.+?)</div>').findall(response)
          for link, img, title, descr in videos:
            img = self.__normalizeImageUrl(img)
            title = Util.normalizeText(title)
            Util.addItem(self.__handle, title, img, '', 'video', { 'title' : title, 'plot' : Util.normalizeText(descr) }, None, { 'id' : 'v', 'page' : link }, True)
            self.__itemsNumber += 1
          self.__showNextPageDir(response, '[0-9]+ <a rel="nofollow" href="(.+?)">(.+?)</a>', 's')

        # Riproduzione di un video.
        elif self.__params['id'] == 'v':
          if response.find('<title>Virgin Radio Tv</title>') == -1: # Per evitare i video non funzionanti.
            title = Util.normalizeText(re.compile('<meta property="og:title" content="(.+?)"').findall(response)[0])
            img = self.__normalizeImageUrl(re.compile('<meta property="og:image" content="(.+?)"').findall(response)[0])
            descr = re.compile('<meta property="og:description" content="(.+?)"').findall(response)[0]
            play = re.compile('clip: \{"url":"(.+?):(.+?)"').findall(response)
            server = re.compile('"hddn":\{"url":"(.+?)","netConnectionUrl":"rtmp:\\\/\\\/(.+?)\\\/(.+?)"\},"').findall(response)
            playBS = play[0][1].replace('\\', '')
            li = Util.createListItem(title, img, '', 'video', { 'title' : title, 'plot' : Util.normalizeText(descr) })
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play('rtmp://{0}:1935/{1}/{2} app={1} playpath={3}:{2} swfUrl={4} pageURL=http://www.virginradio.it swfVfy=true live=false flashVer=LNX 10,1,82,76'.format(server[0][1], server[0][2], playBS, play[0][0], server[0][0].replace('\\', '')), li)
          else:
            xbmcgui.Dialog().ok(namePlugin, Util.getTranslation(self.__idPlugin, 30005)) # Messaggio d'errore "Video non disponibile".

        # Pagina successiva radio.
        elif self.__params['id'] == 't':
          self.__getWebRadio(response)

        # Riproduzione di una radio.
        elif self.__params['id'] == 'r':
          streamParam = self.__getStreamParam(1)
          if streamParam != None:
            title = Util.normalizeText(re.compile('<div class="seo-strip clearfix"> <header> <h1>(.+?)</h1>').findall(response)[0])
            img = re.compile("<meta property='og:image' content='(.+?)'").findall(response)[0]
            #descr = re.compile("<meta property='og:description' content='(.+?)'").findall(response)[0]
            params = re.compile('<param name="movie" value="/wp-content/themes/wirgin/swf//corePlayerStreamingVisible2014_Virgin\.swf\?streamRadio=(.+?)&radioName=(.+?)&.+?>').findall(response)
            li = Util.createListItem(title, img, '', 'music', { 'title' : title })
            xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play('rtmp://{0}:1935/{1}/{2} app={1} playpath={2} swfUrl=http://www.virginradio.it/wp-content/themes/wirgin/corePlayerStreamingVisible2013_counter_VIRGIN.swf?streamRadio={2}&radioName={3}&autoPlay=1&bufferTime=2.5&rateServer=37.247.51.47 pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297'.format(streamParam[0], streamParam[1], params[0][0], params[0][1].replace(' ', '%20')), li)

      else:
        Util.showConnectionErrorDialog(namePlugin) # Errore connessione internet!

    # Diretta e categorie video.
    elif self.__params['content_type'] == 'video':
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
      qlty = int(xbmcplugin.getSetting(self.__handle, 'vid_quality')) + 1
      streamParam = self.__getStreamParam(qlty)
      if streamParam != None:
        response = self.__getVirginResponse('/video')
        if response != None:
          descr = Util.normalizeText(Util.trimTags(re.compile('<aside> <p>(.+?)</p> </aside>').findall(response)[0]))
          title = Util.normalizeText(re.compile('<span class="h2Wrapper" style="font-size: 36px;">(.+?)</span>').findall(response)[0])
          img = '{0}/resources/images/VirginRadioTV.png'.format(os.path.dirname(os.path.abspath(__file__)))
          Util.addItem(self.__handle, Util.getTranslation(self.__idPlugin, 30004), img, '', 'video', { 'title' : title, 'plot' : descr }, None, 'rtmp://{0}:1935/{1}/{2} app={1} playpath={2} swfUrl=http://video.virginradioitaly.it/com/universalmind/swf/video_player_102.swf?xmlPath=http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml&advXML=http://video.virginradioitaly.it/com/universalmind/adsWizzConfig/1.xml pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297'.format(streamParam[0], streamParam[1], streamParam[2]), False) # Diretta.
          self.__itemsNumber += 1
      for nameCat, descr, link in categs:
        Util.addItem(self.__handle, nameCat, '', '', 'video', { 'title' : nameCat, 'plot' : descr }, None, { 'id' : 's', 'page' : link }, True)
        self.__itemsNumber += 1

      if (streamParam == None or not streamParam) and (response == None or not response): # Se sono vuoti oppure liste vuote.
        xbmcgui.Dialog().ok(namePlugin, Util.getTranslation(self.__idPlugin, 30006)) # Errore recupero stream diretta.

    # Web radio.
    elif self.__params['content_type'] == 'audio':
      response = self.__getVirginResponse('/webradio')
      if response != None:
        self.__getWebRadio(response)
      else:
        Util.showConnectionErrorDialog(namePlugin) # Errore connessione internet!

    if self.__itemsNumber > 0:
      xbmcplugin.endOfDirectory(self.__handle)


  def __getVirginResponse(self, link):
    return Util('http://www.virginradio.it{0}'.format(link)).getHtml()


  def __getStreamParam(self, quality):
    result = None
    response = Util('http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml').getHtml()
    if response != None:
      serverParam = re.compile('<serverPath value="auto\|(.+?)\|(.+?)"/>').findall(response)
      stream = re.compile('<rate n="{0}" streamName="(.+?)" bitrate="'.format(str(quality))).findall(response)
      result = [serverParam[0][0], serverParam[0][1], stream[0]]
    return result


  def __isExtensionNumber(self, extension):
    result = False
    try:
      int(extension)
      result = True
    except:
      pass
    return result


  def __normalizeImageUrl(self, img):
    extension = img[-3:]
    if extension[0] == '.':
      isNumber = self.__isExtensionNumber(extension[-2:])
    else:
      isNumber = self.__isExtensionNumber(extension)

    if isNumber:
      img = img.replace(extension, '.jpg')

    return img


  def __showNextPageDir(self, inputString, pattern, idParams):
    if self.__itemsNumber > 0:
      nextPage = re.compile(pattern).findall(inputString)
      if len(nextPage) > 0:
        pageNum = Util.normalizeText(nextPage[0][1])
        Util.AddItemPage(self.__handle, pageNum, '', '', { 'title' : pageNum }, { 'id' : idParams, 'page' : nextPage[0][0] })


  def __getWebRadio(self, response):
    rList = re.compile('<img width="70" height="70" src="(.+?)".+?/> <a href="(.+?)">(.+?)</a>').findall(response)
    #rList = re.compile('<img width="70" height="70" src="(.+?)".+?/> <a href="(.+?)">(.+?)</a> <p><p>(.+?)</p>').findall(response)
    for img, link, title in rList:
      img = img.replace('-70x70', '')
      title = Util.normalizeText(title)
      Util.addItem(self.__handle, title, img, '', 'music', { 'title' : title }, None, { 'id' : 'r', 'page' : link.replace('http://www.virginradio.it', '') }, True)
      self.__itemsNumber += 1
    self.__showNextPageDir(response, "<span class='page-numbers current'>.+?</span><a class='page-numbers' href='(.+?)'>(.+?)</a>", 't')


# Entry point.
#startTime = datetime.datetime.now()
vr = VirginRadio()
del vr
#print '{0} azione {1}'.format(self.__namePlugin, str(datetime.datetime.now() - startTime))
