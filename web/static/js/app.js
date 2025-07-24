// Manalytics Frontend Application - Fixed Version
const API_BASE_URL = 'http://localhost:8000/api';

// State management
const state = {
    currentFormat: 'standard',
    dateRange: 7,
    metaData: null,
    archetypes: [],
    decks: [],
    loading: false,
    error: null
};

// DOM elements
const elements = {
    formatSelect: document.getElementById('formatSelect'),
    dateRange: document.getElementById('dateRange'),
    refreshBtn: document.getElementById('refreshBtn'),
    loadingIndicator: document.getElementById('loadingIndicator'),
    apiStatus: document.getElementById('apiStatus'),
    metaSnapshot: document.getElementById('metaSnapshot'),
    archetypeTable: document.getElementById('archetypeTable'),
    deckList: document.getElementById('deckList')
};

// Chart instance
let archetypeChart = null;

// API client
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL.replace('/api', '')}/health`);
            return response.ok;
        } catch {
            return false;
        }
    }

    async getMetaSnapshot(format, days = 30) {
        try {
            const response = await fetch(`${this.baseURL}/analysis/meta/${format}?days=${days}`);
            if (!response.ok) throw new Error('Failed to fetch meta snapshot');
            return response.json();
        } catch (error) {
            console.error('Error fetching meta snapshot:', error);
            throw error;
        }
    }

    async getArchetypes(format) {
        const response = await fetch(`${this.baseURL}/archetypes/?format=${format}`);
        if (!response.ok) throw new Error('Failed to fetch archetypes');
        return response.json();
    }

    async getDecks() {
        try {
            const response = await fetch(`${this.baseURL}/decks/`);
            if (!response.ok) return [];
            return response.json();
        } catch {
            return [];
        }
    }
}

const api = new APIClient(API_BASE_URL);

// Initialize the application
async function init() {
    // Check API health
    const isHealthy = await api.checkHealth();
    updateAPIStatus(isHealthy);

    // Set up event listeners
    elements.formatSelect.addEventListener('change', handleFormatChange);
    elements.dateRange.addEventListener('change', handleDateRangeChange);
    elements.refreshBtn.addEventListener('click', loadData);

    // Load initial data
    await loadData();
}

function updateAPIStatus(isHealthy) {
    elements.apiStatus.textContent = isHealthy ? 'Online' : 'Offline';
    elements.apiStatus.className = `status-indicator ${isHealthy ? 'online' : 'offline'}`;
}

function handleFormatChange(e) {
    state.currentFormat = e.target.value;
    loadData();
}

function handleDateRangeChange(e) {
    state.dateRange = parseInt(e.target.value);
    loadData();
}

async function loadData() {
    setLoading(true);
    clearError();

    try {
        // Fetch meta data
        const metaSnapshot = await api.getMetaSnapshot(state.currentFormat, state.dateRange);
        
        // Check if we have data
        if (metaSnapshot.total_decks === 0 && metaSnapshot.message) {
            showNoDataMessage(metaSnapshot.message);
            updateEmptyChart();
        } else {
            // We have data, update the UI
            state.metaData = metaSnapshot;
            updateArchetypeChart(metaSnapshot.data);
            updateArchetypeTable(metaSnapshot.data);
        }
        
        // Try to load other data
        try {
            const [archetypes, decks] = await Promise.all([
                api.getArchetypes(state.currentFormat),
                api.getDecks()
            ]);
            state.archetypes = archetypes;
            state.decks = decks;
            updateDeckList();
        } catch (error) {
            console.warn('Failed to load additional data:', error);
        }
        
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Failed to load data. Please check your connection and try again.');
        showMockData();
    } finally {
        setLoading(false);
    }
}

function setLoading(loading) {
    state.loading = loading;
    elements.loadingIndicator.classList.toggle('hidden', !loading);
    elements.refreshBtn.disabled = loading;
}

function clearError() {
    state.error = null;
    const errorElements = document.querySelectorAll('.error, .no-data-message');
    errorElements.forEach(el => el.remove());
}

function showError(message) {
    state.error = message;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    elements.metaSnapshot.prepend(errorDiv);
}

function showNoDataMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'no-data-message';
    messageDiv.innerHTML = `
        <p>${message}</p>
        <p>To collect data, run:</p>
        <code>docker exec manalytics-worker-1 python scripts/run_pipeline.py --format ${state.currentFormat} --days ${state.dateRange}</code>
    `;
    elements.archetypeTable.innerHTML = '';
    elements.archetypeTable.appendChild(messageDiv);
}

function showMockData() {
    // Show mock data when API fails completely
    const mockData = getMockArchetypes();
    updateArchetypeChart(mockData);
    updateArchetypeTable(mockData);
}

function updateEmptyChart() {
    const ctx = document.getElementById('archetypeChart').getContext('2d');
    
    if (archetypeChart) {
        archetypeChart.destroy();
    }
    
    archetypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['No Data'],
            datasets: [{
                data: [1],
                backgroundColor: ['#666666'],
                borderColor: '#30363d',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
}

function updateArchetypeChart(archetypes) {
    const ctx = document.getElementById('archetypeChart').getContext('2d');
    
    // Prepare data for the chart
    const chartData = archetypes.length > 0 ? 
        {
            labels: archetypes.slice(0, 10).map(a => a.archetype || a.name),
            data: archetypes.slice(0, 10).map(a => a.meta_share || (a.meta_share * 100))
        } : 
        prepareChartData([]);
    
    // Destroy existing chart if it exists
    if (archetypeChart) {
        archetypeChart.destroy();
    }
    
    // Create new chart
    archetypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: generateColors(chartData.labels.length),
                borderColor: '#30363d',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#c9d1d9',
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function prepareChartData(archetypes) {
    if (archetypes && archetypes.length > 0) {
        return {
            labels: archetypes.map(a => a.name || a.archetype),
            data: archetypes.map(a => a.meta_share)
        };
    }
    
    // Mock data for demonstration
    return {
        labels: ['Mono Red Aggro', 'UW Control', 'Golgari Midrange', 'Rakdos Sacrifice', 'Other'],
        data: [22.5, 18.3, 15.7, 12.4, 31.1]
    };
}

function generateColors(count) {
    const colors = [
        '#58a6ff', '#3fb950', '#d29922', '#f85149', '#a371f7',
        '#56d364', '#79c0ff', '#d2a8ff', '#ffa657', '#f0883e'
    ];
    
    while (colors.length < count) {
        colors.push(...colors);
    }
    
    return colors.slice(0, count);
}

function updateArchetypeTable(archetypes) {
    if (!archetypes || archetypes.length === 0) {
        elements.archetypeTable.innerHTML = '<p>No archetype data available.</p>';
        return;
    }
    
    const tableHTML = `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Archetype</th>
                    <th>Meta Share</th>
                    <th>Deck Count</th>
                    <th>Tier</th>
                </tr>
            </thead>
            <tbody>
                ${archetypes.slice(0, 15).map((archetype, index) => `
                    <tr>
                        <td>#${archetype.rank || index + 1}</td>
                        <td class="deck-archetype">${archetype.archetype || archetype.name}</td>
                        <td class="percentage">${archetype.meta_share.toFixed(1)}%</td>
                        <td>${archetype.deck_count}</td>
                        <td>${archetype.tier || 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    elements.archetypeTable.innerHTML = tableHTML;
}

function getMockArchetypes() {
    return [
        { name: 'Mono Red Aggro', archetype: 'Mono Red Aggro', meta_share: 22.5, deck_count: 45, tier: 'Tier 1' },
        { name: 'UW Control', archetype: 'UW Control', meta_share: 18.3, deck_count: 37, tier: 'Tier 1' },
        { name: 'Golgari Midrange', archetype: 'Golgari Midrange', meta_share: 15.7, deck_count: 31, tier: 'Tier 2' },
        { name: 'Rakdos Sacrifice', archetype: 'Rakdos Sacrifice', meta_share: 12.4, deck_count: 25, tier: 'Tier 2' },
        { name: 'Simic Ramp', archetype: 'Simic Ramp', meta_share: 9.2, deck_count: 18, tier: 'Tier 3' }
    ];
}

function updateDeckList() {
    const deckData = state.decks.length > 0 ? state.decks : getMockDecks();
    
    const deckHTML = deckData.map(deck => `
        <div class="deck-card">
            <div class="deck-header">
                <div>
                    <div class="deck-archetype">${deck.archetype}</div>
                    <div class="deck-player">by ${deck.player}</div>
                </div>
                <div class="deck-placement">${deck.placement}</div>
            </div>
            <div class="deck-meta">
                <small>${deck.tournament} • ${deck.date}</small>
            </div>
        </div>
    `).join('');
    
    elements.deckList.innerHTML = deckHTML || '<p>No recent decks found.</p>';
}

function getMockDecks() {
    return [
        {
            archetype: 'Mono Red Aggro',
            player: 'ProPlayer123',
            placement: '1st',
            tournament: 'MTGO Challenge',
            date: '2024-01-20'
        },
        {
            archetype: 'UW Control',
            player: 'ControlMaster',
            placement: '2nd',
            tournament: 'MTGO Challenge',
            date: '2024-01-20'
        },
        {
            archetype: 'Golgari Midrange',
            player: 'MidrangeExpert',
            placement: '3rd',
            tournament: 'MTGO Showcase',
            date: '2024-01-19'
        }
    ];
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);