#
# Copyright (C) 2011 Dachary <loic@dachary.org>
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

export COVERAGE=$(shell which coverage || which python-coverage)

all:

check:
	${COVERAGE} -e
	PYTHONPATH=.. ${COVERAGE} -x test_helpers.py
	PYTHONPATH=.. ${COVERAGE} -x test_service.py
	PYTHONPATH=.. ${COVERAGE} -x test_site.py
	PYTHONPATH=.. ${COVERAGE} -x test_tap.py
	PYTHONPATH=.. ${COVERAGE} -x test_game.py
	PYTHONPATH=.. ${COVERAGE} -x test_levels.py
	PYTHONPATH=.. ${COVERAGE} -x test_poll.py
	PYTHONPATH=.. ${COVERAGE} -x test_auth.py
	PYTHONPATH=.. ${COVERAGE} -x test_plugins.py
	${COVERAGE} -m -a -r ../cardstories/*.py

clean:
	rm -fr .coverage _trial_temp*
