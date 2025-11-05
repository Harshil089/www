import Dashboard from './components/Dashboard.jsx';

function App() {
  try {
    return <Dashboard />;
  } catch (error) {
    console.error('Error in App component:', error);
    return (
      <div style={{ padding: '20px', color: '#4ade80', fontFamily: 'monospace' }}>
        <h1>Error Loading Dashboard</h1>
        <pre>{error.message}</pre>
      </div>
    );
  }
}

export default App;