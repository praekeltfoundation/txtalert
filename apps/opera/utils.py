from collections import namedtuple

def element_to_dict(element):
    """
    Turn an ElementTree element '<data><el>1</el></data>' into {el: 1}. Not recursive!
    
    >>> data = ET.fromstring("<data><el>1</el></data>")
    >>> element_to_dict(data)
    {'el': '1'}
    >>>
    
    """
    return dict([(child.tag, child.text) for child in element.getchildren()])

def element_to_namedtuple(element):
    """
    Turn an ElementTree element into an object with named params. Not recursive!
    
    >>> data = ET.fromstring("<data><el>1</el></data>")
    >>> element_to_namedtuple(data)
    data(el='1')
    
    """
    d = element_to_dict(element)
    klass = namedtuple(element.tag, d.keys())
    return klass._make(d.values())

