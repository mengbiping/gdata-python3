#
# Copyright 2009 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License 2.0;


# This module is used for version 2 of the Google Data APIs.
# These tests attempt to connect to Google servers.


# __author__ = 'e.bidelman (Eric Bidelman)'

import unittest

import gdata.client
import gdata.data
import gdata.gauth
import gdata.sites.client
import gdata.sites.data
import gdata.test_config as conf

conf.options.register_option(conf.TEST_IMAGE_LOCATION_OPTION)
conf.options.register_option(conf.APPS_DOMAIN_OPTION)
conf.options.register_option(conf.SITES_NAME_OPTION)


class SitesClientTest(unittest.TestCase):
    def setUp(self):
        self.client = None
        if conf.options.get_value('runlive') == 'true':
            self.client = gdata.sites.client.SitesClient(
                site=conf.options.get_value('sitename'),
                domain=conf.options.get_value('appsdomain'))
            if conf.options.get_value('ssl') == 'true':
                self.client.ssl = True
            conf.configure_client(self.client, 'SitesTest', self.client.auth_service,
                                  True)

    def tearDown(self):
        conf.close_client(self.client)

    def testCreateUpdateDelete(self):
        if not conf.options.get_value('runlive') == 'true':
            return

        # Either load the recording or prepare to make a live request.
        conf.configure_cache(self.client, 'testCreateUpdateDelete')

        new_entry = self.client.CreatePage(
            'webpage', 'Title Of Page', '<b>Your html content</b>')

        self.assertEqual(new_entry.title.text, 'Title Of Page')
        self.assertEqual(new_entry.page_name.text, 'title-of-page')
        self.assertTrue(new_entry.GetAlternateLink().href is not None)
        self.assertEqual(new_entry.Kind(), 'webpage')

        # Change the title of the webpage we just added.
        new_entry.title.text = 'Edited'
        updated_entry = self.client.update(new_entry)

        self.assertEqual(updated_entry.title.text, 'Edited')
        self.assertEqual(updated_entry.page_name.text, 'title-of-page')
        self.assertTrue(isinstance(updated_entry, gdata.sites.data.ContentEntry))

        # Delete the test webpage from the Site.
        self.client.delete(updated_entry)

    def testCreateAndUploadToFilecabinet(self):
        if not conf.options.get_value('runlive') == 'true':
            return

        # Either load the recording or prepare to make a live request.
        conf.configure_cache(self.client, 'testCreateAndUploadToFilecabinet')

        filecabinet = self.client.CreatePage(
            'filecabinet', 'FilesGoHere', '<b>Your html content</b>',
            page_name='diff-pagename-than-title')

        self.assertEqual(filecabinet.title.text, 'FilesGoHere')
        self.assertEqual(filecabinet.page_name.text, 'diff-pagename-than-title')
        self.assertTrue(filecabinet.GetAlternateLink().href is not None)
        self.assertEqual(filecabinet.Kind(), 'filecabinet')

        # Upload a file to the filecabinet
        filepath = conf.options.get_value('imgpath')
        attachment = self.client.UploadAttachment(
            filepath, filecabinet, content_type='image/jpeg', title='TestImageFile',
            description='description here')

        self.assertEqual(attachment.title.text, 'TestImageFile')
        self.assertEqual(attachment.FindParentLink(),
                         filecabinet.GetSelfLink().href)

        # Delete the test filecabinet and attachment from the Site.
        self.client.delete(attachment)
        self.client.delete(filecabinet)


def suite():
    return conf.build_suite([SitesClientTest])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
