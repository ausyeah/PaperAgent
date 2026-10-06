const API_BASE = 'http://localhost:8000/api/paper';
        let currentPaper = null;

        function showLoader(show) {
            document.getElementById('mainLoader').style.display = show ? 'inline-block' : 'none';
        }

        function switchTab(tabId, element) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            element.classList.add('active');
            document.getElementById(tabId).classList.add('active');

            // Re-initialize/run Mermaid when Architecture tab is displayed
            if (tabId === 'tab-architecture' && window.mermaid) {
                mermaid.init(undefined, document.querySelectorAll('.mermaid'));
            }
        }

        async function parsePaper() {
            const source = document.getElementById('sourceInput').value;
            if (!source) {
                alert("Please enter a source.");
                return;
            }

            showLoader(true);
            try {
                const formData = new FormData();
                formData.append('source', source);

                const response = await fetch(`${API_BASE}/parse`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Parse failed");

                currentPaper = await response.json();
                renderPaper(currentPaper);

                document.getElementById('btnAnalyze').disabled = false;
                document.getElementById('btnSynthesize').disabled = false;
                document.getElementById('btnExportMd').disabled = false;
                document.getElementById('btnExportNb').disabled = false;
                document.getElementById('btnExportLatex').disabled = false;
            } catch (err) {
                alert("Error: " + err.message);
            } finally {
                showLoader(false);
            }
        }

        function renderPaper(paper) {
            const html = `
                <h1 class="paper-title">${paper.metadata.title}</h1>
                <div class="paper-authors">${paper.metadata.authors.join(', ')}</div>
                <div class="paper-abstract"><strong>Abstract:</strong><br>${paper.metadata.abstract}</div>

                <details class="section-nav" open>
                    <summary>Sections</summary>
                    <ul>
                        ${paper.sections.map(s => `<li>${s.title}</li>`).join('')}
                    </ul>
                </details>
            `;
            document.getElementById('paperContent').innerHTML = html;
        }

        async function analyzePaper() {
            if (!currentPaper) return;

            showLoader(true);
            try {
                const response = await fetch(`${API_BASE}/analyze`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentPaper)
                });

                if (!response.ok) throw new Error("Analysis failed");

                const report = await response.json();
                renderAnalysis(report);
                renderFormulas(report);
            } catch (err) {
                alert("Error: " + err.message);
            } finally {
                showLoader(false);
            }
        }

        function renderAnalysis(report) {
            const scoreColor = report.reviewer_critique.score >= 7 ? 'var(--success)' :
                               report.reviewer_critique.score >= 4 ? 'var(--warning)' : 'var(--danger)';

            const html = `
                <h3>Executive Brief</h3>
                <p><strong>Summary:</strong> ${report.executive_summary}</p>
                <p><strong>Core Problem:</strong> ${report.core_problem}</p>
                <p><strong>Innovation:</strong> ${report.key_innovation}</p>

                <hr style="margin: 1.5rem 0; border: 0; border-top: 1px solid var(--border-color);">

                <h3>Reviewer Critique</h3>
                <div class="score-badge" style="background-color: ${scoreColor}">Score: ${report.reviewer_critique.score}/10</div>

                <div class="critique-section">
                    <h4>Strengths</h4>
                    <ul>${report.reviewer_critique.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
                </div>
                <div class="critique-section">
                    <h4>Weaknesses</h4>
                    <ul>${report.reviewer_critique.weaknesses.map(s => `<li>${s}</li>`).join('')}</ul>
                </div>
            `;
            document.getElementById('analysisContent').innerHTML = html;

            // Render OpenReview Report
            const openReviewHtml = `
                <div class="badge-container">
                    <span class="badge">Overall <span class="badge-score">${report.reviewer_critique.score}/10</span></span>
                    <span class="badge">Soundness <span class="badge-score">8/10</span></span>
                    <span class="badge">Presentation <span class="badge-score">7/10</span></span>
                    <span class="badge">Contribution <span class="badge-score">9/10</span></span>
                </div>
                <div class="critique-section">
                    <h4>Strengths</h4>
                    <ul>${report.reviewer_critique.strengths.map(s => `<li>${s}</li>`).join('')}</ul>
                </div>
                <div class="critique-section">
                    <h4>Weaknesses</h4>
                    <ul>${report.reviewer_critique.weaknesses.map(s => `<li>${s}</li>`).join('')}</ul>
                </div>
                <div class="critique-section">
                    <h4>Questions for Rebuttal</h4>
                    <ul>
                        ${report.reviewer_critique.boundary_conditions ? report.reviewer_critique.boundary_conditions.map(b => `<li>How does the model handle: ${b}?</li>`).join('') : '<li>No specific questions raised.</li>'}
                    </ul>
                </div>
            `;
            document.getElementById('openreviewContent').innerHTML = openReviewHtml;

            switchTab('tab-analysis', document.querySelector('.tabs .tab:nth-child(1)'));
        }

        function renderFormulas(report) {
            if (!report.formula_explanations.length) {
                document.getElementById('formulaContent').innerHTML = '<p>No formulas extracted.</p>';
                document.getElementById('formulaGalleryContent').innerHTML = '<p style="color: var(--text-muted); text-align: center; margin-top: 2rem;">No formulas found.</p>';
                return;
            }

            const galleryHtml = report.formula_explanations.map(f => `
                <div style="margin-bottom: 1rem; padding: 0.75rem; background: #f8fafc; border: 1px solid var(--border-color); border-radius: 0.375rem;">
                    <code style="display: block; text-align: center; font-size: 1.1rem; color: var(--primary);">${f.latex}</code>
                </div>
            `).join('');
            document.getElementById('formulaGalleryContent').innerHTML = galleryHtml;

            const html = report.formula_explanations.map(f => `
                <div style="margin-bottom: 2rem; padding: 1rem; border: 1px solid var(--border-color); border-radius: 0.375rem;">
                    <code>${f.latex}</code>
                    <h4 style="margin-top: 1rem;">Intuition</h4>
                    <p>${f.intuitive_intuition}</p>
                    <h4 style="margin-top: 1rem;">Glossary</h4>
                    <ul>
                        ${Object.entries(f.variable_glossary).map(([k,v]) => `<li><strong>${k}</strong>: ${v}</li>`).join('')}
                    </ul>
                </div>
            `).join('');
            document.getElementById('formulaContent').innerHTML = html;
        }

        async function synthesizeCode() {
            if (!currentPaper) return;

            showLoader(true);
            try {
                const response = await fetch(`${API_BASE}/synthesize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(currentPaper)
                });

                if (!response.ok) throw new Error("Synthesis failed");

                const result = await response.json();

                // Combine target code and test code for editor
                const fullCode = result.target_module_code + "\n\n" + result.test_suite_code + "\n\n" + (result.toy_benchmark_code || '');
                document.getElementById('codeEditor').value = fullCode;
                document.getElementById('btnRunCode').disabled = false;

                switchTab('tab-code', document.querySelector('.tabs .tab:nth-child(4)'));
            } catch (err) {
                alert("Error: " + err.message);
            } finally {
                showLoader(false);
            }
        }

        async function runCode() {
            const code = document.getElementById('codeEditor').value;
            if (!code) return;

            const consoleOut = document.getElementById('consoleOutput');
            consoleOut.textContent = "Executing...\n";
            document.getElementById('btnRunCode').disabled = true;

            try {
                const response = await fetch(`${API_BASE}/execute`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });

                if (!response.ok) throw new Error("Execution request failed");

                const result = await response.json();

                let output = `[Exit Code: ${result.exit_code}] [Time: ${result.execution_time_seconds.toFixed(2)}s]\n`;
                if (result.stdout) output += `\nSTDOUT:\n${result.stdout}`;
                if (result.stderr) output += `\nSTDERR:\n${result.stderr}`;

                consoleOut.textContent = output;
                consoleOut.style.color = result.success ? '#0f0' : '#f00';

            } catch (err) {
                consoleOut.textContent = "Error: " + err.message;
                consoleOut.style.color = '#f00';
            } finally {
                document.getElementById('btnRunCode').disabled = false;
            }
        }

// Library Drawer Logic
function toggleLibrary() {
    const drawer = document.getElementById('library-drawer');
    drawer.classList.toggle('open');
}


// Export Logic
function exportMarkdown() {
    window.location.href = `${API_BASE}/export/markdown`;
}
function exportNotebook() {
    window.location.href = `${API_BASE}/export/notebook`;
}
function exportLatex() {
    // Placeholder logic for LaTeX export as it might not be implemented in backend yet
    alert("Export LaTeX Bundle (.zip) - Endpoint coming soon!");
}

// Configure Mermaid to not start on load, since it will be handled by tab switch
if (window.mermaid) {
    mermaid.initialize({ startOnLoad: false, theme: 'default' });
}
