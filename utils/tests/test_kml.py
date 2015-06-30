import logging
import sys
import uuid
import os
from django.test import SimpleTestCase
from django.utils import timezone
from django.core.files import File
from unittest import skip
import mock
from mock import patch, Mock

from ..kml import SQliteToKml

logger = logging.getLogger(__name__)


class TestSQliteToKml(SimpleTestCase):
    
    def setUp(self, ):
        self.path = os.path.dirname(os.path.realpath(__file__))
    
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_convert(self, popen, pipe):
        sqlite = '/path/to/query.sqlite'
        kmlfile= '/path/to/query.kml'
        cmd = "ogr2ogr -f 'KML' {0} {1}".format(kmlfile, sqlite)
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        # set zipped to False for testing
        s2k = SQliteToKml(sqlite=sqlite, kmlfile=kmlfile,
                          zipped=False, debug=True)
        out = s2k.convert()
        popen.assert_called_once_with(cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        proc.communicate.assert_called_once()
        proc.wait.assert_called_once()
        self.assertEquals(out, kmlfile)
    
    @patch('os.remove')
    @patch('subprocess.PIPE')
    @patch('subprocess.Popen')
    def test_zip_img_file(self, popen, pipe, remove):
        sqlite = '/path/to/query.sqlite'
        kmlfile= '/path/to/query.kml'
        zipfile = '/path/to/query.kmz'
        zip_cmd = "zip -j {0} {1}".format(zipfile, kmlfile)
        proc = Mock()
        popen.return_value = proc
        proc.communicate.return_value = (Mock(), Mock())
        proc.wait.return_value = 0
        s2k = SQliteToKml(sqlite=sqlite, kmlfile=kmlfile,
                          zipped=False, debug=True)
        result = s2k._zip_kml_file()
        # test subprocess getting called with correct command
        popen.assert_called_once_with(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=pipe, stderr=pipe)
        remove.assert_called_once_with(kmlfile)
        self.assertEquals(result, zipfile)