import { useEffect, useState } from 'react';
import api from '../api/client.js';

export default function Customers() {
  const [customers, setCustomers] = useState([]);

  useEffect(() => {
    api.get('/customers').then(res => setCustomers(res.data)).catch(() => setCustomers([]));
  }, []);

  return (
    <div>
      <h2>Customers</h2>
      <ul>
        {customers.map(c => (
          <li key={c.id}>{c.name}</li>
        ))}
      </ul>
    </div>
  );
}
