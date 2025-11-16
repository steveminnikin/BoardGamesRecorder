const { createApp } = Vue;

const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api'
    : '/api';

createApp({
    data() {
        return {
            currentTab: 'record',
            players: [],
            games: [],
            matches: [],
            stats: [],
            newPlayer: '',
            newGame: '',
            newMatch: {
                gameId: '',
                winnerId: '',
                datePlayed: this.getCurrentDateTime()
            },
            message: '',
            messageType: '',
            isSyncing: false,
            syncResult: null
        };
    },
    mounted() {
        this.loadData();
    },
    methods: {
        async loadData() {
            await this.loadPlayers();
            await this.loadGames();
            await this.loadMatches();
            await this.loadStats();
        },
        async loadPlayers() {
            try {
                const response = await fetch(`${API_URL}/players`);
                this.players = await response.json();
            } catch (error) {
                console.error('Error loading players:', error);
            }
        },
        async loadGames() {
            try {
                const response = await fetch(`${API_URL}/games`);
                this.games = await response.json();
            } catch (error) {
                console.error('Error loading games:', error);
            }
        },
        async loadMatches() {
            try {
                const response = await fetch(`${API_URL}/matches`);
                this.matches = await response.json();
            } catch (error) {
                console.error('Error loading matches:', error);
            }
        },
        async loadStats() {
            try {
                const response = await fetch(`${API_URL}/stats`);
                this.stats = await response.json();
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        },
        async addPlayer() {
            try {
                const response = await fetch(`${API_URL}/players`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: this.newPlayer })
                });

                if (response.ok) {
                    this.newPlayer = '';
                    await this.loadPlayers();
                    this.showMessage('Player added successfully!', 'success');
                } else {
                    this.showMessage('Error adding player', 'error');
                }
            } catch (error) {
                console.error('Error adding player:', error);
                this.showMessage('Error adding player', 'error');
            }
        },
        async addGame() {
            try {
                const response = await fetch(`${API_URL}/games`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: this.newGame })
                });

                if (response.ok) {
                    this.newGame = '';
                    await this.loadGames();
                    this.showMessage('Game added successfully!', 'success');
                } else {
                    this.showMessage('Error adding game', 'error');
                }
            } catch (error) {
                console.error('Error adding game:', error);
                this.showMessage('Error adding game', 'error');
            }
        },
        async syncBGGGames() {
            if (this.isSyncing) {
                return; // Prevent multiple simultaneous syncs
            }

            this.isSyncing = true;
            this.syncResult = null;
            this.showMessage('Syncing BoardGameGeek collection... This may take a few minutes.', 'info');

            try {
                const response = await fetch(`${API_URL}/games/sync-bgg`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                const result = await response.json();

                if (response.ok) {
                    this.syncResult = result;
                    await this.loadGames();
                    await this.loadStats();
                    this.showMessage(
                        `Successfully synced! ${result.games_added} added, ${result.games_updated} updated.`,
                        'success'
                    );
                } else {
                    this.showMessage('Error syncing BoardGameGeek collection', 'error');
                    console.error('Sync error:', result);
                }
            } catch (error) {
                console.error('Error syncing BGG:', error);
                this.showMessage('Error syncing BoardGameGeek collection', 'error');
            } finally {
                this.isSyncing = false;
            }
        },
        async recordMatch() {
            try {
                const matchData = {
                    game_id: parseInt(this.newMatch.gameId),
                    winner_id: parseInt(this.newMatch.winnerId),
                    date_played: new Date(this.newMatch.datePlayed).toISOString()
                };

                const response = await fetch(`${API_URL}/matches`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(matchData)
                });

                if (response.ok) {
                    this.newMatch = {
                        gameId: '',
                        winnerId: '',
                        datePlayed: this.getCurrentDateTime()
                    };
                    await this.loadMatches();
                    await this.loadStats();
                    this.showMessage('Match recorded successfully!', 'success');
                } else {
                    this.showMessage('Error recording match', 'error');
                }
            } catch (error) {
                console.error('Error recording match:', error);
                this.showMessage('Error recording match', 'error');
            }
        },
        getCurrentDateTime() {
            const now = new Date();
            now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
            return now.toISOString().slice(0, 16);
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        formatDateUK(dateString) {
            const date = new Date(dateString);
            const day = String(date.getDate()).padStart(2, '0');
            const month = date.toLocaleString('en-GB', { month: 'short' });
            const year = String(date.getFullYear()).slice(-2);
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${day} ${month} ${year} ${hours}:${minutes}`;
        },
        getWinRateColor(winRate) {
            if (winRate >= 60) return 'color: #22c55e';
            if (winRate >= 40) return 'color: #eab308';
            return 'color: #ef4444';
        },
        showMessage(msg, type) {
            this.message = msg;
            this.messageType = type;
            setTimeout(() => {
                this.message = '';
            }, 3000);
        }
    }
}).mount('#app');
