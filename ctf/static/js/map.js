//                        _     
//  _ __ ___   __ _ _ __ (_)___ 
// | '_ ` _ \ / _` | '_ \| / __|
// | | | | | | (_| | |_) | \__ \
// |_| |_| |_|\__,_| .__// |___/
//                 |_| |__/     
// 

function updateAnnouncements() {
	$(".announcements").html("")
	for (announcement in announcements) {
		var announcement_span = '<div><span class="date">'+announcements[announcement]["time"]+'</span><span class="content"> '+announcements[announcement]["announcement"]+'</span></div>'
		$(".announcements").append(announcement_span)
	}
}

function submitFlag(span) {
	var challenge_id = $(span).data('challenge-id');
	var cc = $(span).data("country-code")
	var flag = $("#text-flag").val()
	if (countries_to_challenges[cc].hasOwnProperty("complete")) {
		dialog("You already completed this challenge!")
	} else {
		$.post("/submit", {"challenge_id": challenge_id, "flag": flag}, function(data) {});
	}
}

function submitSubmission(span) {
	event.preventDefault();
	var challenge_id = $(span).data('challenge-id');
	var cc = $(span).data("country-code");
	var data = new FormData($(span).closest("form")[0])
	data.append('challenge_id', challenge_id);
	data.append('flag', "");
    if (countries_to_challenges[cc].hasOwnProperty("complete")) {
		dialog("You already completed this challenge!")
	} else { 
		$.ajax({
			url: "/submit",
			type: "POST",
			dataType: "JSON",
			data: data,
			processData: false,
			contentType: false
		})
	}        
	// var flag = $("#text-flag").val()
	// if (countries_to_challenges[cc].hasOwnProperty("complete")) {
	// 	dialog("You already completed this challenge!")
	// } else {
	// 	$.post("/submit", {"challenge_id": challenge_id, "flag": flag}, function(data) {});
	// }
}

function buyHint(span) {
	var cc = $(span).data("country-code")
	var challenge_id = $(span).data('challenge-id')
	console.log(cc)
	if (countries_to_challenges[cc].hasOwnProperty("hint")) {
		dialog("You already own this hint!")
	} else {
		$.post("/hint", {"challenge_id": challenge_id}, function(data) {});
	}
}

function launchChallenge(span) {
	var cc = $(span).data("country-code")
	var challenge_id = $(span).data("challenge-id")
	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// make the country pulse
	$(id).addClass("pulse")
	$(id).css({"fill":"#993B2A"})

	$.post("/launch", {"challenge_id": challenge_id}, function(data) {});

	// make the button spin!
	$(span).addClass("active");
	// set the status to launching
	countries_to_challenges[cc]["challenge_url"] = "launching"
}

function killChallenge(span) {
	var cc = $(span).data("country-code")
	var challenge_id = $(span).data("challenge-id")
	$.post("/kill", {"challenge_id": challenge_id}, function(data) {});
	// make the button spin!
	$(span).addClass("active");
	// set the status to killing
	countries_to_challenges[cc]["challenge_url"] = "killing"
}

function killAllChallenges() {
	$.post("/killall", function(data) {});
}

jQuery(document).ready(function() {

	// get the colors for the map
	
	// hide the fullscreen video
	background_color = getComputedStyle($("body")[0]).getPropertyValue('--background-color');
	complete_color = getComputedStyle($("body")[0]).getPropertyValue('--complete-color');
	highlight_color = getComputedStyle($("body")[0]).getPropertyValue('--highlight-color');
	map_color = getComputedStyle($("body")[0]).getPropertyValue('--map-color');
	map_outline = getComputedStyle($("body")[0]).getPropertyValue('--map-outline');

	$(document).on("click",".copy",function(event){
	    var $tempElement = $("<input>");
	    $("body").append($tempElement);
	    $tempElement.val($(this).text()).select();
	    document.execCommand("copy");
	    $tempElement.remove();
	    var original = $(this).text()
	    var span = $(this)
	    $(this).text("copied!")
	    setTimeout(function(){$(span).text(original)},1000)
	});

	$(document).on('click','.submit-multiple', function(e){
		e.preventDefault();
		var challenge_id = $(this).data('challenge-id');
		var flag = $(this).data('flag')
		if (countries_to_challenges[$(this).data("country-code")].hasOwnProperty("complete")) {
			dialog("You already completed this challenge!")
		} else {
			$.post("/submit", {"challenge_id": challenge_id, "flag": flag}, function(data) {});
		}
	});

	// socket.on("challenge_launching", function(data) {
	// 	var cc = data["country_code"]
	//         var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
 //        	$(id).addClass("pulse")
	//         $(id).css({"fill":"#993B2A"})
	// 	$(".launch[data-country-code='"+data["country_code"]+"']").addClass("active");
 //        	countries_to_challenges[data["country_code"]]["challenge_url"] = "launching"
	// });

	// socket.on("challenge_update", function(data){
	// 	$("span.challenge-url[data-country-code='"+data["country_code"]+"']").text(data["update"])
	// });

	// socket.on("challenge_launched", function(data){
	// 	// data contains the country code and the address to the challenge
	// 	// if the challenge is the one open
	// 	var cc = data["country_code"];
	// 	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// 	$(id).removeClass("pulse")
	// 	$(id).css({"fill":$(id).attr("data-original-color")})
	// 	if ($('#modal input#country-code').val() == data["country_code"]) {
	// 			$(".launch").removeClass("active");
	// 			$(".launch").hide();
	// 			$(".kill").show()
	// 			countries_to_challenges[data["country_code"]]["challenge_url"] = data["challenge_url"]
	// 			// append the challenge url to the description
	// 			$('#modal div#challenge-description').html($('#modal div#challenge-description').text() + "\n\nYou can access this challenge here: <span class='copy challenge-url'>"+data["challenge_url"]+"</span>")	

	// 	} else {
	// 		countries_to_challenges[data["country_code"]]["challenge_url"] = data["challenge_url"]
	// 	}
	// 	$("span.challenge-url[data-country-code='"+data["country_code"]+"']").text(data["challenge_url"])
	// 	$(".kill[data-country-code='"+data["country_code"]+"'").show()

	// });

	// socket.on("challenge_failed", function(data){
	// 	// data contains the country code and the address to the challenge
	// 	// if the challenge is the one open
	// 	var cc = data["country_code"];
	// 	dialog(data["error"])
	// 	$(".launch").removeClass("active");
	// 	var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
	// 	$(id).removeClass("pulse")
	// 	$(id).css({"fill":$(id).attr("data-original-color")})
	// 	delete countries_to_challenges[data["country_code"]]["challenge_url"];
	// });

	// socket.on("challenge_killed", function(data){
	// 	// data contains the country code and the address to the challenge
	// 	// if the challenge is the one open
	// 	if ($('#modal input#country-code').val() == data["country_code"]) {
	// 			$(".kill[data-country-code='"+data["country_code"]+"']").removeClass("active");
	// 			$(".kill[data-country-code='"+data["country_code"]+"']").hide();
	// 			$(".launch[data-country-code='"+data["country_code"]+"']").show();
	// 			delete countries_to_challenges[data["country_code"]]["challenge_url"];
	// 			// set description back to default
	// 			$('#modal div#challenge-description').text(countries_to_challenges[data["country_code"]]["description"])
	// 			$("#chals .kill[data-country-code='"+data["country_code"]+"']").closest("tr").remove();
	// 	} else {
	// 		$("#chals .kill[data-country-code='"+data["country_code"]+"']").closest("tr").remove();
	// 		$(".launch[data-country-code='"+data["country_code"]+"']").show();
	// 		delete countries_to_challenges[data["country_code"]]["challenge_url"]
	// 	}
	// });

	// socket.on("challenge_already_launched", function() {
	// 	dialog("Your team already has an instance of this challenge!")
	// });

	// socket.on("too_many_challenges", function() {
	// 	dialog("Your team already has too many challenges running..")
	// });

	// socket.on("challenge_already_killed", function() {
	// 	dialog("Your team doesn't have an instance of this challenge!")
	// });

	doMapColors()

	var vmap = jQuery('#vmap').vectorMap({
		map: 'world_en',
		colors: colors,
		backgroundColor: null,
		selectedColor: null,
		pins: pins,
		color: map_color,
		borderColor: map_outline,
		borderOpacity: '1',
		borderWidth: '0.5',
		hoverColor: null,
		enableZoom: true,
		showTooltip: false,
		onRegionOver: function(event, cc)
        {
			if (cc in countries_to_challenges) {
				if (countries_to_challenges[cc].hasOwnProperty("complete")) {
						// if it has a complete key
							if (countries_to_challenges[cc]["complete"] == false) {
								// if its not complete
								var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
								var offset = $(id).offset();
								var left_offset = offset.left;
								var top_offset = offset.top;
								openPreview(left_offset, top_offset, cc);
							}
				} else {
						// if complete is set to false
						var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
						var offset = $(id).offset();
						var left_offset = offset.left;
						var top_offset = offset.top;
						openPreview(left_offset, top_offset, cc);
						$(id).css({"fill":highlight_color})
				}
			}

        },
		onRegionOut: function(event, cc)
	      {
			var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
			$('#challenge-preview').css({'position':'relative'}).hide();
			if (cc in countries_to_challenges) {
				// if it has a challenge on
				if (countries_to_challenges[cc].hasOwnProperty("complete")) {
						// if it has a complete key
						if (countries_to_challenges[cc]["complete"] == false) {
							// if its not complete
							$(id).css({"fill":background_color})
						} else {
							// if it is complete
							$(id).css({"fill":complete_color})
						}
				} else {
					// if it doesn't have a complete key
					if (countries_to_challenges[cc].hasOwnProperty("color")) {
						$(id).css({"fill":countries_to_challenges[cc]["color"]})
					} else {
						$(id).css({"fill":background_color})
					}
					// if its launching it need to be tomato
					if (countries_to_challenges[cc].hasOwnProperty("challenge_url")) {
						if (countries_to_challenges[cc]["challenge_url"] == "launching") {
							$(id).css({"fill":"#993B2A"})
						}
					}
				}
			}
	      },
		onRegionClick: function(event, cc, region)
				{
					if (cc == "us") {

						showUSMap()

        			} else {

						if (cc in countries_to_challenges) {
							openChallengeModal(cc)
						}
					}
				},
	});

	var usmap = jQuery('#usmap').vectorMap({
		map: 'us_merc',
		colors: colors,
		pins: pins,
		backgroundColor: null,
		selectedColor: null,
		color: map_color,
		borderColor: map_outline,
		borderOpacity: '1',
		borderWidth: '0.5',
		hoverColor: null,
		enableZoom: true,
		showTooltip: false,
		onRegionOver: function(event, cc)
        {
			if (cc in countries_to_challenges) {
				if (countries_to_challenges[cc].hasOwnProperty("complete")) {
						// if it has a complete key
							if (countries_to_challenges[cc]["complete"] == false) {
								// if its not complete
								var id = '#jqvmap2_' + cc;
								var offset = $(id).offset();
								var left_offset = offset.left;
								var top_offset = offset.top;
								openPreview(left_offset, top_offset, cc);
								$(id).css({"fill":highlight_color})
							}
					} else {
							// if complete is set to false
							var id = '#jqvmap2_' + cc;
							var offset = $(id).offset();
							var left_offset = offset.left;
							var top_offset = offset.top;
							openPreview(left_offset, top_offset, cc);
							$(id).css({"fill":highlight_color})
					}
				}
        },
		onRegionOut: function(event, cc)
		{
			var id = '#jqvmap2_' + cc;
			$('#challenge-preview').css({'position':'relative'}).hide();
			if (cc in countries_to_challenges) {
				// if it has a challenge on
				if (countries_to_challenges[cc].hasOwnProperty("complete")) {
						// if it has a complete key
						if (countries_to_challenges[cc]["complete"] == false) {
							// if its not complete
							$(id).css({"fill":background_color})
						} else {
							// if it is complete
							$(id).css({"fill":complete_color})
						}
				} else {
					// if it doesn't have a complete key
					if (countries_to_challenges[cc].hasOwnProperty("color")) {
						$(id).css({"fill":countries_to_challenges[cc]["color"]})
					} else {
						$(id).css({"fill":background_color})
					}
					// if its launching it need to be tomato
					if (countries_to_challenges[cc].hasOwnProperty("challenge_url")) {
						if (countries_to_challenges[cc]["challenge_url"] == "launching") {
							$(id).css({"fill":"#993B2A"})
						}
					}
				}
			}
		},
		onRegionClick: function(event, cc, region)
			{
				if (cc in countries_to_challenges) {
					openChallengeModal(cc)
				}
			},
	});

	$(".completed-triangle[id^='us-']").hide()

	async function showUSMap() {
		$("#vmap").hide()
		$(".completed-triangle").parent(":not([id^='us-'])").hide()
		// do compeleted again so the triangles are in the right place
		await $("#usmap").fadeIn();
		$("[for^='us-']").fadeIn();		
	}



	doMapLaunching();

	// var deadline = new Date(Date.parse(new Date()) + 15 * 24 * 60 * 60 * 1000);
	initializeClock('clockdiv', deadline);
	// put the jqvmap before the scanlines
	// $(".jqvmap-zoomin").insertBefore(".tv-container")
	// $(".jqvmap-zoomout").insertBefore(".tv-container")

});

function getTimeRemaining(endtime) {
  var t = Date.parse(endtime) - Date.parse(new Date());
  var seconds = Math.floor((t / 1000) % 60);
  var minutes = Math.floor((t / 1000 / 60) % 60);
  var hours = Math.floor((t / (1000 * 60 * 60)) % 24);
  var days = Math.floor(t / (1000 * 60 * 60 * 24));
  return {
    'total': t,
    'days': days,
    'hours': hours,
    'minutes': minutes,
    'seconds': seconds
  };


}

function initializeClock(id, endtime) {
	  var clock = document.getElementById(id);
	  var daysSpan = clock.querySelector('.days');
	  var hoursSpan = clock.querySelector('.hours');
	  var minutesSpan = clock.querySelector('.minutes');
	  var secondsSpan = clock.querySelector('.seconds');

	  function updateClock() {
	    var t = getTimeRemaining(endtime);

	    daysSpan.innerHTML = t.days;
	    hoursSpan.innerHTML = ('0' + t.hours).slice(-2);
	    minutesSpan.innerHTML = ('0' + t.minutes).slice(-2);
	    secondsSpan.innerHTML = ('0' + t.seconds).slice(-2);

	    if (t.total <= 0) {
	      clearInterval(timeinterval);
	    }
	  }

	  updateClock();
	  var timeinterval = setInterval(updateClock, 1000);
}

function toggleListView() {
	// make list view bigger/smaller
	$(".list-view-tab").toggleClass("active")
	// toggle modal container smaller
	$(".modal-container").toggleClass("small")
}

async function hideUSMap() {
	$("#usmap").hide()
	$(".completed-triangle").parent("[id^='us-']").hide()
	// do compeleted again so the triangles are in the right place
	await $("#vmap").fadeIn();
	// await doCompleted();
	$(".completed-triangle").parent(":not([id^='us-'])").show()
}

function doMapLaunching() {
	for (cc in countries_to_challenges) {
		// save the original color
		var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
		$(id).attr("data-original-color", colors[cc]);
		if (countries_to_challenges[cc].hasOwnProperty("challenge_url")) {
			if (countries_to_challenges[cc]["challenge_url"] == "launching") {
				$(id).addClass("pulse")
				$(id).css({"fill":"#993B2A"})
			}
		}
		if (countries_to_challenges[cc]["type"] == "timed") {
			var id = cc.includes("us-") ? '#jqvmap2_' + cc : '#jqvmap1_' + cc;
			$(id).addClass("pulse")
		}
	}
}

function doMapColors() {
	colors = {}
	pins = {}
	for (cc in countries_to_challenges) {
		// if its in a us state
		if (cc.split("-")[0] == "us") {
			if (countries_to_challenges[cc].hasOwnProperty("color")) {
				colors["us"] = countries_to_challenges[cc]["color"]
			} else {
				colors["us"] = background_color
			}
		}
		if (countries_to_challenges[cc].hasOwnProperty("complete")) {
			if (countries_to_challenges[cc]["complete"]) {
					colors[cc] = complete_color
					pins[cc] = "<div class='completed-triangle'></div>"
			} else {
				colors[cc] = background_color
			}
		} else {
			if (countries_to_challenges[cc].hasOwnProperty("color")) {
				colors[cc] = countries_to_challenges[cc]["color"]
			} else {
				colors[cc] = background_color
			}
		}
	}
}

function openPreview(x, y, cc) {
	$('#challenge-preview').css({'top':y,'left':x, 'position':'absolute'}).show();
	$('#challenge-preview td.challenge-name').html(countries_to_challenges[cc]["name"])
	$('#challenge-preview span#challenge-type').text(countries_to_challenges[cc]["type"].replace(",", " & "))
	$('#challenge-preview span#challenge-type').attr("class",countries_to_challenges[cc]["type"].replace(",", ""))
	$('#challenge-preview span#challenge-category').text(countries_to_challenges[cc]["category"])
	$('#challenge-preview span#challenge-category').attr("class",countries_to_challenges[cc]["category"])
	$('#challenge-preview span#challenge-points').text(countries_to_challenges[cc]["points"])
}



