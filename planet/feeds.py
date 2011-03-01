# -*- coding: utf-8 -*-

import os
from datetime import datetime

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404, Http404
from django.template.defaultfilters import linebreaks, escape, capfirst
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site

from planet.models import Post, Author, Blog
from tagging.models import Tag, TaggedItem


ITEMS_PER_FEED = getattr(settings, 'PLANET_ITEMS_PER_FEED', 50)

class BasePostFeed(Feed):
    def __init__(self, *args, **kwargs):
        super(BasePostFeed, self).__init__(*args, **kwargs)
        self.site = Site.objects.get(pk=settings.SITE_ID)
        
    def item_id(self, post):
        return post.guid
    
    def item_title(self, post):
        return post.title
    
    def item_updated(self, post):
        return post.date_modified
    
    def item_published(self, post):
        return post.date_created
    
    def item_content(self, post):
        return {"type" : "html", }, linebreaks(escape(post.content))
    
    def item_links(self, post):
        return [{"href" : reverse("post_detail", args=( post.pk,))}]
    
    def item_authors(self, post):
        return [{"name" : post.author}]

class PostFeed(BasePostFeed):
    
    def title(self):
        return _("Posts in %s") % self.site.name

    def description(self):
        return _("All posts")

    def link(self):
        return reverse('posts_list')

    def items(self):
        posts_list = Post.objects.order_by("-date_created")[:ITEMS_PER_FEED]
        return posts_list

class AuthorFeed(BasePostFeed):
    def get_object(self, params):
        return get_object_or_404(Author, pk=params[0], is_active=True)
    
    def title(self, author):
        return _("Posts by %(author_name)s - %(site_name)s") % {'author_name': author.name, 'site_name': self.site.name}

    def link(self, author):
        return  reverse("author_show", args=(author.pk, ))

    def items(self, author):
        return Post.objects.filter(feed__author=author,
            ).distinct().order_by("-date_created")[:ITEMS_PER_FEED]

class TagFeed(BasePostFeed):
    def get_object(self, params):
        return get_object_or_404(Tag, name=params[0])
    
    def title(self, tag):
        return _("Posts under %(tag)s tag - %(site_name)s") % {'tag': tag, 'site_name': self.site.name}

    def link(self, tag):
        return reverse("tag_detail", args=(tag.pk, ))

    def items(self, tag):
        return Post.objects.filter(tags__name=tag, feed__site=self.site
            ).distinct().order_by("-date_created")[:ITEMS_PER_FEED]

class AuthorTagFeed(BasePostFeed):
    
    def get_object(self, author_id, tag):
        self.tag = tag
        return get_object_or_404(Author, pk=author_id, is_active=True)
    
    def title(self, author):
        return _("Posts by %(author_name)s under %(tag)s tag - %(site_name)s")\
            % {'author_name': author.name, 'tag': self.tag, 'site_name': self.site.name}

    def links(self, author):
        return reverse("by_tag_author_show", args=(author.pk, self.tag))

    def items(self, author):
        return Post.objects.filter(
            feed__author=author, tags__name=self.tag
            ).distinct().order_by("-date_created")[:ITEMS_PER_FEED]

