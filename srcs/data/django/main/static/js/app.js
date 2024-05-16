// myapp/static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
  function loadContent(url) {
      fetch(url)
          .then(response => response.text())
          .then(html => {
              document.getElementById('app').innerHTML = html;
              document.title = document.querySelector('#app h1').innerText; // Update the document title
          })
          .catch(error => console.error('Error loading content:', error));
  }

  document.addEventListener('click', function(event) {
      if (event.target.tagName === 'A' && event.target.dataset.spa === 'true') {
          event.preventDefault();
          loadContent(event.target.dataset.url);
      }
  });

  window.addEventListener('popstate', function(event) {
      if (event.state && event.state.url) {
          loadContent(event.state.url);
      }
  });

  // Initialize the content without changing the URL
  loadContent(window.location.pathname);
});
