var counter = 1;
var counter1 = 1;
var counter2 = 1;
var ico = '<p style=" margin-top: 0px;margin-bottom: 0px;cursor: pointer;"' + '><img height="30" width="40" src="/static/fonts/fa-plus-circle-o.svg"' + '></p >';
var segment_count = $("#segment_count").val();
var theCount = $("#theCount").text().trim();
var contentCount = $("#contentCount").text().trim();
var sendCount = $("#sendCount").text().trim();

//Update Counter value for each button click.

$(document).ready(function() {
    $("#addSubject").click(function(){
        if(theCount > 0) {
            counter = theCount;
        }
        if (counter < 3){
            counter++;
            $("#theCount").text(counter);
            theCount = counter;

            var filter = "subject_lines";
            summary(filter, counter);
        }
    });

    $("#minSubject").click(function(){
        if(theCount > 1) {
            counter = theCount;
        }
        if (counter > 1){
            counter--;
            $("#theCount").text(counter);
            theCount = counter;

            var filter = "subject_lines";
            summary(filter, counter);
        }

        if (counter == 1){
            $(this).parent().css("background-color", "#E8E8E8");
            $(this).css("display", "none");
            $("#addSubject").css("display", "none");
            $('#theCount').html(ico);
            $("#contentCount").removeAttr("disabled").on('click', contentFilter());
            $("#contentCount").parent().parent().css("opacity", "1");
            $("#sendCount").removeAttr("disabled").on('click', sendFilter());
            $("#sendCount").parent().parent().css("opacity", "1");
        }
    });

    $("#addContent").click(function(){
        if(contentCount > 0) {
            counter1 = contentCount;
        }
        if (counter1 < 3){
            counter1++;
            $("#contentCount").text(counter1);
            contentCount = counter1;

            var filter = "content_template";
            summary(filter, counter1);
        }
    });

    $("#minContent").click(function(){
        if(contentCount > 1) {
            counter1 = contentCount;
        }
        if (counter1 > 1){
            counter1--;
            $("#contentCount").text(counter1);
            contentCount = counter1;

            var filter = "content_template";
            summary(filter, counter1);
        }
        if (counter1 == 1){
            $(this).parent().css("background-color", "#E8E8E8");
            $(this).css("display", "none");
            $("#addContent").css("display", "none");
            $('#contentCount').html(ico);
            $("#theCount").removeAttr("disabled", "disabled").on('click', countFilter());
            $("#theCount").parent().parent().css("opacity", "1");
            $("#sendCount").removeAttr("disabled", "disabled").on('click', sendFilter());
            $("#sendCount").parent().parent().css("opacity", "1");
        }
    });


    $("#addSend").click(function(){
        if(sendCount > 0) {
            counter2 = sendCount;
        }
        if (counter2 < 3){
            counter2++;
            $("#sendCount").text(counter2);
            sendCount = counter2;

            var filter = "send_time";
            summary(filter, counter2);
        }
    });

    $("#minSend").click(function(){
        if(sendCount > 1) {
            counter2 = sendCount;
        }

        if (counter2 > 1){
            counter2--;
            $("#sendCount").text(counter2);
            sendCount = counter2;

            var filter = "send_time";
            summary(filter, counter2);
        }
        if (counter2 == 1){
            $(this).parent().css("background-color", "#E8E8E8");
            $(this).css("display", "none");
            $("#addSend").css("display", "none");
            $('#sendCount').html(ico);
            $("#theCount").removeAttr("disabled", "disabled").on('click', countFilter());
            $("#theCount").parent().parent().css("opacity", "1");
            $("#contentCount").removeAttr("disabled", "disabled").on('click', contentFilter());
            $("#contentCount").parent().parent().css("opacity", "1");
        }
    });

    countFilter();
    contentFilter();
    sendFilter();
    summaryCalculation();
    check_ini();

});

// Initial values check

function check_ini(){
    if(theCount > 1){
        $("#minSubject").css("display", "inline-block");
        $("#addSubject").css("display", "inline-block");
        $("#theCount").parent().parent().css("background-color", "#fff");
        $("#contentCount").attr("disabled", "disabled").off('click');
        $("#contentCount").parent().parent().css("opacity", "0.5");
        $("#sendCount").attr("disabled", "disabled").off('click');
        $("#sendCount").parent().parent().css("opacity", "0.5");

        $('#counter').val(theCount);
        $('#filter').val("subject_lines");
        slider_val(theCount);

    }
    if(contentCount > 1){
        $("#minContent").css("display", "inline-block");
        $("#addContent").css("display", "inline-block");
        $("#contentCount").parent().parent().css("background-color", "#fff");
        $("#theCount").attr("disabled", "disabled").off('click');
        $("#theCount").parent().parent().css("opacity", "0.5");
        $("#sendCount").attr("disabled", "disabled").off('click');
        $("#sendCount").parent().parent().css("opacity", "0.5");

        $('#counter').val(contentCount);
        $('#filter').val("content_template");
        slider_val(contentCount);
    }
    if(sendCount > 1){
        $("#minSend").css("display", "inline-block");
        $("#addSend").css("display", "inline-block");
        $("#sendCount").parent().parent().css("background-color", "#fff");
        $("#theCount").attr("disabled", "disabled").off('click');
        $("#theCount").parent().parent().css("opacity", "0.5");
        $("#contentCount").attr("disabled", "disabled").off('click');
        $("#contentCount").parent().parent().css("opacity", "0.5");

        $('#counter').val(sendCount);
        $('#filter').val("send_time");
        slider_val(sendCount);
    }
}

// filter enable disable and click

function countFilter(){
    $("#theCount").click("on", function(){
        $("#minSubject").css("display", "inline-block");
        $("#addSubject").css("display", "inline-block");
        $("#addSubject").trigger("click");
        $(this).parent().parent().css("background-color", "#fff");
        $("#contentCount").attr("disabled", "disabled").off('click');
        $("#contentCount").parent().parent().css("opacity", "0.5");
        $("#sendCount").attr("disabled", "disabled").off('click');
        $("#sendCount").parent().parent().css("opacity", "0.5");
    });
}

function contentFilter(){
    $("#contentCount").click("on", function(){
        $("#minContent").css("display", "inline-block");
        $("#addContent").css("display", "inline-block");
        $("#addContent").trigger("click");
        $(this).parent().parent().css("background-color", "#fff");
        $("#theCount").attr("disabled", "disabled").off('click');
        $("#theCount").parent().parent().css("opacity", "0.5");
        $("#sendCount").attr("disabled", "disabled").off('click');
        $("#sendCount").parent().parent().css("opacity", "0.5");
    });
}

function sendFilter(){
    $("#sendCount").click("on", function(){
        $("#minSend").css("display", "inline-block");
        $("#addSend").css("display", "inline-block");
        $("#addSend").trigger("click");
        $(this).parent().parent().css("background-color", "#fff");
        $("#theCount").attr("disabled", "disabled").off('click');
        $("#theCount").parent().parent().css("opacity", "0.5");
        $("#contentCount").attr("disabled", "disabled").off('click');
        $("#contentCount").parent().parent().css("opacity", "0.5");
    });
}

// Campaign slider get & display value on UI.

$(document).ready(function(){
    $("#slider_percentage").slider();
    $("#slider_percentage").on("slide", function(slideEvt) {
        $("#percentage").val(slideEvt.value);
        $("#test_segment").text(slideEvt.value);
        $("#winning_segment").text(slideEvt.value);
        var winning_segment = $("#winning_segment").text();
        var segment_count_value = $("#segment_count_value").text();
        var data = winning_segment/100;
        var test_segment = segment_count_value*data | 0;
        $("#test").text(test_segment);
        $("#winning").text(test_segment);
    });

});

// Summary values calculation with back button

function summaryCalculation(){
    var winning_segment = $("#winning_segment").text();
    var total_segments = $("#total_segments").text();
    var test_segments = $("#test_segment").text();
    var count = $("#count").val();
    var recipients = total_segments/count | 0;
    var data = recipients/100;
    var test_segment = test_segments*data | 0;
    $("#test").text(test_segment);
    $("#winning").text(test_segment);
    $("#segment_count_value").text(recipients);
}

// Summary values calculation

function summary(filter, count){
    var winning_segment = $("#winning_segment").text();
    var val = segment_count/count;
    var value = val.toFixed();
    $("#segment_count_value").text(value);

    var data = winning_segment/100;
    var values = value * data;
    var test_segment = values | 0;
    $("#test").text(test_segment);
    $("#winning").text(test_segment);

    $('#counter').val(count);
    $('#filter').val(filter);

    if(count == 2){
        var bck = "linear-gradient(to right,#fff 1px,transparent 0) 0 0/ 50% 100%";
    }else if(count == 3){
        var bck = "linear-gradient(to right,#fff 1px,transparent 0) 0 0/ 33% 100%";
    }else {
        var bck = "linear-gradient(to right,#fff 1px,transparent 0) 0 0/ 100% 100%";
    }

    $(".slider-selection").css("background", bck).css("background-image", "linear-gradient(to right, rgb(255, 255, 255) 1px, rgba(13, 150, 246) 0px)");

}

// Initial slider value

function slider_val(count){
    if(count == 2){
        var bck = "linear-gradient(to right,#fff 1px,transparent 0) 0 0/ 50% 100%";
    }else if(count == 3){
        var bck = "linear-gradient(to right,#fff 1px,transparent 0) 0 0/ 33% 100%";
    }else {
        var bck = "linear-gradient(to right,#fff 1px,transparent 0) 0 0/ 100% 100%";
    }

    setTimeout(function(){
        $(".slider-selection").css("background", bck).css("background-image", "linear-gradient(to right, rgb(255, 255, 255) 1px, rgba(13, 150, 246) 0px)");
    }, 500);
}

// Post the form data.

$(function(){
    $(".btn_campaign").on("click", function(){
        var theCount = $("#theCount").text().trim();
        var contentCount = $("#contentCount").text().trim();
        var sendCount = $("#sendCount").text().trim();
        var percentage = $("#percentage").val();
        var rate = $("#rate").val();
        var time_after = $("#time_after").val();
        var time_type = $("#time_type").text();
        if(theCount || contentCount || sendCount){
            if(percentage && time_after && rate && time_type){
                $("#ab_campaign_form").submit();
            } else{
                swal("Oops something wasn't right!", "Time field is required!");
            }
        }else{
            swal("Oops something wasn't right!", "Select any one variable!");
        }
    });
});

