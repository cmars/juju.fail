#!/usr/bin/env python

import json
import datetime
import os

from citools import check_blockers

from gi.repository import Notify

#watched_branches = ['1.22', '1.23', '1.24', '1.25', 'master']
watched_branches = ['master']
cacheFile = os.path.join(os.getenv("HOME"), ".cache", "juju-fail", "last.json")
cacheDir = os.path.dirname(cacheFile)
if not os.path.exists(cacheDir):
    os.makedirs(cacheDir)

data = {}

def format_title(s):
    _, uf = s.split(':', 1)
    return uf.replace('"', '', 1)[::-1].replace('"', '', 1)[::-1].strip()


lp = check_blockers.Launchpad.login_anonymously('juju.fail', 'production', version='devel')

for b in watched_branches:
    uhohs = check_blockers.get_lp_bugs(lp, b)

    data[b] = []

    if not uhohs:
        continue

    for bug, bdata in uhohs.iteritems():
        data[b].append({'id': bug, 'url': 'http://pad.lv/%s' % bug,
                        'title': format_title(bdata.title), 'status': bdata.status})

last = {}
if os.path.exists(cacheFile):
    with open(cacheFile, "r") as f:
        last = json.load(f)

Notify.init("juju-fail")

for k, v in data.iteritems():
    title = v and "juju.fail" or "juju.win"
    status = v and "blocked" or "clear"
    if last.get(k, "") != v:
        msg = "%s is %s:\n%s" % (k, status,
            " ".join([buginfo.get("url") for buginfo in v if "url" in buginfo]))
        Notify.set_app_name(title)
        note = Notify.Notification.new(msg)
        note.set_urgency(1)
        note.show()

Notify.uninit()

with open(cacheFile, "w") as f:
    last = json.dump(data, f)

