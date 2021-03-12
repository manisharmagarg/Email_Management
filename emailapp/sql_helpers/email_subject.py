from .database import Database


class EmailSubjectHelper(Database):

    def __init__(self, *args):
        super(EmailSubjectHelper, self).__init__(*args)

    def create_email_subject(self, email_subject, preview_text, user_id):
        data = {"email_subject": email_subject, "preview_text": preview_text, "user_id": user_id}
        email_subject_id = self.insert('email_subject', data)
        return email_subject_id
