#
# Copyright (C) 2011 Loic Dachary <loic@dachary.org>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#
import os

from types import ListType

from twisted.python import log
from twisted.internet import defer
from twisted.enterprise import adbapi

from cardstories.auth import Auth

class Plugin(Auth):

    def __init__(self, service, plugins):
        dirname = os.path.join(service.settings['plugins-libdir'], self.name())
        self.database = os.path.join(dirname, 'auth.sqlite')
        exists = os.path.exists(self.database)
        if not exists:
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            import sqlite3
            db = sqlite3.connect(self.database)
            c = db.cursor()
            c.execute(
                "CREATE TABLE players ( " 
                "  id INTEGER PRIMARY KEY, "
                "  name VARCHAR(255) " 
                "); ")
            c.execute(
                "CREATE INDEX players_idx ON players (name); "
                )
            db.commit()
            db.close()
        self.db = adbapi.ConnectionPool("sqlite3", database=self.database, cp_noisy=True)
        log.msg('plugin auth initialized with ' + self.database)

    def name(self):
        return 'auth'

    def create_player_from_email(self, transaction, email):
        transaction.execute("INSERT INTO players (name) VALUES (?)", [ email ])
        return transaction.lastrowid
        
    @defer.inlineCallbacks
    def get_player_id(self, email, create=False):
        row = yield self.db.runQuery("SELECT id FROM players WHERE name = ?", [ email ])
        if row:
            id = row[0][0]
        elif create:
            id = yield self.db.runInteraction(self.create_player_from_email, email)
        else:
            id = None
        defer.returnValue(id)

    def get_player_name(self, id):
        return "Player " + str(id)

    def authenticate(self, request, requested_player_id):
        # Unsecure/test auth - do not authenticate anything
        pass
