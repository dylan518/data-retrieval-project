import React, { useEffect, useState } from 'react';
import axios from 'axios';
import '../style.scss';

function App() {
  const [chatHistory, setChatHistory] = useState([]);
  const fetchChatHistory = () => {
    axios.get('http://127.0.0.1:5000/get_chat')
      .then((response) => {
        setChatHistory(response.data.chat_history);
      })
      .catch((error) => {
        console.error('Error fetching chat history:', error);
      });
  };
  useEffect(() => {
    fetchChatHistory();
  }, []);

  const displayMessage = (role, content) => {
    setChatHistory((prevChat) => [
      ...prevChat,
      { id: Date.now(), role, content }, // Using Date.now() as a unique key
    ]);
  };

  const sendQuery = () => {
    const query = document.getElementById('query-input').value.trim();
    if (query !== '') {
      axios.post('http://127.0.0.1:5000/query', { query })
        .then((response) => {
          displayMessage('user', query);
          displayMessage('assistant', response.data.response);
          document.getElementById('query-input').value = '';
        })
        .catch((error) => {
          console.error('Error sending query:', error);
        });
    }
  };

  const clearChat = () => {
    axios.post('http://127.0.0.1:5000/clear_chat')
      .then(() => {
        setChatHistory([]);
      })
      .catch((error) => {
        console.error('Error clearing chat:', error);
      });
  };

  const uploadFile = () => {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    axios.post('http://127.0.0.1:5000/upload', formData)
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error('Error uploading file:', error);
      });
  };

  return (
    <div className="container">
      <h1>Disney Corporation Information Retrieval System</h1>
      <div id="chat-container">
        <h4>Chat History</h4>
        <div id="chat-history">
          {chatHistory && chatHistory.map((message) => (
            <div key={message.id} className={message.role === 'user' ? 'user-message' : 'assistant-message'}>
              <strong>{message.role}:</strong> {message.content}
            </div>
          ))}
        </div>
      </div>
      <div>
        <input type="text" id="query-input" placeholder="Enter your question" className="form-control" />
        <button type="button" onClick={sendQuery} className="btn btn-primary">Send</button>
        <button type="button" onClick={clearChat} className="btn btn-secondary">Clear Chat</button>
      </div>
      <div className="mt-4">
        <h4>Upload PDF</h4>
        <div className="input-group">
          <input type="file" id="file-input" accept=".pdf" className="form-control" />
          <button type="button" onClick={uploadFile} className="btn btn-primary">Upload</button>
        </div>
      </div>
    </div>
  );
}

export default App;
