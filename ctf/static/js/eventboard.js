var event_source = new EventSource(event_room);

event_source.addEventListener('team_event', function(event) {
    var data = JSON.parse(event.data);
	var container = "<div data-animation='"+randomChoice(animations)+"'>\
			<fieldset >\
				<legend>"+data['team_name']+"</legend>\
				<table>\
					<tr>\
						<td><img src='/static/img/icons/"+data["team_logo"]+"'></td><td><table><tr><td>"+data['challenge_name']+"</td></tr><tr><td><span class='points'>+"+data['points']+" points</span></td></tr></table></td>\
					</tr>\
				</table>\
			</fieldset>\
		</div>"
	// play the sound
	playSound(data["team_sound"])
	$(container).prependTo("#eventlog").hide().fadeIn(300);
	// setTimeout(function(){
   	// 	$(prepended_element).fadeOut(1000);
	// }, 5000, $(prepended_element).fadeIn(1000));
}, false);

event_source.addEventListener('team_flag_streak', function(event) {
    var data = JSON.parse(event.data);
	var number = "<span class='big-number'>{letter_here}</span>"
	var team_letter = "<span style='color:"+data["team_color"]+"' class='big-number'>{letter_here}</span>"
	var letter = "<span class='big-number'>{letter_here}</span>"
	var html = []
	// for each letter get the html
	var team_name = data["team_name"] + " "
	var str = data["count"] + " flag streak"
	for (var i = 0; i < team_name.length; i++) {
		var new_letter = team_letter.replace("{letter_here}",team_name.charAt(i));
		html.push(new_letter)
	}
	for (var i = 0; i < str.length; i++) {
		if (isCharDigit((str.charAt(i)))) {
			var new_letter = number.replace("{letter_here}",str.charAt(i));
		} else {
			var new_letter = letter.replace("{letter_here}",str.charAt(i));
		}
		html.push(new_letter)
	}
	$(".triple-flag-streak").show();
	$(".triple-flag-streak").addClass("active");
	$(".triple-flag-streak").html(html.join(""))
	// start harlem shake
	//just add elements you want to animate
	$('.eventboard-info,.triple-flag-streak,#eventlog div').harlemShake();
	// letter url
	doScores();
}, false);


// setTimeout(function(){
//    doScores();
// }, 10000);

function randomChoice(arr) {
    return arr[Math.floor(arr.length * Math.random())];
}

function isCharDigit(n){
  return !!n.trim() && n > -1;
}

function playSound(url) {
	var media = new Audio(url);
	const playPromise = media.play();
	if (playPromise !== null){ playPromise.catch(() => { media.play(); })}
}

function doScores() {
	$.getJSON("/scores", function(scores) {
		//console.log(scores)
		$(".leaderboard-table tbody").html("");
		for (team in scores) {
			rank = +team + +1
			score = "<tr><td>"+rank.toString()+"</td><td>"+scores[team]["team_name"]+"</td><td>"+scores[team]["score"].toString()+"</td></tr>"
			$(".leaderboard-table tbody").append($(score))
		}
	});
}

jQuery(document).ready(function() {

	// socket.on('team_event', function(data) {
	// 		container = "<div data-animation='"+randomChoice(animations)+"' style='background-color:"+data['team_color']+";border: 2px outset;'>\
	// 				<fieldset >\
	// 					<legend>"+data['team_name']+"</legend>\
	// 					<table>\
	// 						<tr>\
	// 							<td><img src='/static/img/icons/"+data["team_logo"]+"'></td><td><span class='points'>+"+data['points']+" points</span></td>\
	// 						</tr>\
	// 					</table>\
	// 				</fieldset>\
	// 			</div>"
	// 		// play the sound
	// 		playSound(data["team_sound"])

	// 		$(container).prependTo("#eventlog").hide().fadeIn(300);
	// 		doScores();
	// });

	// socket.on('team_flag_streak', function(data) {
	// 	// the letter
	// 	var number = "<span class='big-number'>{letter_here}</span>"
	// 	var team_letter = "<span style='color:"+data["team_color"]+"' class='big-number'>{letter_here}</span>"
	// 	var letter = "<span class='big-number'>{letter_here}</span>"
	// 	var html = []
	// 	// for each letter get the html
	// 	var team_name = data["team_name"] + " "
	// 	var str = data["count"] + " flag streak"
	// 	for (var i = 0; i < team_name.length; i++) {
	// 		var new_letter = team_letter.replace("{letter_here}",team_name.charAt(i));
	// 		html.push(new_letter)
	// 	}
	// 	for (var i = 0; i < str.length; i++) {
	// 		if (isCharDigit((str.charAt(i)))) {
	// 			var new_letter = number.replace("{letter_here}",str.charAt(i));
	// 		} else {
	// 			var new_letter = letter.replace("{letter_here}",str.charAt(i));
	// 		}
	// 		html.push(new_letter)
	// 	}
	// 	$(".triple-flag-streak").show();
	// 	$(".triple-flag-streak").html(html.join(""))
	// 	// start harlem shake
	// 	//just add elements you want to animate
	// 	$('.eventboard-info,.triple-flag-streak,#eventlog div').harlemShake();
	// 	// letter url
	// 	doScores();
	// });

	// do the scores
	doScores();

	window.setInterval(function(){
	  doScores();
	}, 5000);

});
