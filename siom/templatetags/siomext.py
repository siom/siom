# -*- coding: utf8 -*-

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
	try:
		return value * arg
	except:
		return None

