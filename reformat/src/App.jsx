import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import IndexPage from './pages/IndexPage';
import SignInPage from './pages/SignInPage';
import SignUpPage from './pages/SignUpPage';
import DownloadPage from './pages/DownloadPage';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="content">
          <Routes>
            <Route path="/" element={<IndexPage />} />
            <Route path="/signin" element={<SignInPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/download/:id" element={<DownloadPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;