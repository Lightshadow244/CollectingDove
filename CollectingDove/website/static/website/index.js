var ctx = document.getElementById('myChart').getContext('2d');
var list_label = document.getElementById('list_label').innerHTML
//list_label = JSON.parse("[" + list_label + "]");
list_label = list_label.split(",");

var list_rates = document.getElementById('list_rates').innerHTML;
list_rates = list_rates.split(",")

console.log(list_rates[0]);
//console.log(typeof list_label)
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: list_label,
    datasets: [{
      label: '# of Votes',
      //data: list_rates,
      data: [8300,9000],
      fill: false,
      borderColor: 'rgba(55, 164, 189, 1)',
      borderWidth: 1,
      pointRadius: 0,
      pointHoverRadius:0
    },
    {
      borderColor: 'rgba(0, 50, 255, 1)',
      backgroundColor: 'rgba(0, 50, 255, 1)',
      label: '# of Votes 2',
      data: [8300],
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
