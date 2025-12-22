// Series detail page JavaScript

let seriesData = null;
let sortAscending = true;

document.addEventListener('DOMContentLoaded', () => {
    loadSeries();
    setupNavigation();
});

async function loadSeries() {
    const loading = document.getElementById('loading');
    const content = document.getElementById('seriesContent');
    const errorState = document.getElementById('errorState');
    
    try {
        const response = await fetch(`/api/series/${encodeURIComponent(seriesName)}`);
        
        if (!response.ok) {
            throw new Error('Series not found');
        }
        
        seriesData = await response.json();
        
        loading.style.display = 'none';
        content.style.display = 'block';
        
        displaySeriesInfo();
        displayChapters();
        setupSortButton();
        
    } catch (error) {
        console.error('Error loading series:', error);
        loading.style.display = 'none';
        errorState.style.display = 'flex';
    }
}

function displaySeriesInfo() {
    const coverImg = document.getElementById('coverImg');
    const bannerBg = document.getElementById('bannerBg');
    const title = document.getElementById('seriesTitle');
    const meta = document.getElementById('seriesMeta');
    const description = document.getElementById('seriesDescription');
    const genres = document.getElementById('seriesGenres');
    const altTitles = document.getElementById('alternativeTitles');
    
    // Set cover image and banner background
    if (seriesData.cover) {
        const coverUrl = `/api/image/${seriesData.cover}`;
        coverImg.src = coverUrl;
        coverImg.alt = seriesData.display_name || seriesData.name;
        
        // Set blurred background
        bannerBg.style.backgroundImage = `url('${coverUrl}')`;
    }
    
    // Set title - use display_name or format the name
    const displayName = seriesData.display_name || formatSeriesName(seriesData.name);
    title.textContent = displayName;
    
    // Set metadata
    const metaParts = [];
    
    if (seriesData.author) {
        metaParts.push(`<span><strong>✍️ Author:</strong> ${escapeHtml(seriesData.author)}</span>`);
    }
    
    if (seriesData.status) {
        const statusEmoji = seriesData.status.toLowerCase() === 'ongoing' ? '📖' : '✅';
        metaParts.push(`<span><strong>${statusEmoji} Status:</strong> ${capitalizeFirst(seriesData.status)}</span>`);
    }
    
    const chapterText = seriesData.chapter_count === 1 ? 'Chapter' : 'Chapters';
    metaParts.push(`<span><strong>📚 Total:</strong> ${seriesData.chapter_count} ${chapterText}</span>`);
    
    meta.innerHTML = metaParts.join('');
    
    // Set description
    if (seriesData.description) {
        description.textContent = seriesData.description;
        description.style.display = 'block';
    } else {
        description.style.display = 'none';
    }
    
    // Set genres
    if (seriesData.genres && seriesData.genres.length > 0) {
        genres.innerHTML = seriesData.genres
            .map(genre => `<span class="genre-tag">${escapeHtml(genre)}</span>`)
            .join('');
        genres.style.display = 'flex';
    } else {
        genres.style.display = 'none';
    }
    
    // Set alternative titles
    if (seriesData.alternate_titles && seriesData.alternate_titles.length > 0) {
        const altTitlesHtml = seriesData.alternate_titles
            .map(title => `<span>${escapeHtml(title)}</span>`)
            .join('');
        altTitles.innerHTML = `<strong>Alternative Titles:</strong><br>${altTitlesHtml}`;
        altTitles.style.display = 'block';
    } else {
        altTitles.style.display = 'none';
    }
    
    // Update page title
    document.title = `${displayName} - Manga Library`;
}

function displayChapters() {
    const chapterList = document.getElementById('chapterList');
    const chapterCount = document.getElementById('chapterCount');
    
    const chapterText = seriesData.chapters.length === 1 ? 'chapter' : 'chapters';
    chapterCount.textContent = `${seriesData.chapters.length} ${chapterText}`;
    
    chapterList.innerHTML = '';
    
    // Get chapters in current sort order
    const chapters = getCurrentSortedChapters();
    
    chapters.forEach((chapter, index) => {
        const item = createChapterItem(chapter, index);
        chapterList.appendChild(item);
    });
}

function getCurrentSortedChapters() {
    // Clone the array to avoid mutating original
    const chapters = [...seriesData.chapters];
    
    if (sortAscending) {
        return chapters; // Already sorted ascending from API
    } else {
        return chapters.reverse(); // Reverse for descending
    }
}

function createChapterItem(chapterName, index) {
    const item = document.createElement('div');
    item.className = 'chapter-item';
    
    const leftDiv = document.createElement('div');
    leftDiv.className = 'chapter-info-left';
    
    const number = document.createElement('div');
    number.className = 'chapter-number';
    number.textContent = formatChapterName(chapterName);
    
    // Only show technical name if it's different from formatted name
    const technicalName = formatTechnicalName(chapterName);
    const formattedName = formatChapterName(chapterName);
    
    // Don't show redundant technical name if it's essentially the same
    if (technicalName.toLowerCase() !== formattedName.toLowerCase() && 
        !technicalName.toLowerCase().includes('chapter')) {
        const name = document.createElement('div');
        name.className = 'chapter-name';
        name.textContent = technicalName;
        leftDiv.appendChild(number);
        leftDiv.appendChild(name);
    } else {
        leftDiv.appendChild(number);
    }
    
    const arrow = document.createElement('div');
    arrow.className = 'chapter-arrow';
    arrow.textContent = '→';
    
    item.appendChild(leftDiv);
    item.appendChild(arrow);
    
    // Click handler
    item.addEventListener('click', () => {
        const chapterNum = extractChapterNumber(chapterName);
        window.location.href = `/reader/${encodeURIComponent(seriesName)}/${chapterNum}`;
    });
    
    // Keyboard accessibility
    item.setAttribute('tabindex', '0');
    item.setAttribute('role', 'button');
    item.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            item.click();
        }
    });
    
    return item;
}

function setupSortButton() {
    const sortBtn = document.getElementById('sortBtn');
    const sortIcon = document.getElementById('sortIcon');
    
    sortBtn.addEventListener('click', () => {
        sortAscending = !sortAscending;
        
        // Update icon
        sortIcon.textContent = sortAscending ? '↓' : '↑';
        sortIcon.style.transform = sortAscending ? 'rotate(0deg)' : 'rotate(180deg)';
        
        // Re-render chapters
        displayChapters();
        
        // Animate the sort
        const chapterList = document.getElementById('chapterList');
        chapterList.style.opacity = '0.5';
        setTimeout(() => {
            chapterList.style.opacity = '1';
        }, 150);
    });
}

function formatChapterName(chapterName) {
    // Extract chapter number and remove leading zeros
    const match = chapterName.match(/(\d+(?:\.\d+)?)/);
    if (match) {
        let num = match[1];
        // Remove leading zeros but keep decimal part
        if (num.includes('.')) {
            const [whole, decimal] = num.split('.');
            num = `${parseInt(whole, 10)}.${decimal}`;
        } else {
            num = String(parseInt(num, 10));
        }
        return `Chapter ${num}`;
    }
    
    // Fallback: format the name nicely
    return chapterName.replace(/-/g, ' ').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatTechnicalName(chapterName) {
    // Format the technical folder/file name for display
    return chapterName.replace(/-/g, ' ').replace(/_/g, ' ');
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

function formatSeriesName(name) {
    return name
        .replace(/-/g, ' ')
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setupNavigation() {
    const backBtn = document.getElementById('backBtn');
    
    backBtn.addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // Keyboard shortcut - ESC to go back
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            window.location.href = '/';
        }
    });
}

// Add smooth scrolling animation
document.addEventListener('DOMContentLoaded', () => {
    const chapterList = document.getElementById('chapterList');
    if (chapterList) {
        chapterList.style.transition = 'opacity 0.3s ease';
    }
});