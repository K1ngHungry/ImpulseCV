// ImpulseCV JavaScript Application

class ImpulseCV {
    constructor() {
        this.initializeEventListeners();
        this.loadAssets();
        this.setupDragAndDrop();
        this.pollStatus();
    }

    initializeEventListeners() {
        // File input
        document.getElementById('fileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadFile(e.target.files[0]);
            }
        });

        // Upload area click
        document.getElementById('uploadArea').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });
    }

    async loadAssets() {
        try {
            const response = await fetch('/assets');
            const assets = await response.json();
            
            const assetsList = document.getElementById('assetsList');
            assetsList.innerHTML = '';

            assets.forEach(asset => {
                const assetCard = document.createElement('div');
                assetCard.className = 'col-md-4 mb-3';
                assetCard.innerHTML = `
                    <div class="asset-card" onclick="impulseCV.processAsset('${asset.name}')">
                        <div class="asset-icon">
                            <i class="fas fa-play-circle"></i>
                        </div>
                        <h6>${asset.name}</h6>
                        <small class="text-muted">${this.formatFileSize(asset.size)}</small>
                    </div>
                `;
                assetsList.appendChild(assetCard);
            });
        } catch (error) {
            console.error('Error loading assets:', error);
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showProcessingStatus();
                this.showNotification('File uploaded successfully!', 'success');
            } else {
                this.showNotification(result.error || 'Upload failed', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification('Upload failed. Please try again.', 'error');
        }
    }

    async processAsset(filename) {
        try {
            const response = await fetch(`/process_asset/${filename}`);
            const result = await response.json();
            
            if (response.ok) {
                this.showProcessingStatus();
                this.showNotification(`Processing ${filename}...`, 'info');
            } else {
                this.showNotification(result.error || 'Processing failed', 'error');
            }
        } catch (error) {
            console.error('Processing error:', error);
            this.showNotification('Processing failed. Please try again.', 'error');
        }
    }

    async pollStatus() {
        try {
            const response = await fetch('/status');
            const status = await response.json();
            
            this.updateProcessingStatus(status);
            
            if (status.status === 'processing') {
                setTimeout(() => this.pollStatus(), 1000);
            } else if (status.status === 'completed') {
                this.showResults(status);
                this.hideProcessingStatus();
            } else if (status.status === 'error') {
                this.showNotification(status.message, 'error');
                this.hideProcessingStatus();
            }
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }

    updateProcessingStatus(status) {
        const progressBar = document.getElementById('progressBar');
        const statusMessage = document.getElementById('statusMessage');
        
        if (progressBar && statusMessage) {
            progressBar.style.width = status.progress + '%';
            statusMessage.textContent = status.message;
        }
    }

    showProcessingStatus() {
        document.getElementById('processingSection').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
        
        // Reset progress bar
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('statusMessage').textContent = 'Initializing...';
        
        // Start polling
        this.pollStatus();
    }

    hideProcessingStatus() {
        document.getElementById('processingSection').style.display = 'none';
    }

    showResults(status) {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'block';
        
        // Update data summary
        document.getElementById('dataPoints').textContent = status.data_points || 0;
        
        // Update download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (status.csv_file) {
            downloadBtn.href = `/download/${status.csv_file}`;
            downloadBtn.style.display = 'inline-block';
        }
        
        // Display tracking video
        this.displayTrackingVideo(status.plots?.tracking_video);
        
        // Display plots (excluding tracking video)
        const plotsWithoutVideo = { ...status.plots };
        delete plotsWithoutVideo.tracking_video;
        this.displayPlots(plotsWithoutVideo);
        
        this.showNotification('Analysis completed successfully!', 'success');
    }

    displayTrackingVideo(videoPath) {
        const videoContainer = document.getElementById('trackingVideoContainer');
        const noVideoDiv = document.getElementById('noTrackingVideo');
        const videoElement = document.getElementById('trackingVideo');
        
        if (videoPath) {
            videoElement.src = `/${videoPath}`;
            videoElement.load(); // Force reload of the video
            videoContainer.style.display = 'block';
            noVideoDiv.style.display = 'none';
            
            console.log('🎥 Setting tracking video source:', `/${videoPath}`);
            
            // Add event listener for video load
            videoElement.addEventListener('loadeddata', () => {
                console.log('Tracking video loaded successfully');
            });
            
            // Add event listener for video error
            videoElement.addEventListener('error', () => {
                console.error('Error loading tracking video');
                videoContainer.style.display = 'none';
                noVideoDiv.style.display = 'block';
            });
        } else {
            videoContainer.style.display = 'none';
            noVideoDiv.style.display = 'block';
        }
    }

    displayPlots(plots) {
        const plotGallery = document.getElementById('plotGallery');
        plotGallery.innerHTML = '';
        
        Object.entries(plots).forEach(([name, path]) => {
            const plotDiv = document.createElement('div');
            plotDiv.className = 'col-md-4 mb-3';
            plotDiv.innerHTML = `
                <div class="card">
                    <img src="/${path}" class="plot-image" alt="${name}">
                    <div class="card-body p-2">
                        <h6 class="card-title text-capitalize">${name}</h6>
                    </div>
                </div>
            `;
            plotGallery.appendChild(plotDiv);
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Utility functions
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
}

function scrollToFeatures() {
    document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.impulseCV = new ImpulseCV();
});

// Add some interactive animations
document.addEventListener('DOMContentLoaded', () => {
    // Animate feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Observe stat cards
    document.querySelectorAll('.stat-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
