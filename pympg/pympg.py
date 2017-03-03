"""
A simple wrapper library for mpg123 media player.

For more details about this platform, please refer to the documentation at
https://github.com/vroomfonde1/pympg
"""
import logging
import subprocess

_LOGGER = logging.getLogger(__name__)


class pympg(object):
    """Implementation of mpg123 media player."""
    CMND = 'mpg123'
    STATE_IDLE = 0
    STATE_PAUSED = 1
    STATE_PLAYING = 2

    def __init__(self):
        """Initialize internal variables."""
        import threading

        self._state = self.STATE_IDLE
        self._currentsong = ''
        self._title = ''
        self._artist = ''
        self._album = ''
        self._year = ''
        self._currentoffset = 0.0
        self._duration = 0.0
        self._volume = 0.0
        self.popen = None
        self._mpg123version = None

        _LOGGER.debug('Loading mpg123 instance.')
        try:
            self.popen = subprocess.Popen([self.CMND, "-R"],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          universal_newlines=True)
        except subprocess.SubprocessError:
            _LOGGER.error('Unable to open mpg123')
            self.popen = None
            return

        threading.Thread(target=self._mpg123_sm, daemon=True).start()

    def _clear_song_tags(self):
        self._currentsong = ''
        self._title = ''
        self._artist = ''
        self._album = ''
        self._year = ''

    def _mpg123_sm(self):
        """Implementation of state machine for mpg123 instance."""
        id3v2_title = '@I ID3v2.title:'
        id3v2_artist = '@I ID3v2.artist:'
        id3v2_album = '@I ID3v2.album:'
        id3v2_year = '@I ID3v2.year:'
        while self.popen:
            try:
                line = self.popen.stdout.readline()
            except subprocess.SubprocessError:
                _LOGGER.error('Unable to read from mpg123')
                self.popen = None
                return

            _LOGGER.debug('%s', line)
            line = line.strip('\r\n')
            if line.startswith('@F'):
                """@F 0 279 0.00 6.70"""
                args = line.split()
                self._currentoffset = float(args[3])
                self._duration = float(args[4])
                continue
            if line in ['@P 0']:
                self._state = self.STATE_IDLE
                self._clear_song_tags()
                continue
            if line in ['@P 1']:
                self._state = self.STATE_PAUSED
                continue
            if line in ['@P 2']:
                self._state = self.STATE_PLAYING
                continue
            if line.startswith(id3v2_title):
                self._title = line.replace(id3v2_title, '')
                continue
            if line.startswith(id3v2_album):
                self._album = line.replace(id3v2_album, '')
                continue
            if line.startswith(id3v2_artist):
                self._artist = line.replace(id3v2_artist, '')
                continue
            if line.startswith(id3v2_year):
                self._year = line.replace(id3v2_year, '')
                continue
            if line.startswith('@I ID3:'):
                """ @I ID3:artist  album  year  comment genretext
                    where artist,album and comment are exactly 30 characters each,
                    year is 4 characters, genre text unspecified."""
                self._artist = line[7:36]
                self._album = line[37:66]
                self._year = line[67:70]
                self._title = ''
                continue
            if line.startswith('@V'):
                """@V 30.000000%"""
                args = line.split()
                self._volume = float(args[1])
                continue
            if line.startswith('@R'):
                self._mpg123version = line[3:]
                continue

    def sendmessage(self, msg=None):
        """Send message to mpg123 instance."""
        if msg is None:
            return
        _LOGGER.debug('CMD: %s', msg)
        msg += '\n'
        try:
            self.popen.stdin.write(msg)
            self.popen.stdin.flush()
        except subprocess.SubprocessError:
            _LOGGER.error('Unable to write to mpg123')
            self.popen = None

    def playfile(self, file=None):
        self._clear_song_tags()
        self._currentsong = file
        self.sendmessage('LOAD ' + file)

    def pause(self):
        if self._state == self.STATE_PLAYING:
            self.sendmessage('PAUSE')

    def unpause(self):
        if self._state == self.STATE_PAUSED:
            self.sendmessage('PAUSE')

    def stop(self):
        self.sendmessage('STOP')

    def quit(self):
        self.sendmessage('QUIT')

    def setvolume(self, newvol=0.0):
        if 0.0 <= newvol <= 100.0:
            self.sendmessage('VOLUME ' + str(newvol))

    def seek(self, seek_pos=0.0):
        self.sendmessage('JUMP ' + str(seek_pos) + 's')

    def getduration(self):
        return self._duration

    def getposition(self):
        return self._currentoffset
