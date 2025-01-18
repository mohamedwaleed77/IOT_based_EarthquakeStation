import React from 'react'
 
 
export default function About() {
  return (
    <div className='flex flex-col text-white m10 items-center justify-center bg-sky-900 h-[calc(100vh-40px)]'>
      <h1 className='text-5xl'>Abstract</h1>
      <p className='m-10 text-2xl'>Abstract
This project aims to develop a low-cost IoT-based Earthquake Station that detects
and predicts seismic activity using an accelerometer and Wi-Fi for real-time data transmission. By measuring ground motion and activating the system only during seismic events, the station enhances energy efficiency, crucial for remote or off-grid applications. A mechanical vibration switch and transistor ensure minimal power consumption, allowing the system to operate only when necessary. The project focuses
on reliable earthquake detection, effective communication, and power-saving strategies, following a minimalist design philosophy. Given potential challenges, the Agile
development methodology is used to allow flexibility and continuous improvement
throughout the project</p>
  </div>
  )
}
