var ctx = document.getElementById('myChart').getContext('2d');
var list_label = document.getElementById('list_label').innerHTML
console.log(list_label)
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        //labels: ['1','2','','4','5','6'],
        labels: ['','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6','','','','','','6'],
        //labels: list_label,
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
        },
        elements: {
          line: {
            tension: 0
          }
        }
    }
});
