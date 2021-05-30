let nowPlaying = null;
let queue = [];

let source = new EventSource('/stream');
source.onmessage = function (event) {
  if (nowPlaying == null) {
    nowPlaying = event.data;
  } else {
    queue.push(event.data);
  }
};
