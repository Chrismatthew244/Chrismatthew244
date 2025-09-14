import { useEffect, useState } from 'react';
import api from '../api/client.js';

export default function Tasks() {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    api.get('/tasks').then(res => setTasks(res.data)).catch(() => setTasks([]));
  }, []);

  return (
    <div>
      <h2>Tasks</h2>
      <ul>
        {tasks.map(t => (
          <li key={t.id}>{t.title}</li>
        ))}
      </ul>
    </div>
  );
}
