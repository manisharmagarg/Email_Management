import pytracking
import traceback
from conf.config import EMAIL_OPEN_URL, PYTRACKING_SECRET_KEY
from emailapp import app
import traceback


class EmailTracking:

    def __init__(self):
        self.key = PYTRACKING_SECRET_KEY

    def email_encoding(self):
        try:
            click_tracking_url = pytracking.get_click_tracking_url(
                {"template_id": template_id, "segment_id": segment_id,
                 "campaign_id": campaign_id},
                base_open_tracking_url=EMAIL_OPEN_URL,
                include_webhook_url=False,
                encryption_bytestring_key=self.key)
            return click_tracking_url
        except Exception as exp:
            app.logger.warning(exp)
            app.logger.warning(traceback.format_exc())

    def email_decoding(self, full_url):
        try:
            tracking_result = pytracking.get_open_tracking_result(
                full_url, base_open_tracking_url=EMAIL_OPEN_URL,
                encryption_bytestring_key=self.key)

            app.logger.info(tracking_result)

            return tracking_result
        except Exception as exp:
            app.logger.warning(exp)
            app.logger.warning(traceback.format_exc())


# if __name__ == '__main__':
#     emailtracking = EmailTracking()
#     url = emailtracking.email_encoding()
#     emailtracking.email_decoding(url)
#     emailtracking.email_decoding('http://0.0.0.0:8000/e/o/gAAAAABasOaeBZJSpyPOrI0pgAQ1i9WMmqKVDB7cy8XFTxOEmBK67k0-yzhJ1NIDkjt8DSTUvStB_B9DvXp6Fg7Eq6Kx4CHVOyNtl6sG_BSzxHyeFQUmedmyRMANz5CmY9ATEyN8wVR9')
