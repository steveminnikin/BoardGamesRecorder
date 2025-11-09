# Board Game Tracker

A simple web application to track board game matches, record outcomes, and view statistics about win rates. Built specifically for running on Raspberry Pi 5 with a mobile-first design.

## Features

- **Record Matches**: Log which game was played, when it was played, and who won
- **Match History**: View all past matches with dates and winners
- **Statistics**: See win rates and probability predictions for each player per game
- **Mobile-First Design**: Optimized interface for phones and tablets
- **Docker-Ready**: Easy deployment on Raspberry Pi 5 using Docker

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite
- **Frontend**: Vue.js 3 with vanilla CSS
- **Deployment**: Docker & Docker Compose

## Prerequisites

- Raspberry Pi 5 (or any ARM64/x86_64 system)
- Docker and Docker Compose installed
- Network access to the Raspberry Pi

## Installation

### 🎯 For OpenMediaVault Users

**If you're running OpenMediaVault on your Raspberry Pi 5**, use the simplified deployment process:

📖 **See [OPENMEDIAVAULT_DEPLOYMENT.md](OPENMEDIAVAULT_DEPLOYMENT.md) for detailed OMV-specific instructions**

**Quick Start:**
1. Access OMV web interface
2. Go to Services → Compose → Files
3. Create new compose file with the GitHub repository URL
4. Deploy and access at `http://<your-pi-ip>:8000`

---

### Standard Docker Installation

### 1. Clone the project to your Raspberry Pi

```bash
git clone https://github.com/steveminnikin/BoardGamesRecorder.git
cd BoardGamesRecorder
```

### 2. Build and start the application

```bash
docker-compose up -d
```

This will:
- Build the Docker image for ARM64 architecture
- Start the container
- Expose the app on port 8000
- Create a persistent data volume for the SQLite database

### 3. Access the application

Open your mobile browser and navigate to:
```
http://<raspberry-pi-ip>:8000
```

For example: `http://192.168.1.100:8000`

## Usage

### Initial Setup

1. Navigate to the **Setup** tab
2. Add two players (e.g., your name and your wife's name)
3. Add your board games (e.g., "Catan", "Ticket to Ride", "Pandemic")

### Recording a Match

1. Go to the **Record Match** tab
2. Select the game you played
3. Select who won
4. Choose the date/time (defaults to now)
5. Click **Record Match**

### Viewing History

1. Navigate to the **History** tab
2. See all past matches ordered by most recent first
3. Each entry shows the game name, winner, and date played

### Viewing Statistics

1. Go to the **Statistics** tab
2. See win rates for each player across all games
3. View total matches played per game
4. See win percentage predictions for future games

## Docker Commands

### View logs
```bash
docker-compose logs -f
```

### Stop the application
```bash
docker-compose down
```

### Restart the application
```bash
docker-compose restart
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Remove everything (including data)
```bash
docker-compose down -v
```

## Data Persistence

The SQLite database is stored in the `./data` directory on your host machine, which is mounted to the container. This means your data persists even if you stop or remove the container.

To backup your data:
```bash
cp data/boardgames.db data/boardgames.db.backup
```

## API Documentation

FastAPI provides automatic API documentation:
- Swagger UI: `http://<raspberry-pi-ip>:8000/docs`
- ReDoc: `http://<raspberry-pi-ip>:8000/redoc`

## Customization

### Changing the Port

Edit `docker-compose.yml` and change the port mapping:
```yaml
ports:
  - "3000:8000"  # Access on port 3000 instead of 8000
```

### Adding More Players

The app currently supports 2 players but can be extended. Modify the database models in `backend/models.py` and update the frontend forms to support multiple player selection.

## Troubleshooting

### Container won't start
```bash
docker-compose logs
```

### Can't access from mobile device
- Ensure your mobile device is on the same network as the Raspberry Pi
- Check if port 8000 is open in your Pi's firewall
- Try accessing `http://<pi-ip>:8000` in your browser

### Database errors
```bash
# Reset the database
rm -rf data/
docker-compose restart
```

### Build fails on Raspberry Pi
Ensure you have enough disk space and memory. The Pi 5 should handle this easily, but older models may struggle.

## Development

### Running locally without Docker

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
Open `frontend/index.html` in a browser, or use a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
```

## Project Structure

```
BoardGamesRecorder/
├── backend/
│   ├── main.py           # FastAPI app and routes
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic schemas
│   ├── crud.py           # Database operations
│   ├── database.py       # Database configuration
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Main HTML file
│   ├── app.js            # Vue.js application
│   └── styles.css        # Mobile-first CSS
├── data/                 # SQLite database (created on first run)
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose configuration
└── README.md             # This file
```

## License

Free to use and modify for personal use.

## Contributing

Feel free to fork and customize for your own needs!

---

Built with FastAPI, Vue.js, and SQLite. Optimized for Raspberry Pi 5.
