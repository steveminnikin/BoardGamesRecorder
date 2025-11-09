# Deploying Board Game Tracker on OpenMediaVault

This guide will walk you through deploying the Board Game Tracker on your Raspberry Pi 5 running OpenMediaVault (OMV) using the Docker Compose plugin.

## Prerequisites

- OpenMediaVault installed on Raspberry Pi 5
- OMV Docker plugin (omv-extras) installed
- Docker Compose plugin for OMV installed
- Basic familiarity with OMV web interface

## Installation Steps

### Step 1: Access OpenMediaVault Web Interface

1. Open your browser and navigate to your OMV instance:
   ```
   http://<your-pi-ip>
   ```
2. Log in with your admin credentials

### Step 2: Create a Shared Folder for the App (Optional but Recommended)

1. Go to **Storage** → **Shared Folders**
2. Click **Add** (+)
3. Configure:
   - **Name**: `boardgames`
   - **Device**: Select your storage device
   - **Path**: Leave as default or customize
   - **Permissions**: Default is fine
4. Click **Save**
5. Click **Apply** (yellow banner at top)

### Step 3: Set Up Docker Compose Stack

#### Option A: Using OMV's Compose Plugin UI

1. Go to **Services** → **Compose** → **Files**
2. Click **Add** (+)
3. Configure:
   - **Name**: `boardgames-tracker`
   - **File**: Leave default or choose a location
4. In the compose file editor, paste this content:

```yaml
version: '3.8'

services:
  boardgames:
    build:
      context: https://github.com/steveminnikin/BoardGamesRecorder.git
      dockerfile: Dockerfile
    container_name: boardgames-tracker
    ports:
      - "8000:8000"
    volumes:
      # Update this path to your OMV shared folder if created
      - /srv/dev-disk-by-uuid-<YOUR-UUID>/boardgames/data:/app/data
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
```

5. **Important**: Update the volume path:
   - If you created a shared folder, use its absolute path (check in OMV under Shared Folders → Path)
   - Or use a simple relative path: `./data:/app/data`

6. Click **Save**

#### Option B: Using Portainer (if installed)

1. Go to **Services** → **Portainer**
2. Navigate to **Stacks**
3. Click **Add Stack**
4. Name: `boardgames-tracker`
5. Paste the docker-compose.yml content
6. Click **Deploy the stack**

### Step 4: Deploy the Stack

1. In **Services** → **Compose** → **Files**
2. Select your `boardgames-tracker` compose file
3. Click the **Up** button (play icon) to start the stack
4. Wait for the build to complete (this may take 5-10 minutes on first run)
5. Check the **State** column - it should show "running"

### Step 5: Verify Deployment

1. In OMV, go to **Services** → **Compose** → **Files**
2. Click on your stack and view logs to ensure no errors
3. Alternatively, check containers in **Services** → **Docker** → **Containers**

### Step 6: Access the Application

1. Open your mobile browser
2. Navigate to:
   ```
   http://<your-pi-ip>:8000
   ```
3. You should see the Board Game Tracker interface

## Configuration

### Changing the Port

If port 8000 is already in use:

1. Edit your compose file in OMV
2. Change the ports line:
   ```yaml
   ports:
     - "3000:8000"  # Use port 3000 instead
   ```
3. Save and redeploy the stack (Down → Up)

### Data Persistence

Your game data is stored in the volume path you specified. To back up your data:

1. Navigate to the data directory in OMV file manager
2. Or use SSH: `cp /path/to/data/boardgames.db /path/to/backup/`

### Using a Specific OMV Shared Folder

If you want to store data in a specific shared folder:

1. Create shared folder in OMV (as shown in Step 2)
2. Note the absolute path (shown in Shared Folders list)
3. Update the volume path in your compose file:
   ```yaml
   volumes:
     - /srv/dev-disk-by-uuid-XXXXX/boardgames/data:/app/data
   ```
4. Redeploy the stack

## Updating the Application

When updates are available on GitHub:

1. Go to **Services** → **Compose** → **Files**
2. Select your `boardgames-tracker` stack
3. Click **Down** to stop the container
4. Click **Pull** to get the latest code
5. Click **Up** to restart with updates

Or use the **Recreate** button which does all steps at once.

## Troubleshooting

### Container Won't Start

1. Check logs in **Services** → **Compose** → **Files** → Select stack → **Logs**
2. Common issues:
   - Port already in use: Change port in compose file
   - Volume permission issues: Ensure OMV user has access to the path
   - Build errors: Check Docker logs

### Can't Access from Mobile

1. Ensure your phone is on the same network as the Pi
2. Check OMV firewall settings if enabled
3. Try accessing `http://<pi-ip>:8000` directly in browser
4. Verify container is running in **Services** → **Docker** → **Containers**

### Database Errors

1. Check volume path permissions
2. Ensure the data directory exists and is writable
3. You can reset by stopping the stack, deleting the data folder, and restarting

### Build Takes Too Long

First build on Raspberry Pi can take 5-10 minutes. This is normal for ARM64 architecture.

## Advanced: Using Pre-built Images (Future)

Once GitHub Actions is set up to build images, you can simplify the compose file to use pre-built images instead of building on your Pi.

## Port Forwarding (Access from Anywhere)

To access your tracker from outside your home network:

1. In your router, forward external port → Pi's port 8000
2. Set up dynamic DNS (DuckDNS, No-IP, etc.)
3. Access via: `http://<your-domain>:<port>`

**Security Note**: Consider adding authentication if exposing to the internet.

## Support

For issues or questions:
- Check GitHub issues: https://github.com/steveminnikin/BoardGamesRecorder/issues
- Review application logs in OMV Compose plugin
- Check Docker container logs

---

Enjoy tracking your board game victories! 🎲
