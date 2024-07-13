const $ = (query) => {
  if (query.startsWith('#')) {
    return document.getElementById(query.slice(1));
  }

  const results = document.querySelectorAll(query);
  return Array.from(results);
};

$('#end-year-input').value = new Date().getFullYear().toString();

window.dq = $;
