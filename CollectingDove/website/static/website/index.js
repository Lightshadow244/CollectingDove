var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['1','2','3','4','5','6'],
        datasets: [{
            label: '# of Votes',
            data: [12, 19, 3, 5, 2, 3],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
            ],
            borderWidth: 1,
            pointRadius: 2
        },
        {
          backgroundColor: 'rgba(0, 50, 255, 1)',
          label: '# of Votes 2',
          data: [12, , 3, , 2],
          fill:false,
          pointStyle:"rectRot",
          showLine:false,
          pointRadius: 10
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
});
