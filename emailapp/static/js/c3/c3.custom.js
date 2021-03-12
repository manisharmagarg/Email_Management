function getGraph(month){
    var campaign_id = $("#campaign_id").val();
    var campaign_type = $("#campaign_type").val();

    if(campaign_id == 'None' && campaign_type == 'None'){
        var url = "/graph_data/"
    }else{
        var url = "/graph_data/"+campaign_id+"/"+campaign_type+"/"
    }

    $(".email_graph").each(function(){
        $.post(url, {'data':month}, function(response){
            console.log(response);
            var data = response

            var columns = [];
            var click = data.clicks
            var open = data.open
            var x = data.dates

            console.log(x);

            columns.push(x, click, open);

            var chart = c3.generate({

                bindto: '#splineGraph',
                data: {
                    x : 'x',
                    columns: columns,

                    types: {
                        click: 'spline',
                        open: 'area-spline'
                    },
                    names: {
                        click: 'Clicks',
                        open: 'Open'
                    },
                    colors: {
                        click: '#33FF9F',
                        open: '#33D4FF'
                    }

                },
                axis: {
                    x: {
                        type: 'category',
                        tick: {
                                values: ['']
                        }
                    }
                }

            });
        });
    });
};


$(document).ready(function(){
    getBasegraph();
});

    function getBasegraph(){
        $(".email_graph").each(function(){
            var campaign_id = $(this).attr("campaign_id");
            var campaign_type = $(this).attr("campaign_type");

            if(campaign_id == 'None' && campaign_type == 'None'){
                var url = "/graph_data/"
            }else{
                var url = "/graph_data/"+campaign_id+"/"+campaign_type+"/"
            }

            $.get(url, function(response){
                    console.log(response);
                    var data = response

                    var columns = [];
                    var click = data.clicks
                    var open = data.open
                    var x = data.dates

                    console.log(x);

                    columns.push(x, click, open);

                    var chart = c3.generate({

                        bindto: '#splineGraph',
                        data: {
                            x : 'x',
                            columns: columns,

                            types: {
                                click: 'spline',
                                open: 'area-spline'
                            },
                            names: {
                                click: 'Clicks',
                                open: 'Open'
                            },
                            colors: {
                                click: '#33FF9F',
                                open: '#33D4FF'
                            }

                        },
                        axis: {
                            x: {
                                type: 'category',
                                tick: {
                                        values: ['']
                                }
                            }
                        }

                    });
                });

        });
    }
