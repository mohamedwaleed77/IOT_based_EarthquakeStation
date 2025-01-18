import React from 'react'
import { NavLink} from 'react-router-dom'

export default function Navbar() {

  return (
    <div className='bg-gray-800 text-white text-2xl flex justify-between items-center h-10 border-b border-black overflow-hidden navbar'>
        <NavLink to="/home" className=' px-16 h-10 flex items-center hover:bg-sky-900 hover:text-white'>Earthquake Stations</NavLink>
        <div className='flex justify-around items-center '>
            <NavLink className='px-16 h-10 flex items-center hover:bg-sky-900 hover:text-white' to='/about'>About</NavLink>
            
        </div>
    </div>
  )
}
