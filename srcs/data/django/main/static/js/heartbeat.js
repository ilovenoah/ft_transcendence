function sendHeartbeat() {
    fetch("https://localhost", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // CSRFトークンを適切に取得
        },
        body: JSON.stringify({ status: 'active' })
    })
    .then(response => {
        if (response.ok) {
            console.log('Heartbeat sent successfully');
        } else {
            console.error('Error sending heartbeat');
        }
    })
    .catch(error => console.error('Error sending heartbeat:', error));
}

// 1分ごと（60000ミリ秒）に心拍を送信
setInterval(sendHeartbeat, 60000);

function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}
