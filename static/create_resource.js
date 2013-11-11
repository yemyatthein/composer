$(document).ready(function(){
    var images = new Array();
    var cur_index = 0
    $("#url").bind('paste', function() {
        setTimeout(function () {
            var url_str = $("#url").val()
            $.getJSON($SCRIPT_ROOT + "extract_webinfo", {
                url: url_str
            }, function(data) {
                images = data.images
                $("#title").val(data.title)
                $("#desc").val(data.desc)
                $("#thumbnail").attr("src", data.img);
                $('#img_block').show()
            });
        }, 100);
    });
    $("#previous_image").click(function() {
        if (cur_index == 0) {
            cur_index = images.length - 1
        }
        else{
            cur_index = cur_index - 1
        }
        $("#thumbnail").attr("src", images[cur_index]);
        return false;
    });
    $("#next_image").click(function() {
        if (cur_index == images.length - 1) {
            cur_index = 0
        }
        else{
            cur_index = cur_index + 1
        }
        $("#thumbnail").attr("src", images[cur_index]);
        return false;
    });
    $("#submit").click(function() {
        $("#image_url").val($("#thumbnail").attr("src"))
    });
});