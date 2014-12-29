#!/usr/bin/env python2
# coding: utf-8

import cgi

# TeX macro
def tex(text, kind):
	if not text:
		return u''
	
	text = cgi.escape(text)
	
	return u'<div class="mathjax">$${0}$$</div>'.format(text)

# code macro
def code(text, kind, lang = None):
	if not text:
		return u''
	
	if lang:
		return u'<pre class="prettyprint lang-{0}">{1}</pre>'.format(
				lang, cgi.escape(text))
	
	else:
		return u'<pre class="prettyprint">{0}</pre>'.format(cgi.escape(text))

# font macro
def font(text, kind, size = None, color = None):
	
	if text:
		tag = u'<span style="'
	
	else:
		tag = u'<div style="'
	
	if size:
		tag += u'font-size: {0}px;'.format(size)
	
	if color:
		tag += u'color: {0};'.format(color)
	
	if text:
		tag += u'">{0}</span>'.format(text)
	
	else:
		tag += u'">'
		
	return tag

# endfont macro
def endfont(text, kind):
	return u'</div>'

# br macro
def br(text, kind):
	return u'<br />'

# nop macro
def nop(text, kind):
	return u''

# img macro
def img(text, kind, src, alt = u'', href = None):
	
	if href is None:
		return u'<img src="{0}" alt="{1}" />'.format(src, alt)
	
	return u'<a href="{0}"><img src="{1}" alt="{2}" /></a>'.format(href, src, alt)

# textarea macro
def textarea(text, kind, rows = 10):
	
	return u'<textarea rows="{0}" cols="70">{1}</textarea>'.format(rows, cgi.escape(text))

if __name__ == '__main__':
	pass

# vim: se noet ts=4 sw=4 sts=0 ft=python :
