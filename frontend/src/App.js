import About from './components/about';
import Home from './components/home'
import Navbar from './components/navbar';
import './App.css';
import { Route,Routes } from 'react-router-dom';
function App() {
  return (
    <div>
      <Navbar></Navbar>
      <Routes>
        <Route path='about' element={<About></About>}></Route>
        <Route path='home' element={<Home></Home>}></Route>
        <Route path='*' element={<Home></Home>}></Route>
      </Routes>
  </div>
  );
}

export default App;
