from django.template import Library, Node, Variable
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

register = Library()

# usage: {% stylize "language" %}...language text...{% endstylize %}
class StylizeNode(Node):
	def __init__(self, nodelist, *varlist):
		self.nodelist, self.vlist = (nodelist, varlist)

	def render(self, context):
		style = 'text'
		if len(self.vlist) > 0:
			style = Variable(self.vlist[0]).resolve(context)
		return highlight(self.nodelist.render(context),
				get_lexer_by_name(style, encoding='UTF-8'), HtmlFormatter())

def stylize(parser, token):
	nodelist = parser.parse(('endstylize',))
	parser.delete_first_token()
	return StylizeNode(nodelist, *token.contents.split()[1:])

stylize = register.tag(stylize)
