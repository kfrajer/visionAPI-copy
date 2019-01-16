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
        photo=jdata['requests'][0]['image']['content']
        photostr=base64.b64decode(photo)
        
        if photostr:
            img = images.Image(image_data=photostr)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write("Image information: WxH ")
            self.response.out.write(str(img.width) + "x" + str(img.height))
            return

        # Either "id" wasn't provided, or there was no image with that ID
        # in the datastore.
        self.error(404)
# [END thumbnailer]

class HelloWorldMessage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("Hello world HULK!")

app = webapp2.WSGIApplication([('/img', Thumbnailer),
                               ('/hw', HelloWorldMessage),
                               ('/info', ImageInfo)], debug=True)
# [END all]
