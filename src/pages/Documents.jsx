import { useEffect, useState } from 'react';
import api from '../api/client.js';

export default function Documents() {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    api.get('/documents').then(res => setDocuments(res.data)).catch(() => setDocuments([]));
  }, []);

  return (
    <div>
      <h2>Documents</h2>
      <ul>
        {documents.map(d => (
          <li key={d.id}>{d.title}</li>
        ))}
      </ul>
    </div>
  );
}
