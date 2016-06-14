# -*- coding: utf-8 -*-
'''
The module initialize some global data structures used in xml_update_2_0 module
'''
# init Topic Starter message indices dictionary
# key - Topic Starter message index
# values - list of all commentators message indices
topstIds = {}

# init Topic Starter message indices dictionary
# key - commentator message index
# value - Topic Starter message index
commIds = {}

# init Stack of Topic Starter message indices
# key - Topic Starter message index
# value - date/time of the Topic Starter post
topicIdStack = []
