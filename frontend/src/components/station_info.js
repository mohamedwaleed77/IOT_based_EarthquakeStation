import React, { useEffect, useState } from "react";
import History from "./history";

export default function Station_info(props) {
  let id = props.station_id;
  let location=props.location;
  let coordinates=props.coordinates
  let [arrow, arrow_setter] = useState(
    <div className="rounded-full ml-2 bg-black h-4 w-4"></div>
  );
  let [iscollapsed, iscollapsed_setter] = useState(false);
  let [stationinfo, setstationinfo] = useState([]);
  let [history, setHistory] = useState([]);
  let [loading, setLoading] = useState(true); // For station info
  let [loadingHistory, setLoadingHistory] = useState(true); // For history

  // Function to fetch history data using REST remains unchanged
  const fetchHistoryData = async () => {
    console.log(coordinates)
    try {
      const response = await fetch(`http://localhost:3001/history/${id}`);
      const result = await response.json();
      setHistory(result.data);
      setLoadingHistory(false);
    } catch (error) {
      console.error("Error fetching history data:", error);
      setLoadingHistory(false);
    }
  };

  // Client-side WebSocket connection for real-time station data
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:3001");

    ws.onopen = () => {
      console.log("WebSocket connected for station info");
      ws.send(JSON.stringify({ type: "getStationLastRead", station_id: id }));
    };

    ws.onmessage = (event) => {
     
      try {
        const data = JSON.parse(event.data);
        if (data.type === "stationLastRead" && data.data.station_id === id) {
          setstationinfo([data.data]); 
          setLoading(false);
 
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
        setLoading(false);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket connection closed for station info");
    };
 
  }, [id]);

  // Keep REST polling for history data every 5 seconds
  useEffect(() => {
    fetchHistoryData(); // Initial fetch for history data

    const interval = setInterval(() => {
      fetchHistoryData();
    }, 5000);

    return () => clearInterval(interval);
  }, [id]);

  useEffect(() => {
    iscollapsed_setter(false);
    arrow_setter(
      <div className="rounded-full ml-2 block bg-black h-4 w-4"></div>
    );
  }, [props.colapse]);

  function toggle_collapse() {
    iscollapsed_setter(!iscollapsed);
    arrow_setter(
      <div
        className={`rounded-full ml-2 block h-4 w-4 ${
          iscollapsed ? "bg-black" : "bg-sky-900"
        }`}
      ></div>
    );
  }

  return (
    <div className="flex flex-col justify-center items-center border border-black">
      <button
        className="flex w-full bg-gray-300 h-full items-center gap-2 text-lg hover:bg-gray-500"
        onClick={toggle_collapse}
      >
        {arrow} Station ({id})
      </button>

      <div
        className="bg-gray-600 text-white px-10 w-full overflow-hidden"
        style={{
          maxHeight: !iscollapsed ? "0" : "500px",
          transition: "max-height 0.15s ease-in-out",
        }}
      >
        <table className="w-full">
          <thead className="text-center">
            <tr>
              <th>Location</th>
              <th>Acceleration</th>
              <th>Velocity</th>
              <th>Displacement</th>
              <th>Richter's Magnitude</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody className="text-center">
            {loading ? (
              <tr>
                <td colSpan="6">No movement detected</td>
              </tr>
            ) : stationinfo.length > 0 ? (
              <tr>
                <td>{location}</td>
                <td>{stationinfo[0]?.acceleration}</td>
                <td>{stationinfo[0]?.velocity}</td>
                <td>{stationinfo[0]?.displacement}</td>
                <td>{stationinfo[0]?.richter}</td>
                <td>{stationinfo[0]?.date}</td>
              </tr>
            ) : (
              <tr>
                <td colSpan="6">No Data Available</td>
              </tr>
            )}
          </tbody>
        </table>

        <div>
          <p className="bg-gray-300 text-black text-center">History</p>
          <History info={history} />
        </div>
          <div className="mt-2 p-2">
        <iframe
          title={`map-${id}`}
          width="100%"
          height="250"
          style={{ border: 0 }}
          loading="lazy"
          allowFullScreen
          referrerPolicy="no-referrer-when-downgrade"
          src={`https://www.google.com/maps?q=${coordinates}&z=14&output=embed`}
        />
      </div>
      </div>
    </div>
  );
}
