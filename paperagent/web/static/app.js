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

function renderCommitteeReview(committeeData) {
    if (!committeeData || !committeeData.reviews) {
        document.getElementById('committeeContent').innerHTML = '<p>No committee review available.</p>';
        return;
    }
    const decisionColor = committeeData.final_decision.includes('Accept') ? 'var(--success)' : 'var(--danger)';
    let html = `
        <div style="background: #f1f5f9; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border-left: 4px solid ${decisionColor};">
            <h3 style="margin-top: 0;">Area Chair Meta-Review</h3>
            <div style="font-weight: bold; margin-bottom: 0.5rem; color: ${decisionColor};">Decision: ${committeeData.final_decision}</div>
            <p>${committeeData.meta_review}</p>
        </div>
        <h3>Reviewer Committee Evals</h3>
    `;
    committeeData.reviews.forEach(r => {
        html += `
            <div style="margin-bottom: 1.25rem; padding: 1rem; border: 1px solid var(--border-color); border-radius: 0.375rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong>${r.persona} (${r.reviewer_id})</strong>
                    <span class="badge" style="background: var(--primary); color: white;">Score: ${r.score}/10</span>
                </div>
                <p>${r.detailed_critique}</p>
                ${r.strengths.length ? `<div style="color: var(--success);"><strong>+ Strengths:</strong> ${r.strengths.join('; ')}</div>` : ''}
                ${r.weaknesses.length ? `<div style="color: var(--danger); margin-top: 0.25rem;"><strong>- Weaknesses:</strong> ${r.weaknesses.join('; ')}</div>` : ''}
            </div>
        `;
    });
    document.getElementById('committeeContent').innerHTML = html;
}

function renderScorecard(scorecardData) {
    if (!scorecardData) {
        document.getElementById('scorecardContent').innerHTML = '<p>No scorecard available.</p>';
        return;
    }
    let html = `
        <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1.5rem;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;">
                ${scorecardData.score}/100
            </div>
            <div>
                <h3 style="margin: 0;">Reproducibility Scorecard</h3>
                <div style="color: var(--text-muted);">${scorecardData.verdict_level}</div>
            </div>
        </div>
        <h4>Criteria Checklist</h4>
        <ul style="list-style: none; padding-left: 0;">
    `;
    if (scorecardData.criteria_checklist) {
        Object.entries(scorecardData.criteria_checklist).forEach(([k, v]) => {
            const icon = v ? '<span style="color: green; font-weight: bold;">[PASS]</span>' : '<span style="color: red; font-weight: bold;">[FAIL]</span>';
            html += `<li style="padding: 0.25rem 0; border-bottom: 1px solid #f1f5f9;">${icon} ${k}</li>`;
        });
    }
    html += '</ul>';
    if (scorecardData.improvement_recommendations && scorecardData.improvement_recommendations.length) {
        html += `
            <h4 style="margin-top: 1rem;">Actionable Recommendations</h4>
            <ul>
                ${scorecardData.improvement_recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
    }
    document.getElementById('scorecardContent').innerHTML = html;
}

function renderPodcast(podcastData) {
    if (!podcastData || !podcastData.turns) {
        document.getElementById('podcastContent').innerHTML = '<p>No podcast dialogue available.</p>';
        return;
    }
    let html = `
        <h3>Episode: ${podcastData.episode_title}</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Total Duration: ~${podcastData.total_duration_minutes || 5} min</p>
        <div style="display: flex; flex-direction: column; gap: 1rem;">
    `;
    podcastData.turns.forEach(turn => {
        const isA = turn.speaker.includes('Host A') || turn.speaker.includes('Alex');
        const bg = isA ? '#eff6ff' : '#f8fafc';
        const border = isA ? '#bfdbfe' : '#e2e8f0';
        html += `
            <div style="background: ${bg}; border: 1px solid ${border}; border-radius: 0.5rem; padding: 0.75rem 1rem;">
                <div style="font-weight: bold; font-size: 0.85rem; color: var(--primary); margin-bottom: 0.25rem;">${turn.speaker} (${turn.tone})</div>
                <div>${turn.speech}</div>
            </div>
        `;
    });
    html += '</div>';
    document.getElementById('podcastContent').innerHTML = html;
}

