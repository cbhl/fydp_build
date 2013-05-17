$(function() {
    var $logDiv = $('<div class="log">');
    $("body").append($logDiv);

    var displayLog = function(data) {
        $logDiv.empty();
        _.each(data, function(line) {
            $lineDiv = $('<div class="log-line">');
            $lineDiv.text(line);
            $logDiv.append($lineDiv);
        });
        $logDiv.css({
            position:'absolute',
            left: 50,
            top: 50,
            width: $(window).width() - 100,
            height: $(window).height() -100,
            overflow: 'scroll'
        });
        $logDiv.animate({ scrollTop: $logDiv.scrollHeight}, 1000);
    };

    var logAjaxError = function(jqXHR, textStatus) {
        console.log("ERROR: " + textStatus);
    };

    var updateLog = function() {
        $.ajax({
            dataType: "json",
            url: "/log.json"
        }).then(displayLog, logAjaxError).then(function() {
            window.setTimeout(updateLog, 1000);
        });
    };

    updateLog();
});
