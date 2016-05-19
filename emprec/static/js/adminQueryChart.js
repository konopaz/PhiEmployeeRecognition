$(function() {
  $('a#chartHere').bind('click', function() {
    $.getJSON($SCRIPT_ROOT + '/handleQuery', {
      type: $('input[name="type"]').val(),
      recipientName: $('input[name="recipientName"]').val(),
      recipientEmail: $('input[name="recipientEmail"]').val(),
      creator: $('input[name="creator"]').val(),
      date: $('input[name="date"]').val(),
      chartType: $('input[name="option"]:checked').val(),
      sortField: $('input[name="sortField"]:checked').val()
    }, function(data) {
      console.log(data);
      var chartType = data['final']['chartType'];
      var results = data['final']['query'];
      var users = data.final.users;
      console.log(results);
      console.log(users);

      google.charts.load('current', {'packages':['corechart', 'table']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.charts.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and draws it.
      function drawChart() {

        var tableData = new google.visualization.DataTable(results);
        console.log("Results", results);
        tableData.addColumn('string', 'Recipient Name');
        tableData.addColumn('string', 'Recipient Email');
        tableData.addColumn('string', 'Award Type');
        tableData.addColumn('date', 'Date');

        for(var j=0; j<users.length; j++){
          users[j].numAwards = 0;
        }

        for(var i=0;i<results.length; i++){
            var t = results[i].date.split(/[- :]/);
            var d = new Date(t[0], t[1]-1, t[2], t[3], t[4], t[5]);
            tableData.addRow([results[i].recipientName, results[i].recipientEmail, results[i].type, d] );
        }

        console.log(users);
        var chartData = new google.visualization.DataTable(results);
        chartData.addColumn('string', 'Recipient Name');
        chartData.addColumn('number', 'Number of Awards');

        for(var i=0;i<results.length; i++){
          for(j=0;j<users.length;j++){
            if(users[j].username == results[i].recipientEmail)
              users[j].numAwards++;
          }
        }
        for(i=0;i<users.length;i++){
          chartData.addRow([users[i].username, users[i].numAwards]);
        }

        // Set chart options
        var options = {'title':'Number of Awards Per Person',
                       'width':600,
                       'height':450};

        // Show results in a chart of the user's choice
        if(chartType == 'bar')
          var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
        else
          var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
        chart.draw(chartData, options);

        // Show results in a table
        var table = new google.visualization.Table(document.getElementById('table_div'));
        table.draw(tableData, {showRowNumber: true, width: '70%', height: '100%'});
      }

      });
      return false;
    });
});
