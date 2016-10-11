import re as _re
from urllib.parse import quote as _quote
from html.entities import name2codepoint as _name2codepoint
from itertools import zip_longest as _zip_longest

_text_type = str
_knownNamespaces = set(['Template'])
_templatePrefix = ''
_acceptedNamespaces = ['w', 'wiktionary', 'wikt']
_discardElements = [
    'gallery', 'timeline', 'noinclude', 'pre',
    'table', 'tr', 'td', 'th', 'caption', 'div',
    'form', 'input', 'select', 'option', 'textarea',
    'ul', 'li', 'ol', 'dl', 'dt', 'dd', 'menu', 'dir',
    'ref', 'references', 'img', 'imagemap', 'source', 'small',
    'sub', 'sup', 'indicator'
]
_urlbase = ''
_selfClosingTags = ('br', 'hr', 'nobr', 'ref', 'references', 'nowiki')
_ignoredTags = (
    'abbr', 'b', 'big', 'blockquote', 'center', 'cite', 'em',
    'font', 'h1', 'h2', 'h3', 'h4', 'hiero', 'i', 'kbd',
    'p', 'plaintext', 's', 'span', 'strike', 'strong',
    'tt', 'u', 'var'
)
_placeholder_tags = {'math': 'formula', 'code': 'codice'}
_wgUrlProtocols = [
    'bitcoin:', 'ftp://', 'ftps://', 'geo:', 'git://', 'gopher://', 'http://',
    'https://', 'irc://', 'ircs://', 'magnet:', 'mailto:', 'mms://', 'news:',
    'nntp://', 'redis://', 'sftp://', 'sip:', 'sips:', 'sms:', 'ssh://',
    'svn://', 'tel:', 'telnet://', 'urn:', 'worldwind://', 'xmpp:', '//'
]
_substWords = 'subst:|safesubst:'
_listOpen = {'*': '<ul>', '#': '<ol>', ';': '<dl>', ':': '<dl>'}
_listClose = {'*': '</ul>', '#': '</ol>', ';': '</dl>', ':': '</dl>'}

_EXT_LINK_URL_CLASS = r'[^][<>"\x00-\x20\x7F\s]'
_ANCHOR_CLASS = r'[^][\x00-\x08\x0a-\x1F]'
_EXT_IMAGE_REGEX = _re.compile(
    r"""^(http://|https://)([^][<>"\x00-\x20\x7F\s]+)
    /([A-Za-z0-9_.,~%\-+&;#*?!=()@\x80-\xFF]+)\.((?i)gif|png|jpg|jpeg)$""",
    _re.X | _re.S | _re.U)
_ExtLinkBracketedRegex = _re.compile(
    '\[(((?i)' + '|'.join(_wgUrlProtocols) + ')' + _EXT_LINK_URL_CLASS + r'+)' +
    r'\s*((?:' + _ANCHOR_CLASS + r'|\[\[' + _ANCHOR_CLASS + r'+\]\])' + r'*?)\]',
    _re.S | _re.U)
_comment = _re.compile(r'<!--.*?-->', _re.DOTALL)
_nowiki = _re.compile(r'<nowiki>.*?</nowiki>')
_ignored_tag_patterns = []
_selfClosing_tag_patterns = [
    _re.compile(r'<\s*%s\b[^>]*/\s*>' % tag, _re.DOTALL | _re.IGNORECASE) for tag in _selfClosingTags
    ]
_placeholder_tag_patterns = [
    (_re.compile(r'<\s*%s(\s*| [^>]+?)>.*?<\s*/\s*%s\s*>' % (tag, tag), _re.DOTALL | _re.IGNORECASE),
     repl) for tag, repl in _placeholder_tags.items()
    ]
_bold_italic = _re.compile(r"'''''(.*?)'''''")
_bold = _re.compile(r"'''(.*?)'''")
_italic_quote = _re.compile(r"''\"([^\"]*?)\"''")
_italic = _re.compile(r"''(.*?)''")
_quote_quote = _re.compile(r'""([^"]*?)""')
_spaces = _re.compile(r' {2,}')
_dots = _re.compile(r'\.{4,}')

_tailRE = _re.compile('\w+')
_syntaxhighlight = _re.compile('&lt;syntaxhighlight .*?&gt;(.*?)&lt;/syntaxhighlight&gt;', _re.DOTALL)
_section = _re.compile(r'(==+)\s*(.*?)\s*\1')

_templates = {}
_redirects = {}
_templateCache = {}

def _get_url(uid):
    return "%s?curid=%s" % (_urlbase, uid)

def _unescape(text):
    def fixup(m):
        text = m.group(0)
        code = m.group(1)
        try:
            if text[1] == "#":  # character reference
                if text[2] == "x":
                    return chr(int(code[1:], 16))
                else:
                    return chr(int(code))
            else:  # named entity
                return chr(_name2codepoint[code])
        except:
            return text  # leave as is

    return _re.sub("&#?(\w+);", fixup, text)

def _ignoreTag(tag):
    left = _re.compile(r'<%s\b.*?>' % tag, _re.IGNORECASE | _re.DOTALL)  # both <ref> and <reference>
    right = _re.compile(r'</\s*%s>' % tag, _re.IGNORECASE)
    _ignored_tag_patterns.append((left, right))

for _tag in _ignoredTags:
    _ignoreTag(_tag)

class _Template(list):
    @classmethod
    def _parse(cls, body):
        tpl = _Template()
        start = 0
        for s, e in _findMatchingBraces(body, 3):
            tpl.append(_TemplateText(body[start:s]))
            tpl.append(_TemplateArg(body[s + 3:e - 3]))
            start = e
        tpl.append(_TemplateText(body[start:]))  # leftover
        return tpl

    def _subst(self, params, extractor, depth=0):
        if depth > extractor._maxParameterRecursionLevels:
            extractor.recursion_exceeded_3_errs += 1
            return ''

        return ''.join([tpl._subst(params, extractor, depth) for tpl in self])

    def __str__(self):
        return ''.join([_text_type(x) for x in self])

class _TemplateText(_text_type):
    def _subst(self, params, extractor, depth):
        return self

class _TemplateArg(object):
    def __init__(self, parameter):
        parts = _splitParts(parameter)
        self.name = _Template._parse(parts[0])
        if len(parts) > 1:
            self.default = _Template._parse(parts[1])
        else:
            self.default = None

    def __str__(self):
        if self.default:
            return '{{{%s|%s}}}' % (self.name, self.default)
        else:
            return '{{{%s}}}' % self.name

    def _subst(self, params, extractor, depth):
        paramName = self.name._subst(params, extractor, depth + 1)
        paramName = extractor._transform(paramName)
        res = ''
        if paramName in params:
            res = params[paramName]  # use parameter value specified in template invocation
        elif self.default:  # use the default value
            defaultValue = self.default._subst(params, extractor, depth + 1)
            res = extractor._transform(defaultValue)
        return res


class _Frame(object):
    def __init__(self, title='', args=[], prev=None):
        self.title = title
        self.args = args
        self.prev = prev
        self.depth = prev.depth + 1 if prev else 0

    def _push(self, title, args):
        return _Frame(title, args, self)

    def _pop(self):
        return self.prev

    def __str__(self):
        res = ''
        prev = this.prev
        while prev:
            if res: res += ', '
            res += '(%s, %s)' % (prev.title, prev.args)
            prev = prev.prev
        return '<Frame [' + res + ']>'

class Extractor(object):
    _keepSections = True
    _keepLists = False
    _expand_templates = True

    def __init__(self):
        self.frame = _Frame()
        self.recursion_exceeded_1_errs = 0  # template recursion within expand()
        self.recursion_exceeded_2_errs = 0  # template recursion within expandTemplate()
        self.recursion_exceeded_3_errs = 0  # parameter recursion
        self.template_title_errs = 0

    def extract(self, article_text):
        text = article_text
        text = self._transform(text)
        text = self._wiki2text(text)
        text = self._clean(text)
        text = _compact(text)              # This method does some weird stuff..
        return text

    def _transform(self, wikitext):
        res = ''
        cur = 0
        for m in _nowiki.finditer(wikitext, cur):
            res += self._transform1(wikitext[cur:m.start()]) + wikitext[m.start():m.end()]
            cur = m.end()
        res += self._transform1(wikitext[cur:])
        return res

    def _transform1(self, text):
        if Extractor._expand_templates:
            return self._expand(text)
        else:
            return _dropNested(text, r'{{', r'}}')

    def _wiki2text(self, text):
        text = _dropNested(text, r'{{', r'}}')
        text = _dropNested(text, r'{\|', r'\|}')
        text = _bold_italic.sub(r'\1', text)
        text = _bold.sub(r'\1', text)
        text = _italic_quote.sub(r'"\1"', text)
        text = _italic.sub(r'"\1"', text)
        text = _quote_quote.sub(r'"\1"', text)
        text = text.replace("'''", '').replace("''", '"')
        text = _replaceInternalLinks(text)
        text = _replaceExternalLinks(text)
        text = _magicWordsRE.sub('', text)

        res = ''
        cur = 0
        for m in _syntaxhighlight.finditer(text):
            res += _unescape(text[cur:m.start()]) + m.group(1)
            cur = m.end()
        text = res + _unescape(text[cur:])

        return text

    def _clean(self, text):
        spans = []

        for m in _comment.finditer(text):
            spans.append((m.start(), m.end()))

        for pattern in _selfClosing_tag_patterns:
            for m in pattern.finditer(text):
                spans.append((m.start(), m.end()))

        for left, right in _ignored_tag_patterns:
            for m in left.finditer(text):
                spans.append((m.start(), m.end()))
            for m in right.finditer(text):
                spans.append((m.start(), m.end()))

        text = _dropSpans(spans, text)

        for tag in _discardElements:
            text = _dropNested(text, r'<\s*%s\b[^>/]*>' % tag, r'<\s*/\s*%s>' % tag)

        text = _unescape(text)

        for pattern, placeholder in _placeholder_tag_patterns:
            index = 1
            for match in pattern.finditer(text):
                text = text.replace(match.group(), '%s_%d' % (placeholder, index))
                index += 1

        text = text.replace('<<', '«').replace('>>', '»')
        text = text.replace('\t', ' ')
        text = _spaces.sub(' ', text)
        text = _dots.sub('...', text)
        text = _re.sub(' (,:\.\)\]»)', r'\1', text)
        text = _re.sub('(\[\(«) ', r'\1', text)
        text = _re.sub(r'\n\W+?\n', '\n', text, flags=_re.U)  # lines with only punctuations
        text = text.replace(',,', ',').replace(',.', '.')
        
        return text

    _maxTemplateRecursionLevels = 30
    _maxParameterRecursionLevels = 10

    _reOpen = _re.compile('(?<!{){{(?!{)', _re.DOTALL)

    def _expand(self, wikitext):
        res = ''
        if self.frame.depth >= self._maxTemplateRecursionLevels:
            self.recursion_exceeded_1_errs += 1
            return res

        cur = 0
        for s, e in _findMatchingBraces(wikitext, 2):
            res += wikitext[cur:s] + self._expandTemplate(wikitext[s + 2:e - 2])
            cur = e
        res += wikitext[cur:]
        return res

    def _templateParams(self, parameters):
        _templateParams = {}

        if not parameters:
            return _templateParams

        unnamedParameterCounter = 0

        for param in parameters:
            m = _re.match(' *([^=]*?) *?=(.*)', param, _re.DOTALL)
            if m:
                parameterName = m.group(1).strip()
                parameterValue = m.group(2)

                if ']]' not in parameterValue:  # if the value does not contain a link, trim whitespace
                    parameterValue = parameterValue.strip()
                _templateParams[parameterName] = parameterValue
            else:
                unnamedParameterCounter += 1

                if ']]' not in param:  # if the value does not contain a link, trim whitespace
                    param = param.strip()
                _templateParams[str(unnamedParameterCounter)] = param
        return _templateParams

    def _expandTemplate(self, body):
        if self.frame.depth >= self._maxTemplateRecursionLevels:
            self.recursion_exceeded_2_errs += 1
            return ''

        parts = _splitParts(body)
        title = parts[0].strip()
        title = self._expand(title)

        subst = False
        if _re.match(_substWords, title, _re.IGNORECASE):
            title = _re.sub(_substWords, '', title, 1, _re.IGNORECASE)
            subst = True

        colon = title.find(':')
        if colon > 1:
            funct = title[:colon]
            parts[0] = title[colon + 1:].strip()  # side-effect (parts[0] not used later)
            ret = _callParserFunction(funct, parts, self)
            return ret

        title = _fullyQualifiedTemplateTitle(title)
        if not title:
            self.template_title_errs += 1
            return ''

        redirected = _redirects.get(title)
        if redirected:
            title = redirected

        if title in _templateCache:
            template = _templateCache[title]
        elif title in _templates:
            template = _Template._parse(_templates[title])
            _templateCache[title] = template
            del _templates[title]
        else:
            return ''

        params = parts[1:]

        if not subst:
            params = [self._transform(p) for p in params]

        params = self._templateParams(params)
        self.frame = self.frame._push(title, params)
        instantiated = template._subst(params, self)
        value = self._transform(instantiated)
        self.frame = self.frame._pop()
        return value

def _splitParts(paramsList):
    sep = '|'
    parameters = []
    cur = 0
    for s, e in _findMatchingBraces(paramsList):
        par = paramsList[cur:s].split(sep)
        if par:
            if parameters:
                parameters[-1] += par[0]
                if len(par) > 1:
                    parameters.extend(par[1:])
            else:
                parameters = par
        elif not parameters:
            parameters = ['']  # create first param
        parameters[-1] += paramsList[s:e]
        cur = e
    par = paramsList[cur:].split(sep)
    if par:
        if parameters:
            parameters[-1] += par[0]
            if len(par) > 1:
                parameters.extend(par[1:])
        else:
            parameters = par

    return parameters


def _findMatchingBraces(text, ldelim=0):
    if ldelim:  # 2-3
        _reOpen = _re.compile('[{]{%d,}' % ldelim)  # at least ldelim
        reNext = _re.compile('[{]{2,}|}{2,}')  # at least 2
    else:
        _reOpen = _re.compile('{{2,}|\[{2,}')
        reNext = _re.compile('{{2,}|}{2,}|\[{2,}|]{2,}')  # at least 2

    cur = 0
    while True:
        m1 = _reOpen.search(text, cur)
        if not m1:
            return
        lmatch = m1.end() - m1.start()
        if m1.group()[0] == '{':
            stack = [lmatch]  # stack of opening braces lengths
        else:
            stack = [-lmatch]  # negative means [
        end = m1.end()
        while True:
            m2 = reNext.search(text, end)
            if not m2:
                return  # unbalanced
            end = m2.end()
            brac = m2.group()[0]
            lmatch = m2.end() - m2.start()

            if brac == '{':
                stack.append(lmatch)
            elif brac == '}':
                while stack:
                    openCount = stack.pop()  # opening span
                    if openCount == 0:  # illegal unmatched [[
                        continue
                    if lmatch >= openCount:
                        lmatch -= openCount
                        if lmatch <= 1:  # either close or stray }
                            break
                    else:
                        # put back unmatched
                        stack.append(openCount - lmatch)
                        break
                if not stack:
                    yield m1.start(), end - lmatch
                    cur = end
                    break
                elif len(stack) == 1 and 0 < stack[0] < ldelim:
                    cur = end
                    break
            elif brac == '[':  # [[
                stack.append(-lmatch)
            else:  # ]]
                while stack and stack[-1] < 0:  # matching [[
                    openCount = -stack.pop()
                    if lmatch >= openCount:
                        lmatch -= openCount
                        if lmatch <= 1:  # either close or stray ]
                            break
                    else:
                        stack.append(lmatch - openCount)
                        break
                if not stack:
                    yield m1.start(), end - lmatch
                    cur = end
                    break
                cur = end


def _findBalanced(text, openDelim=['[['], closeDelim=[']]']):
    openPat = '|'.join([_re.escape(x) for x in openDelim])
    afterPat = {o: _re.compile(openPat + '|' + c, _re.DOTALL) for o, c in zip(openDelim, closeDelim)}
    stack = []
    start = 0
    cur = 0
    startSet = False
    startPat = _re.compile(openPat)
    nextPat = startPat
    while True:
        next = nextPat.search(text, cur)
        if not next:
            return
        if not startSet:
            start = next.start()
            startSet = True
        delim = next.group(0)
        if delim in openDelim:
            stack.append(delim)
            nextPat = afterPat[delim]
        else:
            opening = stack.pop()
            if stack:
                nextPat = afterPat[stack[-1]]
            else:
                yield start, next.end()
                nextPat = startPat
                start = next.end()
                startSet = False
        cur = next.end()


def _if_empty(*rest):
    for arg in rest:
        if arg:
            return arg
    return ''

def _functionParams(args, vars):
    params = {}
    index = 1
    for var in vars:
        value = args.get(var)
        if value is None:
            value = args.get(str(index))
            if value is None:
                value = ''
            else:
                index += 1
        params[var] = value
    return params

def _string_sub(args):
    params = _functionParams(args, ('s', 'i', 'j'))
    s = params.get('s', '')
    i = int(params.get('i', 1) or 1) # or handles case of '' value
    j = int(params.get('j', -1) or -1)
    if i > 0: i -= 1             # lua is 1-based
    if j < 0: j += 1
    if j == 0: j = len(s)
    return s[i:j]


def _string_len(args):
    params = _functionParams(args, ('s'))
    s = params.get('s', '')
    return len(s)

def _string_find(args):
    params = _functionParams(args, ('source', 'target', 'start', 'plain'))
    source = params.get('source', '')
    pattern = params.get('target', '')
    start = int('0'+params.get('start', 1)) - 1 # lua is 1-based
    plain = int('0'+params.get('plain', 1))
    if source == '' or pattern == '':
        return 0
    if plain:
        return source.find(pattern, start) + 1 # lua is 1-based
    else:
        return (_re.compile(pattern).search(source, start) or -1) + 1
        
def _roman_main(args):
    num = int(float(args.get('1')))
 
    if 0 > num or num >= 5000:
        return args.get('2', 'N/A')
 
    def _toRoman(n, romanNumeralMap):
        result = ""
        for integer, numeral in romanNumeralMap:
            while n >= integer:
                result += numeral
                n -= integer
        return result

    _smallRomans = (
        (1000, "M"),
        (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
        (90, "XC"), (50, "L"), (40, "XL"), (10, "X"),
        (9, "IX"), (5, "V"), (4, "IV"), (1, "I") 
    )
    return _toRoman(num, _smallRomans)

_modules = {
    'convert': {
        'convert': lambda x, u, *rest: x + ' ' + u,
    },
    'If empty': {
        'main': _if_empty
    },
    'String': {
        'sub': _string_sub,
        'len': _string_len,
        'find': _string_find
    },
    'Roman': {
        'main': _roman_main
    },
    'Numero romano': {
        'main': _roman_main
    }
}

class _MagicWords(object):
    def __init__(self):
        self.values = {'!': '|'}

    def __getitem__(self, name):
        return self.values.get(name)

    def __setitem__(self, name, value):
        self.values[name] = value

    _switches = (
        '__NOTOC__',
        '__FORCETOC__',
        '__TOC__',
        '__TOC__',
        '__NEWSECTIONLINK__',
        '__NONEWSECTIONLINK__',
        '__NOGALLERY__',
        '__HIDDENCAT__',
        '__NOCONTENTCONVERT__',
        '__NOCC__',
        '__NOTITLECONVERT__',
        '__NOTC__',
        '__START__',
        '__END__',
        '__INDEX__',
        '__NOINDEX__',
        '__STATICREDIRECT__',
        '__DISAMBIG__'
    )

_magicWordsRE = _re.compile('|'.join(_MagicWords._switches))

def _ucfirst(string):
    if string:
        return string[0].upper() + string[1:]
    else:
        return ''


def _lcfirst(string):
    if string:
        if len(string) > 1:
            return string[0].lower() + string[1:]
        else:
            return string.lower()
    else:
        return ''


def _fullyQualifiedTemplateTitle(templateTitle):
    if templateTitle.startswith(':'):
        return _ucfirst(templateTitle[1:])
    else:
        m = _re.match('([^:]*)(:.*)', templateTitle)
        if m:
            prefix = _normalizeNamespace(m.group(1))
            if prefix in _knownNamespaces:
                return prefix + _ucfirst(m.group(2))

    if templateTitle:
        return _templatePrefix + _ucfirst(templateTitle)
    else:
        return ''  # caller may log as error


def _normalizeNamespace(ns):
    return _ucfirst(ns)

class _Infix:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return _Infix(lambda x, self=self, other=other: self.function(other, x))

    def __or__(self, other):
        return self.function(other)

    def __rlshift__(self, other):
        return _Infix(lambda x, self=self, other=other: self.function(other, x))

    def __rshift__(self, other):
        return self.function(other)

    def __call__(self, value1, value2):
        return self.function(value1, value2)

_ROUND = _Infix(lambda x, y: round(x, y))

def _sharp_expr(extr, expr):
    """Tries converting a lua expr into a Python expr."""
    try:
        expr = extr._expand(expr)
        expr = _re.sub('(?<![!<>])=', '==', expr) # negative lookbehind
        expr = _re.sub('mod', '%', expr)          # no \b here
        expr = _re.sub('\bdiv\b', '/', expr)
        expr = _re.sub('\bround\b', '|_ROUND|', expr)
        return _text_type(eval(expr))
    except:
        return '<span class="error">%s</span>' % expr


def _sharp_if(extr, testValue, valueIfTrue, valueIfFalse=None, *args):
    if testValue.strip():
        valueIfTrue = extr._expand(valueIfTrue.strip()) # eval
        if valueIfTrue:
            return valueIfTrue
    elif valueIfFalse:
        return extr._expand(valueIfFalse.strip()) # eval
    return ""


def _sharp_ifeq(extr, lvalue, rvalue, valueIfTrue, valueIfFalse=None, *args):
    rvalue = rvalue.strip()
    if rvalue:
        if lvalue.strip() == rvalue:
            if valueIfTrue:
                return extr._expand(valueIfTrue.strip())
        else:
            if valueIfFalse:
                return extr._expand(valueIfFalse.strip())
    return ""


def _sharp_iferror(extr, test, then='', Else=None, *args):
    if _re.match('<(?:strong|span|p|div)\s(?:[^\s>]*\s+)*?class="(?:[^"\s>]*\s+)*?error(?:\s[^">]*)?"', test):
        return extr._expand(then.strip())
    elif Else is None:
        return test.strip()
    else:
        return extr._expand(Else.strip())


def _sharp_switch(extr, primary, *params):
    primary = primary.strip()
    found = False  # for fall through cases
    default = None
    rvalue = None
    lvalue = ''
    for param in params:
        pair = param.split('=', 1)
        lvalue = extr._expand(pair[0].strip())
        rvalue = None
        if len(pair) > 1:
            rvalue = extr._expand(pair[1].strip())
            if found or primary in [v.strip() for v in lvalue.split('|')]:
                return rvalue
            elif lvalue == '#default':
                default = rvalue
            rvalue = None  # avoid defaulting to last case
        elif lvalue == primary:
            found = True
    if rvalue is not None:
        return lvalue
    elif default is not None:
        return default
    return ''


def _sharp_invoke(module, function, args):
    functions = _modules.get(module)
    if functions:
        funct = functions.get(function)
        if funct:
            return str(funct(args))
    return ''

_parserFunctions = {
    '#expr': _sharp_expr,
    '#if': _sharp_if,
    '#ifeq': _sharp_ifeq,
    '#iferror': _sharp_iferror,
    '#ifexpr': lambda *args: '',  # not supported
    '#ifexist': lambda *args: '',  # not supported
    '#rel2abs': lambda *args: '',  # not supported
    '#switch': _sharp_switch,
    '#language': lambda *args: '',  # not supported
    '#time': lambda *args: '',  # not supported
    '#timel': lambda *args: '',  # not supported
    '#titleparts': lambda *args: '',  # not supported
    'urlencode': lambda string, *rest: _quote(string.encode('utf-8')),
    'lc': lambda string, *rest: string.lower() if string else '',
    'lcfirst': lambda string, *rest: _lcfirst(string),
    'uc': lambda string, *rest: string.upper() if string else '',
    'ucfirst': lambda string, *rest: _ucfirst(string),
    'int': lambda string, *rest: str(int(string)),
}


def _callParserFunction(functionName, args, extractor):
    try:
        functionName = functionName.lower()
        if functionName == '#invoke':
            module, fun = args[0].strip(), args[1].strip()
            if len(args) == 2:
                templateTitle = _fullyQualifiedTemplateTitle(module)
                params = None
                frame = extractor.frame
                while frame:
                    if frame.title == templateTitle:
                        params = frame.args
                        break
                    frame = frame.prev
            else:
                params = [extractor._transform(p) for p in args[2:]] # evaluates them
                params = extractor._templateParams(params)
            ret = _sharp_invoke(module, fun, params)
            return ret
        if functionName in _parserFunctions:
            return _parserFunctions[functionName](extractor, *args)
    except:
        return ""
    return ""




def _dropNested(text, openDelim, closeDelim):
    openRE = _re.compile(openDelim, _re.IGNORECASE)
    closeRE = _re.compile(closeDelim, _re.IGNORECASE)
    spans = []                  # pairs (s, e) for each partition
    nest = 0                    # nesting level
    start = openRE.search(text, 0)
    if not start:
        return text
    end = closeRE.search(text, start.end())
    next = start
    while end:
        next = openRE.search(text, next.end())
        if not next:            # termination
            while nest:         # close all pending
                nest -= 1
                end0 = closeRE.search(text, end.end())
                if end0:
                    end = end0
                else:
                    break
            spans.append((start.start(), end.end()))
            break
        while end.end() < next.start():
            if nest:
                nest -= 1
                last = end.end()
                end = closeRE.search(text, end.end())
                if not end:     # unbalanced
                    if spans:
                        span = (spans[0][0], last)
                    else:
                        span = (start.start(), last)
                    spans = [span]
                    break
            else:
                spans.append((start.start(), end.end()))
                start = next
                end = closeRE.search(text, next.end())
                break           # { }
        if next != start:
            nest += 1
    return _dropSpans(spans, text)


def _dropSpans(spans, text):
    spans.sort()
    res = ''
    offset = 0
    for s, e in spans:
        if offset <= s:         # handle nesting
            if offset < s:
                res += text[offset:s]
            offset = e
    res += text[offset:]
    return res

def _replaceInternalLinks(text):
    cur = 0
    res = ''
    for s, e in _findBalanced(text):
        m = _tailRE.match(text, e)
        if m:
            trail = m.group(0)
            end = m.end()
        else:
            trail = ''
            end = e
        inner = text[s + 2:e - 2]
        pipe = inner.find('|')
        if pipe < 0:
            title = inner
            label = title
        else:
            title = inner[:pipe].rstrip()
            curp = pipe + 1
            for s1, e1 in _findBalanced(inner):
                last = inner.rfind('|', curp, s1)
                if last >= 0:
                    pipe = last  # advance
                curp = e1
            label = inner[pipe + 1:].strip()
        res += text[cur:s] + _makeInternalLink(title, label) + trail
        cur = end
    return res + text[cur:]

def _makeInternalLink(title, label):
    colon = title.find(':')
    if colon > 0 and title[:colon] not in _acceptedNamespaces:
        return ''
    if colon == 0:
        colon2 = title.find(':', colon + 1)
        if colon2 > 1 and title[colon + 1:colon2] not in _acceptedNamespaces:
            return ''
    return label

def _replaceExternalLinks(text):
    s = ''
    cur = 0
    for m in _ExtLinkBracketedRegex.finditer(text):
        s += text[cur:m.start()]
        cur = m.end()

        url = m.group(1)
        label = m.group(3)

        m = _EXT_IMAGE_REGEX.match(label)
        if m:
            label = ''

        s += label

    return s + text[cur:]

def _compact(text):
    page = []             # list of paragraph
    headers = {}          # Headers for unfilled sections
    emptySection = False  # empty sections are discarded
    listLevel = []        # nesting of lists

    for line in text.split('\n'):
        if not line:
            continue
        m = _section.match(line)
        if m:
            title = m.group(2)
            lev = len(m.group(1)) # header level
            if title and title[-1] not in '!?':
                title += '.'    # terminate sentence.
            headers[lev] = title
            for i in list(headers.keys()):
                if i > lev:
                    del headers[i]
            emptySection = True
            listLevel = []
            continue
        elif line.startswith('++'):
            title = line[2:-2]
            if title:
                if title[-1] not in '!?':
                    title += '.'
                page.append(title)
        elif line[0] == ':':
            continue
        elif line[0] in '*#;:':
            i = 0
            for c, n in _zip_longest(listLevel, line, fillvalue=''):
                if not n or n not in '*#;:': # shorter or different
                    if c:
                        listLevel = listLevel[:-1]
                        continue
                    else:
                        break
                if c != n and (not c or (c not in ';:' and n not in ';:')):
                    if c:
                        listLevel = listLevel[:-1]
                    listLevel += n
                i += 1
            n = line[i - 1]  # last list char
            line = line[i:].strip()
            if line:
                if Extractor._keepLists:
                    items = sorted(headers.items())
                    for i, v in items:
                        page.append(v)
                    headers.clear()
                    bullet = '1. ' if n == '#' else '- '
                    page.append('{0:{1}s}'.format(bullet, len(listLevel)) + line)
        elif len(listLevel):
            page.append(line)
            listLevel = []
        elif line[0] in '{|' or line[-1] == '}':
            continue
        elif (line[0] == '(' and line[-1] == ')') or line.strip('.-') == '':
            continue
        elif len(headers):
            if Extractor._keepSections:
                items = sorted(headers.items())
                for i, v in items:
                    page.append(v)
            headers.clear()
            page.append(line)  # first line
            emptySection = False
        elif not emptySection:
            if line[0] != ' ':  # dangerous
                page.append(line)

    return "".join(page)
