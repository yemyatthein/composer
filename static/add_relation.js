$(document).ready(function(){
    $(".av_resource").click(function() {
        to_hide_id = $(this).attr('id')
        to_hide_val = $(this).attr('value')
        x = $("#" + to_hide_id + "_div").remove()
        $('#added_div').show()
        $('#added_div').append(x)
        
        $('#form').append("<input type='checkbox' class='added_chk' name='resources' checked value=" + to_hide_val + " />"); 
        $(".added_chk").hide()
        return false;
    });
    
    $("#relation_name").autocomplete({
        source: function(req, add){
            $.getJSON($SCRIPT_ROOT + "get_relation_names", {
                rid: $("#resource_id").attr("value")
            }, function(data) {
                available_relations =  data.relation_names
            });
            add(available_relations);
        }  
    });
});
