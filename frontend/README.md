# AgriTech Frontend

Modern Next.js frontend for the SIH26210 agriculture intelligence backend.

## Run
```bash
cp .env.local.example .env.local
npm install
npm run dev
```

Frontend: http://localhost:3000  
Backend: http://localhost:8000

The frontend leaves the existing `server/` module untouched and communicates only through:
- `POST /generate-report`
- `GET /sensor-data/{device_id}`

## Important image requirement
The current backend accepts image **URLs**, not browser file uploads. The dashboard therefore provides URL fields. Use a publicly reachable image URL when running report generation.

## Report history
Generated reports are saved to browser localStorage. They are not uploaded to a database and stay within the current browser profile.

## PDF
Report pages can be downloaded directly as PDF from the report screen.
