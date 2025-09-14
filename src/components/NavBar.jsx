import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext.jsx';

export default function NavBar() {
  const { token, logout } = useAuth();
  if (!token) return null;
  return (
    <nav>
      <Link to="/">Dashboard</Link> |
      <Link to="/customers">Customers</Link> |
      <Link to="/tasks">Tasks</Link> |
      <Link to="/invoices">Invoices</Link> |
      <Link to="/documents">Documents</Link> |
      <button onClick={logout}>Logout</button>
    </nav>
  );
}
