const source = new EventSource('/stream');
source.addEventListener('Song request', function(event) {
  let song = JSON.parse(event.data);
  let requestLabel = document.getElementById('request_label');
  requestLabel.innerHTML = song.name + ' - ' + song.artists.join(', ');
});
