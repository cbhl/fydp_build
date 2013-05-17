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
