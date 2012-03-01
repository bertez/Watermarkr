# -*- coding: utf-8 -*-

import cherrypy
import os
import helpers
import settings

from mako.template import Template
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories=['templates'], default_filters=['decode.utf8'])

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)


class WaterMarkr(object):

    def index(self):
        tmpl = lookup.get_template('index.html')
        return tmpl.render(title='Watermarkr')

    index.exposed = True

    def upload(self, theFile = None):
        if not theFile:
            return helpers.generate_error('Error processing request','Try changing the filename')

        size = 0
        allData = ''
        while True and size < settings.MAX_FILE_SIZE:
            data = theFile.file.read(8192)
            if not data:
                break
            size += len(data)
            allData += data
        else:
            return helpers.generate_error('File too big','The max file size is 2mb')

        finalName = helpers.getmd5(allData) + os.path.splitext(theFile.filename)[1]

        storageFile = absDir + settings.UPLOADS_DIR + finalName

        tmpl = lookup.get_template('uploaded.html')

        if not os.path.exists(storageFile):
            output = open(storageFile, 'w')
            output.write(allData)
            output.close()

            import Image

            try:
                im=Image.open(storageFile)
                mark = Image.open(settings.WATERMARK_IMG)

                position = (im.size[0]-mark.size[0] - 30, im.size[1]-mark.size[1] - 30)

                helpers.watermark(im, mark, position, 0.9).save(absDir + settings.UPLOADS_DIR + settings.PROCESSED_PREFIX + finalName)

                return tmpl.render(title='Uploaded', filename=finalName)
            except IOError:
                os.remove(storageFile)
                return helpers.generate_error('Invalid format', 'You can only upload image files');
        else:
            return tmpl.render(title='Uploaded', filename=finalName)

    upload.exposed = True

cherrypy.quickstart(WaterMarkr(), '/', 'rkr.config')
