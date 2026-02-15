import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import TraderAdmin from './pages/TraderAdmin-simple';

function App() {
  return (
    <div>
      <h1 style={{color: 'red', fontSize: '48px', padding: '20px'}}>FRONTEND IS ALIVE - MINIMAL VERSION</h1>
      <Router>
        <Routes>
          <Route path="/" element={<TraderAdmin />} />
          <Route path="/admin" element={<TraderAdmin />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
