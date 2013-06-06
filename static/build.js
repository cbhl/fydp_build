$(function() {
    var $logDiv = $('<div class="log">');
    var $logContentDiv = $('<div class="log-content">');
    $logDiv.append($logContentDiv);
    $("body").append($logDiv);

    var resizeLog = function(e) {
        $logDiv.css({
            position:'absolute',
            left: 0,
            top: 0,
            width: $(window).width(),
            height: $(window).height(),
            overflow: 'scroll'
        });
    }

    resizeLog();
    $(window).on("resize", resizeLog);

    if (!!window.EventSource) {
        var source = new EventSource("/build_log_stream");
        source.addEventListener('message', function(e) {
            console.log("ERROR: Got unexpected message event.");
            console.log(e);
            console.log(e.data);
        });
        source.addEventListener('buildlog', function(e) {
            $lineDiv = $('<div class="log-line">');
            $lineDiv.text(e.data);
            $logContentDiv.append($lineDiv);
        });
        source.addEventListener('buildloganimate', function(e) {
            $logDiv.animate({scrollTop: $logContentDiv.height()}, 500);
        });
        source.addEventListener('open', function(e) {
            console.log("INFO: Connection was opened.");
        });
        source.addEventListener('error', function(e) {
            if (e.readyState == EventSource.CLOSED) {
                console.log("INFO: Connection was closed.");
            }else{
                console.log("ERROR: EventSource reported an error.");
                console.log(e);
            }
        });
    }else{
        console.log("ERROR: EventSource isn't available.")
    }
});
