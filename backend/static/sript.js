function sendQuery() {
    const query = document.getElementById('query-input').value;
    if (query.trim() !== '') {
        fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
            .then(response => response.json())
            .then(data => {
                displayMessage('user', query);
                displayMessage('assistant', data.response);
                document.getElementById('query-input').value = '';
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

function clearChat() {
    fetch('/clear_chat', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById('chat-history').innerHTML = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fileInput.value = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function displayMessage(role, content) {
    const chatHistory = document.getElementById('chat-history');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${role}:</strong> ${content}`;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Fetch chat history on page load
fetch('/get_chat')
    .then(response => response.json())
    .then(data => {
        data.chat_history.forEach(message => {
            displayMessage(message.role, message.content);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
document.getElementById('send-query-btn').addEventListener('click', sendQuery);
document.getElementById('clear-chat-btn').addEventListener('click', clearChat);
document.getElementById('upload-file-btn').addEventListener('click', uploadFile);