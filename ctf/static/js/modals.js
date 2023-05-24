//                      _       _     
//  _ __ ___   ___   __| | __ _| |___ 
// | '_ ` _ \ / _ \ / _` |/ _` | / __|
// | | | | | | (_) | (_| | (_| | \__ \
// |_| |_| |_|\___/ \__,_|\__,_|_|___/
// 

function getRunning() {
	$("#discord").css("display","none")
	$(".modal").hide();
	$("table#instances tbody#chals").html("")
	$("table#instances tbody#chals").show();
	$("#overlay").show();
	$.getJSON("/running", function(instances) {
		for (instance in instances) {
			if (instances[instance]["url"] == "launching") {
				$("table#instances tbody#chals").append("<tr><td>"+instances[instance]["challenge_name"]+" </td><td><span data-country-code='"+instances[instance]["country_code"]+"' class='challenge-url copy'>"+instances[instance]["message"]+"</span></td><td><button style='margin-left:1em;width:100px;display:none;' type='button' class='kill' data-challenge-id='"+instances[instance]["challenge_id"]+"' data-country-code='"+instances[instance]["country_code"]+"' onclick='killChallenge(this)' style=''><span>Kill</span><img class='loading-img' src='/static/img/loading_animation.gif'></button></td></tr>")
			} else {
				$("table#instances tbody#chals").append("<tr><td>"+instances[instance]["challenge_name"]+" </td><td><span data-country-code='"+instances[instance]["country_code"]+"' class='challenge-url copy'>"+instances[instance]["url"]+"</span></td><td><button style='margin-left:1em;width:100px;' type='button' class='kill' data-challenge-id='"+instances[instance]["challenge_id"]+"' data-country-code='"+instances[instance]["country_code"]+"' onclick='killChallenge(this)' style=''><span>Kill</span><img class='loading-img' src='/static/img/loading_animation.gif'></button></td></tr>")
			}
		}
	});
	$(".modal-container").css("display","flex");
	$("#running-instances").css("display","block")
}

function openDiscord() {
	$(".modal").hide();
	$("#overlay").show();
	$(".modal-container").css("display","flex");
	$("#discord").css("display","block")
}

function closeScoreboard() {
	$("#overlay").hide()
	$(".modal-container").css("display","none")
	$("#scoreboard").css("display","none")
}

function closeInstances() {
	$("#overlay").hide()
	$(".modal-container").css("display","none")
	$("#instances").css("display","none")
}

function openScoreboard() {
	$(".modal").hide();
	$("table#scores tbody#noobs").html("")
	// get the latest scoreboard
	$.getJSON("/scores", function(scores) {
		counter = 1
		for (team in scores) {
			if (team == 0) {
				$("table#first-place").find("td.logo").html("<img src='/static/img/icons/"+scores[team]["logo"]+"'>")
				$("table#first-place").find("td.team-name").html(scores[team]["team_name"] + ": <span class='team-score'>Ð"+scores[team]["score"]+"</span>")
			} else if (team == 1) {
				$("table#second-place").find("td.logo").html("<img src='/static/img/icons/"+scores[team]["logo"]+"'>")
				$("table#second-place").find("td.team-name").html(scores[team]["team_name"] + ": <span class='team-score'>Ð"+scores[team]["score"]+"</span>")
			} else if (team == 2) {
				$("table#third-place").find("td.logo").html("<img src='/static/img/icons/"+scores[team]["logo"]+"'>")
				$("table#third-place").find("td.team-name").html(scores[team]["team_name"] + ": <span class='team-score'>Ð"+scores[team]["score"]+"</span>")
			} else {
				$("table#scores tbody#noobs").append("<tr><table><tr><td class='rank'>"+counter+".</td><td class='team-name'>"+scores[team]["team_name"]+": <span class='team-score'>Ð"+scores[team]["score"]+"</span></td></tr></table></tr>")
			}
			counter = counter + 1
		}
	});
	$("#overlay").show();
	$(".modal-container").css("display","flex");
	$("#scoreboard").css("display","block")
	$("#discord").css("display","none")
}

function openDiscord() {
	$(".modal").hide();
	$("#overlay").show();
	$(".modal-container").css("display","flex");
	$("#discord").css("display","block")
}

window.onclick = function(event) {
     if ($(event.target).hasClass('modal-container')) {
		closeModal();
     }
}

function dialog(message) {
	$("#dialog").css("display","block")
	$("#dialog p").text(message);
}

function closeDialog() {
	$("#dialog").css("display","none")
	$("#dialog p").text("");
}

function closeModal() {
	$(".modal").hide();
	$("#overlay").hide()
	$(".modal-container").css("display","none")
	$("#modal").css("display","none")
	$("#scoreboard").css("display","none")
	$("#discord").css("display","none")
	$("#running-instances").css("display","none")
	$('audio').each(function(){
	    this.pause(); // Stop playing
	    this.currentTime = 0; // Reset time
	}); 
}

function openChallengeModal(cc) {
	$("#discord").css("display","none")
	$(".modal").hide()
	$(".launch").removeClass("active");
	$(".kill").removeClass("active");
	$(".launch").hide()
	$(".kill").hide()

	$("#overlay").show();
	$("#running-instances").css("display","none");
	$("#discord").css("display","none");
	$(".modal-container").css("display","flex");
	$("#challengeModal").css("display","block")
	$('#challengeModal input#country-code').val(cc)
	$('#challengeModal span#challenge-name').html(countries_to_challenges[cc]["name"])
	$('#challengeModal div#challenge-description').html(countries_to_challenges[cc]["description"])
	$('#challengeModal span#challenge-type').text(countries_to_challenges[cc]["type"].replace(","," & "))
	$('#challengeModal span#challenge-type').attr("class",countries_to_challenges[cc]["type"].replace(",",""))
	$('#challengeModal span#challenge-category').text(countries_to_challenges[cc]["category"])
	$('#challengeModal span#challenge-category').attr("class",countries_to_challenges[cc]["category"])
	$('#challengeModal span#challenge-points').text(countries_to_challenges[cc]["points"])
	$('#challengeModal span#flag-penalty').text(countries_to_challenges[cc]["flag_penalty"])
	$('#challengeModal span#hint-penalty').text(countries_to_challenges[cc]["hint_penalty"])

	//  for submit and hint buttons we need to provide challenge id information
	$('#challengeModal #hint-btn').data('challenge-id',countries_to_challenges[cc]["id"])
	$('#challengeModal #hint-btn').data('country-code',cc)
	$('#challengeModal #submit').data('country-code',cc)
	$('#challengeModal #submit').data('challenge-id',countries_to_challenges[cc]["id"])
	$('#challengeModal .launch').data('country-code',cc)
	$('#challengeModal .launch').data('challenge-id',countries_to_challenges[cc]["id"])
	$('#challengeModal .launch').attr('data-country-code',cc)
	$('#challengeModal .launch').attr('data-challenge-id',countries_to_challenges[cc]["id"])
	$('#challengeModal .kill').data('country-code',cc)
	$('#challengeModal .kill').data('challenge-id',countries_to_challenges[cc]["id"])
	$('#challengeModal .kill').attr('data-country-code',cc)
	$('#challengeModal .kill').attr('data-challenge-id',countries_to_challenges[cc]["id"])

	// if it has a dockerfile its launchable
	if (countries_to_challenges[cc].hasOwnProperty("launchable")) {
		$(".launch").show()
		// get the average launching time
		chal_id = countries_to_challenges[cc]["id"]
		$.getJSON("/get_average_launch_time/"+chal_id, function(launch_time) {
			$('#challengeModal span#launch-time').html("Average launch time: " + launch_time+"s");
		});
	} else {
		$('#challengeModal span#launch-time').html("");
	}

	if (countries_to_challenges[cc].hasOwnProperty("challenge_url")) {
		// its still launching
		if (countries_to_challenges[cc]["challenge_url"] == "launching") {
			// if its still launching
			$(".launch").addClass("active");
		} else if (countries_to_challenges[cc]["challenge_url"] == "killing") {
			// if its killing
			$(".launch").hide()
			$(".kill").show()
			$(".kill").addClass("active");
		} else {
			// if its launched
			// hide the launch button
			$(".launch").hide();
			$(".kill").show()
			// append the challenge url to the links
			$('#challengeModal div#challenge-description').html($('#challengeModal div#challenge-description').text() + "\n\nYou can access this challenge here: <span class='copy challenge-url'>"+countries_to_challenges[cc]["challenge_url"]+"</span>")	
		}
	}

	// if it has audio
	if (countries_to_challenges[cc].hasOwnProperty("audio")) {
		$('#challengeModal span#audio-player').html('<audio controls="controls" src="/challenge_resource/'+countries_to_challenges[cc]["audio"]+'"></audio>');
	} else {
		$('#challengeModal span#audio-player').html('');
	}

	// show hint table again
	$('#challengeModal #hint table').show();
	$("#challengeModal div#countdown-form").hide()

	// remove previous links
	$("#challengeModal #challenge-links .link").remove()

	// if the challenge has links
	if (countries_to_challenges[cc].hasOwnProperty("links")) {
		var json_links = JSON.parse(countries_to_challenges[cc]["links"])
		for (link in json_links) {
			var new_link = $('#challengeModal span.skeleton-link').eq(0).clone().removeClass("skeleton-link").addClass("link")
			new_link.find("a").attr("href", json_links[link])
			new_link.find("a").text("Link " + link)
			$("#challengeModal #challenge-links").append(new_link).show()
		}
	}

	// if it has a downloadable resource
	if (countries_to_challenges[cc].hasOwnProperty("downloadables")) {
		// add it to the current links
		var json_links = JSON.parse(countries_to_challenges[cc]["downloadables"])
		for (link in json_links) {
			var new_link = $('#challengeModal span.skeleton-link').eq(0).clone().removeClass("skeleton-link").addClass("link")
			new_link.find("a").attr("href", "/challenge_resource/"+json_links[link])
			new_link.find("a").attr("download",json_links[link])
			new_link.find("a").text("Download " + link)
			$("#challengeModal #challenge-links").append(new_link).show()
		}
	} 
	// if its a multiple choice question
	if (countries_to_challenges[cc]["type"] == "multiple") {
		$("#challengeModal form#flag-form").hide()
		$("#challengeModal form#upload-form").hide()
		$("#challengeModal form#multiple-form").show()
		// add the multiple choice values
		$("#challengeModal form#multiple-form td#challenge-a").text(countries_to_challenges[cc]["a"]).attr("class","").addClass(countries_to_challenges[cc]["a"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_"))
		$("#challengeModal form#multiple-form td#challenge-b").text(countries_to_challenges[cc]["b"]).attr("class","").addClass(countries_to_challenges[cc]["b"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_"))
		$("#challengeModal form#multiple-form td#challenge-c").text(countries_to_challenges[cc]["c"]).attr("class","").addClass(countries_to_challenges[cc]["c"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_"))
		$("#challengeModal form#multiple-form td#challenge-d").text(countries_to_challenges[cc]["d"]).attr("class","").addClass(countries_to_challenges[cc]["d"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_"))
		$("#challengeModal form#multiple-form .submit-multiple#flag-a").data("flag", countries_to_challenges[cc]["a"])
		$("#challengeModal form#multiple-form .submit-multiple#flag-b").data("flag", countries_to_challenges[cc]["b"])
		$("#challengeModal form#multiple-form .submit-multiple#flag-c").data("flag", countries_to_challenges[cc]["c"])
		$("#challengeModal form#multiple-form .submit-multiple#flag-d").data("flag", countries_to_challenges[cc]["d"])
		$('.submit-multiple').each(function(){
			$(this).removeClass("inactive").removeClass("correct")
			$(this).data('country-code',cc)
			$(this).data('challenge-id',countries_to_challenges[cc]["id"])
		});
	} else if (countries_to_challenges[cc]["type"] == "timed") {
		$("#challengeModal form#flag-form").hide()
		$("#challengeModal div#countdown-form").show()
		$("#challengeModal form#upload-form").hide()
		$("#challengeModal form#multiple-form").hide()
		// initialise the clock with the deadline
		initializeClock('countdown-form', countries_to_challenges[cc]["deadline"]);
		$('#challengeModal #hint table').hide();
	} 
	else if (countries_to_challenges[cc]["type"] == "upload") {
		$("#challengeModal form#flag-form").hide()
		$("#challengeModal div#countdown-form").hide()
		$("#challengeModal form#multiple-form").hide()
		$("#challengeModal form#upload-form").show()
		// initialise the clock with the deadline
		// initializeClock('countdown-form', countries_to_challenges[cc]["deadline"]);
		$('#challengeModal #hint table').hide();
	} else if (countries_to_challenges[cc]["type"] == "timed,upload") {
		$("#challengeModal form#flag-form").hide()
		$("#challengeModal div#countdown-form").show()
		$("#challengeModal form#multiple-form").hide()
		$("#challengeModal form#upload-form").show()
		// initialise the clock with the deadline
		initializeClock('countdown-form', countries_to_challenges[cc]["deadline"]);
		$('#challengeModal #hint table').hide();
	} else {
		$("#challengeModal form#flag-form").show()
		$("#challengeModal form#upload-form").hide()
		$("#challengeModal div#countdown-form").hide()
		$("#challengeModal form#multiple-form").hide()
	}

	// if the hint has already been bought
	if (countries_to_challenges[cc].hasOwnProperty("hint")) {
		$('#challengeModal td#hint-content').text(countries_to_challenges[cc]["hint"])
		$('#challengeModal #hint table').addClass("greyed-out")
		$('#challengeModal #hint table').removeClass("inactive")
		$('#challengeModal #hint-btn').hide()
	} else {
		$('#challengeModal td#hint-content').text("use a hint..")
		$('#challengeModal #hint table').removeClass("greyed-out")
		$('#challengeModal #hint table').removeClass("inactive")
		$('#challengeModal #hint-btn').show()
	}

	// if its already been completed
	if (countries_to_challenges[cc].hasOwnProperty("complete")) {
		if (countries_to_challenges[cc]["complete"])
			if (countries_to_challenges[cc]["type"] == "jeopardy") {
				$('#challengeModal input#text-flag').val(countries_to_challenges[cc]["flag"]).addClass("inactive").prop("disabled",true);
				$('#challengeModal #submit').hide()
				$('#challengeModal #hint table').addClass("inactive")
			} else if (countries_to_challenges[cc]["type"] == "multiple") {
				$("table#multiple-choice td."+countries_to_challenges[cc]["flag"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_")).addClass("correct");
				$("table#multiple-choice td."+countries_to_challenges[cc]["flag"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_")).prev("th").find("button").addClass("correct");
				$("table#multiple-choice td:not(."+countries_to_challenges[cc]["flag"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_")+")").addClass("inactive");
				$("table#multiple-choice td:not(."+countries_to_challenges[cc]["flag"].replace(/[^a-zA-Z ]/g, "").replace(/ /g,"_")+")").prev("th").find("button").addClass("inactive");
			}
		} else {
			$('#challengeModal input#text-flag').val("").removeClass("inactive").prop("disabled",false);
			$('#challengeModal #submit').show()
		}

		// reset the teams completed table
		$("table#teams-completed tbody").html("")
		// do the teams already completed
		for (team in countries_to_challenges[cc]["teams_completed"]) {
			row = "<tr><td>"+countries_to_challenges[cc]["teams_completed"][team]+"</td></tr>"
			$("table#teams-completed tbody").append(row)
		}
}

//   
// 
// 
//      