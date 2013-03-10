import os 
import sys
import cherrypy
import ConfigParser
import urllib2
import pprint
import simplejson as json
import webtools
import requests

from pyechonest import artist, playlist, util


good_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Sms> Music artist %s \n Url: %s</Sms>
</Response>
""" 

bad_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Sms> Couldn't find any music for '%s' </Sms>
</Response>
""" 


class SmsServer(object):
    def __init__(self, config):
        self.production_mode = config.getboolean('settings', 'production')
        self.artist_cache = {}

    def message(self, AccountSid='', ApiVersion='', Body='', From='', FromCity='', FromCountry='', FromState='',
            FromZip='', SmsMessageSid='', SmsSid='', SmsStatus='', To='', ToCity='', ToCountry='', ToState='', ToZip='', html=''):

        cherrypy.response.headers['Content-Type']= 'application/xml'

        testUrl = 'http://open.spotify.com/track/7tb5U8D40bQbjl025FTPFs'


        if False:
            print 'AccounSid', AccountSid
            print 'ApiVersion', ApiVersion
            print 'Body', Body
            print 'From', From
            print 'FromCity', FromCity
            print 'FromCountry', FromCountry
            print 'FromState', FromState
            print 'FromZip', FromZip
            print 'SmsMessageSid', SmsMessageSid
            print 'SmsSid', SmsSid
            print 'SmsStatus', SmsStatus
            print 'To', To
            print 'ToCity', ToCity
            print 'ToCountry', ToCountry
            print 'ToState', ToState
            print 'ToZip', ToZip
        else:
            print 'Body', Body

        artist = Body
        id, name = self.get_track_id(artist)

        if html:
            cherrypy.response.headers['Content-Type']= 'text/html'
            if id:
                return '<body> <a href="%s"> %s </a> </body>' % (id, name)
            else:
                return '<body> "%s" not found </body>' % (name)
        else:
            cherrypy.response.headers['Content-Type']= 'application/xml'
            if id:
                response = good_response % (name, id)
            else:
                response = bad_response % (Body, )

        print
        print response
        print
        return response

    message.exposed = True

    def get_track_id(self, artist_name):

        if artist_name.lower() in self.artist_cache:
            return self.artist_cache[artist_name.lower()]

        id, name = self.find_artist(artist_name)

        if id:
            if id in self.artist_cache:
                return self.artist_cache[id]
            url = self.get_spotify_url(id)
        else:
            url = None

        self.artist_cache[artist_name.lower()] = (url, name)

        if name:
            self.artist_cache[name.lower()] = (url, name)
        if id:
            self.artist_cache[id] = (url, name)

        return url, name

    def find_artist(self, artist_name):
        try:
            results = artist.search(name=artist_name, results=1, buckets=["id:spotify-WW"], limit=True)
            if results and len(results) > 0:
                return results[0].id, results[0].name
            else:
                return None, None
        except util.EchoNestAPIError:
            return None, None

    def get_spotify_url(self, artist_id):
        try:
            results = playlist.static(artist_id=artist_id, results=10, buckets=["id:spotify-WW", "tracks"], limit=True)
            for song in results:
                tracks = song.get_tracks('spotify-WW')
                if len(tracks) > 0:
                    # pprint.pprint(tracks[0])
                    tid = tracks[0]['foreign_id']
                    fields = tid.split(':')
                    tid =  'http://open.spotify.com/track/' + fields[2]
                    avail = self.is_track_available(tid)
                    print avail, song.title
                    if avail:
                        return tid
            else:
                return None
        except util.EchoNestAPIError:
            return None

    def is_track_available(self, tid):
        print tid
        avail = False
        r = requests.get('http://ws.spotify.com/lookup/1/.json?uri=' + tid)
        results = r.json()
        pprint.pprint(results)
        pprint.pprint(results['info'])
        pprint.pprint(results['track'])
        try:
            avail = results['track']['available']
            popularity = float(results['track']['popularity'])
            if popularity < .1:
                avail = False
        except:
            avail = False
        return avail

if __name__ == '__main__':
    urllib2.install_opener(urllib2.build_opener())
    conf_path = os.path.abspath('web.conf')
    print 'reading config from', conf_path
    cherrypy.config.update(conf_path)

    config = ConfigParser.ConfigParser()
    config.read(conf_path)
    production_mode = config.getboolean('settings', 'production')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.

    if production_mode:
        print "Starting in production mode"
        cherrypy.config.update({'environment': 'production',
                                'log.error_file': 'simdemo.log',
                                'log.screen': True})
    else:
        print "Starting in development mode"
        cherrypy.config.update({'noenvironment': 'production',
                                'log.error_file': 'site.log',
                                'log.screen': True})

    conf = webtools.get_export_map_for_directory("static")
    cherrypy.quickstart(SmsServer(config), '/SmsServer', config=conf)

