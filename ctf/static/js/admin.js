jQuery(document).ready(function () {
	// on submit of any forms
	$(document).on('submit', 'form', function (e) {
		e.preventDefault()
		form = $(this)
		button = $(form).find("button[type='submit']");
		// make button 'work'
		$(button).html("<i class='fas fa-spinner fa-pulse'></i>")
		// send the data to /admin
		$.post('/admin', $(this).serialize(), function (data) {
			if (data.hasOwnProperty("reload")) {
				window.location.reload();
			} else if ("error" in data) {
				error(data["error"]);
			} else {
				// set button to success
				button.html("Success!");
				// set it back in 3s 
				setTimeout(function() { $(button).html("Submit"); }, 3000);
			}
		});
	});
	// ninitialize toltips
	$('[data-toggle="tooltip"]').tooltip({ html: true, container: 'body'})
	// initialise the popovers
	$("[data-toggle='popover']").popover({ html: true }).click(function (event) {
		event.stopPropagation();

	}).on('inserted.bs.popover', function () {
		$(".popover").click(function (event) {
			event.stopPropagation();
		})
	})
	$(document).click(function () {
		$("[data-toggle='popover']").popover('hide')
	})
	// when clicked!
	$(document).on("click",".copy", function(event){
		$(this).find(".copy-this").each(function() {
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
	});
});

function error(message) {
	alert(message);
}
