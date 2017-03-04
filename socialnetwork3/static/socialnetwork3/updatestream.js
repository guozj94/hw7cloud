function getStream() {
	$.ajax({
		url: "/socialnetwork3/getstream",
		data: "csrfmiddlewaretoken="+getCSRFToken(),
		dataType: "json",
		success: updateStream
	});
}

function updateStream(posts) {
	$("ol li").remove();
	console.log("remove!");
	var count = 0;
	$(posts).each(function() {
		$("#posts").append(
			'<li><form method="post" action="/socialnetwork3/profile"><input type="hidden" value="'+this.id+'"><div class="row" style="background: white; margin-bottom: 10px; width: 100%;"><img src="/socialnetwork3/photo/'+
			this.user_id+
			'" width="100px" height="100px" style="margin: 10px;"><div class="column" style="width: 100%"><div class="row" id="personal"><p>'+
			this.first_name+
			'</p><p>&nbsp</p><p>'+
			this.last_name+
			'</p><p>&nbsp &nbsp</p><button type="submit" name="username" id="username" value="'+
			this.username+
			'">'+
			this.username+
			'</button><p>&nbsp &nbsp</p><p style="color: grey; font-weight: 300;">'+
			this.date.replace('T', '  ').replace('Z', ' ') +
			'</p><p>&nbsp &nbsp &nbsp</p><button type="submit" name="follow" id="username" value="Follow">Follow</button><p>&nbsp &nbsp &nbsp</p><button type="submit" name="unfollow" id="username" value="Unfollow">Unfollow</button><input type="hidden" name="followuser" value="'+
			this.username+
			'"></div><div class="row" id="content"><p>'+
			this.post+
			'</p></div>'+ //here start the comments
			'<div class="column comments thisismsg" id="message'+count+'"style="background: rgb(240,240,240); padding: 0;margin-top: 40px;">'+
			'</div>'+//end the comments, start the input
			'<div class="row create-new-comment" style="padding: 0">'+
			'<input type="text" class="create-new-comment-input" style="margin-left: 20px;width: 400px;">'+
			'<button type="button" class="create-new-comment-submit">Create Comment</button>'+
			'</div>'+
			'</div></div><input type="hidden" name="csrfmiddlewaretoken" value="'+
			getCSRFToken()+
			'"></form></li>');
		//append comment class and input at each message
		$(this.comments).each(function() {
			$('#message'+count+'').append(
				'<div class="row comment" style="background: rgb(240,240,240);padding: 10px;">'+
				'<img src="/socialnetwork3/photo/'+this.user_id+'" width="50px" height="50px">'+
				'<div class="column" id="comment" style="background: rgb(240,240,240);padding: 0; padding-left: 10px;">'+
				'<div class="row">'+
				'<p>'+this.user__first_name+'</p>'+
				'<p>&nbsp</p>'+
				'<p>'+this.user__last_name+'</p>'+
				'<p>&nbsp &nbsp</p>'+
				'<p style="color: grey; font-weight: 300;">'+
				''+this.commentdate.replace('T', '  ').replace('Z', ' ')+'</p>'+
				'</div>'+
				'<div class="row">'+
				'<p>'+this.comment+'</p>'+
				'</div>'+
				'</div>'+
				'</div>');
		});
		count++;
	});
}

function generateURL(keyword) {
	return "{% url some_url %}".replace("some_url", keyword)
}

function displayError(message) {
    $(".error").append('<p>'+message+'</p>');
}

function create_comment() {
	$(document).on("click", ".create-new-comment-submit", function() {
		new_comment_element = $(this).parent().find(".create-new-comment-input");
		new_comment = new_comment_element.val();

		comment_to_message = $(this).parent().parent().parent().parent().find("input").val();
		displayError('');
		console.log(comment_to_message);
		new_comment_element.val('');
		$.ajax({
			url: "/socialnetwork3/create_comment_ajax",
			type: "POST",
			data: "comment="+new_comment+"&comment_to_message="+comment_to_message+"&csrfmiddlewaretoken="+getCSRFToken(),
			dataType: "json",
			success: function(response) {
				if(response.success) getStream();
				else displayError(response.error);
			}
		});
	});
}

function create() {
    $("#new-post-submit").click(function() {
        new_post = $("#input-content").val();
        if(new_post == '') {
        	displayError("You must create some content");
        	return "error";
        }
        if(new_post.length > 200) {
        	displayError("Text length must less than 200 characters.");
        	return "error";
        }
        $("#input-content").val('');
        displayError('');
        console.log("yay");
        $.ajax({
        	url: "/socialnetwork3/create_ajax",
        	type: "POST",
        	data: "content="+new_post+"&csrfmiddlewaretoken="+getCSRFToken(),
        	dataType: "json",
        	success: function(response) {
        		if(response.success) getStream();
        		else displayError(response.error);
        	}
        });
    });
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

function isInputEmpty() {
	var isInputEmpty_flag = true;
	$(".create-new-comment-input").each(function() {
		if($(this).val()) {
			isInputEmpty_flag = false;
			return false;
		}
	});
	return isInputEmpty_flag;
}

$(document).ready(function() {
	var keypress_flag = false;
	console.log("ready");
	getStream();
	create();
	create_comment();
	reload = setInterval(getStream, 5000);
	$(document).on("click", ".create-new-comment-submit", function() {
		clearInterval(reload);
		reload = setInterval(getStream, 5000);
	});
	setInterval(function() {
		if(isInputEmpty()) {
			clearInterval(reload);
			getStream();
		}
		else {
			clearInterval(reload);
		}
	}, 5000);
});