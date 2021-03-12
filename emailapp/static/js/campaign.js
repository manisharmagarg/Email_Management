$(function(){
    $(".email_graph").each(function(){
        var self = $(this);
        var campaign_id = $(this).attr("campaign_id");
        $.get("/campaign/get-graph-data/"+ campaign_id, function(response){
        var total = response.total_emails;
        var unsubscribe_emails = response.unsubscribe_emails;
        var sent_emails =  response.sent_emails;
        var error_emails =  response.error_emails;

        var graph_id = self.attr("id");
        Highcharts.chart(graph_id, {
            chart: {
                type: 'column'
            },
            title: {
                text: ''
            },
            xAxis: {
                categories: ['Campaign Progress']
            },
            yAxis: {
                enabled: false,
                min: 0,
                title: {
                    text: ''
                },
                stackLabels: {
                    enabled: true,
                    style: {
                        fontWeight: 'bold',
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            },

            tooltip: {
                formatter: function(){
                    console.log(this);
                    return "<b>"+ this.series.name +" Emails : " + this.point.y + "</b>"
                },
                useHTML: true
            },

            series: [{
                name: 'Sent',
                color: 'green',
                data: [sent_emails]
            },
            {
                name: 'Unsubscribe',
                color: 'orange',
                data: [unsubscribe_emails]
            },
            {
                name: 'Error',
                color: 'red',
                data: [error_emails]
            },
            {
                name: 'Total',
                color: 'black',
                data: [total]
            }]
        });
      });
    });
});
