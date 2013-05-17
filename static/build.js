$(function() {
    var $logDiv = $('<div class="log">');
    $("body").append($logDiv);

    $.ajax({
        dataType: "json",
        url: "/log.json"
    }).then(function(data) {
        console.log(data);
        _.each(data, function(line) {
            $lineDiv = $('<div class="log-line">');
            $lineDiv.text(line);
            $logDiv.append($lineDiv);
        });
    }, function(a,b) {
        console.log(b);
    });
});
