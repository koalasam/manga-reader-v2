// Library view JavaScript

let allSeries = [];

// Load library on page load
document.addEventListener('DOMContentLoaded', () => {
    loadLibrary();
    setupSearch();
});

async function loadLibrary() {
    const loading = document.getElementById('loading');
    const grid = document.getElementById('libraryGrid');
    
    try {
        const response = await fetch('/api/library');
        const series = await response.json();
        
        allSeries = series;
        
        loading.style.display = 'none';
        
        if (series.length === 0) {
            showNoResults('No manga series found in library');
            return;
        }
        
        displaySeries(series);
    } catch (error) {
        console.error('Error loading library:', error);
        loading.textContent = 'Error loading library';
    }
}

function displaySeries(series) {
    const grid = document.getElementById('libraryGrid');
    const noResults = document.getElementById('noResults');
    
    grid.innerHTML = '';
    
    if (series.length === 0) {
        grid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    grid.style.display = 'grid';
    noResults.style.display = 'none';
    
    series.forEach(s => {
        const card = createSeriesCard(s);
        grid.appendChild(card);
    });
}

function createSeriesCard(series) {
    const card = document.createElement('div');
    card.className = 'series-card';
    
    // Cover image
    const cover = document.createElement('div');
    cover.className = 'series-cover';
    
    if (series.cover) {
        const img = document.createElement('img');
        img.src = `/api/image/${series.cover}`;
        img.alt = series.name;
        img.onerror = () => {
            cover.innerHTML = '📖';
            cover.classList.add('no-cover');
        };
        cover.appendChild(img);
    } else {
        cover.innerHTML = '📖';
        cover.classList.add('no-cover');
    }
    
    // Series info
    const info = document.createElement('div');
    info.className = 'series-info';
    
    const name = document.createElement('div');
    name.className = 'series-name';
    // Format series name for display
    name.textContent = formatSeriesName(series.name);
    
    const meta = document.createElement('div');
    meta.className = 'series-meta';
    meta.textContent = `${series.chapter_count} chapter${series.chapter_count !== 1 ? 's' : ''}`;
    
    info.appendChild(name);
    info.appendChild(meta);
    
    // Add description if available
    if (series.description) {
        const desc = document.createElement('div');
        desc.className = 'series-description';
        desc.textContent = series.description;
        info.appendChild(desc);
    }
    
    card.appendChild(cover);
    card.appendChild(info);
    
    // Click handler to view series chapters
    card.addEventListener('click', () => {
        viewSeries(series);
    });
    
    return card;
}

function viewSeries(series) {
    // Navigate to series page
    window.location.href = `/series/${encodeURIComponent(series.name)}`;
}

function formatSeriesName(name) {
    // Replace dashes and underscores with spaces and capitalize words
    return name
        .replace(/-/g, ' ')
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

function extractChapterNumber(chapterName) {
    const match = chapterName.match(/(\d+(?:\.\d+)?)/);
    if (match) {
        let num = match[1];
        // Remove leading zeros
        if (num.includes('.')) {
            const [whole, decimal] = num.split('.');
            return `${parseInt(whole, 10)}.${decimal}`;
        } else {
            return String(parseInt(num, 10));
        }
    }
    return '1';
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        
        if (query === '') {
            displaySeries(allSeries);
            return;
        }
        
        const filtered = allSeries.filter(series => {
            // Search in series name (formatted)
            const formattedName = formatSeriesName(series.name).toLowerCase();
            if (formattedName.includes(query)) {
                return true;
            }
            
            // Search in original series name
            if (series.name.toLowerCase().includes(query)) {
                return true;
            }
            
            // Search in alternate titles
            if (series.alternate_titles) {
                return series.alternate_titles.some(title => 
                    title.toLowerCase().includes(query)
                );
            }
            
            return false;
        });
        
        displaySeries(filtered);
    });
}

function showNoResults(message) {
    const grid = document.getElementById('libraryGrid');
    const noResults = document.getElementById('noResults');
    
    grid.style.display = 'none';
    noResults.style.display = 'block';
    noResults.textContent = message;
}