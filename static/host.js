const source = new EventSource('/stream');
source.addEventListener('Song request', function(event) {
  let requestLabel = document.getElementById('request_label');
  requestLabel.innerHTML = event.data;
});
