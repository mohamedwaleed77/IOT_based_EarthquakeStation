import React, { useState } from "react";

export default function Introduction() {
  const [colapse, set_colapse] = useState(false);

  function handle_colapse() {
    set_colapse(!colapse);
  }

  return (
    <div className="flex justify-center w-full">
      <button
        onClick={handle_colapse}
        className="text-center italic m-2 p-2 w-full bg-gradient-to-l from-gray-800 via-blue-500 to-gray-800 text-white text-sm font-mono border border-black flex flex-col items-center"
      >
        <h2 className="font-bold not-italic">Welcome to the Earthquake Station Dashboard</h2>
        {colapse && (
          <div>
            <p>
              This platform provides real-time data from our IoT-based earthquake detection system. Our station continuously monitors seismic activity, detecting even the smallest vibrations. The data is displayed live, helping you stay informed about any significant events in the area.
            </p>
            <p>
              Below, you’ll find key insights including earthquake magnitude, displacement readings, and real-time alerts. You can also explore historical data and adjust station settings to tailor the monitoring to your needs.
            </p>
            <br />
            <h1>Know more about earthquakes:</h1>
            <iframe
              className="w-full h-64"
              src="https://www.youtube.com/embed/vEgLjgnv_3c"
            ></iframe>
          </div>
        )}
      </button>
    </div>
  );
}
