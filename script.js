const $ = (query) => {
  const results = document.querySelectorAll(query);

  return results.length === 1 ? results[0] : results;
};

$('#end-year-input').value = new Date().getFullYear().toString();
