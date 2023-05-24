var all_source = new EventSource(all_room);
var team_source = new EventSource(team_room);
var user_source = new EventSource(user_room);

user_source.addEventListener('dialog', function(event) {
    var data = JSON.parse(event.data);
	dialog(data["message"])
}, false);

user_source.addEventListener('country_flag_wrong', function(event) {
	var data = JSON.parse(event.data);
    var cc = data["country_code"]
    // if they currently have the modal open
	if ($('#challengeModal input#country-code').val() == cc) {
		// if its a jeopardy
		if (($("#challengeModal span#challenge-type").text() == "jeopardy") || ($("#challengeModal span#challenge-type").text() == "practice")) {
			// make flag text wrong
			$('#text-flag').val("Wrong!")
			// make it red
			$('#text-flag').addClass("wrong")
			// after 2000ms make it normal again
			setTimeout(function(){$('#text-flag').removeClass("wrong");$('#text-flag').val("")},2000)
		// if its a multiple choice
		} else if ($("#challengeModal span#challenge-type").text() == "multiple") {
			// make the buttons all red
			$("table#multiple-choice td").addClass("wrong");
			$("table#multiple-choice th").find("button").each(function(){$(this).addClass("wrong")});
			// after 2000ms make it normal again
			setTimeout(function(){$('table#multiple-choice td').removeClass("wrong");$("table#multiple-choice th").find("button").each(function(){$(this).removeClass("wrong")});},2000)
		}
	}	
}, false);

all_source.addEventListener('announcement', function(event) {
    var announcement = JSON.parse(event.data);
	announcements.push(announcement)
	announcements = announcements.slice(-5)
	updateAnnouncements();
}, false);

all_source.addEventListener('country_color_change', function(event) {
    var data = JSON.parse(event.data);
	var cc = data["country_code"]
	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// set the color of the country
	$(id).css({"fill":data["color"]})
	countries_to_challenges[cc]["color"] = data["color"]
}, false);

all_source.addEventListener('country_completed_by', function(event) {
    var data = JSON.parse(event.data);
	var cc = data["country_code"]
	countries_to_challenges[cc]["teams_completed"].push(data["team"])
}, false);

team_source.addEventListener('points_awarded', function(event) {
    var data = JSON.parse(event.data);
    agent.show();
	agent.speak("You have been awarded "+data["points"]+" points for: '"+data["reason"]+"'");
	agent.play("Congratulate");
});

team_source.addEventListener('hint_bought', function(event) {
    var data = JSON.parse(event.data);
  	var cc = data["country_code"]  
	var hint = data["hint"]
	console.log(data)
  	// if the user has it open currently
	if ($('.modal input#country-code').val() == cc) {
		// put the hint in the box straight away
		$('.modal td#hint-content').text(hint)
		$('.modal #hint table').addClass("greyed-out")	
		$('.modal #hint-btn').hide()
	}
	// put the hint in the dictionary
	countries_to_challenges[cc]["hint"] = hint
});

team_source.addEventListener('country_launched', function(event) {
    var data = JSON.parse(event.data);
    var cc = data["country_code"]
    var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;

    // remove pulsinng
    $(id).removeClass("pulse")
    // set original color
    $(id).css({"fill":$(id).attr("data-original-color")})
    // if the challenge is the one open
    if ($('.modal input#country-code').val() == cc) {
		// remove the active class on the button
		$(".launch[data-country-code='"+cc+"']").removeClass("active");
		// hide launch button
		$(".launch[data-country-code='"+cc+"']").hide();
		// show kill button again
		$(".kill[data-country-code='"+cc+"']").show();
		// set the challenge url
		countries_to_challenges[data["country_code"]]["challenge_url"] = data["challenge_url"]
		// append url to description
		$('.modal div#challenge-description').html($('.modal div#challenge-description').text() + "\n\nYou can access this challenge here: <span class='copy challenge-url'>"+data["challenge_url"]+"</span>")	
    }
    // set the challenge url
    countries_to_challenges[data["country_code"]]["challenge_url"] = data["challenge_url"]
    // show all kill buttons
	$(".kill[data-country-code='"+cc+"']").show();
	// remove launch buttont
	$(".launch[data-country-code='"+cc+"']").hide();
    // set url in launching modal
    $("span.challenge-url[data-country-code='"+data["country_code"]+"']").text(data["challenge_url"])
    country_launched_audio.play();
    agent.show();
    agent.speak("Hey, '"+countries_to_challenges[data["country_code"]]["name"]+"' has finished launching.");
    // get position of country
    var position = $(id).position();
    agent.gestureAt(position.left, position.top)
});


team_source.addEventListener('country_update', function(event) {
    var data = JSON.parse(event.data);
    // set url in launching
    $("span.challenge-url[data-country-code='"+data["country_code"]+"']").text(data["update"])
});

team_source.addEventListener('country_killed', function(event) {
    var data = JSON.parse(event.data);
  	var cc = data["country_code"]  
	// if the challenge is the one open
	if ($('.modal input#country-code').val() == cc) {
		// remove the active class on the button
		$(".kill[data-country-code='"+cc+"']").removeClass("active");
		// hide kill button
		$(".kill[data-country-code='"+cc+"']").hide();
		// show launch button again
		$(".launch[data-country-code='"+cc+"']").show();
		// remove the challenge url
		delete countries_to_challenges[cc]["challenge_url"];
		// set description back to default
		$('.modal div#challenge-description').text(countries_to_challenges[cc]["description"])
		// remove it from the launched modal
		$("#chals .kill[data-country-code='"+cc+"']").closest("tr").remove();
	} else {
		// if its not the open challenge just remove it from the launched modal
		$("#chals .kill[data-country-code='"+cc+"']").closest("tr").remove();
		$(".launch[data-country-code='"+cc+"']").show();
		// remove challenge url
		delete countries_to_challenges[cc]["challenge_url"]
	}
});

team_source.addEventListener('country_failed', function(event) {
    var data = JSON.parse(event.data);
  	var cc = data["country_code"]  
	// dialog(data["message"])
	// set the button back to normal
	$(".launch[data-country-code='"+cc+"']").removeClass("active");
	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// set the country back to non pulsing
	$(id).removeClass("pulse")
	$(id).css({"fill":$(id).attr("original")})
	// delete the challenge url status
	delete countries_to_challenges[data["country_code"]]["challenge_url"];
});

team_source.addEventListener('country_unlock', function(event) {
	country_unlock_audio.play();
	var data = JSON.parse(event.data);
  	var cc = data["country_code"]  
  	var challenge_info = data["challenge_info"]
	// put challenge into dictionary
	countries_to_challenges[cc] = challenge_info
	// get id of country
	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// make the country the correct color
	if (countries_to_challenges[cc].hasOwnProperty("color")) {
		$(id).css({"fill":countries_to_challenges[cc]["color"]})
	} else {
		$(id).css({"fill":background_color})
	}
	// append to the sidebar
	appendToSidebar(challenge_info, cc)
	// if its in the us make the us the color
	if (cc.split("-")[0] == "us") {
		if (countries_to_challenges[cc].hasOwnProperty("color")) {
			$("#jqvmap1_us").css({"fill":countries_to_challenges[cc]["color"]})
		} else {
			$("#jqvmap1_us").css({"fill":background_color})
		}
	}
	agent.show();
	agent.speak("A new challenge: '"+data["challenge_info"]["name"]+"' has been unlocked!");
	agent.play("GetAttention")
});

function appendToSidebar(data, cc) {
  	var challenge_info = data["challenge_info"]
  	var type = data["type"]
  	var category = data["category"]
	var rows = "<tr onclick='openModal(&quot;"+$.trim(cc)+"&quot;); event.stopPropagation();'>\
		<td>\
			<a>"+data["name"]+"</a>\
		</td>\
	</tr>\
	<tr onclick='openModal(&quot;"+$.trim(cc)+"&quot;); event.stopPropagation();'>\
		<td>\
			<span class='"+type+"' id='challenge-type'>"+type+"</span>\
			<span class='"+category+"' id='challenge-category'>"+category+"</span>\
			"+data["points"]+"\
		</td>\
	</tr>"
	$(rows).appendTo(".challenge-table table");
}

all_source.addEventListener('country_unlock', function(event) {
	country_unlock_audio.play();
    var data = JSON.parse(event.data);
  	var cc = data["country_code"]  
  	var challenge_info = data["challenge_info"]
	// put challenge into dictionary
	countries_to_challenges[cc] = challenge_info
	// get id of country
	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// make the country the correct color
	if (countries_to_challenges[cc].hasOwnProperty("color")) {
		$(id).css({"fill":countries_to_challenges[cc]["color"]})
	} else {
		$(id).css({"fill":background_color})
	}
	if (countries_to_challenges[cc]["type"] == "timed") {
		$(id).addClass("pulse")
	}
	// if its in the us make the us the color
	if (cc.split("-")[0] == "us") {
		if (countries_to_challenges[cc].hasOwnProperty("color")) {
			$("#jqvmap1_us").css({"fill":countries_to_challenges[cc]["color"]})
		} else {
			$("#jqvmap1_us").css({"fill":background_color})
		}
	}
	// append to the sidebar
	appendToSidebar(challenge_info, cc)
	agent.show();
	agent.speak("A new challenge: '"+data["challenge_info"]["name"]+"' has been unlocked!");
	agent.play("GetAttention")
});

team_source.addEventListener('country_complete', function(event) {
    var data = JSON.parse(event.data);
	var cc = data["country_code"]
	var flag = data["flag"]
	// if the user has the same country currently open
	if ($('.modal input#country-code').val() == cc) {
		// if its a jeopardy challenge
		if (($(".modal span#challenge-type").text() == "jeopardy") || ($(".modal span#challenge-type").text() == "practice")) {
			// set content to correct
			$('#text-flag').val("Correct!")
			// make it green
			$('#text-flag').addClass("correct")
			// after 2000ms set back to normal 
			setTimeout(function(){$('#text-flag').removeClass("correct").addClass("inactive");$('#text-flag').val(flag)},2000)
			$('.modal #submit').hide()
		// if its a multiple
		} else if ($(".modal span#challenge-type").text() == "multiple") {
			// make the button green
			$("table#multiple-choice th button").addClass("inactive");
			//$("table#multiple-choice td."+flag.replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_")).addClass("correct");
			$("table#multiple-choice td."+flag.replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_")).prev("th").find("button").addClass("correct");
		}
	}

	// set complete in dictionary
	countries_to_challenges[cc]["complete"] = true
	countries_to_challenges[cc]["flag"] = flag

	// set pin on map
	pins[cc] = "<div class='completed-triangle'></div>"
	//jQuery('#vmap').vectorMap('set', 'pins', pins);
	//jQuery('#usmap').vectorMap('set', 'pins', pins);

	// set color of country to the complete color
	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	$(id).css({"fill":complete_color})
	$(".challenge-table a:contains('"+countries_to_challenges[cc]["name"]+"')").addClass("strikethrough");

}, false);

team_source.addEventListener('points_update', function(event) {
    var data = JSON.parse(event.data);
	var points = data["points"]
	$("#total-points").text(points);
})





