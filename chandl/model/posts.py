# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Posts(list):
    """
    Represents a list of posts in a thread.
    """

    def __init__(self, *args):
        """
        Initialise a new posts list.

        :param args: The list of posts.
        """

        super(Posts, self).__init__(*args)

    def filter(self, predicate):
        """
        Take a subset of this list of posts.

        :param predicate: The predicate to use to choose which posts make the
                          cut.
        :return: The filtered posts.
        """

        return Posts(filter(predicate, self))

    def map(self, transformation):
        """
        Applies a transformation function to each post, returning a list of this
        function's returned values.

        :param transformation: The transformation function.
        :return: The transformed list of posts.
        """

        return map(transformation, self)

    def foreach(self, function):
        """
        Call a function  for each post.

        :param function: A function taking a post argument. Return values are
        ignored.
        """

        for post in self:
            function(post)
