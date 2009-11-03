from django.utils import simplejson 
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.xmlutils import SimplerXMLGenerator
from StringIO import StringIO

class JSONResourcePublisher(object):
    def publish(self, data, root=None):
        return simplejson.dumps(data, cls=DjangoJSONEncoder)

class XMLResourcePublisher(object):
    def publish(self, data, root=None):
        root = root or 'resource'
        output = StringIO()
        xml = SimplerXMLGenerator(output, settings.DEFAULT_CHARSET)
        xml.startDocument()
        xml.startElement("%s-list" % root, {})
        for entry in data:
            xml.startElement(root, {})
            for key, value in entry.items():
                xml.startElement(key, {})
                if value:
                    xml.characters(unicode(value))
                else:
                    xml.addQuickElement('None')
                xml.endElement(key)
            xml.endElement(root)
        xml.endElement("%s-list" % root)
        value = output.getvalue()
        output.close()
        return value

