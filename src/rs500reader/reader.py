from sys import stderr
from typing import Optional

import hid
import time

from .do import Response, TempHum


class Rs500Reader(object):

    def __init__(self, vendor_id=0x0483, product_id=0x5750):
        self.vendor = vendor_id
        self.product = product_id

    def __query(self) -> list:
        try:
            rs500_hid = hid.device()
            rs500_hid.open(self.vendor, self.product)
            rs500_hid.set_nonblocking(1)
            # Inquiry 04, returns the temperatures and humidity
            rs500_hid.write([0x7b, 0x03, 0x40, 0x7d] + [0] * 60)
            time.sleep(0.75)
            data = []
            while True:
                d = rs500_hid.read(64)
                if d:
                    data.extend(d)
                else:
                    break
            rs500_hid.close()
            return data
        except IOError as e:
            print(
                'Read error reading from HID device: "{}"; either the hardware is not present or '
                'defective, or there is a permissions problem.'.format(s),
                file=stderr
            )
            raise

    def get_data(self) -> Optional[Response]:
        try:
            data = self.__query()
        except IOError:
            return None
        if len(data) != 64:
            print('Invalid length: {}'.format(len(data)), file=stderr)
            return None
        response = Response()
        channel = 0
        for i in range(1, 24, 3):
            channel += 1
            t1 = data[i]
            t2 = data[i+1]
            hu = data[i+2]
            if not (t1 == 0x7f and t2 == 0xff and hu == 0xff):
                response.set_channel_data(channel, TempHum.from_protocol([t1, t2], hu))
        return response
