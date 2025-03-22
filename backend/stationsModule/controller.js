import { connect } from "../database/database.js";
import moment from "moment";  
import { WebSocketServer } from 'ws';


const connection = connect;
export const getAllStations = (req,res)=>{
    connection.execute(`SELECT * FROM station_table`,(err,data)=>{
        return res.status(200).json({data})
    })
}
 

function getCurrentDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

export const addEvent = async (ws, wsServer, message) => {
    try {
        const data = JSON.parse(message);
        const { station_id, acceleration, velocity, displacement, richter } = data;
        const date = getCurrentDateTime();

        // Insert the new event into the database using safe values
        await connection.execute(
            `INSERT INTO events (station_id, acceleration, velocity, displacement, richter, date) VALUES (?, ?, ?, ?, ?, ?)`,
            [station_id, acceleration, velocity, displacement, richter, date]
        );
 

        // Format the data for broadcasting
        const formattedData = {
            station_id,
            acceleration: parseFloat(acceleration).toFixed(8),
            velocity: parseFloat(velocity).toFixed(8),
            displacement: parseFloat(displacement).toFixed(8),
            richter: parseFloat(richter).toFixed(8),
            date: moment.utc(date).utcOffset(2).format("hh:mm:ss A"),
        };

        // Broadcast directly to all WebSocket clients
        wsServer.clients.forEach(client => {
            if (client.readyState === 1) { // 1 means WebSocket.OPEN
                client.send(JSON.stringify({ type: "stationLastRead", data: formattedData }));
            }
        });
 

    } catch (error) {

    }
};

export const getStationHistory = (req, res) => {
    const { id } = req.params;

    const lastReadQuery = `
        SELECT acceleration, velocity, displacement, richter, date
        FROM events
        WHERE station_id = ?
        ORDER BY date DESC
        LIMIT 1;
    `;

    const maxRichterQuery = `
SELECT 
  acceleration, 
  velocity, 
  displacement, 
  richter, 
  date
FROM (
  SELECT 
    e.*,
    @row_number := IF(
      @current_date = DATE(date), 
      @row_number + 1, 
      1
    ) AS rn,
    @current_date := DATE(date) AS event_date
  FROM 
    events e,
    (SELECT @row_number := 0, @current_date := NULL) AS vars
  WHERE 
    e.station_id = ?
    AND e.richter = (
      SELECT MAX(richter)
      FROM events
      WHERE station_id = e.station_id
        AND DATE(date) = DATE(e.date)
    )
  ORDER BY 
    DATE(date) DESC,  -- Group by date
    richter DESC,      -- Prioritize max Richter
    date DESC          -- Break ties with latest timestamp
) AS ranked
WHERE rn = 1  -- Keep only the first row per day
ORDER BY date DESC;
    `;

    connection.execute(lastReadQuery, [id], (err1, lastReadData) => {
        if (err1) return res.status(500).json({ error: "Failed to fetch last read." });

        connection.execute(maxRichterQuery, [id], (err2, richterData) => {
            if (err2) return res.status(500).json({ error: "Failed to fetch station history." });

            const formattedLastRead = lastReadData[0]
                ? {
                      ...lastReadData[0],
                      acceleration: parseFloat(lastReadData[0].acceleration).toFixed(8),
                      velocity: parseFloat(lastReadData[0].velocity).toFixed(8),
                      displacement: parseFloat(lastReadData[0].displacement).toFixed(8),
                      richter: parseFloat(lastReadData[0].richter).toFixed(8),
                      date: lastReadData[0].date, // Preserving full date and time
                  }
                : null;

            const formattedRichterData = richterData.map((row) => ({
                ...row,
                acceleration: row.acceleration ? parseFloat(row.acceleration).toFixed(8) : row.acceleration,
                velocity: row.velocity ? parseFloat(row.velocity).toFixed(8) : row.velocity,
                displacement: row.displacement ? parseFloat(row.displacement).toFixed(8) : row.displacement,
                richter: row.richter ? parseFloat(row.richter).toFixed(8) : row.richter,
                date: row.date, // Preserving full date and time
            }));

            const combinedData = formattedLastRead
                ? [formattedLastRead, ...formattedRichterData]
                : [...formattedRichterData];

            // Save all the data (including last read) to the database
            connection.execute(`DELETE FROM events WHERE station_id = ?`, [id]);

            const insertQuery = `
                INSERT INTO events (station_id, acceleration, velocity, displacement, richter, date)
                VALUES (?, ?, ?, ?, ?, ?)
            `;

            for (const row of combinedData) {
                connection.execute(insertQuery, [
                    id,
                    row.acceleration,
                    row.velocity,
                    row.displacement,
                    row.richter,
                    row.date,
                ]);
            }

            // Exclude the last read entry from the response
            const responseData = formattedRichterData; // Remove formattedLastRead from the response

            // Send the response
            return res.status(200).json({ data: responseData });
        });
    });
};