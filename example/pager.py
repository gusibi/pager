# -*- coding: utf-8 -*-
from __future__ import unicode_literals

'''Helper utilities and decorators.'''

from math import ceil

from flask import request
from flask import render_template
from jinja2 import Markup
from werkzeug.urls import url_encode
from werkzeug.utils import cached_property
from werkzeug.datastructures import MultiDict


class Pager(object):

    template = 'pager.html'

    def __init__(self, total_count=None, per_page=20):
        self.per_page = per_page
        self.total_count = total_count
        self.url = request.base_url

    @property
    def current_page(self):
        """ 获取当前页码"""
        current_page = request.args.get('page', 1)
        try:
            current_page = int(current_page)
        except ValueError:
            current_page = 1
        if current_page < 1:
            current_page = 1
        elif self.total_count is None:
            pass
        elif current_page > self.pages > 0:
            current_page = self.pages
        return current_page

    @property
    def offset(self):
        if self.current_page == 1:
            return 0
        return self.per_page * (self.current_page - 1)

    @property
    def pages(self):
        if self.total_count is None:
            return 1
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.current_page > 1

    @property
    def prev_page(self):
        prev_page = self.current_page - 1
        if prev_page < 1:
            prev_page = None
        return prev_page

    @property
    def has_next(self):
        return self.current_page < self.pages

    @property
    def next_page(self):
        next_page = self.current_page + 1
        if next_page > self.pages:
            next_page = None
        return next_page

    @staticmethod
    def _url_sort_key(key):
        return key[0]

    @cached_property
    def _base_url(self):
        return request.base_url

    def url_for(self, page):
        """对应页码的url"""
        params = MultiDict(request.args)
        if page > 1:
            params['page'] = page
        else:
            params.pop('page', None)
        suffix = url_encode(params, sort=True, key=self._url_sort_key)
        mark = '?' if suffix else ''
        return self._base_url + mark + suffix

    def iter_pages(self, left_edge=1, left_current=2,
                   right_current=3, right_edge=1):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.current_page - left_current - 1 and
                     num < self.current_page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def __call__(self):
        return Markup(render_template(self.template, pager=self))
