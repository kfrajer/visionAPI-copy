# -*- coding: utf-8 -*-
# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sample application that demonstrates how to use the App Engine Images API.

For more information, see README.md.
"""

# [START all]
# [START thumbnailer]
from google.appengine.api import images

import webapp2
import json
import base64

## ------ python-docs-samples/appengine/standard/storage/appengine-client/main.py
import os
import cloudstorage
from google.appengine.api import app_identity

#from PIL import Image
#from cStringIO import StringIO
#from base64 import decodestring

## TEST URL: http://localhost:8080/img

## curl -H "Content-Type: application/json" --data @photoWide.json "http://localhost:8080/info"
## curl -H "Content-Type: application/json" --data @photoPortrait.json "http://localhost:8080/info"

## c:\Users\cmosquera\Downloads\devFolder\workspace\python\visonAPI-copy>curl -H "Content-Type: application/json" --data @photoWide.json "http://cmosquera-dev.appspot.com/info"
## Image information: WxH 1350x900
## c:\Users\cmosquera\Downloads\devFolder\workspace\python\visonAPI-copy>curl -H "Content-Type: application/json" --data @photoPortrait.json "http://cmosquera-dev.appspot.com/info"
## Image information: WxH 634x951

## curl with paramters: https://superuser.com/questions/149329/what-is-the-curl-command-line-syntax-to-do-a-post-request
## PORTRAIT:  https://unsplash.com/photos/L7gNs5dfF1w
## LANDSCAPE: https://unsplash.com/photos/-ePZt0Fxnfc

DEFAULT_FILE_NAME = 'vision-demo'

# [START retries]
cloudstorage.set_default_retry_params(
    cloudstorage.RetryParams(
        initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15
        ))
# [END retries]
    
class Thumbnailer(webapp2.RequestHandler):
    def get(self):

        #image_data – String of the source image data
        photostr=''
        
        if photostr:
            img = images.Image(image_data=photostr)
            img.resize(width=80, height=100)
            img.im_feeling_lucky()
            thumbnail = img.execute_transforms(output_encoding=images.JPEG)

            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(thumbnail)
            return

        # Either "id" wasn't provided, or there was no image with that ID
        # in the datastore.
        self.error(404)
# [END thumbnailer]


class ImageInfo(webapp2.RequestHandler):
    def post(self):

        #image_data – String of the source image data
        #jdata = json.loads(cgi.escape(self.request.body))
        jdata = json.loads(self.request.body)
        corefname = jdata['requests'][0]['image']['corefn'] || DEFAULT_FILE_NAME
        photo=jdata['requests'][0]['image']['content']
        photostr=base64.b64decode(photo)
        
        if photostr:
            img = images.Image(image_data=photostr)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write("Image information: WxH ")
            self.response.out.write(str(img.width) + "x" + str(img.height))
            #bt = BucketTest(webapp2.RequestHandler)
            #bt.vision_into_bucket(str(img.width) + "x" + str(img.height))
            self.vision_into_bucket(self.fmt_msg(str(img.width) + "x" + str(img.height)),'/'+corefname+'-raw')
            #self.vision_into_bucket(photo.encode('utf-8'),'/vision-demo-rawphoto')
            self.vision_into_bucket(base64.b64decode(photo),'/'+corefname+'-rawphoto.jpg')

            img.im_feeling_lucky()
            transformedphoto = img.execute_transforms(output_encoding=images.JPEG)
            self.vision_into_bucket(self.fmt_msg(str(img.width) + "x" + str(img.height)),'/'+corefname+'-transformed')
            self.vision_into_bucket(transformedphoto,'/'+corefname+'-transformedphoto.jpg')
            return

        # Either "id" wasn't provided, or there was no image with that ID
        # in the datastore.
        self.error(404)

    # [START test_vision_into_bucket]
    def vision_into_bucket(self,body,obj_name):
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        
        bucket = '/' + bucket_name
        filename = bucket + obj_name
        self.create_file2(filename,body)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("Done writing filename: " + filename)
        self.response.write("Done writing body:     " + body)        
        
    # [END test_vision_into_bucket]

# [START fmt_msg]
    def fmt_msg(self, body):
        """Format body to have a header and footer"""

        headerStr="{\nheader:'header'\n"
        bodyStr="body:'"+body+"'\n"
        footerStr="footer:'footer'\n}\n"
        return headerStr + bodyStr + footerStr

# [END fmt_msg]    
    
# [START write2]
# execute_transforms() returns A string of the image data after the transformations have been performed on it.
#execute_transforms(output_encoding=0, quality=None, parse_source_metadata=False, transparent_substitution_rgb=None, rpc=None)
#parse_source_metadata – When True, the metadata (EXIF) of the source image is parsed before any transformations. The results can be retrieved via Image.get_original_metadata.
    def create_file2(self, filename,body):
        """Create a file."""

        ##ERROR
        ## self.response.write('Creating file {}\n'.format(filename))
        ## AttributeError: 'NoneType' object has no attribute 'write'"

        # self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
            filename, 'w', content_type='text/plain', options={
                'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write(body)  ## self.fmt_msg(body)
        # self.tmp_filenames_to_clean_up.append(filename)
# [END write2]


# [END thumbnailer]


## ==================================================

class BucketTest(webapp2.RequestHandler):
    """Main page for GCS demo application."""

# [START test_vision_into_bucket]
    def vision_into_bucket(self,body):
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        
        bucket = '/' + bucket_name
        filename = bucket + '/vision-demo-testfile'
        self.create_file2(filename,body)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("Done writing filename: " + filename)
        self.response.write("Done writing body:     " + body)        
        
# [END test_vision_into_bucket]

    
# [START get_default_bucket]
    def get(self):
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(
            'Demo GCS Application running from Version: {}\n'.format(
                os.environ['CURRENT_VERSION_ID']))
        self.response.write('Using bucket name: {}\n\n'.format(bucket_name))
# [END get_default_bucket]

        bucket = '/' + bucket_name
        filename = bucket + '/demo-testfile'
        self.tmp_filenames_to_clean_up = []

        self.create_file(filename)
        self.response.write('\n\n')

        self.read_file(filename)
        self.response.write('\n\n')

        self.stat_file(filename)
        self.response.write('\n\n')

        self.create_files_for_list_bucket(bucket)
        self.response.write('\n\n')

        self.list_bucket(bucket)
        self.response.write('\n\n')

        self.list_bucket_directory_mode(bucket)
        self.response.write('\n\n')

        self.delete_files()
        self.response.write('\n\nThe demo ran successfully!\n')

# [START fmt_msg]
    def fmt_msg(self, body):
        """Format body to have a header and footer"""

        headerStr="{\nheader:'header'\n"
        bodyStr="body:'"+body+"'\n"
        footerStr="footer:'footer'}\n"
        return headerStr + bodyStr + footerStr

# [END fmt_msg]

# [START write]
    def create_file(self, filename):
        """Create a file."""

        self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
            filename, 'w', content_type='text/plain', options={
                'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write('abcde\n')
                    cloudstorage_file.write('f'*1024*4 + '\n')
        self.tmp_filenames_to_clean_up.append(filename)
# [END write]

# [START write2]
    def create_file2(self, filename,body):
        """Create a file."""

        ##ERROR
        ## self.response.write('Creating file {}\n'.format(filename))
        ## AttributeError: 'NoneType' object has no attribute 'write'"

        # self.response.write('Creating file {}\n'.format(filename))

        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        with cloudstorage.open(
            filename, 'w', content_type='text/plain', options={
                'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
                retry_params=write_retry_params) as cloudstorage_file:
                    cloudstorage_file.write(self.fmt_msg(body))
        # self.tmp_filenames_to_clean_up.append(filename)
# [END write2]

# [START read]
    def read_file(self, filename):
        self.response.write(
            'Abbreviated file content (first line and last 1K):\n')

        with cloudstorage.open(filename) as cloudstorage_file:
            self.response.write(cloudstorage_file.readline())
            cloudstorage_file.seek(-1024, os.SEEK_END)
            self.response.write(cloudstorage_file.read())
# [END read]

    def stat_file(self, filename):
        self.response.write('File stat:\n')

        stat = cloudstorage.stat(filename)
        self.response.write(repr(stat))

    def create_files_for_list_bucket(self, bucket):
        self.response.write('Creating more files for listbucket...\n')
        filenames = [bucket + n for n in [
            '/foo1', '/foo2', '/bar', '/bar/1', '/bar/2', '/boo/']]
        for f in filenames:
            self.create_file(f)

# [START list_bucket]
    def list_bucket(self, bucket):
        """Create several files and paginate through them."""

        self.response.write('Listbucket result:\n')

        # Production apps should set page_size to a practical value.
        page_size = 1
        stats = cloudstorage.listbucket(bucket + '/foo', max_keys=page_size)
        while True:
            count = 0
            for stat in stats:
                count += 1
                self.response.write(repr(stat))
                self.response.write('\n')

            if count != page_size or count == 0:
                break
            stats = cloudstorage.listbucket(
                bucket + '/foo', max_keys=page_size, marker=stat.filename)
# [END list_bucket]

    def list_bucket_directory_mode(self, bucket):
        self.response.write('Listbucket directory mode result:\n')
        for stat in cloudstorage.listbucket(bucket + '/b', delimiter='/'):
            self.response.write(stat)
            self.response.write('\n')
            if stat.is_dir:
                for subdir_file in cloudstorage.listbucket(
                        stat.filename, delimiter='/'):
                    self.response.write('  {}'.format(subdir_file))
                    self.response.write('\n')

# [START delete_files]
    def delete_files(self):
        self.response.write('Deleting files...\n')
        for filename in self.tmp_filenames_to_clean_up:
            self.response.write('Deleting file {}\n'.format(filename))
            try:
                cloudstorage.delete(filename)
            except cloudstorage.NotFoundError:
                pass
# [END delete_files]

## ==================================================



class HelloWorldMessage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("Hello world HULK!")
        self.response.out.write("\n")
        self.response.out.write("'/img', Thumbnailer \n")
        self.response.out.write("'/hw', HelloWorldMessage\n")
        self.response.out.write("'/help', HelloWorldMessage\n")
        self.response.out.write("'/bucket', BucketTest\n")
        self.response.out.write("'/info', ImageInfo\n")
        self.response.out.write("\n")
        self.response.out.write("C'est tout\n")


app = webapp2.WSGIApplication([('/img', Thumbnailer),
                               ('/hw', HelloWorldMessage),
                               ('/help', HelloWorldMessage),
                               ('/bucket', BucketTest),
                               ('/info', ImageInfo)], debug=True)
# [END all]
