$(function() {
  document.getElementById('exportToCSV').style.visibility = 'hidden';

  $('a#chartHere').bind('click', function() {
    $.getJSON($SCRIPT_ROOT + '/handleQuery', {
      type: $('input[name="type"]').val(),
      recipientName: $('input[name="recipientName"]').val(),
      recipientEmail: $('input[name="recipientEmail"]').val(),
      creator: $('input[name="creator"]').val(),
      chartType: $('input[name="option"]:checked').val(),
      sortField: $('input[name="sortField"]:checked').val(),
      queryType: $('input[name="queryType"]:checked').val()
    }, function(data) {
      document.getElementById('exportToCSV').style.visibility = 'visible';
      console.log(data);
      var chartType = data['final']['chartType'];
      var queryResult = data['final']['queryResults'];
      var queryType = data['final']['queryType'];

      console.log(queryResult);

      google.charts.load('current', {'packages':['corechart', 'table']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var tableData = new google.visualization.DataTable(results);
        console.log("Results", results);

        console.log(tableData);
        var colTitle1, colTitle2, colTitle3, colTitle4, field, thetype;
        var chartData = new google.visualization.DataTable(results);
        if(queryType){
          if(queryType == 'numEachType'){
            colTitle1 = 'Award Type';
            colTitle2 = 'Count';
            thetype = 'number';
            field = 'awardType';
          }else if(queryType == 'numRcvdPU'){
            colTitle1 = 'Recipient Email';
            colTitle2 = 'Count';
            thetype = 'number';
            field = 'recipientEmail';
          }else if(queryType == 'numGivenPU'){
            colTitle1 = 'Creator Email';
            colTitle2 = 'Count';
            thetype = 'number';
            field = 'creatorEmail';
          }
          chartData.addColumn('string', colTitle1);
          chartData.addColumn('number', colTitle2);
          tableData.addColumn('string', colTitle1);
          tableData.addColumn(thetype, colTitle2);
        }else{
          // show all awards
          console.log("other");
          colTitle1 = 'Recipient Email';
          colTitle2 = 'Creator Email';
          colTitle3 = 'Date'
          colTitle4 = 'Award Type'
          thetype = 'string';
          tableData.addColumn(thetype, colTitle3);
          tableData.addColumn(thetype, colTitle4);
          tableData.addColumn('string', colTitle1);
          tableData.addColumn(thetype, colTitle2);
        }

        for(var i=0;i<queryResult.length;i++){
          if(queryType == 'numRcvdPU' || queryType == 'numGivenPU'){
            chartData.addRow([queryResult[i][field], queryResult[i].numAwards]);
            tableData.addRow([queryResult[i][field], queryResult[i].numAwards]);
          }else if(queryType == 'numEachType'){
            chartData.addRow([queryResult[i]['awardType'], queryResult[i].numAwards]);
            tableData.addRow([queryResult[i]['awardType'], queryResult[i].numAwards]);
          }else{
            console.log("else");
            tableData.addRow([queryResult[i]['recipientEmail'], queryResult[i]['creatorEmail'], queryResult[i]['date'], queryResult[i]['type']]);
          }
        }

        // Set chart options
        var options = {'title':data['final']['title'], 'width':600, 'height':450};

        // Show results in a chart of the user's choice
        if(queryType){
          if(chartType == 'bar')
            var chart = new google.visualization.BarChart(document.getElementById('chart_div'));
          else
            var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
          chart.draw(chartData, options);
        }

        // Show results in a table
        var table = new google.visualization.Table(document.getElementById('table_div'));
        table.draw(tableData, {showRowNumber: true, width: '70%', height: '100%'});
      }

      });
      return false;
    });
});
