async function sendMessage() {
  const input = document.getElementById('user-msg');
  const text = input.value.trim();
  if (!text) return;
  addMessage('Você', text);
  input.value = '';
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });
  const data = await res.json();
  addMessage('IA', data.response);
  if (data.figure) {
    const fig = JSON.parse(data.figure);
    Plotly.newPlot('chart', fig.data, fig.layout);
  }
}

function addMessage(author, text) {
  const messages = document.getElementById('messages');
  const div = document.createElement('div');
  div.textContent = author + ': ' + text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}
