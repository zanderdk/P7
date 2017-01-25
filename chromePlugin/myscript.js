var url = window.location.href
url = url.split("/wiki/")[1]

prefix = "http://192.38.56.57:10008/checkpage?title="

$(function() {

        var randomLink = $('a[href="/wiki/Special:Random"]').attr("href", "/wiki/IBM")
	$.getJSON(prefix+url, (data) => {

		lst = []
		data.forEach((x) => {
			if (x.includes("_")) {
				lst.push(x.replace(/_/g, " "))
			}
		})
		lst.sort((a,b) => {
			return b.length - a.length;
		});

		console.log(lst)

		$("p").html((index, html) => {

			lst.forEach(x => {
				var searchMask = x;
				var regEx = new RegExp('(' + searchMask + ')', "ig");
				var replaceMask = "<mark>$1</mark>";

				var result = html.replace(regEx, replaceMask);
				html = result
				//html = html.replace("/" + x + "/ig", "<mark>" + x + "</mark>")
			})

			return html
		})

	})

});

