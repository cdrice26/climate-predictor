const $ = (query) => {
  const results = document.querySelectorAll(query);

  return results.length === 1 ? results[0] : results;
};

const updateOutput = () => {
  Array.from($('.parameter')).forEach(
    (el) =>
      (el.textContent = getParameterName(
        $('#parameter-select').value
      ).toLowerCase())
  );
  Array.from($('.location')).forEach(
    (el) => (el.textContent = $('#location-input').value)
  );
};

const getParameterName = (parameter) => {
  switch (parameter) {
    case 'temperature_2m_max':
      return 'High Temperature';
    case 'temperature_2m_min':
      return 'Low Temperature';
    case 'apparent_temperature_max':
      return 'Max Heat Index';
    case 'apparent_temperature_min':
      return 'Min Heat Index';
    case 'precipitation_sum':
      return 'Precipitation';
    case 'rain_sum':
      return 'Rainfall';
    case 'snowfall_sum':
      return 'Snowfall';
    default:
      return 'Wind Speed';
  }
};

$('#end-year-input').value = new Date().getFullYear().toString();

$('#parameter-select').addEventListener('change', updateOutput);
$('#location-input').addEventListener('input', updateOutput);

updateOutput();

window.get_parameter_name = getParameterName;
