# BoardGameGeek API Setup Guide

## Overview

The BoardGameGeek (BGG) XML API now requires authentication for most API operations. This guide explains how to register for API access and configure your application to use an API token.

## Why is Authentication Required?

As of late 2024/early 2025, BGG introduced mandatory API registration to:
- Monitor and regulate API usage
- Prevent abuse and excessive rate limiting
- Ensure fair access to API resources

Without an API token, you'll receive `401 Unauthorized` errors when trying to sync your BGG collection.

## Registration Process

### Step 1: Create a BGG Application

1. Visit the BGG Applications page: https://boardgamegeek.com/applications
2. Click on "Create New Application" or similar option
3. Fill in the application details:
   - **Application Name**: BoardGamesRecorder (or your preferred name)
   - **Description**: Personal board game tracking application
   - **Purpose**: Personal use for syncing BGG collection
4. Submit your application

**Important**: It may take a week or more for BGG to review and approve your application. Plan accordingly.

### Step 2: Generate API Token

Once your application is approved:

1. Go to https://boardgamegeek.com/applications
2. Find your approved application in the list
3. Click "Tokens" or "Generate Token" next to your application
4. Copy the generated token (it will look like a long string of characters)
5. Store it securely - you'll need it for configuration

## Configuration

### For Docker Deployment (Recommended)

You have two options for setting the API token:

#### Option 1: Environment Variable (Recommended)

1. Set the environment variable before running docker-compose:

```bash
export BGG_API_TOKEN="your-token-here"
docker compose -f docker-compose.rpi.yml up -d
```

2. Or add it to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
echo 'export BGG_API_TOKEN="your-token-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Option 2: Direct in docker-compose.yml

Edit `docker-compose.rpi.yml` and replace the token line:

```yaml
environment:
  # ... other variables
  BGG_API_TOKEN: "your-actual-token-here"
```

**Warning**: This method stores your token in the file. Be careful not to commit it to version control!

### For Local Development

Set the environment variable before running the application:

```bash
export BGG_API_TOKEN="your-token-here"
python backend/main.py
```

## Verifying Setup

After configuration, restart your application and check the logs:

```bash
docker compose -f docker-compose.rpi.yml logs boardgames
```

You should see:
```
INFO:backend.bgg_integration:BGG API token configured for authenticated requests
```

If the token is missing, you'll see:
```
WARNING:backend.bgg_integration:No BGG API token configured. API requests may be rate-limited or fail.
```

## Testing the Sync

1. Open your Board Game Tracker application
2. Go to the "Setup" tab
3. Click "Sync BGG Collection"
4. If successful, you should see your games imported with thumbnails and metadata

## Troubleshooting

### 401 Unauthorized Errors

If you still get 401 errors after setting the token:
- Verify the token is correctly set: `echo $BGG_API_TOKEN`
- Check that you've restarted the application after setting the token
- Ensure there are no extra spaces or quotes in the token
- Verify your BGG application is still approved

### Rate Limiting

The BGG API has rate limits (recommended 5 seconds between requests):
- The application automatically handles rate limiting
- Large collections may take several minutes to sync
- Be patient during the first sync

### Token Expiration

If your token stops working:
- BGG tokens may expire or be revoked
- Generate a new token from https://boardgamegeek.com/applications
- Update your environment variable with the new token

## Security Notes

- Never commit your API token to version control
- Don't share your token publicly
- If your token is compromised, regenerate it immediately
- Use environment variables or secrets management for production deployments

## Additional Resources

- BGG XML API Documentation: https://boardgamegeek.com/wiki/page/BGG_XML_API2
- Using the XML API: https://boardgamegeek.com/using_the_xml_api
- BGG API Guild: https://boardgamegeek.com/guild/1229

## Current Status

As of January 2025, BGG API tokens are **required** for collection endpoints. The transition period has ended, and unauthenticated requests will fail with 401 errors.
