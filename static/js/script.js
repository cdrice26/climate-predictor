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
  const data = await results.json();
  console.log(data);
  $('#results').style.display = 'block';
  $('#r-squared').textContent = Math.round(data.r_squared * 100);
  $('#change').textContent = Math.abs(data.slope.toFixed(4));
  $('#significance').textContent =
    (data.p_value < 0.05
      ? 'statistically significant'
      : 'not statistically significant') + ` (P = ${data.p_value.toFixed(4)})`;
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
});
