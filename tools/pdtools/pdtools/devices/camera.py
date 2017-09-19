import base64

import requests
import six


class Camera(object):
    def __init__(self, host):
        self.host = host

    def __repr__(self):
        return "Camera({})".format(self.host)

    def get_image(self):
        """
        Get an image from the camera.

        Returns image data as a BytesIO/StringIO object.
        """
        url = "http://{}/image.jpg".format(self.host)

        encoded = base64.b64encode('admin:'.encode('utf-8')).decode('ascii')

        headers = {
            'Authorization': 'Basic ' + encoded
        }

        result = requests.get(url, headers=headers)
        if result.ok:
            return six.BytesIO(result.content)

        else:
            return None
