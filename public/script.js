const $ = (query) =>
  query.startsWith('#')
    ? document.getElementById(query.slice(1))
    : Array.from(document.querySelectorAll(query));

$('#end-year-input').value = new Date().getFullYear().toString();

$('#go-button').addEventListener('click', async () => {
  const startYear = parseInt($('#start-year-input').value);
  const endYear = parseInt($('#end-year-input').value);
  const movingAverage = parseInt($('#moving-average-input').value);
  const location = $('#location-input').value;
  const parameter = $('#parameter-select').value;
  const results = await fetch(
    `/data?parameter=${parameter}&location=${location}&start_year=${startYear}&end_year=${endYear}&moving_average=${movingAverage}`
  );
  if (!results.ok) {
    $('#results').style.display = 'none';
    $('#canvas').style.display = 'none';
    $('.error').forEach((el) => (el.style.display = 'block'));
    return;
  }
  const data = await results.json();

  $('#results').style.display = 'block';
  $('#canvas').style.display = 'block';
  $('.error').forEach((el) => (el.style.display = 'none'));
  $('#r-squared').textContent = Math.round(data.r_squared * 100);
  $('#change').textContent = Math.abs(data.slope.toFixed(4));
  $('#significance').textContent =
    (data.p_value < 0.05
      ? 'statistically significant'
      : 'not statistically significant') +
    ` at \u03B1 = 0.05 (P = ${data.p_value.toFixed(4)})`;
  $('.parameter').forEach(
    (el) =>
      (el.textContent =
        data.parameter_name.toLowerCase() +
        (movingAverage > 1 ? ` (${movingAverage}-year moving average)` : ''))
  );
  $('.direction').forEach(
    (el) =>
      (el.textContent =
        data.slope > 0
          ? 'increasing'
          : data.slope < 0
          ? 'decreasing'
          : 'stable')
  );
  $('.location').forEach((el) => (el.textContent = data.location));
  $('.units').forEach((el) => (el.textContent = data.units));

  const dataTrace = {
    x: data.xvals,
    y: data.yvals,
    type: 'line',
    name: data.parameter_name
  };

  const extendedX = data.xvals.concat(
    new Array(20)
      .fill(0)
      .map((_x, i) => data.xvals[data.xvals.length - 1] + i + 1)
  );

  const regTrace = {
    x: extendedX,
    y: extendedX.map((x) => x * data.slope + data.intercept),
    type: 'scatter',
    name: 'Regression Line'
  };

  const graphData = [dataTrace, regTrace];

  Plotly.newPlot('canvas', graphData, {
    title: `${data.parameter_name} in ${data.location} from ${startYear} to ${endYear}`,
    xaxis: { title: 'Year' },
    yaxis: { title: `${data.parameter_name} (${data.units})` }
  });
});
