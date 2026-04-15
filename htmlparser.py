SELF_CLOSING_TAGS = ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr']
INDENT = "  "
def unstring(string):
    if string[0]=="'" and string[-1]=="'":
        return string[1:-1]
    if string[0]=='"' and string[-1]=='"':
        return string[1:-1]
    return string

def strip(string, chars=[' ']):
    if not string:
        return ""
    i, j = 0, len(string)-1
    while i<=j and string[i] in chars:i+=1
    while i<=j and string[j] in chars:j-=1

    return string[i:j+1]

def all_in(arr1, arr2):
    for i in stripArray(arr1):
        if i not in arr2:
            return False
    return True

def strip_text(text):
    text = strip(text)
    text = ' '.join(stripArray(split(text, ' ')))
    text = '\n'.join(stripArray(split(text, '\n')))
    text = text.replace('\t', '')
    return text


def stripArray(array):
    return [i for i in array if i not in [None, ' ', '']]

def split(string, char=" "):
    opened = None
    elements = []
    cur=""
    for i in string:
        if opened is None and i in ['"', "'"]:
            opened = i
            cur+=i
        elif opened and i==opened:
            opened=None
            cur+=i
        elif not opened and i == char and cur:
            elements.append(cur)
            cur=""
        else:
            cur+=i
    if cur:
        elements.append(cur)
    return elements

class Element:
    def __init__(self, tag, attributes={}, children=[], innerText=""):
        self.tag = tag
        self.attributes = attributes if attributes else dict()
        self.children = children if children else list()
        self.innertext = innerText if innerText else str()

    def getAttribute(self, name, default=None):
        return self.attributes.get(name, default)
    
    def setAttribute(self, name, value):
        self.attributes[name] = value
    
    def removeAttribute(self, name):
        self.attributes.pop(name)
    
    def appendChild(self, child):
        self.children.append(child)
    
    def removeChild(self, child):
        self.children.remove(child)
    
    def getElementsByTagName(self, tag):
        elements = [self] if self.tag==tag else []
        for c in self.children:
            elements+=c.getElementsByTagName(tag)
        return elements

    def getElementsByClassName(self, class_name):
        elements = [self] if all_in(class_name.split(" "), self.getAttribute('class', '').split(' ')) else []
        for c in self.children:
            elements+=c.getElementsByClassName(class_name)
        return elements
    
    def getElementById(self, id):
        if self.attributes.get('id', '') == id:
            return self
        for c in self.children:
            if (ele:=c.getElementById(id)) is not None:
                return ele
        return None

    def querySelector(self, selector):
        if selector.startswith('#'):
            return self.getElementById(selector[1:])
        if selector.startswith('.'):
            return self.getElementsByClassName(selector[1:])[0]
        return self.getElementsByTagName(selector)[0]

    def querySelectorAll(self, selector):
        if selector.startswith('#'):
            return [self.getElementById(selector[1:])]
        if selector.startswith('.'):
            return self.getElementsByClassName(selector[1:])
        return self.getElementsByTagName(selector)

    def __repr__(self):
        return f'<{self.tag} {parse_attributes(self.attributes)}>'
    
    def __str__(self):
        return f'<{self.tag} {parse_attributes(self.attributes)}>'
    
    @property
    def innerText(self):
        children_text = ' '.join([c.innerText for c in self.children])
        if children_text:
            return self.innertext + '\n' + children_text
        return strip(self.innertext)

    def innerHTML(self, level = 0):
        if self.tag==1:
            return level * INDENT + self.innerText
        innerhtml = [level * INDENT+self.__str__()]
        for c in self.children:
            if c.tag=="Text":
                innerhtml.append(c.innertext)
            innerhtml.append(c.innerHTML(level+1) + ' ')
        innerhtml.append(f'</{self.tag}>')
        return strip(('\n'+INDENT*level).join(innerhtml))
    def structure(self, level=0):
        if self.tag=="Text":
            return ""
            return level*INDENT + '"' + self.innerText + '"'
        structure = INDENT*level + "<"+self.tag+" />\n"
        for c in self.children:
            structure+=c.structure(level+1)
        return structure


def get(string, openig, closing, breaker=None):
    i = 0
    while string[i] != openig:
        if breaker and string[i] == breaker:
            return None
        i += 1
        if i>=len(string):
            return None
    j = i
    while string[j] != closing:
        if breaker and string[j] == breaker:
            return None
        j += 1
        if j>=len(string):
            return None
    return i, j

def getUntil(string, options):
    i = 0
    while i<len(string) and string[i] not in options:
        i += 1
    return i


def getOptional(string, options={"'": "'", '"':'"'}, breaker=None):
    i = 0
    while string[i] not in options:
        if breaker and string[i] == breaker:
            return None
        i += 1
        if i>=len(string):
            return None
    j = i
    closing = options[string[i]]
    while string[j] != closing:
        if breaker and string[j] == breaker:
            return None
        j += 1
        if j>=len(string):
            return None
    return i, j
    

def parse_attributes(attrs):
    if not attrs:
        return ""
    return ' '.join([attr + ('="' + str(attrs[attr]) + '"')*int(type(attrs[attr])==str) for attr in attrs])

class DOM:
    def __init__(self, html):
        self.html = html
        self.root = Element("")
    
    def parse(self):
        import sys
        sys.setrecursionlimit(1000000)
        self._parse(self.html, [self.root])
        sys.setrecursionlimit(1000)
        if len(self.root.children)==1:
            return self.root.children[0]
        return self.root
        
    def _parse(self, html, dom):
        # checking if there is some text before tag and adding it to children as <Text/>
        textIndex = getUntil(html, "<")
        text = strip(html[:textIndex], chars=[' ', '\n', '\t'])
        if text!="":
            dom[-1].innertext=text
        html = html[textIndex:]
        if not html:
            return dom
        # getting tag
        tag = get(html, "<", ">")
        if html[tag[0]+1]=='/': # checking if its a closing tag
            tagName = strip(html[tag[0]+2:tag[1]])
            if tagName != dom[-1].tag:
                raise Exception(f"Invalid HTML, expected closing tag for {dom[-1]} found {tagName}")
            return self._parse(html[tag[1]+1:], dom[:-1])
        if not tag:
            raise Exception("Invalid HTML, expected '>'")
        # getting attributes
        i, j = tag
        innerTag = html[i+1:j]
        parts = split(innerTag)
        tag = parts[0]
        attributes = {}
        curarg = None
        for part in parts[1:]:
            if strip(part)[0]=='=':
                if not curarg:
                    raise Exception("Invalid HTML got unexpected '='")
                attributes[curarg]=unstring(strip(part.split('=')[1]))
                curarg=None
                continue
            elif curarg:
                attributes[curarg]=True
                curarg=None
            if '=' in part:
                key, value = split(part, "=")
                attributes[strip(key)] = unstring(strip(value))
                continue
            
            curarg=strip(part)
        if curarg:
            attributes[curarg]=True
        
        if tag in SELF_CLOSING_TAGS: # cheking if tag is a self closing tag
            dom[-1].appendChild(Element(tag, attributes=attributes))
            return self._parse(html[j+1:], dom)
        if tag == "script":
            p = j
            c=0
            opened = None
            while p<len(html) and ((opened is not None) or html[p:p+2]!='</'):
                # if html[p+1:p+2]=='</':
                if html[p] == opened:
                    opened = None
                    c+=1
                elif opened is None and html[p] in ['"', "'"]:
                    opened = html[p]
                    c+=1
                p+=1

            closing_tag = getUntil(html[p+2:], ">")
            if strip(html[p+2:p+2+closing_tag]) != "script":
                raise Exception("Invalid HTML, expected closing tag for 'script' got ", html[p+2:p+2+closing_tag])
            script = html[j+1:p+2]
            ele = Element(tag, attributes=attributes, innerText=script)
            dom[-1].appendChild(ele)
            return self._parse(html[p+2+closing_tag+1:], dom)
            
        ele = Element(tag, attributes=attributes)
        dom[-1].appendChild(ele)
        return self._parse(html[j+1:], dom+[ele])

