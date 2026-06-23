document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('resume-file');
    const fileDropArea = document.getElementById('file-drop-area');
    const fileMsg = document.getElementById('file-msg');
    const jobDescription = document.getElementById('job-description');
    const scanBtn = document.getElementById('scan-btn');
    const btnText = scanBtn.querySelector('.btn-text');
    const loader = scanBtn.querySelector('.loader');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');

    let selectedFile = null;

    // File Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileDropArea.addEventListener(eventName, () => fileDropArea.classList.remove('dragover'), false);
    });

    fileDropArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        handleFiles({ target: { files: dt.files } });
    }

    function handleFiles(e) {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            fileMsg.textContent = selectedFile.name;
        }
    }

    // Submit Action
    scanBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            showError("Please upload a resume file.");
            return;
        }
        if (!jobDescription.value.trim()) {
            showError("Please enter a job description.");
            return;
        }

        // UI State
        errorMessage.classList.add('hidden');
        resultsSection.classList.add('hidden');
        scanBtn.disabled = true;
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');

        const formData = new FormData();
        formData.append('resume', selectedFile);
        formData.append('job_description', jobDescription.value);

        try {
            const response = await fetch('/scan', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to scan resume.');
            }

            const data = await response.json();
            renderResults(data);
        } catch (error) {
            showError(error.message);
        } finally {
            scanBtn.disabled = false;
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
        }
    });

    function renderResults(data) {
        resultsSection.classList.remove('hidden');

        // Animate Counters
        animateValue("val-overall", 0, data.overall_fit || 0, 1500);
        animateValue("val-skills", 0, data.skills_match || 0, 1500);
        animateValue("val-exp", 0, data.experience_match || 0, 1500);
        animateValue("val-keywords", 0, data.keyword_score || 0, 1500);

        // Skills
        const skillsContainer = document.getElementById('skills-container');
        skillsContainer.innerHTML = '';
        (data.skill_breakdown || []).forEach(skill => {
            const html = `
                <div class="skill-row">
                    <div class="skill-labels"><span>${skill.skill}</span><span>${skill.score}%</span></div>
                    <div class="progress-bg"><div class="progress-fill" style="width: 0%"></div></div>
                </div>
            `;
            skillsContainer.insertAdjacentHTML('beforeend', html);
        });

        // Trigger progress bar animation after a tiny delay
        setTimeout(() => {
            const fills = skillsContainer.querySelectorAll('.progress-fill');
            (data.skill_breakdown || []).forEach((skill, idx) => {
                if(fills[idx]) fills[idx].style.width = `${skill.score}%`;
            });
        }, 50);

        // Keywords
        const keywordsContainer = document.getElementById('keywords-container');
        keywordsContainer.innerHTML = '';
        (data.keywords || []).forEach((kw, i) => {
            const icon = kw.status === 'matched' ? '✓' : kw.status === 'partial' ? '−' : '✗';
            const html = `<div class="pill ${kw.status}" style="animation-delay: ${i * 0.05}s"><span>${icon}</span>${kw.word}</div>`;
            keywordsContainer.insertAdjacentHTML('beforeend', html);
        });

        // Recommendation
        document.getElementById('recommendation-text').textContent = data.recommendation || 'No recommendation provided.';
        
        // Scroll to results smoothly
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function animateValue(id, start, end, duration) {
        const obj = document.getElementById(id);
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        errorMessage.classList.remove('hidden');
    }
});
