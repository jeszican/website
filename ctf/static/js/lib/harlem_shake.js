(function( $ ) {

    var othersTimeouts = [];
    var stopped = false;

    $.fn.harlemShake = function(options) {

        var that = this;
        var timeout = 0;
        var pivotTimeout = 0;
        var endTime = 6000;
        var beforeEndTime = 28800;
        var defaultAnimation = 'wobble';

        if(options == 'stop') {
            end(that);
        } else {

            this.each(function(i, item) {
                var animation = $(item).data('animation');
                var animSpeed = $(item).data('animation-speed');
                var pivot = $(item).data('pivot');

                if(pivot) {
                    var tim = setTimeout( function() {
                        $(item).addClass('hs-animate');
                        animate(item, animation, animSpeed);
                    }, pivotTimeout);
                    othersTimeouts.push(tim);
                } else {
                    var tim = setTimeout( function() {
                        $(item).addClass('hs-animate');
                        animate(item, animation, animSpeed);
                    }, timeout);
                    othersTimeouts.push(tim);
                }
            });
        }

        var tim = setTimeout( function() {
            end(that);
        }, endTime);
        othersTimeouts.push(tim);

        var tim = setTimeout( function() {
            beforeEnd(that);
        }, beforeEndTime);
        othersTimeouts.push(tim);

        function animate(item, animation, speed) {
            if(speed) {
                $(item).addClass('hs-animate-'+speed);
            }
            if(animation) {
                $(item).addClass(animation);
            } else {
                $(item).addClass(defaultAnimation);
            }
        }

        function beforeEnd(items) {
            $(items).each(function(i, item) {
                $(item).addClass('hs-animate-slow');
            });
        }

        function end(items) {
            $(items).each(function(i, item) {
                var animation = $(item).data('animation');
                var animSpeed = $(item).data('animation-speed');
                $(item).removeClass('hs-animate');
                if(animSpeed)
                    $(item).removeClass('hs-animate-'+animSpeed);
                if(animation)
                    $(item).removeClass(animation);
                $(item).removeClass(defaultAnimation);
                $(item).removeClass('hs-animate-slow');
                $(item).removeClass('hs-animate-fast');
            });
            var timeoutsLength = othersTimeouts.length;
            while(timeoutsLength--) {
                var tim = othersTimeouts[timeoutsLength];
                clearTimeout(tim);
                othersTimeouts.splice(-1,1);
            }
            stopped = true;
	    $(".triple-flag-streak").hide();
        }

        return this;
    };
}) ( jQuery );
