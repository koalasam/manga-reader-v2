// Reader JavaScript - Multi-mode support including dual page

let currentChapter = null;
let observer = null;
let currentVisiblePage = 1;
let currentPageIndex = 0;
let currentPairIndex = 0;
let settings = {
    reader_mode: 'scroll',
    reading_direction: 'ltr',
    fit_mode: 'width'
};
let preloadedChapters = {
    next: null,
    prev: null
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
    const dualReader = document.getElementById('dualReader');
    
    // Hide all readers first
    scrollReader.style.display = 'none';
    singleReader.style.display = 'none';
    dualReader.style.display = 'none';
    
    // Remove all mode classes
    document.body.classList.remove('single-mode', 'dual-mode');
    
    if (settings.reader_mode === 'scroll') {
        scrollReader.style.display = 'block';
        if (currentChapter) {
            displayScrollReader();
        }
    } else if (settings.reader_mode === 'single') {
        singleReader.style.display = 'flex';
        document.body.classList.add('single-mode');
        if (currentChapter) {
            displaySingleReader();
        }
    } else if (settings.reader_mode === 'dual') {
        dualReader.style.display = 'flex';
        document.body.classList.add('dual-mode');
        if (currentChapter) {
            displayDualReader();
        }
    }
    
    // Hide/show controls based on mode
    try {
        const pageCounter = document.getElementById('pageCounter');
        const pairCounter = document.getElementById('pairCounter');
        const singleControls = document.querySelectorAll('.single-page-controls');
        const footerIndicator = document.getElementById('pageIndicator');
        
        if (settings.reader_mode === 'scroll') {
            singleControls.forEach(c => c.style.display = 'none');
            if (footerIndicator) footerIndicator.style.display = 'block';
        } else if (settings.reader_mode === 'single') {
            if (pageCounter) pageCounter.parentElement.style.display = 'flex';
            if (pairCounter) pairCounter.parentElement.style.display = 'none';
            if (footerIndicator) footerIndicator.style.display = 'block';
        } else if (settings.reader_mode === 'dual') {
            if (pageCounter) pageCounter.parentElement.style.display = 'none';
            if (pairCounter) pairCounter.parentElement.style.display = 'flex';
            if (footerIndicator) footerIndicator.style.display = 'block';
        }
    } catch (e) {
        // ignore if elements not present yet
    }
    
    // Apply fit mode to containers
    const singleContainer = document.getElementById('singlePageContainer');
    const dualContainer = document.getElementById('dualPageContainer');
    
    if (singleContainer) {
        singleContainer.className = 'single-page-container';
        singleContainer.classList.add(`fit-${settings.fit_mode}`);
    }
    
    if (dualContainer) {
        dualContainer.className = 'dual-page-container';
        dualContainer.classList.add(`fit-${settings.fit_mode}`);
    }
    
    // Show/hide settings based on active reader mode
    const directionSetting = document.getElementById('directionSetting');
    const fitModeSetting = document.getElementById('fitModeSetting');
    
    if (directionSetting && fitModeSetting) {
        if (settings.reader_mode === 'scroll') {
            // Scroll mode: hide both direction and fit mode
            directionSetting.style.display = 'none';
            fitModeSetting.style.display = 'none';
        } else if (settings.reader_mode === 'single') {
            // Single mode: show both direction and fit mode
            directionSetting.style.display = 'block';
            fitModeSetting.style.display = 'block';
        } else if (settings.reader_mode === 'dual') {
            // Dual mode: hide direction (always RTL), show fit mode
            directionSetting.style.display = 'none';
            fitModeSetting.style.display = 'block';
        }
    }
    
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
        
        // Preload adjacent chapters in background
        preloadAdjacentChapters();
        
    } catch (error) {
        console.error('Error loading chapter:', error);
        loading.textContent = 'Error loading chapter';
    }
}

async function preloadAdjacentChapters() {
    if (!currentChapter?.navigation) return;
    
    const nav = currentChapter.navigation;
    
    // Preload next chapter
    if (nav.next_chapter) {
        preloadChapter(nav.next_chapter, 'next');
    }
    
    // Preload previous chapter
    if (nav.prev_chapter) {
        preloadChapter(nav.prev_chapter, 'prev');
    }
}

async function preloadChapter(chapterNum, direction) {
    try {
        console.log(`Preloading ${direction} chapter: ${chapterNum}`);
        
        const response = await fetch(`/api/chapter/${encodeURIComponent(seriesName)}/${chapterNum}`);
        
        if (!response.ok) {
            console.warn(`Failed to preload ${direction} chapter`);
            return;
        }
        
        const chapterData = await response.json();
        
        // Store preloaded data
        preloadedChapters[direction] = {
            chapterNum: chapterNum,
            data: chapterData,
            timestamp: Date.now()
        };
        
        // Preload first few images
        const imagesToPreload = direction === 'next' ? 
            chapterData.pages.slice(0, 3) : // Preload first 3 pages of next chapter
            chapterData.pages.slice(-3);     // Preload last 3 pages of prev chapter
        
        imagesToPreload.forEach(imagePath => {
            const img = new Image();
            img.src = `/api/image/${imagePath}`;
        });
        
        console.log(`Successfully preloaded ${direction} chapter: ${chapterNum}`);
        
    } catch (error) {
        console.error(`Error preloading ${direction} chapter:`, error);
    }
}

function getPreloadedChapter(chapterNum) {
    // Check if we have this chapter preloaded
    if (preloadedChapters.next?.chapterNum == chapterNum) {
        const data = preloadedChapters.next.data;
        preloadedChapters.next = null; // Clear after use
        return data;
    }
    
    if (preloadedChapters.prev?.chapterNum == chapterNum) {
        const data = preloadedChapters.prev.data;
        preloadedChapters.prev = null; // Clear after use
        return data;
    }
    
    return null;
}

function updateHeaderInfo() {
    const seriesTitle = document.getElementById('seriesTitle');
    const chapterInfo = document.getElementById('chapterInfo');
    
    const formattedSeriesName = formatDisplayName(currentChapter.series_name);
    seriesTitle.textContent = formattedSeriesName;
    
    const chapterDisplay = currentChapter.chapter_display || formatChapterName(currentChapter.chapter);
    chapterInfo.textContent = `${chapterDisplay} - ${currentChapter.page_count} pages`;
    
    // Update offset button if in dual mode
    updateOffsetButton();
}

function formatDisplayName(name) {
    return name.replace(/-/g, ' ').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatChapterName(chapterName) {
    const match = chapterName.match(/(\d+(?:\.\d+)?)/);
    if (match) {
        let num = match[1];
        if (num.includes('.')) {
            const [whole, decimal] = num.split('.');
            num = `${parseInt(whole, 10)}.${decimal}`;
        } else {
            num = String(parseInt(num, 10));
        }
        return `Chapter ${num}`;
    }
    return chapterName.replace(/-/g, ' ').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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
    updatePageIndicator(1, currentChapter.page_count);
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
                    updatePageIndicator(pageNum, currentChapter.page_count);
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
    
    // Trigger preload when nearing end of chapter
    checkPreloadTrigger();
}

function showPage(index) {
    if (!currentChapter || index < 0 || index >= currentChapter.pages.length) {
        return;
    }
    
    currentPageIndex = index;
    const img = document.getElementById('currentPageImg');
    img.src = `/api/image/${currentChapter.pages[index]}`;
    
    updateSinglePageControls();
    updatePageIndicator(index + 1, currentChapter.page_count);
    
    // Trigger preload check
    checkPreloadTrigger();
}

function checkPreloadTrigger() {
    if (!currentChapter) return;
    
    // In single page mode, preload when within 3 pages of end
    if (settings.reader_mode === 'single') {
        const pagesFromEnd = currentChapter.pages.length - currentPageIndex - 1;
        if (pagesFromEnd <= 3 && currentChapter.navigation?.next_chapter) {
            if (!preloadedChapters.next || 
                preloadedChapters.next.chapterNum != currentChapter.navigation.next_chapter) {
                preloadChapter(currentChapter.navigation.next_chapter, 'next');
            }
        }
    }
    
    // In dual mode, preload immediately (pairing script is slow)
    if (settings.reader_mode === 'dual') {
        if (currentChapter.navigation?.next_chapter) {
            if (!preloadedChapters.next || 
                preloadedChapters.next.chapterNum != currentChapter.navigation.next_chapter) {
                preloadChapter(currentChapter.navigation.next_chapter, 'next');
            }
        }
    }
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

    prevBtn.replaceWith(prevBtn.cloneNode(true));
    nextBtn.replaceWith(nextBtn.cloneNode(true));
    
    const newPrevBtn = document.getElementById('prevPageBtn');
    const newNextBtn = document.getElementById('nextPageBtn');

    newPrevBtn.addEventListener('click', () => {
        if (currentPageIndex > 0) {
            showPage(currentPageIndex - 1);
        } else if (currentChapter?.navigation?.prev_chapter) {
            navigateToChapter(currentChapter.navigation.prev_chapter);
        }
    });

    newNextBtn.addEventListener('click', () => {
        if (currentPageIndex < currentChapter.pages.length - 1) {
            showPage(currentPageIndex + 1);
        } else if (currentChapter?.navigation?.next_chapter) {
            navigateToChapter(currentChapter.navigation.next_chapter);
        }
    });

    container.addEventListener('click', (e) => {
        const rect = container.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercentage = clickX / rect.width;

        if (settings.reading_direction === 'ltr') {
            if (clickPercentage < 0.4) {
                // Left side - previous
                if (currentPageIndex > 0) {
                    showPage(currentPageIndex - 1);
                } else if (currentChapter?.navigation?.prev_chapter) {
                    navigateToChapter(currentChapter.navigation.prev_chapter);
                }
            } else if (clickPercentage > 0.6) {
                // Right side - next
                if (currentPageIndex < currentChapter.pages.length - 1) {
                    showPage(currentPageIndex + 1);
                } else if (currentChapter?.navigation?.next_chapter) {
                    navigateToChapter(currentChapter.navigation.next_chapter);
                }
            }
        } else {
            if (clickPercentage < 0.4) {
                // Left side in RTL - next
                if (currentPageIndex < currentChapter.pages.length - 1) {
                    showPage(currentPageIndex + 1);
                } else if (currentChapter?.navigation?.next_chapter) {
                    navigateToChapter(currentChapter.navigation.next_chapter);
                }
            } else if (clickPercentage > 0.6) {
                // Right side in RTL - previous
                if (currentPageIndex > 0) {
                    showPage(currentPageIndex - 1);
                } else if (currentChapter?.navigation?.prev_chapter) {
                    navigateToChapter(currentChapter.navigation.prev_chapter);
                }
            }
        }
    });

    document.addEventListener('keydown', handleKeyboardNavigation);
}

// ===== Dual Page Reader Mode =====
function displayDualReader() {
    currentPairIndex = 0;
    showPair(currentPairIndex);
    setupDualPageControls();
    
    // Trigger preload when nearing end of chapter
    checkPreloadTrigger();
}

function showPair(index) {
    if (!currentChapter || !currentChapter.page_pairs || 
        index < 0 || index >= currentChapter.page_pairs.length) {
        return;
    }
    
    currentPairIndex = index;
    const pair = currentChapter.page_pairs[index];
    
    const rightImg = document.getElementById('rightPageImg');
    const leftImg = document.getElementById('leftPageImg');
    const wrapper = document.getElementById('dualPageWrapper');
    
    // Page pairer outputs [right_page, left_page], so swap them for display
    if (pair.length === 2) {
        // Two pages - pair[0] is right, pair[1] is left in the array
        // But we need to display: left image on left side, right image on right side
        leftImg.src = `/api/image/${pair[0]}`;
        rightImg.src = `/api/image/${pair[1]}`;
        rightImg.style.display = 'block';
        leftImg.style.display = 'block';
        wrapper.classList.remove('single-in-pair');
    } else if (pair.length === 1) {
        // Single page (likely double-spread or last page) - center it
        rightImg.src = `/api/image/${pair[0]}`;
        rightImg.style.display = 'block';
        leftImg.style.display = 'none';
        wrapper.classList.add('single-in-pair');
    }
    
    updateDualPageControls();
    
    // Calculate current page range for indicator
    let startPage = 0;
    for (let i = 0; i < index; i++) {
        startPage += currentChapter.page_pairs[i].length;
    }
    startPage += 1; // Convert to 1-indexed
    const endPage = startPage + pair.length - 1;
    
    if (pair.length === 1) {
        updatePageIndicator(startPage, currentChapter.page_count);
    } else {
        updatePageIndicator(`${startPage}-${endPage}`, currentChapter.page_count);
    }
    
    // Trigger preload check
    checkPreloadTrigger();
}

function updateDualPageControls() {
    const prevBtn = document.getElementById('prevPairBtn');
    const nextBtn = document.getElementById('nextPairBtn');
    const counter = document.getElementById('pairCounter');
    
    prevBtn.disabled = currentPairIndex === 0;
    nextBtn.disabled = currentPairIndex === currentChapter.page_pairs.length - 1;
    counter.textContent = `Spread ${currentPairIndex + 1} / ${currentChapter.page_pairs.length}`;
}

function setupDualPageControls() {
    const prevBtn = document.getElementById('prevPairBtn');
    const nextBtn = document.getElementById('nextPairBtn');
    const container = document.getElementById('dualPageContainer');

    prevBtn.replaceWith(prevBtn.cloneNode(true));
    nextBtn.replaceWith(nextBtn.cloneNode(true));
    
    const newPrevBtn = document.getElementById('prevPairBtn');
    const newNextBtn = document.getElementById('nextPairBtn');

    newPrevBtn.addEventListener('click', () => {
        if (currentPairIndex > 0) {
            showPair(currentPairIndex - 1);
        } else if (currentChapter?.navigation?.prev_chapter) {
            navigateToChapter(currentChapter.navigation.prev_chapter);
        }
    });

    newNextBtn.addEventListener('click', () => {
        if (currentPairIndex < currentChapter.page_pairs.length - 1) {
            showPair(currentPairIndex + 1);
        } else if (currentChapter?.navigation?.next_chapter) {
            navigateToChapter(currentChapter.navigation.next_chapter);
        }
    });

    // Click navigation - RTL (click left = next, click right = prev)
    container.addEventListener('click', (e) => {
        const rect = container.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercentage = clickX / rect.width;

        // RTL navigation for dual mode
        if (clickPercentage < 0.4) {
            // Left side - next spread
            if (currentPairIndex < currentChapter.page_pairs.length - 1) {
                showPair(currentPairIndex + 1);
            } else if (currentChapter?.navigation?.next_chapter) {
                navigateToChapter(currentChapter.navigation.next_chapter);
            }
        } else if (clickPercentage > 0.6) {
            // Right side - previous spread
            if (currentPairIndex > 0) {
                showPair(currentPairIndex - 1);
            } else if (currentChapter?.navigation?.prev_chapter) {
                navigateToChapter(currentChapter.navigation.prev_chapter);
            }
        }
    });

    document.addEventListener('keydown', handleKeyboardNavigationDual);
}

function handleKeyboardNavigation(e) {
    if (settings.reader_mode !== 'single') return;
    
    if (e.key === 'ArrowLeft') {
        if (settings.reading_direction === 'ltr') {
            // LTR: Left arrow = previous
            if (currentPageIndex > 0) {
                showPage(currentPageIndex - 1);
            } else if (currentChapter?.navigation?.prev_chapter) {
                navigateToChapter(currentChapter.navigation.prev_chapter);
            }
        } else {
            // RTL: Left arrow = next
            if (currentPageIndex < currentChapter.pages.length - 1) {
                showPage(currentPageIndex + 1);
            } else if (currentChapter?.navigation?.next_chapter) {
                navigateToChapter(currentChapter.navigation.next_chapter);
            }
        }
    } else if (e.key === 'ArrowRight') {
        if (settings.reading_direction === 'ltr') {
            // LTR: Right arrow = next
            if (currentPageIndex < currentChapter.pages.length - 1) {
                showPage(currentPageIndex + 1);
            } else if (currentChapter?.navigation?.next_chapter) {
                navigateToChapter(currentChapter.navigation.next_chapter);
            }
        } else {
            // RTL: Right arrow = previous
            if (currentPageIndex > 0) {
                showPage(currentPageIndex - 1);
            } else if (currentChapter?.navigation?.prev_chapter) {
                navigateToChapter(currentChapter.navigation.prev_chapter);
            }
        }
    }
}

function handleKeyboardNavigationDual(e) {
    if (settings.reader_mode !== 'dual') return;
    
    // RTL navigation for dual mode
    if (e.key === 'ArrowLeft') {
        // Left arrow = next (RTL)
        if (currentPairIndex < currentChapter.page_pairs.length - 1) {
            showPair(currentPairIndex + 1);
        } else if (currentChapter?.navigation?.next_chapter) {
            navigateToChapter(currentChapter.navigation.next_chapter);
        }
    } else if (e.key === 'ArrowRight') {
        // Right arrow = previous (RTL)
        if (currentPairIndex > 0) {
            showPair(currentPairIndex - 1);
        } else if (currentChapter?.navigation?.prev_chapter) {
            navigateToChapter(currentChapter.navigation.prev_chapter);
        }
    }
}

// ===== Page Indicator =====
function updatePageIndicator(page, total) {
    const indicator = document.getElementById('pageIndicator');
    if (typeof page === 'number') {
        indicator.textContent = `Page ${page} of ${total}`;
    } else {
        indicator.textContent = `Pages ${page} of ${total}`;
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
        if (currentChapter?.navigation?.prev_chapter) {
            navigateToChapter(currentChapter.navigation.prev_chapter);
        }
    });
    
    nextBtn.addEventListener('click', () => {
        if (currentChapter?.navigation?.next_chapter) {
            navigateToChapter(currentChapter.navigation.next_chapter);
        }
    });
}

function updateNavigation() {
    const prevBtn = document.getElementById('prevChapterBtn');
    const nextBtn = document.getElementById('nextChapterBtn');
    
    if (currentChapter?.navigation) {
        const nav = currentChapter.navigation;
        
        if (nav.prev_chapter) {
            prevBtn.style.display = 'block';
            const prevDisplay = nav.prev_chapter_display || formatChapterName(nav.prev_chapter);
            prevBtn.textContent = `← ${prevDisplay}`;
        } else {
            prevBtn.style.display = 'none';
        }
        
        if (nav.next_chapter) {
            nextBtn.style.display = 'block';
            const nextDisplay = nav.next_chapter_display || formatChapterName(nav.next_chapter);
            nextBtn.textContent = `${nextDisplay} →`;
        } else {
            nextBtn.style.display = 'none';
        }
    }
}

function navigateToChapter(chapterNum) {
    if (observer) {
        observer.disconnect();
    }
    
    // Check if we have preloaded data for this chapter
    const preloaded = getPreloadedChapter(chapterNum);
    
    if (preloaded) {
        console.log('Using preloaded chapter data');
        // Update URL without full page reload
        const newUrl = `/reader/${encodeURIComponent(seriesName)}/${chapterNum}`;
        window.history.pushState({}, '', newUrl);
        
        // Hide current content and show loading
        document.getElementById('scrollReader').style.display = 'none';
        document.getElementById('singleReader').style.display = 'none';
        document.getElementById('dualReader').style.display = 'none';
        
        const loading = document.getElementById('loading');
        loading.style.display = 'block';
        loading.textContent = 'Loading chapter...';
        
        // Small delay to show loading state
        setTimeout(() => {
            currentChapter = preloaded;
            
            // Update global chapter number
            window.chapterNum = chapterNum;
            
            loading.style.display = 'none';
            
            updateHeaderInfo();
            updateNavigation();
            applySettings();
            
            // Reset page/pair indices
            currentPageIndex = 0;
            currentPairIndex = 0;
            
            // Preload next adjacent chapters
            preloadAdjacentChapters();
            
            // Scroll to top
            window.scrollTo(0, 0);
        }, 100);
    } else {
        // Fallback to full page reload if not preloaded
        console.log('Chapter not preloaded, doing full reload');
        window.location.href = `/reader/${encodeURIComponent(seriesName)}/${chapterNum}`;
    }
}

// ===== Settings Panel =====
function setupSettings() {
    const settingsBtn = document.getElementById('settingsBtn');
    const closeBtn = document.getElementById('closeSettings');
    const resetBtn = document.getElementById('resetSettings');
    const offsetBtn = document.getElementById('offsetBtn');
    const panel = document.getElementById('settingsPanel');
    
    settingsBtn.addEventListener('click', () => {
        panel.classList.add('open');
    });
    
    closeBtn.addEventListener('click', () => {
        panel.classList.remove('open');
    });
    
    panel.addEventListener('click', (e) => {
        if (e.target === panel) {
            panel.classList.remove('open');
        }
    });
    
    document.querySelectorAll('.setting-option').forEach(btn => {
        btn.addEventListener('click', () => {
            const settingName = btn.dataset.setting;
            const value = btn.dataset.value;
            
            settings[settingName] = value;
            saveSettings();
        });
    });
    
    resetBtn.addEventListener('click', async () => {
        settings = {
            reader_mode: 'scroll',
            reading_direction: 'ltr',
            fit_mode: 'width'
        };
        await saveSettings();
    });
    
    // Offset toggle button
    if (offsetBtn) {
        offsetBtn.addEventListener('click', async () => {
            await toggleOffset();
        });
    }
}

async function toggleOffset() {
    if (!currentChapter) return;
    
    const offsetBtn = document.getElementById('offsetBtn');
    offsetBtn.disabled = true;
    offsetBtn.textContent = '⏳ Updating...';
    
    try {
        const response = await fetch(
            `/api/chapter/${encodeURIComponent(seriesName)}/${chapterNum}/offset`,
            { method: 'POST' }
        );
        
        if (response.ok) {
            const result = await response.json();
            currentChapter.has_offset = result.has_offset;
            
            // Reload the chapter to apply new offset
            await loadChapter();
            
            updateOffsetButton();
        } else {
            console.error('Failed to toggle offset');
            offsetBtn.textContent = '❌ Error';
            setTimeout(() => updateOffsetButton(), 2000);
        }
    } catch (error) {
        console.error('Error toggling offset:', error);
        offsetBtn.textContent = '❌ Error';
        setTimeout(() => updateOffsetButton(), 2000);
    } finally {
        offsetBtn.disabled = false;
    }
}

function updateOffsetButton() {
    const offsetBtn = document.getElementById('offsetBtn');
    const offsetGroup = document.getElementById('offsetSetting');
    
    if (!offsetBtn || !offsetGroup) return;
    
    // Only show in dual mode
    if (settings.reader_mode === 'dual') {
        offsetGroup.style.display = 'block';
        
        if (currentChapter && currentChapter.has_offset) {
            offsetBtn.classList.add('active');
            offsetBtn.innerHTML = `
                <span class="option-icon">✓</span>
                <div class="option-content">
                    <span class="option-label">Page Offset: ON</span>
                    <span class="option-desc">First page displayed alone</span>
                </div>
            `;
        } else {
            offsetBtn.classList.remove('active');
            offsetBtn.innerHTML = `
                <span class="option-icon">⊟</span>
                <div class="option-content">
                    <span class="option-label">Page Offset: OFF</span>
                    <span class="option-desc">Standard pairing from page 1</span>
                </div>
            `;
        }
    } else {
        offsetGroup.style.display = 'none';
    }
}

// ===== Cleanup =====
window.addEventListener('beforeunload', () => {
    if (observer) {
        observer.disconnect();
    }
});