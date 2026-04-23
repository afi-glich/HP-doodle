import React, { useEffect, useState } from "react";
import { checkHealth, HealthResponse } from "../services/api";

const HomePage: React.FC = () => {
const [health, setHealth] = useState<HealthResponse | null>(null);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
checkHealth()
.then((data) => {
setHealth(data);
setError(null);
})
.catch(() => {
setHealth(null);
setError("Cannot connect to backend API. Is it running?");
});
}, []);

return (
<div className="container">
<h1>🗓️ Doodle Clone</h1>
<p>A collaborative event scheduling playground.</p>

<section>
<h3>System Status</h3>
{error && (
<div className="status-card error">
❌ {error}
</div>
)}
{health && (
<div className="status-card success">
✅ Backend: {health.message}
</div>
)}
{!health && !error && <p>Checking connection...</p>}
</section>

<section>
<h3>Upcoming Work</h3>
<ul>
<li>Create events with time slots</li>
<li>Invite participants with magic links</li>
<li>Collect availability preferences</li>
<li>Suggest the optimal time</li>
</ul>
</section>
</div>
);
};

export default HomePage;
