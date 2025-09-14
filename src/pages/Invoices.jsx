import { useEffect, useState } from 'react';
import api from '../api/client.js';

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    api.get('/invoices').then(res => setInvoices(res.data)).catch(() => setInvoices([]));
  }, []);

  return (
    <div>
      <h2>Invoices</h2>
      <ul>
        {invoices.map(i => (
          <li key={i.id}>{i.number}</li>
        ))}
      </ul>
    </div>
  );
}
