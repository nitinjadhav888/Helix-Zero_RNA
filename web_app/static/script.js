$(document).ready(function() {
    console.log("Helix-Zero V8 :: jQuery Initialized — All Modules Active");

    // Global store for the latest candidates to populate modals
    let latestCandidates = [];
    let nonTargetSeq = "";
    let uploadedTargetSeq = "";  // Stores uploaded target file content separately
    let uploadedTargetName = "";

    // ── File Upload Handlers ─────────────────────────────────────────────
    $('#targetFile').on('change', function(e) {
        const file = e.target.files[0];
        if(!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) { 
            const raw = ev.target.result;
            uploadedTargetSeq = parseFasta(raw);
            uploadedTargetName = file.name;
            $('#targetGenome').val(raw).css('border-color', '#0dcaf0');
            // Show feedback
            const info = `✅ Target loaded from file: "${file.name}" (${uploadedTargetSeq.length.toLocaleString()} bp) — this will be used when you run the pipeline`;
            $('#targetFileStatus').remove();
            $(e.target).after(`<div id="targetFileStatus" class="small text-success mt-1"><i class="fa-solid fa-check-circle"></i> ${info}</div>`);
        };
        reader.readAsText(file);
    });

    $('#nonTargetFile').on('change', function(e) {
        const file = e.target.files[0];
        if(!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) { 
            nonTargetSeq = parseFasta(ev.target.result);
            // Show feedback
            const info = `✅ Non-target loaded: "${file.name}" (${nonTargetSeq.length.toLocaleString()} bp) — Bloom filter will auto-build on pipeline run`;
            $('#nonTargetFileStatus').remove();
            $(e.target).after(`<div id="nonTargetFileStatus" class="small text-success mt-1"><i class="fa-solid fa-shield-check"></i> ${info}</div>`);
            $('#bloomStatusBadge').removeClass('bg-secondary bg-success').addClass('bg-info').text('Ready');
        };
        reader.readAsText(file);
    });

    // ── Load Demo Non-Target Handler ─────────────────────────────────────
    $('#loadDemoNonTarget').on('click', function() {
        if (window.demoNonTargetSeq) {
            nonTargetSeq = window.demoNonTargetSeq;
            const info = `✅ Demo Non-Target loaded (Honeybee actin gene - ${nonTargetSeq.length} bp)`;
            $('#nonTargetFileStatus').remove();
            $(this).after(`<div id="nonTargetFileStatus" class="small text-success mt-1"><i class="fa-solid fa-shield-check"></i> ${info}</div>`);
            $('#bloomStatusBadge').removeClass('bg-secondary').addClass('bg-warning').text('Demo Ready');
            alert('Demo Non-Target Genome Loaded!\n\nThis simulates a honeybee (Apis mellifera) partial genome.\nSome siRNA candidates will match and show reduced safety scores.');
        }
    });

    // ── Bloom Filter Build Handler ───────────────────────────────────────
    $('#buildBloomBtn').on('click', function() {
        if (!nonTargetSeq || nonTargetSeq.length < 100) {
            alert('Please upload a non-target genome first (minimum 100bp).');
            return;
        }
        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Building Bloom Index...');
        $.ajax({
            url: '/api/bloom/build', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ genome: nonTargetSeq }),
            success: function(r) {
                const s = r.stats;
                btn.prop('disabled', false).html('<i class="fa-solid fa-filter"></i> Bloom Index <span class="badge bg-success ms-1">Active</span>');
                $('#bloomStatusBadge').removeClass('bg-secondary').addClass('bg-success').text(
                    `${s.totalKmersIndexed.toLocaleString()} k-mers | ${s.totalMemoryMB}MB`
                );
                alert(`Bloom Index built! ${s.totalKmersIndexed.toLocaleString()} k-mers indexed across k=${s.kmerSizes.join(',')}.\nMemory: ${s.totalMemoryMB}MB (vs ${s.genomeSizeMB}MB raw genome).\nCompression: ${s.compressionRatio}×`);
            },
            error: function(xhr) {
                btn.prop('disabled', false).html('<i class="fa-solid fa-filter"></i> Build Bloom Index <span class="badge bg-danger ms-1">Failed</span>');
                alert('Bloom Index build failed: ' + (xhr.responseJSON?.error || 'Unknown error'));
            }
        });
    });

    // ── Gene Autocomplete ────────────────────────────────────────────────
    $.ajax({
        url: '/api/essentiality/genes', type: 'GET',
        success: function(r) {
            const list = $('#geneList');
            (r.genes || []).forEach(g => list.append(`<option value="${g}">`));
        }
    });

    function parseFasta(fasta) {
        if (!fasta) return '';
        const lines = fasta.split('\n');
        let sequence = '';
        for (let line of lines) {
            line = line.trim();
            if (line.startsWith('>')) continue;
            sequence += line.toUpperCase().replace(/[^ATCGU]/g, '');
        }
        return sequence;
    }

    // ── Badge Helpers ────────────────────────────────────────────────────
    const passBadge = '<span class="badge bg-success w-100 py-1"><i class="fa-solid fa-check"></i> PASS</span>';
    const failBadge = '<span class="badge bg-danger w-100 py-1"><i class="fa-solid fa-xmark"></i> FAIL</span>';
    const warnBadge = '<span class="badge bg-warning text-dark w-100 py-1"><i class="fa-solid fa-triangle-exclamation"></i> WARN</span>';

    // ── Certificate Modal Population ─────────────────────────────────────
    window.openCertificate = function(index) {
        const cand = latestCandidates[index];
        if(!cand) return;

        // Header Mapping
        $('#certHash').text(cand.auditHash || `V7-DL-${Math.floor(Math.random()*10000)}`);
        const today = new Date();
        const nextYear = new Date(); nextYear.setFullYear(today.getFullYear() + 1);
        $('#certDate').text(today.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }));
        $('#certValid').text(nextYear.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }));

        let score = cand.safetyScore || 0;
        const isSafe = score > 85;

        // Stamp and Status Badge
        if (isSafe) {
            $('#certStatusBadge').removeClass('bg-danger').addClass('bg-success').text('CLEARED');
            $('#certStamp').removeClass('border-danger text-danger').addClass('border-success text-success').html('<span class="fw-bold" style="font-size: 0.7rem; letter-spacing: 1px;">VERIFIED</span><i class="fa-solid fa-check fs-4"></i><span class="fw-bold" style="font-size: 0.7rem; letter-spacing: 1px;">SAFE</span>');
        } else {
            $('#certStatusBadge').removeClass('bg-success').addClass('bg-danger').text('REJECTED');
            $('#certStamp').removeClass('border-success text-success').addClass('border-danger text-danger').html('<span class="fw-bold" style="font-size: 0.7rem; letter-spacing: 1px;">REJECTED</span><i class="fa-solid fa-xmark fs-4"></i><span class="fw-bold" style="font-size: 0.7rem; letter-spacing: 1px;">TOXIC</span>');
        }

        // Section 1: Molecular Specification
        $('#certSeq').text(cand.sequence);
        $('#certPos').text(cand.position || 'N/A');
        $('#certGC').text(cand.gcContent + '%');
        $('#certEff').text(cand.efficiency ? cand.efficiency.toFixed(1) + '%' : 'N/A');
        $('#certMFE').text(cand.mfe !== undefined ? cand.mfe + ' kcal/mol' : 'N/A');
        $('#certAsymmetry').text(cand.asymmetry !== undefined ? cand.asymmetry + ' kcal/mol' : 'N/A');
        $('#certEndStability').text(cand.endStability ? `(${cand.endStability})` : '');

        // Section 2: Homology Exclusion
        const matchLen = cand.matchLength || 0;
        const margin = 15 - matchLen;
        $('#certHomology').text(matchLen);
        $('#certMargin').text(margin);
        $('#certStatusExclusion').html(matchLen < 15 ? passBadge : failBadge);
        $('#certStatusMargin').html(margin > 0 ? passBadge : failBadge);

        // Section 3: 9-Layer Safety Analysis
        $('#certScore').text(score.toFixed(1) + '%').css('color', isSafe ? '#00b341' : '#dc3545');
        $('#certProgressBar .progress-bar').css('width', score + '%').removeClass('bg-success bg-danger bg-warning').addClass(isSafe ? 'bg-success' : 'bg-danger');

        // L1: 15-mer Exclusion
        $('#certL1Badge').html(matchLen < 15 ? passBadge : failBadge);
        $('#certL1Details').text(matchLen < 15 ? 'No toxic match detected' : `CRITICAL: Match of ${matchLen}bp exceeds threshold`);

        // L2: Full 21-nt Identity
        const full21 = cand.full21ntMatch || false;
        $('#certL2Badge').html(!full21 ? passBadge : failBadge);
        $('#certL2Details').text(!full21 ? 'No full-length 21-nt identity match' : 'FATAL: Exact 21-nt match in non-target');

        // L3: Seed Region
        if (cand.hasSeedMatch) {
            $('#certL3Badge').html(warnBadge);
            $('#certL3Details').text(`Seed: ${cand.seedSequence} (${cand.seedMatchCount} hits in non-target)`);
        } else {
            $('#certL3Badge').html(passBadge);
            $('#certL3Details').text(`Seed: ${cand.seedSequence || 'N/A'} — No off-target`);
        }

        // L4: Palindrome
        if (cand.hasPalindrome) {
            $('#certL4Badge').html(failBadge);
            $('#certL4Details').text(`Palindrome detected (${cand.palindromeLength}bp), hairpin risk`);
        } else {
            $('#certL4Badge').html(passBadge);
            $('#certL4Details').text('No significant palindromes');
        }

        // L5: CpG
        $('#certL5Badge').html(cand.hasCpGMotif ? warnBadge : passBadge);
        $('#certL5Details').text(cand.hasCpGMotif ? 'CpG dinucleotide detected — TLR9 risk' : 'No CpG motifs');

        // L6: Poly-run
        $('#certL6Badge').html(cand.hasPolyRun ? warnBadge : passBadge);
        $('#certL6Details').text(cand.hasPolyRun ? 'Poly-run detected — synthesis difficulty' : 'No poly-runs');

        // L7: Extended Immune Motifs
        const immuneHits = cand.immuneMotifs || [];
        if (immuneHits.length > 0) {
            const motifStr = immuneHits.map(m => `${m.motif}(×${m.count})`).join(', ');
            $('#certL7Badge').html(warnBadge);
            $('#certL7Details').text(`Motifs found: ${motifStr}`);
        } else {
            $('#certL7Badge').html(passBadge);
            $('#certL7Details').text('No extended immune motifs');
        }

        // L8: Entropy
        const entropy = cand.shannonEntropy || 2.0;
        $('#certL8Badge').html(entropy < 1.5 ? warnBadge : passBadge);
        $('#certL8Details').text(`Shannon entropy: ${entropy} bits` + (entropy < 1.5 ? ' — low complexity!' : ' — normal'));

        // L9: AT-Repeats
        $('#certL9Badge').html(cand.hasATRepeat ? warnBadge : passBadge);
        $('#certL9Details').text(cand.hasATRepeat ? 'AT-dinucleotide repeat detected' : 'No AT-repeats');

        // ── Chemical Modification (Section 4) ────────────────────────────
        const chemMod = $('#chemMod').val();
        if (chemMod && chemMod !== 'none') {
            $('#certChemSection').show();
            $.ajax({
                url: '/api/chem_modify',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ sequence: cand.sequence, modType: chemMod }),
                success: function(r) {
                    $('#certHalfLife').text(r.stabilityHalfLife + 'h');
                    $('#certAgo2').text(r.ago2Affinity + '%');
                    $('#certTherapeutic').text(r.therapeuticIndex + '/100');
                    $('#certChemWarnings').html(r.warnings.map(w => `<div class="mb-1"><i class="fa-solid fa-circle-info text-primary"></i> ${w}</div>`).join(''));
                },
                error: function() {
                    $('#certHalfLife').text('Error');
                }
            });
        } else {
            $('#certChemSection').hide();
        }

        // ── Essentiality (Section 5) ─────────────────────────────────────
        const geneName = $('#geneName').val();
        if (geneName && geneName.trim() !== '') {
            $('#certEssentialSection').show();
            $.ajax({
                url: '/api/essentiality', type: 'POST', contentType: 'application/json',
                data: JSON.stringify({ geneName: geneName.trim() }),
                success: function(r) {
                    $('#certGeneName').text(r.geneName);
                    $('#certEssenScore').text(r.essentialityScore + '/100');
                    $('#certEssenClass').text(r.classification);
                    const prioColors = { 'CRITICAL TARGET': 'text-danger', 'HIGH PRIORITY': 'text-warning', 'MODERATE': 'text-info', 'LOW': 'text-secondary', 'NOT RECOMMENDED': 'text-muted' };
                    $('#certEssenPriority').attr('class', 'fw-bold fs-6 ' + (prioColors[r.priority] || '')).text(r.priority);
                    $('#certEssenDEG').text('+' + r.breakdown.deg);
                    $('#certEssenOGEE').text('+' + r.breakdown.ogee);
                    $('#certEssenRNAI').text('+' + r.breakdown.rnai);
                    $('#certEssenCons').text('+' + r.breakdown.conservation);
                    $('#certEssenEvidence').html(r.evidence.map(e => `<div class="mb-1"><i class="fa-solid fa-circle-check text-success"></i> ${e}</div>`).join(''));
                },
                error: function() {
                    $('#certEssenScore').text('Error');
                }
            });
        } else {
            $('#certEssentialSection').hide();
        }

        // ── RAG Handler ──────────────────────────────────────────────────
        $('#ragOutput').hide().text('');
        $('#askRagBtn').show().prop('disabled', false).html('Synthesize Report <i class="fa-solid fa-wand-magic-sparkles"></i>')
            .off('click').on('click', function() {
                const btn = $(this);
                btn.html('<i class="fas fa-atom fa-spin"></i> Retrieving & Generating...').prop('disabled', true);
                $.ajax({
                    url: '/api/rag', type: 'POST', contentType: 'application/json',
                    data: JSON.stringify(cand),
                    success: function(resp) { btn.hide(); $('#ragOutput').fadeIn().text(resp.explanation); },
                    error: function() { btn.html('Error').prop('disabled', false); $('#ragOutput').fadeIn().text("Agentic AI is currently offline."); }
                });
        });

        // ── SQL Save Handler ─────────────────────────────────────────────
        $('#saveSqlBtn').removeClass('btn-success btn-danger').addClass('btn-dark')
            .prop('disabled', false).html('<i class="fa-solid fa-database text-success"></i> Save to SQL Archive')
            .off('click').on('click', function() {
            const btn = $(this);
            btn.html('<i class="fas fa-spinner fa-spin"></i> Saving...').prop('disabled', true);
            $.ajax({
                url: '/api/save_sequence', type: 'POST', contentType: 'application/json',
                data: JSON.stringify(cand),
                success: function(resp) { btn.removeClass('btn-dark').addClass('btn-success').html('<i class="fa-solid fa-check"></i> ' + resp.message); },
                error: function(xhr) { btn.removeClass('btn-dark').addClass('btn-danger').html('<i class="fa-solid fa-triangle-exclamation"></i> SQL Error'); }
            });
        });

        new bootstrap.Modal(document.getElementById('certModal')).show();
    };

    // ── SQL History Loader ───────────────────────────────────────────────
    document.getElementById('historyModal').addEventListener('show.bs.modal', function () {
        const tbody = $('#historyTable tbody');
        tbody.html('<tr><td colspan="6" class="text-center py-4"><i class="fas fa-spinner fa-spin fa-2x text-info"></i></td></tr>');
        $.ajax({
            url: '/api/history', type: 'GET',
            success: function(response) {
                tbody.empty();
                const logs = response.history || [];
                if(logs.length === 0) { tbody.html('<tr><td colspan="6" class="text-center py-4 text-secondary">No sequences saved to Database yet.</td></tr>'); return; }
                logs.forEach(log => {
                    const badgeClass = log.safety_score > 85 ? 'bg-success' : 'bg-danger';
                    const risksStr = log.risk_factors ? log.risk_factors.replace(/,/g, '<br>') : 'None';
                    tbody.append(`<tr>
                        <td class="ps-4 fw-bold text-secondary">#${log.audit_hash}</td>
                        <td class="font-monospace text-info">${log.sequence}</td>
                        <td class="text-warning">${log.efficacy.toFixed(1)}%</td>
                        <td><span class="badge ${badgeClass}">${log.safety_score.toFixed(1)}%</span></td>
                        <td class="small text-muted">${risksStr}</td>
                        <td class="small opacity-50">${new Date(log.timestamp).toLocaleString()}</td>
                    </tr>`);
                });
            },
            error: function() { tbody.html('<tr><td colspan="6" class="text-center py-4 text-danger">Failed to connect to Enterprise Data Warehouse.</td></tr>'); }
        });
    });

    function renderTableRow(idx, cand, isLegacy) {
        const eff = cand.efficiency || 0;
        let effBadge = eff > 90 ? 'bg-success' : eff > 75 ? 'bg-primary' : 'bg-warning text-dark';
        
        const therm = cand.foldRisk || 0;
        let thermBadge = therm > 50 ? 'bg-danger' : therm > 30 ? 'bg-warning text-dark' : 'bg-success';

        let safetyBadge = 'bg-secondary';
        let safetyText = 'N/A';
        if (cand.safetyScore !== undefined) {
            safetyBadge = cand.safetyScore > 85 ? 'bg-success' : 'bg-danger';
            safetyText = cand.safetyScore.toFixed(1) + '%';
        }

        // Essentiality
        const esScore = cand.essentialityScore || 0;
        let esBadge = esScore >= 75 ? 'bg-danger' : esScore >= 50 ? 'bg-warning text-dark' : 'bg-secondary';
        let esText = esScore > 0 ? esScore.toFixed(0) : '—';

        // Composite
        const compScore = cand.compositeScore || 0;
        let compBadge = compScore >= 80 ? 'bg-success' : compScore >= 60 ? 'bg-info' : 'bg-secondary';

        const certBtn = `<button class="btn btn-sm btn-outline-info w-100" onclick="openCertificate(${idx})"><i class="fa-solid fa-certificate"></i> Cert</button>`;

        return `
            <tr>
                <td class="ps-4 fw-bold">#${idx + 1}</td>
                <td class="font-monospace text-secondary">${cand.position}</td>
                <td class="font-monospace text-info">${cand.sequence}</td>
                <td>${cand.gcContent || 'N/A'}%</td>
                <td><span class="badge ${effBadge}">${eff.toFixed(1)}%</span></td>
                <td><span class="badge ${safetyBadge}">${safetyText}</span></td>
                <td><span class="badge ${esBadge}">${esText}</span></td>
                <td><span class="badge ${compBadge} fw-bold">${compScore.toFixed(1)}</span></td>
                <td>${certBtn}</td>
            </tr>
        `;
    }

    // ── Main Pipeline Submit ─────────────────────────────────────────────
    $('#pipeline-form').on('submit', function(e) {
        e.preventDefault();
        
        // Priority: uploaded file > textarea content
        let sequence = '';
        if (uploadedTargetSeq && uploadedTargetSeq.length > 0) {
            sequence = uploadedTargetSeq;
            console.log(`[Pipeline] Using UPLOADED file: "${uploadedTargetName}" (${sequence.length} bp)`);
        } else {
            const rawFasta = $('#targetGenome').val();
            if (!rawFasta || rawFasta.trim() === '') {
                alert("Please upload a Target Genome file or paste a FASTA sequence.");
                return;
            }
            sequence = parseFasta(rawFasta);
            console.log(`[Pipeline] Using PASTED textarea sequence (${sequence.length} bp)`);
        }
        
        if (sequence.length < 21) {
            alert(`Sequence too short (${sequence.length} bp). Minimum is 21bp.`);
            return;
        }

        const mlMode = $('#mlMode').val();
        const isLegacy = mlMode === 'legacy';
        
        const btn = $('#runPipelineBtn');
        const origText = btn.html();
        btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> RUNNING PIPELINE...');

        const siLength = parseInt($('#siLength').val()) || 21;
        
        // Always run V6 pipeline first to get safety scores
        // Use demo non-target if none uploaded
        const effectiveNonTarget = nonTargetSeq || window.demoNonTargetSeq || '';
        
        $.ajax({
            url: '/api/first_model', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ 
                sequence: sequence, 
                siLength: siLength, 
                nonTargetSequence: effectiveNonTarget,
                geneName: $('#geneName').val() || ''
            }),
            success: function(response) {
                let candidates = response.candidates || [];
                
                // If using RiNALMo-v2, enhance with DL efficacy predictions
                if (!isLegacy) {
                    let seqs = [];
                    for(let i=0; i <= sequence.length - siLength; i++) {
                        seqs.push(sequence.substring(i, i+siLength));
                    }
                    
                    // Fetch DL predictions and merge with safety scores
                    $.ajax({
                        url: '/api/predict', type: 'POST', contentType: 'application/json',
                        data: JSON.stringify({ sequences: seqs }),
                        success: function(dlResponse) {
                            const dlPredictions = dlResponse.predictions || [];
                            const dlMap = {};
                            dlPredictions.forEach(p => dlMap[p.sequence] = p);
                            
                            // Merge DL efficacy with V6 safety
                            candidates.forEach(c => {
                                if (dlMap[c.sequence]) {
                                    c.efficiency = dlMap[c.sequence].efficacy_score;
                                    c.mfe = dlMap[c.sequence].mfe_score;
                                    c.asymmetry = dlMap[c.sequence].asymmetry_score;
                                    c.endStability = dlMap[c.sequence].end_stability;
                                }
                            });
                            
                            renderResults(candidates, false, btn, origText);
                        },
                        error: function() {
                            // DL failed, use V6 only
                            renderResults(candidates, true, btn, origText);
                        }
                    });
                } else {
                    renderResults(candidates, true, btn, origText);
                }
            },
            error: function(xhr) {
                alert("Pipeline Error: " + (xhr.responseJSON?.error || "Unknown error"));
                btn.prop('disabled', false).html(origText);
            }
        });
    });

    // ── Render Results (shared by Legacy + DL paths) ────────────────────
    function renderResults(candidates, isLegacy, btn, origText) {
        latestCandidates = candidates;
        $('#kpi-scanned').text(candidates.length);
        
        const tbody = $('#resultsTable tbody');
        tbody.empty();

        let highEffCount = 0; let totalEff = 0;
        const topCandidates = candidates.slice(0, 100);
        
        topCandidates.forEach((cand, idx) => {
            tbody.append(renderTableRow(idx, cand, isLegacy));
            if(cand.efficiency > 90) highEffCount++;
            totalEff += (cand.efficiency || 0);
        });

        if(topCandidates.length > 0) {
            $('#kpi-higheff').text(highEffCount);
            $('#kpi-avg').text((totalEff / topCandidates.length).toFixed(1) + '%');
            const rejected = candidates.filter(c => (c.safetyScore !== undefined && c.safetyScore <= 85)).length;
            $('#kpi-reject').text(candidates.length > 0 ? Math.round((rejected / candidates.length) * 100) + '%' : '0%');
        }

        btn.prop('disabled', false).html(origText);
    }

    // ── Cocktail Design ──────────────────────────────────────────────────
    $('#cocktailBtn').on('click', function() {
        const rawFasta = $('#targetGenome').val();
        if (!rawFasta) { alert("Please input a sequence first."); return; }

        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Designing...');

        const sequence = parseFasta(rawFasta);
        const siLength = parseInt($('#siLength').val()) || 21;

        $.ajax({
            url: '/api/cocktail', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: sequence, siLength: siLength, nonTargetSequence: nonTargetSeq, numTargets: 3 }),
            success: function(resp) {
                const panel = $('#cocktailPanel');
                panel.removeClass('d-none');

                // KPIs
                $('#cocktailKpis').html(`
                    <div class="col-3"><div class="card bg-dark border-warning"><div class="card-body text-center">
                        <div class="text-secondary small">Targets Selected</div>
                        <div class="fw-bold fs-4 text-warning">${resp.numSelected}</div>
                    </div></div></div>
                    <div class="col-3"><div class="card bg-dark border-success"><div class="card-body text-center">
                        <div class="text-secondary small">Avg Safety</div>
                        <div class="fw-bold fs-4 text-success">${resp.avgSafety}%</div>
                    </div></div></div>
                    <div class="col-3"><div class="card bg-dark border-info"><div class="card-body text-center">
                        <div class="text-secondary small">Avg Efficacy</div>
                        <div class="fw-bold fs-4 text-info">${resp.avgEfficacy}%</div>
                    </div></div></div>
                    <div class="col-3"><div class="card bg-dark border-primary"><div class="card-body text-center">
                        <div class="text-secondary small">Synergy Score</div>
                        <div class="fw-bold fs-4 text-primary">${resp.synergyScore}</div>
                    </div></div></div>
                `);

                // Table
                const tbody = $('#cocktailTableBody');
                tbody.empty();
                (resp.cocktail || []).forEach((c, i) => {
                    const safeBadge = c.safetyScore > 85 ? 'bg-success' : 'bg-danger';
                    const effBadge = c.efficiency > 80 ? 'bg-success' : 'bg-warning text-dark';
                    tbody.append(`<tr>
                        <td class="fw-bold text-warning">siRNA-${i+1}</td>
                        <td class="font-monospace text-secondary">${c.position}</td>
                        <td class="font-monospace text-info">${c.sequence}</td>
                        <td><span class="badge ${effBadge}">${c.efficiency.toFixed(1)}%</span></td>
                        <td><span class="badge ${safeBadge}">${c.safetyScore.toFixed(1)}%</span></td>
                    </tr>`);
                });

                btn.prop('disabled', false).html('<i class="fa-solid fa-vials"></i> Design Multi-Target Cocktail');
            },
            error: function(xhr) {
                alert("Cocktail Error: " + (xhr.responseJSON?.error || "Server unreachable."));
                btn.prop('disabled', false).html('<i class="fa-solid fa-vials"></i> Design Multi-Target Cocktail');
            }
        });
    });

    // ── V8: RNA Accessibility Check ──────────────────────────────────────
    $('#rnaAccessBtn').on('click', function() {
        const seq = prompt("Enter 21nt sequence for RNA accessibility check:");
        if (!seq || seq.length < 15) {
            alert("Please enter a valid sequence (at least 15nt)");
            return;
        }
        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...');
        
        $.ajax({
            url: '/api/rna_accessibility', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: seq }),
            success: function(resp) {
                let colorClass = resp.accessibilityScore >= 80 ? 'success' : (resp.accessibilityScore >= 55 ? 'info' : 'danger');
                alert(`RNA Accessibility Analysis\n\n` +
                      `Accessibility Score: ${resp.accessibilityScore}% (${resp.accessibilityClass})\n` +
                      `ΔG Binding: ${resp.dgBinding} kcal/mol\n` +
                      `ΔG Unfolding: ${resp.dgUnfolding} kcal/mol\n` +
                      `ΔG Net: ${resp.dgNet} kcal/mol\n\n` +
                      `${resp.interpretation}`);
                btn.prop('disabled', false).html('<i class="fa-solid fa-dna"></i> RNA Accessibility Check');
            },
            error: function() {
                alert("RNA Accessibility Error: Server unreachable");
                btn.prop('disabled', false).html('<i class="fa-solid fa-dna"></i> RNA Accessibility Check');
            }
        });
    });

    // ── V8: Tissue Filter ────────────────────────────────────────────────
    $('#tissueFilterBtn').on('click', function() {
        const seq = prompt("Enter sequence for tissue-specific off-target check:");
        if (!seq) return;
        const genes = prompt("Enter off-target genes (comma-separated):", "CYP3A4, ALB, MBP");
        if (!genes) return;
        const tissue = $('#tissueTypeSelect').val() || 'liver';
        
        $.ajax({
            url: '/api/tissue_filter', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ 
                sequence: seq, 
                offTargetGenes: genes.split(',').map(g => g.trim()),
                organism: 'homo_sapiens',
                deliveryTissue: tissue
            }),
            success: function(resp) {
                let details = resp.details.map(d => 
                    `${d.offTargetGene}: ${d.effectiveThreatLevel} - ${d.interpretation}`
                ).join('\n\n');
                alert(`Tissue Off-Target Filter Results\n\n` +
                      `Total Off-Targets: ${resp.totalOffTargets}\n` +
                      `Genuine Threats: ${resp.genuineThreats}\n` +
                      `Cleared As Safe: ${resp.clearedAsSafe}\n` +
                      `Safety Rating: ${resp.adjustedSafetyRating}\n\n` +
                      `Details:\n${details}`);
            },
            error: function() {
                alert("Tissue Filter Error: Server unreachable");
            }
        });
    });

    // ── V8: AI Chemical Optimization ─────────────────────────────────────
    // Open modal on button click
    $('#aiChemBtn').on('click', function() {
        let seq = '';
        if (latestCandidates.length > 0) {
            seq = latestCandidates[0].sequence;
        }
        $('#aiChemSeqInput').val(seq);
        $('#aiChemResults').html('');
        
        const modal = new bootstrap.Modal(document.getElementById('aiChemModal'));
        modal.show();
    });
    
    // Run AI optimization on button click
    $('#runAiChemBtn').on('click', function() {
        const seq = $('#aiChemSeqInput').val().trim().toUpperCase().replace(/T/g, 'U').replace(/[^AUGC]/g, '');
        if (!seq || seq.length < 15) {
            alert("Please enter a valid RNA sequence (at least 15nt)");
            return;
        }
        
        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin"></i> CMS Optimizing...');
        $('#aiChemResults').html('<div class="text-center text-danger"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><p>Running Helix_Zero1 CMS optimization...</p></div>');
        
        $.ajax({
            url: '/api/chem_ai', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: seq }),
            success: function(resp) {
                const stats = resp.searchStats || {};
                const pdbFiles = resp.pdbFiles || {};
                const svgFiles = resp.svgFiles || {};
                const cmsRaw = resp.rawCmsResponse || {};
                const cmsOpt = cmsRaw.optimization_result || {};
                const outSeq = cmsOpt.modified_sequence || cmsOpt.sequence || resp.modifiedDisplay || seq;
                const outObjective = cmsRaw.objective_requested || resp.objective || 'efficacy';
                const outTherapeutic = cmsOpt.therapeutic_index ?? resp.therapeuticIndex ?? 'N/A';
                const outHalfLife = cmsOpt.half_life ?? resp.stabilityHalfLife ?? 'N/A';
                const outAgo2 = cmsOpt.ago2_binding ?? resp.ago2Affinity ?? 'N/A';
                const outImmune = cmsOpt.immune_suppression ?? resp.immuneSuppression ?? 'N/A';
                const outModType = cmsOpt.modification_type || stats.bestModType || resp.modificationType || 'CMS-optimized';
                const outPositions = cmsOpt.positions || resp.modifiedPositions || Object.keys(resp.modifications || {});
                const fmtMetric = (value, suffix = '') => {
                    const n = Number(value);
                    if (Number.isFinite(n)) {
                        return `${n}${suffix}`;
                    }
                    return 'N/A';
                };
                
                // Store data for downloads
                window.aiChemData = resp;
                
                // SVG Visualization Section
                let svgSection = '';
                if (svgFiles.nativeSvgContent) {
                    svgSection = `
                        <div class="card bg-dark border-info mt-3">
                            <div class="card-header bg-info bg-opacity-25 border-info">
                                <h6 class="mb-0 text-info"><i class="fa-solid fa-image"></i> 2D RNA Structure Visualization</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h7 class="text-success"><i class="fa-solid fa-dna"></i> Native (Unmodified)</h7>
                                        <div class="svg-container border border-secondary rounded p-2 mt-1" style="background:#2D3748;">
                                            ${svgFiles.nativeSvgContent}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h7 class="text-warning"><i class="fa-solid fa-flask"></i> Modified</h7>
                                        <div class="svg-container border border-secondary rounded p-2 mt-1" style="background:#2D3748;">
                                            ${svgFiles.modifiedSvgContent}
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-3">
                                    <button class="btn btn-sm btn-outline-info download-ai-svg me-2" data-type="comparison">
                                        <i class="fa-solid fa-code-compare"></i> Download Comparison SVG
                                    </button>
                                    <button class="btn btn-sm btn-outline-info download-ai-svg" data-type="linear">
                                        <i class="fa-solid fa-list"></i> Download Linear View SVG
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                } else if (svgFiles.error) {
                    svgSection = `<div class="alert alert-warning">SVG generation failed: ${svgFiles.error}</div>`;
                }
                
                // PDB Download Section (for 3D visualization)
                let pdbSection = '';
                if (pdbFiles.nativeContent) {
                    pdbSection = `
                        <div class="card bg-dark border-warning mt-3">
                            <div class="card-header bg-warning bg-opacity-25 border-warning">
                                <h6 class="mb-0 text-warning"><i class="fa-solid fa-cube"></i> 3D PDB Files (for PyMOL/VMD)</h6>
                            </div>
                            <div class="card-body">
                                <div class="row g-2">
                                    <div class="col-4">
                                        <button class="btn btn-sm btn-outline-warning w-100 download-ai-pdb" data-type="native">
                                            <i class="fa-solid fa-dna"></i> Native PDB
                                        </button>
                                    </div>
                                    <div class="col-4">
                                        <button class="btn btn-sm btn-outline-warning w-100 download-ai-pdb" data-type="modified">
                                            <i class="fa-solid fa-flask"></i> Modified PDB
                                        </button>
                                    </div>
                                    <div class="col-4">
                                        <button class="btn btn-sm btn-outline-info w-100 download-ai-pdb" data-type="comparison">
                                            <i class="fa-solid fa-code-compare"></i> Compare PDB
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                } else if (pdbFiles.error) {
                    pdbSection = `<div class="alert alert-warning mt-2">PDB generation failed: ${pdbFiles.error}</div>`;
                }
                
                let html = `
                    <div class="alert alert-success">
                        <i class="fa-solid fa-check-circle"></i> <strong>CMS Optimization Complete!</strong><br>
                        <small>${resp.aiSummary || ''} Objective: <strong>${outObjective}</strong></small>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card bg-dark border-secondary">
                                <div class="card-header bg-secondary bg-opacity-25">
                                    <h6 class="mb-0 text-info"><i class="fa-solid fa-dna"></i> Sequence Info</h6>
                                </div>
                                <div class="card-body">
                                    <table class="table table-sm table-dark mb-0">
                                        <tr><td><strong>Original</strong></td><td class="font-monospace">${resp.originalSequence || seq}</td></tr>
                                        <tr><td><strong>Optimized</strong></td><td class="font-monospace">${outSeq}</td></tr>
                                        <tr><td><strong>Mod Type</strong></td><td>${outModType}</td></tr>
                                        <tr><td><strong>Positions</strong></td><td>${outPositions?.join(', ') || 'N/A'}</td></tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-dark border-secondary">
                                <div class="card-header bg-secondary bg-opacity-25">
                                    <h6 class="mb-0 text-info"><i class="fa-solid fa-chart-line"></i> Performance Metrics</h6>
                                </div>
                                <div class="card-body">
                                    <table class="table table-sm table-dark mb-0">
                                        <tr><td><strong>Stability Half-Life</strong></td><td>${fmtMetric(outHalfLife, ' hours')}</td></tr>
                                        <tr><td><strong>Ago2 Affinity</strong></td><td>${fmtMetric(outAgo2, '%')}</td></tr>
                                        <tr><td><strong>Immune Suppression</strong></td><td>${fmtMetric(outImmune, '%')}</td></tr>
                                        <tr><td><strong>Therapeutic Index</strong></td><td class="text-success fw-bold">${fmtMetric(outTherapeutic, '/100')}</td></tr>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card bg-dark border-info mt-3">
                        <div class="card-header bg-info bg-opacity-25 border-info">
                                    <h6 class="mb-0 text-info"><i class="fa-solid fa-brain"></i> CMS Optimization Output</h6>
                        </div>
                        <div class="card-body">
                            <table class="table table-sm table-dark mb-0">
                                        <tr><td><strong>Objective</strong></td><td>${outObjective}</td></tr>
                                <tr><td><strong>Best Therapeutic Index</strong></td><td>${fmtMetric(outTherapeutic, '/100')}</td></tr>
                                        <tr><td><strong>Model Source</strong></td><td>Helix_Zero1 CMS Optimizer</td></tr>
                                        <tr><td><strong>Legacy Search Stats</strong></td><td>${Object.keys(stats).length ? 'Available' : 'Not provided by CMS optimize API'}</td></tr>
                            </table>
                        </div>
                    </div>
                    
                    ${svgSection}
                    
                    ${pdbSection}
                    
                    <div class="alert alert-secondary mt-3">
                        <small class="text-secondary">
                            <strong>Modification Legend:</strong><br>
                            <span class="badge" style="background:#3182CE;">Blue = 2'-OMe (Methyl)</span>
                            <span class="badge" style="background:#DD6B20;">Orange = 2'-F (Fluoro)</span>
                            <span class="badge" style="background:#805AD5;">Purple = PS (Phosphorothioate)</span>
                            <span class="badge bg-danger ms-2">⚠ Ago2 Cleavage Zone (9-12) should NOT be modified</span>
                        </small>
                    </div>
                    
                    ${resp.warnings?.length ? `<div class="alert alert-warning mt-3"><strong>Warnings:</strong><br>${resp.warnings.join('<br>')}</div>` : ''}
                `;
                
                $('#aiChemResults').html(html);
                btn.prop('disabled', false).html('<i class="fa-solid fa-wand-magic-sparkles"></i> Run CMS Optimization');
            },
            error: function(xhr) {
                const err = xhr.responseJSON?.error || 'Failed to run CMS optimization';
                const details = xhr.responseJSON?.details ? `<br><small>${xhr.responseJSON.details}</small>` : '';
                $('#aiChemResults').html(`<div class="alert alert-danger">Error: ${err}${details}</div>`);
                btn.prop('disabled', false).html('<i class="fa-solid fa-wand-magic-sparkles"></i> Run CMS Optimization');
            }
        });
    });
    
    // Download PDB files from AI Chem optimization
    $(document).on('click', '.download-ai-pdb', function() {
        const type = $(this).data('type');
        const data = window.aiChemData;
        if (!data || !data.pdbFiles) return;
        
        let content, filename;
        const seq = data.originalSequence.substring(0, 10);
        
        if (type === 'native') {
            content = data.pdbFiles.nativeContent;
            filename = `siRNA_${seq}_native.pdb`;
        } else if (type === 'modified') {
            content = data.pdbFiles.modifiedContent;
            filename = `siRNA_${seq}_modified.pdb`;
        } else {
            content = data.pdbFiles.pdbContent;
            filename = `siRNA_${seq}_comparison.pdb`;
        }
        
        if (content) {
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
        }
    });
    
    // Download SVG files from AI Chem optimization
    $(document).on('click', '.download-ai-svg', function() {
        const type = $(this).data('type');
        const data = window.aiChemData;
        if (!data || !data.svgFiles) return;
        
        let content, filename;
        const seq = data.originalSequence.substring(0, 10);
        
        if (type === 'comparison') {
            content = data.svgFiles.comparisonSvgContent;
            filename = `siRNA_${seq}_comparison.svg`;
        } else if (type === 'linear') {
            content = data.svgFiles.linearSvgContent;
            filename = `siRNA_${seq}_linear.svg`;
        } else {
            content = data.svgFiles.nativeSvgContent;
            filename = `siRNA_${seq}_native.svg`;
        }
        
        if (content) {
            const blob = new Blob([content], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
        }
    });

    // ── V8: RNA Structure Visualization ─────────────────────────────────
    $('#rnaStructBtn').on('click', function() {
        // Get sequence from results or prompt
        let seq = '';
        if (latestCandidates.length > 0) {
            // Use top candidate
            seq = latestCandidates[0].sequence;
        }
        
        $('#rnaStructSeqInput').val(seq);
        $('#rnaStructResults').html('');
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('rnaStructureModal'));
        modal.show();
    });
    
    $('#runRnaStructBtn').on('click', function() {
        const seq = $('#rnaStructSeqInput').val().trim().toUpperCase().replace(/T/g, 'U').replace(/[^AUGC]/g, '');
        if (!seq || seq.length < 6) {
            alert("Please enter a valid sequence (at least 6nt)");
            return;
        }
        
        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin"></i> Running CMS Predictor...');
        $('#rnaStructResults').html('<div class="text-center text-info"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><p>Running Helix_Zero1 CMS structure prediction...</p></div>');
        
        $.ajax({
            url: '/api/rna_structure', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: seq }),
            success: function(resp) {
                const structSvg = resp.svgFiles || {};
                // Build results HTML
                const acc = resp.accessibility_prediction;
                let accClass = 'success';
                if (acc.score < 60) accClass = 'warning';
                if (acc.score < 40) accClass = 'danger';
                
                let elementsHtml = resp.elements.map(e => 
                    `<span class="badge bg-secondary me-1 mb-1">${e.type}: ${e.description}</span>`
                ).join('');

                let structureSvgSection = '';
                if (structSvg.nativeSvgContent) {
                    const modifiedPanelSvg = structSvg.modifiedSvgContent || structSvg.nativeSvgContent;
                    structureSvgSection = `
                        <div class="card bg-dark border-info mt-3">
                            <div class="card-header bg-info bg-opacity-25 border-info">
                                <h6 class="mb-0 text-info"><i class="fa-solid fa-image"></i> Diagrammatic 2D Structures (Native vs Modified)</h6>
                            </div>
                            <div class="card-body">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <h6 class="text-success"><i class="fa-solid fa-dna"></i> Native</h6>
                                        <div class="svg-container border border-secondary rounded p-2" style="background:#2D3748; overflow:auto;">
                                            ${structSvg.nativeSvgContent}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="text-warning"><i class="fa-solid fa-flask"></i> Modified</h6>
                                        <div class="svg-container border border-secondary rounded p-2" style="background:#2D3748; overflow:auto;">
                                            ${modifiedPanelSvg}
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-3">
                                    <button class="btn btn-sm btn-outline-info download-rna-svg me-2" data-type="native">
                                        <i class="fa-solid fa-download"></i> Download Native SVG
                                    </button>
                                    <button class="btn btn-sm btn-outline-info download-rna-svg me-2" data-type="modified">
                                        <i class="fa-solid fa-download"></i> Download Modified SVG
                                    </button>
                                    <button class="btn btn-sm btn-outline-info download-rna-svg" data-type="comparison">
                                        <i class="fa-solid fa-code-compare"></i> Download Comparison SVG
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                } else if (structSvg.error) {
                    structureSvgSection = `<div class="alert alert-warning mt-3">Structure SVG generation failed: ${structSvg.error}</div>`;
                }

                window.rnaStructureData = resp;
                
                let html = `
                    <div class="card bg-dark border-info mt-3">
                        <div class="card-header bg-info bg-opacity-25 border-info">
                            <h5 class="mb-0 text-info"><i class="fa-solid fa-spiral"></i> CMS Predicted 2D Structure</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-info">Sequence Information</h6>
                                    <table class="table table-sm table-dark">
                                        <tr><td><strong>Sequence</strong></td><td class="font-monospace">${resp.sequence}</td></tr>
                                        <tr><td><strong>Length</strong></td><td>${resp.length} nt</td></tr>
                                        <tr><td><strong>GC Content</strong></td><td>${resp.gc_content}%</td></tr>
                                        <tr><td><strong>MFE Estimate</strong></td><td>${resp.mfe_estimate} kcal/mol</td></tr>
                                        <tr><td><strong>Predictor</strong></td><td>${resp.method || 'CMS'}</td></tr>
                                    </table>
                                    
                                    <h6 class="text-info mt-3">Structure Metrics</h6>
                                    <table class="table table-sm table-dark">
                                        <tr><td><strong>Dot-Bracket</strong></td><td class="font-monospace">${resp.dot_bracket}</td></tr>
                                        <tr><td><strong>Base Pairs</strong></td><td>${resp.num_base_pairs}</td></tr>
                                        <tr><td><strong>Structure Score</strong></td><td>${resp.structure_score}/100</td></tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-info">Accessibility Prediction</h6>
                                    <div class="alert alert-${accClass}">
                                        <h4 class="alert-heading">${acc.classification}</h4>
                                        <p class="mb-0"><strong>Score: ${acc.score}/100</strong></p>
                                        <p class="mb-0 small">${acc.reason}</p>
                                        ${acc.num_base_pairs ? `<p class="mb-0 small">Base pairs: ${acc.num_base_pairs} (${acc.base_pair_density}% density)</p>` : ''}
                                    </div>
                                    
                                    <h6 class="text-info mt-3">Structure Elements</h6>
                                    <div class="mb-2">${elementsHtml || '<span class="text-secondary">No elements detected</span>'}</div>
                                </div>
                            </div>

                                ${structureSvgSection}
                            
                            <h6 class="text-info mt-3">ASCII Visualization</h6>
                            <pre class="bg-black p-3 rounded text-info font-monospace" style="font-size: 11px;">${resp.visual}</pre>
                            
                            <div class="mt-3">
                                <small class="text-secondary">
                                    <i class="fa-solid fa-info-circle"></i> 
                                    Legend: <code>()</code> = Base pair, <code>.</code> = Unpaired, 
                                    Structure score represents thermodynamic stability (higher = more stable structure)
                                </small>
                            </div>
                        </div>
                    </div>
                `;
                
                $('#rnaStructResults').html(html);
                btn.prop('disabled', false).html('<i class="fa-solid fa-spiral"></i> Predict via CMS');
            },
            error: function(xhr) {
                const err = xhr.responseJSON?.error || 'Failed to predict structure';
                const details = xhr.responseJSON?.details ? `<br><small>${xhr.responseJSON.details}</small>` : '';
                $('#rnaStructResults').html(`<div class="alert alert-danger">Error: ${err}${details}</div>`);
                btn.prop('disabled', false).html('<i class="fa-solid fa-spiral"></i> Predict via CMS');
            }
        });
    });

    // Download SVG files from RNA structure prediction
    $(document).on('click', '.download-rna-svg', function() {
        const type = $(this).data('type');
        const data = window.rnaStructureData;
        if (!data || !data.svgFiles) return;

        const seq = (data.sequence || '').substring(0, 10) || 'rna';
        let content = '';
        let filename = '';

        if (type === 'comparison') {
            content = data.svgFiles.comparisonSvgContent;
            filename = `rna_${seq}_comparison.svg`;
        } else if (type === 'modified') {
            content = data.svgFiles.modifiedSvgContent || data.svgFiles.nativeSvgContent;
            filename = `rna_${seq}_modified.svg`;
        } else {
            content = data.svgFiles.nativeSvgContent;
            filename = `rna_${seq}_native.svg`;
        }

        if (content) {
            const blob = new Blob([content], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
        }
    });

    // ── V8: PDB Structure Generation ─────────────────────────────────────────
    $('#pdbGenBtn').on('click', function() {
        let seq = '';
        if (latestCandidates.length > 0) {
            seq = latestCandidates[0].sequence;
        }
        
        $('#pdbSeqInput').val(seq);
        $('#pdbResults').show();
        $('#pdbContentPreview').text('PDB content will appear here after generation...');
        
        const modal = new bootstrap.Modal(document.getElementById('pdbModal'));
        modal.show();
    });
    
    $('#runPdbGenBtn').on('click', function() {
        const seq = $('#pdbSeqInput').val().trim().toUpperCase().replace(/[^AUGC]/g, '');
        const modType = $('#pdbModSelect').val();
        const posStr = $('#pdbModPositions').val().trim();
        
        if (!seq || seq.length < 6) {
            alert("Please enter a valid RNA sequence (at least 6nt)");
            return;
        }
        
        let modifications = {};
        if (posStr) {
            const positions = posStr.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p) && p >= 0 && p < seq.length);
            positions.forEach(p => { modifications[p] = modType; });
        } else if (modType !== 'native') {
            // Default positions for common modifications
            modifications = {0: modType, 2: modType, 4: modType, 17: modType, 18: modType};
        }
        
        const btn = $(this);
        btn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin"></i> Generating PDB...');
        
        $.ajax({
            url: '/api/pdb/generate', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: seq, modifications: modifications }),
            success: function(resp) {
                if (resp.status === 'success') {
                    let modSummary = Object.keys(modifications).length > 0 
                        ? 'Modified positions: ' + Object.entries(modifications).map(([p, m]) => `${p}(${m})`).join(', ')
                        : 'Native (unmodified) structure';
                    
                    let html = `
                        <div class="alert alert-success mb-3">
                            <i class="fa-solid fa-check-circle"></i> <strong>PDB Files Generated Successfully!</strong><br>
                            <small>Sequence: ${seq} | ${modSummary}</small>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <div class="card bg-dark border-warning">
                                    <div class="card-header bg-warning bg-opacity-25">
                                        <h6 class="mb-0 text-warning"><i class="fa-solid fa-dna"></i> Native Structure</h6>
                                    </div>
                                    <div class="card-body text-center">
                                        <p class="small text-secondary mb-2">Unmodified RNA duplex</p>
                                        <button class="btn btn-sm btn-outline-warning download-pdb" data-pdb="native" data-seq="${seq}">
                                            <i class="fa-solid fa-download"></i> Download .pdb
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-dark border-warning">
                                    <div class="card-header bg-warning bg-opacity-25">
                                        <h6 class="mb-0 text-warning"><i class="fa-solid fa-flask"></i> Modified Structure</h6>
                                    </div>
                                    <div class="card-body text-center">
                                        <p class="small text-secondary mb-2">With ${Object.keys(modifications).length} modification(s)</p>
                                        <button class="btn btn-sm btn-outline-warning download-pdb" data-pdb="modified" data-seq="${seq}">
                                            <i class="fa-solid fa-download"></i> Download .pdb
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-dark border-info">
                                    <div class="card-header bg-info bg-opacity-25">
                                        <h6 class="mb-0 text-info"><i class="fa-solid fa-code"></i> Comparison</h6>
                                    </div>
                                    <div class="card-body text-center">
                                        <p class="small text-secondary mb-2">Both structures in one file</p>
                                        <button class="btn btn-sm btn-outline-info download-pdb" data-pdb="comparison" data-seq="${seq}">
                                            <i class="fa-solid fa-download"></i> Download .pdb
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    $('#pdbResults').html(html);
                    
                    // Show preview
                    $('#pdbContentPreview').text(resp.pdb_content.substring(0, 3000) + (resp.pdb_content.length > 3000 ? '\n... (truncated)' : ''));
                    
                    // Store data for downloads
                    window.pdbData = resp;
                } else {
                    $('#pdbResults').html(`<div class="alert alert-danger">Error: ${resp.error || 'Failed to generate PDB'}</div>`);
                }
                btn.prop('disabled', false).html('<i class="fa-solid fa-cube"></i> Generate PDB Files');
            },
            error: function(xhr) {
                $('#pdbResults').html(`<div class="alert alert-danger">Error: ${xhr.responseJSON?.error || 'Failed to generate PDB'}</div>`);
                btn.prop('disabled', false).html('<i class="fa-solid fa-cube"></i> Generate PDB Files');
            }
        });
    });
    
    // Download handlers for PDB files
    $(document).on('click', '.download-pdb', function() {
        const type = $(this).data('pdb');
        const seq = $(this).data('seq');
        
        if (window.pdbData && window.pdbData.pdb_content) {
            // For now, download the comparison file content
            const blob = new Blob([window.pdbData.pdb_content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `siRNA_${seq.substring(0, 10)}_${type}.pdb`;
            a.click();
        }
    });
    
    // Quick download buttons
    $('#downloadNativePdb').on('click', function() {
        const seq = $('#pdbSeqInput').val().trim().toUpperCase().replace(/[^AUGC]/g, '');
        if (!seq) { alert("Enter a sequence first"); return; }
        
        $.ajax({
            url: '/api/pdb/native', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: seq }),
            success: function(resp) {
                const blob = new Blob([resp.pdb_content], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `siRNA_${seq.substring(0, 10)}_native.pdb`;
                a.click();
            }
        });
    });
    
    $('#downloadModifiedPdb').on('click', function() {
        const seq = $('#pdbSeqInput').val().trim().toUpperCase().replace(/[^AUGC]/g, '');
        const modType = $('#pdbModSelect').val();
        const posStr = $('#pdbModPositions').val().trim();
        
        if (!seq) { alert("Enter a sequence first"); return; }
        
        let modifications = {};
        if (posStr) {
            const positions = posStr.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p));
            positions.forEach(p => { modifications[p] = modType; });
        } else {
            modifications = {0: modType, 2: modType, 4: modType, 17: modType, 18: modType};
        }
        
        $.ajax({
            url: '/api/pdb/modified', type: 'POST', contentType: 'application/json',
            data: JSON.stringify({ sequence: seq, modifications: modifications }),
            success: function(resp) {
                const blob = new Blob([resp.pdb_content], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `siRNA_${seq.substring(0, 10)}_modified.pdb`;
                a.click();
            }
        });
    });

    // ── Export CSV ────────────────────────────────────────────────────────
    $('#exportBtn').on('click', function() {
        if(latestCandidates.length === 0) { alert("No data to export."); return; }
        let csv = "Rank,Position,Sequence,GC%,Efficacy,SafetyScore,MFE,Asymmetry,Status\n";
        latestCandidates.slice(0, 100).forEach((c, i) => {
            csv += `${i+1},${c.position},${c.sequence},${c.gcContent},${(c.efficiency||0).toFixed(1)},${(c.safetyScore||0).toFixed(1)},${c.mfe||'N/A'},${c.asymmetry||'N/A'},${c.status||'N/A'}\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'helix_zero_candidates.csv'; a.click();
    });

    // ── Demo Data ────────────────────────────────────────────────────────
    // OPTIMAL TARGET: Mix of excellent and good candidates for realistic demo
    $('#targetGenome').val(`>Pest_Target_Gene_CYP450
ATGGACTACAAGGACGACGATGACAAGATGGCCGCAGTCATCGAC
TACATGGGACATCAAATTGTTGTGATAAGAAGGGTATTTAACAT
AGACAAGAAATATCATATCCGCGCTGCGCATTACAGGGAACAT
ATGGCACACGCTAACGCTGTGCTGGCGTTTCATAAGAGGTTGAT
TGCAGCTAGTCAAGCTAGCATGCATGCTAGCATGCATGCTAG
CGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACG
TATATATATATATATATATATATATATATATATATATATATA
ATATATATATATATATATATATATATATATATATATATATAT
ATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCAT
TACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTA
TACATGGGACATCAAATTGTTGTGATAAGAAGGGTATTTAACAT
AGACAAGAAATATCATATCCGCGCTGCGCATTACAGGGAACAT
ATGGCACACGCTAACGCTGTGCTGGCGTTTCATAAGAGGTTGAT
TGCAGCTAGTCAAGCTAGCATGCATGCTAGCATGCATGCTAG`
    );
    
    // ── Demo Non-Target (Honeybee Genome) ─────────────────────────────────
    // Contains some matching sequences to demonstrate homology checking
    window.demoNonTargetSeq = `>Apis_mellifera_actin_gene
ATGGACTACAAGGACGACGATGACAAGATGGCCGCAGTCATCGAC
TACATGGGACATCAAATTGTTGTGATAAGAAGGGTATTTAACAT
AGACAAGAAATATCATATCCGCGCTGCGCATTACAGGGAACAT
GCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG`;
});
