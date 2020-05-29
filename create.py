# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 19:52:19 2020

@author: Asus
"""
import os

accountname = os.environ['ACCNAME']
botname = os.environ['BOTNAME']
botpassword = os.environ['BOTPASS']

f = open("user-password.py", "w")
f.write("(u'{0}', BotPassword(u'{1}', u'{2}'))".format(accountname, botname, botpassword))
f.close()

f = open("user-config.py", "w")
f.write("""password_file = "user-password.py"\n""")
f.write("""mylang = 'wikidata'\n""")
f.write("""family = 'wikidata'\n""")
f.write("""usernames['wikidata']['wikidata'] = u'{0}'""".format(accountname))
f.close()

