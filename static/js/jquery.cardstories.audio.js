//
//     Copyright (C) 2011 Farsides <contact@farsides.com>
//
//     Authors:
//              Matjaz Gregoric <gremat@gmail.com>
//
//     This program is free software: you can redistribute it and/or modify
//     it under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//
//     This program is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU General Public License for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
(function($) {

    $.cardstories_audio = {

        name: 'audio',

        init: function(player_id, game_id, root) {
            var $root = $(root);

            // Don't initialize twice.
            if ($root.data('cardstories_audio')) {
                return;
            }

            soundManager.onready(function() {
                // Create SoundManager sound objects.
                var sounds = {};
                $.each($root.data('sounds'), function(sound_id, url) {
                    sounds[sound_id] = soundManager.createSound({
                        id: sound_id,
                        url: url
                    });
                });

                // Save sound objects for later use.
                $root.data('cardstories_audio', {
                    sounds: sounds
                });
            });

            soundManager.ontimeout(function() {
                throw "cardstories_audio: Couldn't load SoundManager2 SWF files. No sound will be played.";
            });
        },

        play: function(sound_id, root) {
            var data = $(root).data('cardstories_audio');
            if (data && data.sounds && data.sounds[sound_id]) {
                data.sounds[sound_id].play();
            }
        }
    };

    $.fn.cardstories_audio = function() {
        $.cardstories_audio.init(null, null, this);
        return this;
    };

    // Register cardstories plugin.
    $.cardstories.register_plugin($.cardstories_audio);

})(jQuery);