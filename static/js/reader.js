// Reader JavaScript - Multi-mode support

let currentChapter = null;
let observer = null;
let currentVisiblePage = 1;
let currentPageIndex = 0;
let settings = {
    reader_mode: 'scroll',
    reading_direction: 'ltr',
    fit_mode: 'width'
};

document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    loadChapter();
    setupNavigation();
    setupSettings();
});

// ===== Settings Management =====
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        if (response.ok) {
            settings = await response.json();
            applySettings();
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function saveSettings() {
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        if (response.ok) {
            applySettings();
        }
    } catch (error) {
        console.error('Error saving settings:', error);
    }
}

function applySettings() {
    // Apply reader mode
    const scrollReader = document.getElementById('scrollReader');
    const singleReader = document.getElementById('singleReader');
    
    if (settings.reader_mode === 'scroll') {
        scrollReader.style.display = 'block';
        singleReader.style.display = 'none';
        document.body.classList.remove('single-mode');
        if (currentChapter) {
            displayScrollReader();
        }
    } else {
        scrollReader.style.display = 'none';
        singleReader.style.display = 'flex';
        document.body.classList.add('single-mode');
        if (currentChapter) {
            displaySingleReader();
        }
    }
    
    // Apply fit mode
    const container = document.getElementById('singlePageContainer');
    container.className = 'single-page-container';
    container.classList.add(`fit-${settings.fit_mode}`);
    
    // Update settings panel UI
    updateSettingsUI();
}

function updateSettingsUI() {
    document.querySelectorAll('.setting-option').forEach(btn => {
        const settingName = btn.dataset.setting;
        const value = btn.dataset.value;
        if (settings[settingName] === value) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// ===== Chapter Loading =====
async function loadChapter() {
    const loading = document.getElementById('loading');
    
    try {
        const response = await fetch(`/api/chapter/${encodeURIComponent(seriesName)}/${chapterNum}`);
        
        if (!response.ok) {
            throw new Error('Chapter not found');
        }
        
        currentChapter = await response.json();
        
        loading.style.display = 'none';
        
        updateHeaderInfo();
        updateNavigation();
        applySettings();
        
    } catch (error) {
        console.error('Error loading chapter:', error);
        loading.textContent = 'Error loading chapter';
    }
}

function updateHeaderInfo() {
    const seriesTitle = document.getElementById('seriesTitle');
    const chapterInfo = document.getElementById('chapterInfo');
    
    seriesTitle.textContent = currentChapter.series_name;
    chapterInfo.textContent = `${currentChapter.chapter} - ${currentChapter.page_count} pages`;
}

// ===== Scroll Reader Mode =====
function displayScrollReader() {
    const container = document.getElementById('scrollPageContainer');
    container.innerHTML = '';
    
    currentChapter.pages.forEach((page, index) => {
        const pageDiv = document.createElement('div');
        pageDiv.className = 'manga-page';
        pageDiv.dataset.pageNumber = index + 1;
        
        const img = document.createElement('img');
        img.src = `/api/image/${page}`;
        img.alt = `Page ${index + 1}`;
        img.loading = 'lazy';
        
        pageDiv.appendChild(img);
        container.appendChild(pageDiv);
    });
    
    setupScrollTracking();
    updatePageIndicator(1);
}

function setupScrollTracking() {
    if (observer) {
        observer.disconnect();
    }
    
    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
                const pageNum = parseInt(entry.target.dataset.pageNumber);
                if (pageNum !== currentVisiblePage) {
                    currentVisiblePage = pageNum;
                    updatePageIndicator(pageNum);
                }
            }
        });
    }, {
        threshold: 0.5,
        rootMargin: '-100px 0px'
    });
    
    setTimeout(() => {
        const pages = document.querySelectorAll('.manga-page');
        pages.forEach(page => observer.observe(page));
    }, 100);
}

// ===== Single Page Reader Mode =====
function displaySingleReader() {
    currentPageIndex = 0;
    showPage(currentPageIndex);
    setupSinglePageControls();
}

function showPage(index) {
    if (!currentChapter || index < 0 || index >= currentChapter.pages.length) {
        return;
    }
    
    currentPageIndex = index;
    const img = document.getElementById('currentPageImg');
    img.src = `/api/image/${currentChapter.pages[index]}`;
    
    updateSinglePageControls();
    updatePageIndicator(index + 1);
}

function updateSinglePageControls() {
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    const counter = document.getElementById('pageCounter');
    
    prevBtn.disabled = currentPageIndex === 0;
    nextBtn.disabled = currentPageIndex === currentChapter.pages.length - 1;
    counter.textContent = `Page ${currentPageIndex + 1} / ${currentChapter.pages.length}`;
}

function setupSinglePageControls() {
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    const container = document.getElementById('singlePageContainer');
    
    // Button controls
    prevBtn.addEventListener('click', () => {
        if (currentPageIndex > 0) {
            showPage(currentPageIndex - 1);
        }
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentPageIndex < currentChapter.pages.length - 1) {
            showPage(currentPageIndex + 1);
        } else {
            // Go to next chapter if available
            if (currentChapter.navigation.next_chapter_num) {
                navigateToChapter(currentChapter.navigation.next_chapter_num);
            }
        }
    });
    
    // Click navigation on image
    container.addEventListener('click', (e) => {
        const rect = container.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercentage = clickX / rect.width;
        
        // Determine which side was clicked based on reading direction
        if (settings.reading_direction === 'ltr') {
            if (clickPercentage < 0.4) {
                // Left side - go previous
                if (currentPageIndex > 0) {
                    showPage(currentPageIndex - 1);
                }
            } else if (clickPercentage > 0.6) {
                // Right side - go next
                if (currentPageIndex < currentChapter.pages.length - 1) {
                    showPage(currentPageIndex + 1);
                }
            }
        } else { // rtl
            if (clickPercentage < 0.4) {
                // Left side - go next
                if (currentPageIndex < currentChapter.pages.length - 1) {
                    showPage(currentPageIndex + 1);
                }
            } else if (clickPercentage > 0.6) {
                // Right side - go previous
                if (currentPageIndex > 0) {
                    showPage(currentPageIndex - 1);
                }
            }
        }
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', handleKeyboardNavigation);
}

function handleKeyboardNavigation(e) {
    if (settings.reader_mode !== 'single') return;
    
    if (e.key === 'ArrowLeft') {
        if (settings.reading_direction === 'ltr') {
            // Previous page
            if (currentPageIndex > 0) {
                showPage(currentPageIndex - 1);
            }
        } else {
            // Next page
            if (currentPageIndex < currentChapter.pages.length - 1) {
                showPage(currentPageIndex + 1);
            }
        }
    } else if (e.key === 'ArrowRight') {
        if (settings.reading_direction === 'ltr') {
            // Next page
            if (currentPageIndex < currentChapter.pages.length - 1) {
                showPage(currentPageIndex + 1);
            }
        } else {
            // Previous page
            if (currentPageIndex > 0) {
                showPage(currentPageIndex - 1);
            }
        }
    }
}

// ===== Page Indicator =====
function updatePageIndicator(pageNum) {
    const indicator = document.getElementById('pageIndicator');
    if (currentChapter) {
        indicator.textContent = `Page ${pageNum} of ${currentChapter.page_count}`;
    }
}

// ===== Navigation =====
function setupNavigation() {
    const backBtn = document.getElementById('backBtn');
    const prevBtn = document.getElementById('prevChapterBtn');
    const nextBtn = document.getElementById('nextChapterBtn');
    
    backBtn.addEventListener('click', () => {
        window.location.href = `/series/${encodeURIComponent(seriesName)}`;
    });
    
    prevBtn.addEventListener('click', () => {
        if (currentChapter && currentChapter.navigation.prev_chapter_num) {
            navigateToChapter(currentChapter.navigation.prev_chapter_num);
        }
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentChapter && currentChapter.navigation.next_chapter_num) {
            navigateToChapter(currentChapter.navigation.next_chapter_num);
        }
    });
}

function updateNavigation() {
    const prevBtn = document.getElementById('prevChapterBtn');
    const nextBtn = document.getElementById('nextChapterBtn');
    
    if (currentChapter && currentChapter.navigation) {
        const nav = currentChapter.navigation;
        
        if (nav.prev_chapter) {
            prevBtn.style.display = 'block';
            prevBtn.textContent = `← Chapter ${nav.prev_chapter_num}`;
        } else {
            prevBtn.style.display = 'none';
        }
        
        if (nav.next_chapter) {
            nextBtn.style.display = 'block';
            nextBtn.textContent = `Chapter ${nav.next_chapter_num} →`;
        } else {
            nextBtn.style.display = 'none';
        }
    }
}

function navigateToChapter(chapterNum) {
    if (observer) {
        observer.disconnect();
    }
    window.location.href = `/reader/${encodeURIComponent(seriesName)}/${chapterNum}`;
}

// ===== Settings Panel =====
function setupSettings() {
    const settingsBtn = document.getElementById('settingsBtn');
    const closeBtn = document.getElementById('closeSettings');
    const resetBtn = document.getElementById('resetSettings');
    const panel = document.getElementById('settingsPanel');
    
    settingsBtn.addEventListener('click', () => {
        panel.classList.add('open');
    });
    
    closeBtn.addEventListener('click', () => {
        panel.classList.remove('open');
    });
    
    // Close panel when clicking outside
    panel.addEventListener('click', (e) => {
        if (e.target === panel) {
            panel.classList.remove('open');
        }
    });
    
    // Setting options
    document.querySelectorAll('.setting-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const settingName = btn.dataset.setting;
            const value = btn.dataset.value;
            
            settings[settingName] = value;
            saveSettings();
        });
    });
    
    // Reset button
    resetBtn.addEventListener('click', async () => {
        settings = {
            reader_mode: 'scroll',
            reading_direction: 'ltr',
            fit_mode: 'width'
        };
        await saveSettings();
    });
}

// ===== Cleanup =====
window.addEventListener('beforeunload', () => {
    if (observer) {
        observer.disconnect();
    }
});