class Headers:
    def __init__(self, sid):
        try:
            headers = {
                "NDCDEVICEID": "019B6133991CBC2428F822E55AEF0499B3E674928B3268072CC9381881024F07047DCB9A82899C91B8"
            }
            self.header = headers
            if sid != 0:
                headers['NDCAUTH'] = "sid="+sid['sid']
                self.uid = sid['auid']
            self.headers = headers
        except: print('error in lib report!')