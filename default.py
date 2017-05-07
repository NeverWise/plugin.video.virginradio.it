#!/usr/bin/python
import neverwise as nw, re, subprocess, sys, os, xbmcplugin#, datetime


class VirginRadio(object):

  _handle = int(sys.argv[1])
  _params = nw.urlParametersToDict(sys.argv[2])
  _fanart = nw.addon.getAddonInfo('fanart')
  _def_size_img = '600/340'

  def __init__(self):

    # Audio, Video, Foto.
    if len(self._params) == 0:

      nw.createAudioVideoItems(self._handle, self._fanart)
      xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'content_type' : 'image' }), nw.createListItem(nw.getTranslation(30005), thumbnailImage = 'DefaultPicture.png', fanart = self._fanart), True)
      xbmcplugin.endOfDirectory(self._handle)

    elif 'content_type' in self._params:

      # Video.
      if self._params['content_type'] == 'video':
        qlty = int(xbmcplugin.getSetting(self._handle, 'vid_quality')) + 1
        streamParam = self._getStreamParam(qlty)
        if streamParam != None:
          title = nw.getTranslation(30003)
          img = '{0}/resources/images/VirginRadioTV.png'.format(os.path.dirname(os.path.abspath(__file__)))
          li = nw.createListItem(title, thumbnailImage = img, fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : title }) # Diretta.
          url = 'rtmp://{0}:1935/{1}/{2} app={1} playpath={2} swfUrl=http://video.virginradioitaly.it/com/universalmind/swf/video_player_102.swf?xmlPath=http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml&advXML=http://video.virginradioitaly.it/com/universalmind/adsWizzConfig/1.xml pageURL=http://www.virginradio.it swfVfy=true live=true timeout=30 flashVer=LNX 11,2,202,297'.format(streamParam[0], streamParam[1], streamParam[2])
          xbmcplugin.addDirectoryItem(self._handle, url, li)

        page_num = 700
        addon_page = 2
        response = self._getVirginResponse('VideoList.jsp?x_pag={0}&page=1'.format(page_num))
        if response.isSucceeded:
          for video in response.body['videos']:
            li = self._setVideoListItem(video)

          nw.createNextPageItem(self._handle, addon_page, { 'action' : 'v', 'page' : page_num + 1, 'page_tot' : response.body['total'], 'addon_page' : addon_page + 1 }, self._fanart)

        xbmcplugin.endOfDirectory(self._handle)

        if (streamParam == None or not streamParam) or (response == None or not response or not response.isSucceeded):
          nw.showNotification(nw.getTranslation(30004))

      # Audio.
      elif self._params['content_type'] == 'audio':
        xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'r' }), nw.createListItem('Radio', thumbnailImage = 'DefaultFolder.png', fanart = self._fanart), True)
        xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'p' }), nw.createListItem('Podcast', thumbnailImage = 'DefaultFolder.png', fanart = self._fanart), True)
        xbmcplugin.endOfDirectory(self._handle)

      # Foto.
      elif self._params['content_type'] == 'image':
        response = self._getVirginResponse('GalleryList.jsp')
        if response.isSucceeded:
          response = self._getVirginResponse('GalleryList.jsp?thumbSize=1280x720&x_pag={0}'.format(response.body['total']))
          if response.isSucceeded:
            for gallery in response.body['gallery']:
              title = self._formatTitle(gallery)
              img = gallery['thumb']
              descr = self._formatDescr(gallery)
              li = nw.createListItem(title, thumbnailImage = img, fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : title, 'plot' : descr })
              xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'f', 'id' : gallery['id'], 'fanart' : img }), li, True)
              
        xbmcplugin.endOfDirectory(self._handle)

    # Video - pagina o riproduzione.
    elif self._params['action'] == 'v':
      if 'id' in self._params:
        response = self._getVirginResponse('Video.jsp?id={0}'.format(self._params['id']))
        if response.isSucceeded:
          video = response.body['videos']
          vd = self._getVideoInfo(video)
          nw.playStream(self._handle, vd['title'], vd['img'], video['file_video'], 'video', { 'title' : vd['title'], 'plot' : vd['descr'] })
      elif 'page' in self._params:
        video_num = 0
        page_num = int(self._params['page'])
        page_tot = int(self._params['page_tot'])
        addon_page = int(self._params['addon_page'])
        while video_num < 30 and page_num <= page_tot:
          response = self._getVirginResponse('VideoList.jsp?x_pag=1&page={0}'.format(page_num), show_error_msg = False)
          if response.isSucceeded:
            page_tot = response.body['total']
            if response.body['videos'] != None and len(response.body['videos']) > 0:
              for video in response.body['videos']:
                li = self._setVideoListItem(video)
                video_num += 1
          page_num += 1

        if page_num < page_tot:
          nw.createNextPageItem(self._handle, addon_page, { 'action' : 'v', 'page' : page_num + 1, 'page_tot' : page_tot, 'addon_page' : addon_page + 1 }, self._fanart)

        xbmcplugin.endOfDirectory(self._handle)

    # Video - download.
    elif self._params['action'] == 'd':
      response = self._getVirginResponse('Video.jsp?id={0}'.format(self._params['id']))
      if response.isSucceeded:
        video = response.body['videos']
        vd = self._getVideoInfo(video)
        name = ''.join([i if ord(i) < 128 else '' for i in vd['title'].replace(' ', '_')])
        name = '{0}.mp4'.format(name)
        os.chdir(nw.addon.getSetting('download_path'))
        #~ subprocess.call([nw.addon.getSetting('ffmpeg_path'), '-i', video['file_video'], '-c', 'copy', name])
        subprocess.Popen([nw.addon.getSetting('ffmpeg_path'), '-i', video['file_video'], '-c', 'copy', name])
      else:
        nw.showVideoNotAvailable()

    # Radio
    elif self._params['action'] == 'r':
      response = self._getVirginResponse('WebRadioList.jsp')
      if response.isSucceeded:
        self._setRadiosListItem(response.body['webradios']['webradioChannel'])
        self._setRadiosListItem(response.body['webradios']['musicStar'])

      xbmcplugin.endOfDirectory(self._handle)

      if response == None or not response or not response.isSucceeded:
        nw.showNotification(nw.getTranslation(30004))

    # Podcast.
    elif self._params['action'] == 'p':
      if 'id' in self._params:
        response = self._getVirginResponse('PodcastAudio.jsp?slug={0}'.format(self._params['id']))
        if response.isSucceeded:
          for podcast in response.body['podcast_audio']['podcasts']:
            title = self._formatTitle(podcast)
            li = nw.createListItem(title, fanart = self._params['fanart'], streamtype = 'music', infolabels = { 'title' : title }, isPlayable = True)
            xbmcplugin.addDirectoryItem(self._handle, podcast['file'], li)
      else:
        response = self._getVirginResponse('PodcastAudioList.jsp?imageSize=1280x720')
        if response.isSucceeded:
          for podcast in response.body['podcast_audio']:
            title = podcast['titolo']
            img = podcast['immagine']
            descr = self._formatDescr(podcast)
            li = nw.createListItem(title, thumbnailImage = img, fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : title, 'plot' : descr })
            xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'p', 'id' : podcast['slug'], 'fanart' : img }), li, True)

      xbmcplugin.endOfDirectory(self._handle)

    # Foto.
    elif self._params['action'] == 'f':
      response = self._getVirginResponse('Gallery.jsp?id={0}'.format(self._params['id']))
      if response.isSucceeded:
        for idx, photo in enumerate(response.body['gallery']['immagini']):
          title = '{0} {1}'.format(nw.getTranslation(30005), idx + 1)
          img = photo['thumb'].replace('100/100', self._def_size_img)
          li = nw.createListItem(title, thumbnailImage = img, fanart = self._params['fanart'], streamtype = 'image', infolabels = { 'title' : title })
          xbmcplugin.addDirectoryItem(self._handle, photo['original'], li)

      xbmcplugin.endOfDirectory(self._handle)


  def _setVideoListItem(self, video):
    vd = self._getVideoInfo(video)
    cm = None
    if os.path.isfile(nw.addon.getSetting('ffmpeg_path')) and os.path.isdir(nw.addon.getSetting('download_path')):
      cm = nw.getDownloadContextMenu('RunPlugin({0})'.format(nw.formatUrl({ 'action' : 'd', 'id' : video['id'] })), vd['title'])
    li = nw.createListItem(vd['title'], thumbnailImage = vd['img'], fanart = self._fanart, streamtype = 'video', infolabels = { 'title' : vd['title'], 'plot' : vd['descr'] }, isPlayable = True, contextMenu = cm)
    xbmcplugin.addDirectoryItem(self._handle, nw.formatUrl({ 'action' : 'v', 'id' : video['id'] }), li)


  def _getVideoInfo(self, video):
    title = self._formatTitle(video)
    img = video['anteprima'].replace('300/170', self._def_size_img)
    descr = self._formatDescr(video)
    return { 'img' : img, 'title' : title, 'descr' : descr }


  def _formatTitle(self, video):
    return nw.htmlDecode(u'{0} ({1})'.format(video['titolo'].strip(), video['data'].strip()))


  def _formatDescr(self, video):
    return nw.htmlDecode(nw.stripTags(video['descrizione']).strip())


  def _setRadiosListItem(self, radios):
    for radio in radios:
      title = radio['titolo']
      li = nw.createListItem(title, thumbnailImage = radio['immagine']['smartTv'], fanart = self._fanart, streamtype = 'music', infolabels = { 'title' : title })
      xbmcplugin.addDirectoryItem(self._handle, radio['streaming']['iOS'], li)


  def _getVirginResponse(self, route):
    return nw.getResponseJson('http://www.virginradio.it/custom_widget/finelco/ws_apps_vrg/get{0}'.format(route))


  def _getStreamParam(self, quality):
    result = None
    response = nw.getResponseBS('http://video.virginradioitaly.it/com/universalmind/tv/virgin/videoXML.xml')
    if response.isSucceeded:
      serverParam = re.search('auto\|(.+?)\|(.+)', response.body.find('serverpath')['value'])
      result = [serverParam.group(1), serverParam.group(2), response.body.find('rate', {'n' : str(quality)})['streamname']]
    return result


# Entry point.
#startTime = datetime.datetime.now()
vr = VirginRadio()
del vr
#xbmc.log('{0} azione {1}'.format(nw.addonName, str(datetime.datetime.now() - startTime)))
