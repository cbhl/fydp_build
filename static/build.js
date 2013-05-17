$(function() {
    var $logDiv = $('<div class="log">');
    var $logContentDiv = $('<div class="log-content">');
    $logDiv.append($logContentDiv);
    $("body").append($logDiv);

    var displayLog = function(data) {
        $logContentDiv.empty();
        _.each(data, function(line) {
            $lineDiv = $('<div class="log-line">');
            $lineDiv.text(line);
            $logContentDiv.append($lineDiv);
        });
        $logDiv.css({
            position:'absolute',
            left: 50,
            top: 50,
            width: $(window).width() - 100,
            height: $(window).height() -100,
            overflow: 'scroll'
        });
        $logDiv.animate({ scrollTop: $logContentDiv.height()}, 500);
    };

    var logAjaxError = function(jqXHR, textStatus) {
        console.log("ERROR: " + textStatus);
    };

    var updateLog = function() {
        $.ajax({
            dataType: "json",
            url: "/log.json"
        }).then(displayLog, logAjaxError).then(function() {
            window.setTimeout(updateLog, 10000);
        });
    };

    updateLog();
});
