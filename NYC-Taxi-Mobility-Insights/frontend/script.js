const API_BASE = "http://192.168.18.12:5000"; // Flask server

let allTripsData = [];
let tripsData = [];

// --------------------
// Fetch trips data
// --------------------
async function fetchTrips() {
  try {
    const res = await fetch(`${API_BASE}/trips`);
    allTripsData = await res.json();
    // Convert numeric fields to numbers for safety
    allTripsData.forEach(t => {
      t.trip_distance_km = Number(t.trip_distance_km) || 0;
      t.speed_kmph = Number(t.speed_kmph) || 0;
      t.trip_duration = Number(t.trip_duration) || 0;
      t.pickup_hour = Number(t.pickup_hour) || 0;
      t.pickup_dayofweek = Number(t.pickup_dayofweek) || 0;
      t.passenger_count = Number(t.passenger_count) || 0;
    });
    tripsData = [...allTripsData]; // copy for filtering
    updateDashboard();
  } catch (err) {
    console.error("Error fetching trips:", err);
  }
}

// --------------------
// Update Summary Cards
// --------------------
function updateSummary() {
  const totalTrips = tripsData.length;
  const avgDuration = (tripsData.reduce((sum, t) => sum + t.trip_duration, 0) / totalTrips || 0).toFixed(1);

  // Most common passenger count
  const countMap = {};
  tripsData.forEach(t => {
    const c = t.passenger_count;
    countMap[c] = (countMap[c] || 0) + 1;
  });
  const commonPassenger = Object.keys(countMap).reduce((a, b) => countMap[a] > countMap[b] ? a : b, 0);

  document.getElementById("totalTrips").textContent = totalTrips;
  document.getElementById("avgDuration").textContent = `${avgDuration} sec`;
  document.getElementById("commonPassenger").textContent = commonPassenger;
}

// --------------------
// Render Charts
// --------------------
let tripsChart, durationChart;

function updateCharts() {
  const tripsByHour = Array(24).fill(0);
  const tripsMorningRush = Array(24).fill(0);
  const tripsEveningRush = Array(24).fill(0);

  tripsData.forEach(t => {
    const h = t.pickup_hour;
    const d = t.pickup_dayofweek;
    tripsByHour[h]++;
    if (d >= 1 && d <= 5) { // weekdays
      if (h >= 8 && h <= 10) tripsMorningRush[h]++;
      if (h >= 17 && h <= 19) tripsEveningRush[h]++;
    }
  });

  // Trips Over Time
  if (tripsChart) tripsChart.destroy();
  const ctx1 = document.getElementById("tripsChart").getContext("2d");
  tripsChart = new Chart(ctx1, {
    type: "bar",
    data: {
      labels: [...Array(24).keys()].map(h => `${h}:00`),
      datasets: [
        { label: "Total Trips", data: tripsByHour, backgroundColor: "rgba(75,192,192,0.6)" },
        { label: "Morning Rush (8–11 AM)", data: tripsMorningRush, backgroundColor: "rgba(255,206,86,0.6)" },
        { label: "Evening Rush (5–8 PM)", data: tripsEveningRush, backgroundColor: "rgba(255,99,132,0.6)" }
      ]
    },
    options: { responsive: true, plugins: { legend: { position: "top" } }, scales: { y: { title: { display: true, text: "Number of Trips" } } } }
  });

  // Avg Trip Duration by Hour
  const durationByHour = Array(24).fill(0);
  const countByHour = Array(24).fill(0);
  tripsData.forEach(t => {
    durationByHour[t.pickup_hour] += t.trip_duration;
    countByHour[t.pickup_hour]++;
  });
  const avgDurationByHour = durationByHour.map((sum, i) => countByHour[i] ? (sum / countByHour[i]).toFixed(1) : 0);

  if (durationChart) durationChart.destroy();
  const ctx2 = document.getElementById("durationChart").getContext("2d");
  durationChart = new Chart(ctx2, {
    type: "line",
    data: {
      labels: [...Array(24).keys()].map(h => `${h}:00`),
      datasets: [{ label: "Avg Duration (sec)", data: avgDurationByHour, borderColor: "rgba(54,162,235,1)", fill: false, tension: 0.3 }]
    },
    options: { responsive: true, plugins: { legend: { position: "top" } }, scales: { y: { title: { display: true, text: "Duration (sec)" } } } }
  });
}

// --------------------
// Populate Top Trips Table
// --------------------
function updateTopTrips() {
  const sortBy = document.getElementById("sortBy").value;
  const sorted = [...tripsData].sort((a, b) => (b[sortBy] || 0) - (a[sortBy] || 0)).slice(0, 10);

  const tbody = document.getElementById("topTripsBody");
  tbody.innerHTML = "";

  const dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  
  sorted.forEach(t => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.trip_id}</td>
      <td>${t.trip_distance_km.toFixed(2)}</td>
      <td>${t.speed_kmph.toFixed(2)}</td>
      <td>${t.trip_duration}</td>
      <td>${t.pickup_hour}:00</td>
      <td>${dayNames[t.pickup_dayofweek % 7]}</td>
    `;
    tbody.appendChild(tr);
  });
}

// --------------------
// Update all dashboard
// --------------------
function updateDashboard() {
  updateSummary();
  updateCharts();
  updateTopTrips();
}

// --------------------
// Event Listeners
// --------------------
document.getElementById("applyFilters").addEventListener("click", () => {
  const minD = parseFloat(document.getElementById("minDistance").value) || 0;
  const maxD = parseFloat(document.getElementById("maxDistance").value) || Infinity;
  const peak = document.getElementById("peakHours").value;

  tripsData = allTripsData.filter(t => {
    const d = t.trip_distance_km;
    const h = t.pickup_hour;
    const day = t.pickup_dayofweek;
    let pass = d >= minD && d <= maxD;

    if (peak === "morning") pass = pass && day >= 1 && day <= 5 && h >= 8 && h <= 10;
    if (peak === "evening") pass = pass && day >= 1 && day <= 5 && h >= 17 && h <= 19;

    return pass;
  });

  updateDashboard();
});

document.getElementById("resetFilters").addEventListener("click", () => {
  tripsData = [...allTripsData];
  updateDashboard();
});

document.getElementById("sortBy").addEventListener("change", updateTopTrips);

// --------------------
// Initial load
// --------------------
fetchTrips();
