import React from 'react'
 
 
export default function About() {
  return (
    <div className='flex flex-col text-white m10 items-center justify-center bg-sky-900 h-[calc(100vh-40px)]'>
      <h1 className='text-5xl'>Abstract</h1>
      <p className='m-10 text-2xl'>
This project presents a cost-effective IoT-based Earthquake Station designed to detect seismic activity using an accelerometer and Wi-Fi for real-time data transmission. The system measures ground motion and operates only during seismic events,
ensuring optimal energy efficiency, an essential feature for remote or off-grid locations. The system is only activated when needed. The project emphasizes reliable
earthquake detection, efficient communication, and energy-saving techniques, adhering to a streamlined design approach. To address potential challenges, the agile development methodology is adopted, enabling flexibility and continuous refinement
throughout the project lifecycle.</p>
  </div>
  )
}
