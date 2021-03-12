import pytracking
import traceback
import logging
from conf.config import EMAIL_OPEN_URL, PYTRACKING_SECRET_KEY


class EmailTracking:

    def __init__(self):
        self.key = PYTRACKING_SECRET_KEY
        self.log = logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    def email_encoding(self, template_id, campaign_id, segment_id):
        try:
            click_tracking_url = pytracking.get_open_tracking_url(
                {"template_id": template_id, "segment_id": segment_id, "campaign_id": campaign_id},
                base_open_tracking_url=EMAIL_OPEN_URL,
                include_webhook_url=False,
                encryption_bytestring_key=self.key)

            return click_tracking_url
        except Exception as e:
            logging.warning('[EmailTracking] :: email_encoding() :: Got exception: ' % e)

    def email_decoding(self, full_url):
        try:
            tracking_result = pytracking.get_open_tracking_result(
                full_url, base_open_tracking_url=EMAIL_OPEN_URL,
                encryption_bytestring_key=self.key)

            return tracking_result
        except Exception as e:
            logging.warning('[EmailTracking] :: email_decoding() :: Got exception: ' % e)
            logging.warning(traceback.format_exc())
