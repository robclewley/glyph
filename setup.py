#!/usr/bin/env python

from distutils.core import setup

setup(name='glyph',
      version='2.6.5b',
      author='Chandler Armstrong',
      author_email='omni.armstrong@gmail.com',
      url='http://code.google.com/p/glyph/',
      description='Pygame typesetting library',
      download_url='http://code.google.com/p/glyph/downloads/list',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Topic :: Software Development :: Libraries :: pygame',
                   'Topic :: Text Processing'],
      packages=['glyph'],
      requires=['pygame(>=1.9.1)'],
      provides=['glyph'])
