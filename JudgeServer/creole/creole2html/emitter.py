# coding: utf-8


"""
    WikiCreole to HTML converter

    :copyleft: 2008-2011 by python-creole team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from __future__ import division, absolute_import, print_function, unicode_literals

from xml.sax.saxutils import escape
import sys
import traceback
import mimetypes
import urllib
import re
import functools
import creole

from urlparse import urlparse

from creole.creole2html.parser import CreoleParser
from creole.py3compat import TEXT_TYPE, repr2
from creole.shared.utils import string2dict

from creole.creole2html import macro

class HtmlEmitter:
    """
    Generate HTML output for the document
    tree consisting of DocNodes.
    """
    def __init__(self, root, macros=None, verbose=1, stderr=sys.stderr, env = {}):
        self.root = root
#        self.macros = macros
        self.verbose = verbose
        self.stderr  = stderr
        self.env     = env
        
        self.macros = {
                u'tex'     : macro.tex,
                u'code'    : macro.code,
                u'c'       : functools.partial(macro.code, lang = u'c'),
                u'cpp'     : functools.partial(macro.code, lang = u'cpp'),
                u'java'    : functools.partial(macro.code, lang = u'java'),
                u'python'  : functools.partial(macro.code, lang = u'py'),
                u'pascal'  : functools.partial(macro.code, lang = u'pascal'),
                u'font'    : macro.font,
                u'endfont' : macro.endfont,
                u'br'      : macro.br,
                u'nop'     : macro.nop,
                u'img'     : macro.img,
                u'textarea': macro.textarea,
                
                u'if_admin':  self.if_admin,
                u'if_login':  self.if_login,
                u'if_logout': self.if_logout
                }

    def get_text(self, node):
        """Try to emit whatever text is in the node."""
        try:
            return node.children[0].content or ''
        except:
            return node.content or ''

    def html_escape(self, text):
        return escape(text)

    def attr_escape(self, text):
        return self.html_escape(text).replace('"', '&quot')

    # *_emit methods for emitting nodes of the document:

    def document_emit(self, node):
        return self.emit_children(node)

    def text_emit(self, node):
        return self.html_escape(node.content)

    def separator_emit(self, node):
        return '<hr />\n\n'

    def paragraph_emit(self, node):
    	
    	child = self.emit_children(node)
    	
    	if child.find('<img') > -1:
    		return '<p class="img">%s</p>\n' % child
    	
    	else:
        	return '<p>%s</p>\n' % child

    def _list_emit(self, node, list_type):
        if node.parent.kind in ("document",):
            # The first list item
            formatter = ''
        else:
            formatter = '\n'

        if list_type == "li":
            formatter += (
                '%(i)s<%(t)s>%(c)s</%(t)s>'
            )
        else:
            formatter += (
                '%(i)s<%(t)s>%(c)s\n'
                '%(i)s</%(t)s>'
            )
        return formatter % {
            "i": "\t" * node.level,
            "c": self.emit_children(node),
            "t": list_type,
        }

    def bullet_list_emit(self, node):
        return self._list_emit(node, list_type="ul")

    def number_list_emit(self, node):
        return self._list_emit(node, list_type="ol")

    def list_item_emit(self, node):
        return self._list_emit(node, list_type="li")

    def table_emit(self, node):
        return '<table>\n%s</table>\n' % self.emit_children(node)

    def table_row_emit(self, node):
        return '<tr>\n%s</tr>\n' % self.emit_children(node)

    def table_cell_emit(self, node):
        return '\t<td>%s</td>\n' % self.emit_children(node)

    def table_head_emit(self, node):
        return '\t<th>%s</th>\n' % self.emit_children(node)

    #--------------------------------------------------------------------------

    def _typeface(self, node, tag):
        return '<%(tag)s>%(data)s</%(tag)s>' % {
            "tag": tag,
            "data": self.emit_children(node),
        }

    # TODO: How can we generalize that:
    def emphasis_emit(self, node):
        return self._typeface(node, tag="em")
    def strong_emit(self, node):
        return self._typeface(node, tag="strong")
    def monospace_emit(self, node):
        return self._typeface(node, tag="tt")
    def superscript_emit(self, node):
        return self._typeface(node, tag="sup")
    def subscript_emit(self, node):
        return self._typeface(node, tag="sub")
    
    def underline_emit(self, node):
        return u'<span class="underline">{0}</span>'.format(self.emit_children(node))
    
#        return self._typeface(node, tag="u")

    def small_emit(self, node):
        return self._typeface(node, tag="small")
    def delete_emit(self, node):
        return self._typeface(node, tag="del")

    #--------------------------------------------------------------------------

    def header_emit(self, node):
        return '<h{0}>{1}</h{0}>\n'.format(
                node.level + 1, self.html_escape(node.content))
        
#        return '<h%d>%s</h%d>\n' % (
#            node.level, self.html_escape(node.content), node.level)

    def preformatted_emit(self, node):
        return '<pre>%s</pre>' % self.html_escape(node.content)

    def link_emit(self, node):
        target = node.content
        if node.children:
            inside = self.emit_children(node)
        else:
            inside = self.html_escape(target)
        
        page    = re.match(ur'^page:(\w+)$', target)
        problem = re.match(ur'^problem:(\d+)$', target)
        contest = re.match(ur'^contest:(\w+)$', target)
        
        if page:
            target = u'/page/{0}/'.format(page.group(1))
        
        elif problem:
            target = u'/problem/{0}/'.format(problem.group(1))
        
        elif contest:
            target = u'/contest/{0}/'.format(contest.group(1))
        
        return '<a href="%s">%s</a>' % (
            self.attr_escape(target), inside)

    def image_emit(self, node):
        target = node.content
        text = self.attr_escape(self.get_text(node))
        
        # MIME TYPE を取得
        mime = mimetypes.guess_type(target)
        
        url = urlparse(target)
        
        # 相対 URL な場合、エスケープ処理を行う
        if not url.scheme and url.path[0] != '/':
            target = urllib.quote(target.encode('utf-8'))
            
        # 画像かどうか調べる
        # 画像であれば、img 要素を返す
        if mime[0] and mime[0].startswith('image'):
            return '<img src="%s" title="%s" alt="%s" />' % (
                self.attr_escape(target), text, text)
        
        else:
            return '<a href="%s">%s</a>' % (
                    self.attr_escape(target), text)
    

    def macro_emit(self, node):
        #print(node.debug())
        macro_name = node.macro_name
        text = node.content
        macro = None

        args = node.macro_args
        try:
            macro_kwargs = string2dict(args)
        except ValueError as e:
            exc_info = sys.exc_info()
            return self.error(
                "Wrong macro arguments: %s for macro '%s' (maybe wrong macro tag syntax?)" % (
                    repr2(args), macro_name
                ),
                exc_info
            )

        macro_kwargs[u'text'] = text
        macro_kwargs[u'kind'] = node.kind

        if callable(self.macros) == True:
            raise DeprecationWarning("Callable macros are not supported anymore!")
            return

        exc_info = None
        if isinstance(self.macros, dict):
            try:
                macro = self.macros[macro_name]
            except KeyError as e:
                exc_info = sys.exc_info()
        else:
            try:
                macro = getattr(self.macros, macro_name)
            except AttributeError as e:
                exc_info = sys.exc_info()

        if macro == None:
            return self.error(
                "Macro '%s' doesn't exist" % macro_name,
                exc_info
            )

        try:
            result = macro(**macro_kwargs)
        except TypeError as err:
            msg = "Macro '%s' error: %s" % (macro_name, err)
            exc_info = sys.exc_info()
            if self.verbose > 1:
                # Inject more information about the macro in traceback
                etype, evalue, etb = exc_info
                import inspect
                filename = inspect.getfile(macro)
                try:
                    sourceline = inspect.getsourcelines(macro)[0][0].strip()
                except IOError as err:
                    evalue = etype("%s (error getting sourceline: %s from %s)" % (evalue, err, filename))
                else:
                    evalue = etype("%s (sourceline: %r from %s)" % (evalue, sourceline, filename))
                exc_info = etype, evalue, etb

            return self.error(msg, exc_info)
        except Exception as err:
            return self.error(
                "Macro '%s' error: %s" % (macro_name, err),
                exc_info=sys.exc_info()
            )

        if not isinstance(result, TEXT_TYPE):
            msg = "Macro '%s' doesn't return a unicode string!" % macro_name
            if self.verbose > 1:
                msg += " - returns: %r, type %r" % (result, type(result))
            return self.error(msg)

        if node.kind == "macro_block":
            result += "\n"

        return result
    macro_inline_emit = macro_emit
    macro_block_emit = macro_emit

    def break_emit(self, node):
        if node.parent.kind == "list_item":
            return "<br />\n" + "\t" * node.parent.level
        elif node.parent.kind in ("table_head", "table_cell"):
            return "<br />\n\t\t"
        else:
            return "<br />\n"

    def line_emit(self, node):
        return "\n"

    def pre_block_emit(self, node):
        """ pre block, with newline at the end """
        return "<pre>%s</pre>\n" % self.html_escape(node.content)

    def pre_inline_emit(self, node):
        """ pre without newline at the end """
        return "<tt>%s</tt>" % self.html_escape(node.content)

    def default_emit(self, node):
        """Fallback function for emitting unknown nodes."""
        raise NotImplementedError("Node '%s' unknown" % node.kind)

    def emit_children(self, node):
        """Emit all the children of a node."""
        return ''.join([self.emit_node(child) for child in node.children])

    def emit_node(self, node):
        """Emit a single node."""
        #print("%s_emit: %r" % (node.kind, node.content))
        emit = getattr(self, '%s_emit' % node.kind, self.default_emit)
        return emit(node)

    def emit(self):
        """Emit the document represented by self.root DOM tree."""
        return self.emit_node(self.root).strip()

    def error(self, text, exc_info=None):
        """
        Error Handling.
        """
        if self.verbose > 1 and exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            exception = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.stderr.write(exception)

        if self.verbose > 0:
            return "[Error: %s]\n" % text
        else:
            # No error output
            return ""
    
    #--------------------------------------------------------------------------
    # macros
    
    def macro_text_emit(self, text):
        return creole.creole2html(text, emitter_kwargs = {
            u'env': self.env
            })
    
    def if_login(self, text, kind):
        if self.env[u'is_login']:
            return self.macro_text_emit(text)
        
        else:
            return u''
    
    # ログアウト時に表示するマクロ
    def if_logout(self, text, kind):
        if not self.env[u'is_login']:
            return self.macro_text_emit(text)
        
        else:
            return u''
    
    def if_admin(self, text, kind):
        if self.env[u'is_admin']:
            return self.macro_text_emit(text)
        
        else:
            return u''

    
if __name__ == "__main__":
    txt = """A <<test_macro1 args="foo1">>bar1<</test_macro1>> in a line..."""

    print("-" * 80)
#    from creole_alt.creole import CreoleParser
    p = CreoleParser(txt)
    document = p.parse()
    p.debug()

    from creole.shared.unknown_tags import escape_unknown_nodes
    html = HtmlEmitter(document,
        macros=escape_unknown_nodes
    ).emit()
    print(html)
    print("-" * 79)
    print(html.replace(" ", ".").replace("\n", "\\n\n"))

# vim: se et sw=4 sw=4 sts=4 ft=python :
