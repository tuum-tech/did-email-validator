import datetime
from mongoengine import StringField, DictField, DateTimeField, Document

class DidImport(Document):
    did = StringField(max_length=128)
    created = DateTimeField()
    modified = DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):
        return str(self.as_dict())

    def as_dict(self):
        return {
            "did": self.did,
            "created": str(self.created),
            "modified": str(self.modified)
        }

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.datetime.utcnow()
        self.modified = datetime.datetime.utcnow()
        return super(DidImport, self).save(*args, **kwargs)