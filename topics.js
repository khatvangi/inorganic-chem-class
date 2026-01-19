/**
 * CHEM 361 Topic Explorer
 * Interactive knowledge graph visualization
 */

// state
const state = {
    graph: null,
    selectedTopic: null,
    showLabels: true,
    simulation: null,
};

// color scheme for major topics (others get auto-generated)
const topicColors = {
    'Coordination Chemistry': '#8b5cf6',
    'Crystal Field Theory': '#a855f7',
    'Solid State Chemistry': '#f59e0b',
    'Main Group Chemistry': '#06b6d4',
    'Electrochemistry': '#10b981',
    'Chemical Bonding': '#3b82f6',
    'Molecular Orbital Theory': '#6366f1',
    'Symmetry And Group Theory': '#ec4899',
    'Periodic Trends': '#14b8a6',
    'Acid-Base Chemistry': '#f43f5e',
    'Bioinorganic Chemistry': '#22c55e',
    'Catalysis': '#eab308',
    'Spectroscopy': '#f97316',
    'Nuclear Chemistry': '#ef4444',
    'Organometallic Chemistry': '#84cc16',
    'Lanthanide Chemistry': '#a78bfa',
    'Crystal Structures': '#c084fc',
    'Atomic Structure And Electronic Configuration': '#0ea5e9',
    'Nanomaterials And Self-Assembly': '#d946ef',
    'Industrial Chemistry': '#78716c',
};

// generate consistent color from string hash
const stringToColor = (str) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const hue = Math.abs(hash % 360);
    return `hsl(${hue}, 65%, 55%)`;
};

// display settings
const DISPLAY_SETTINGS = {
    maxTopicsInList: 100,      // show top N topics in sidebar
    maxNodesInGraph: 150,      // limit graph nodes for performance
    minCountForGraph: 10,      // minimum count to show in graph
};

// fallback topic data (used if knowledge_graph.json not available)
const fallbackTopics = {
    nodes: [
        { id: 'Coordination Chemistry', type: 'topic', count: 450 },
        { id: 'Crystal Field Theory', type: 'topic', count: 380 },
        { id: 'Solid State Chemistry', type: 'topic', count: 320 },
        { id: 'Main Group Chemistry', type: 'topic', count: 290 },
        { id: 'Electrochemistry', type: 'topic', count: 260 },
        { id: 'Chemical Bonding', type: 'topic', count: 240 },
        { id: 'Molecular Orbital Theory', type: 'topic', count: 220 },
        { id: 'Symmetry and Group Theory', type: 'topic', count: 180 },
        { id: 'Periodic Trends', type: 'topic', count: 170 },
        { id: 'Acid-Base Chemistry', type: 'topic', count: 150 },
        { id: 'Quantum Mechanics', type: 'topic', count: 140 },
        { id: 'Bioinorganic Chemistry', type: 'topic', count: 120 },
        { id: 'Catalysis', type: 'topic', count: 110 },
        { id: 'Spectroscopy', type: 'topic', count: 100 },
        { id: 'Nuclear Chemistry', type: 'topic', count: 80 },
        { id: 'Transition Metal Chemistry', type: 'topic', count: 200 },
        // prerequisites
        { id: 'Electron Configuration', type: 'prerequisite', count: 50 },
        { id: 'Atomic Structure', type: 'prerequisite', count: 45 },
        { id: 'Oxidation States', type: 'prerequisite', count: 40 },
        { id: 'Hybridization', type: 'prerequisite', count: 35 },
    ],
    edges: [
        // prerequisite relationships
        { source: 'Electron Configuration', target: 'Crystal Field Theory', relation: 'prerequisite_for', weight: 15 },
        { source: 'Electron Configuration', target: 'Molecular Orbital Theory', relation: 'prerequisite_for', weight: 12 },
        { source: 'Atomic Structure', target: 'Periodic Trends', relation: 'prerequisite_for', weight: 10 },
        { source: 'Oxidation States', target: 'Electrochemistry', relation: 'prerequisite_for', weight: 8 },
        { source: 'Oxidation States', target: 'Coordination Chemistry', relation: 'prerequisite_for', weight: 7 },
        { source: 'Hybridization', target: 'Chemical Bonding', relation: 'prerequisite_for', weight: 9 },
        // leads_to relationships
        { source: 'Crystal Field Theory', target: 'Spectroscopy', relation: 'leads_to', weight: 12 },
        { source: 'Crystal Field Theory', target: 'Coordination Chemistry', relation: 'leads_to', weight: 15 },
        { source: 'Coordination Chemistry', target: 'Bioinorganic Chemistry', relation: 'leads_to', weight: 10 },
        { source: 'Coordination Chemistry', target: 'Catalysis', relation: 'leads_to', weight: 11 },
        { source: 'Periodic Trends', target: 'Main Group Chemistry', relation: 'leads_to', weight: 14 },
        { source: 'Chemical Bonding', target: 'Molecular Orbital Theory', relation: 'leads_to', weight: 13 },
        { source: 'Molecular Orbital Theory', target: 'Spectroscopy', relation: 'leads_to', weight: 8 },
        { source: 'Solid State Chemistry', target: 'Electrochemistry', relation: 'leads_to', weight: 7 },
        { source: 'Quantum Mechanics', target: 'Molecular Orbital Theory', relation: 'leads_to', weight: 10 },
        { source: 'Symmetry and Group Theory', target: 'Crystal Field Theory', relation: 'leads_to', weight: 9 },
        { source: 'Symmetry and Group Theory', target: 'Spectroscopy', relation: 'leads_to', weight: 8 },
    ],
};

// UI elements
const ui = {
    topicList: document.getElementById('topicList'),
    searchBox: document.getElementById('searchBox'),
    graph: document.getElementById('graph'),
    contentPanel: document.getElementById('contentPanel'),
    panelTitle: document.getElementById('panelTitle'),
    panelSubtitle: document.getElementById('panelSubtitle'),
    panelBody: document.getElementById('panelBody'),
    closePanel: document.getElementById('closePanel'),
    resetZoom: document.getElementById('resetZoom'),
    toggleLabels: document.getElementById('toggleLabels'),
};

// load knowledge graph
const loadGraph = async () => {
    try {
        // try to load the generated knowledge graph
        const res = await fetch('./experiments/results/knowledge_graph.json');
        if (res.ok) {
            const fullGraph = await res.json();
            console.log('Loaded knowledge graph:', fullGraph.metadata);
            console.log(`Full graph: ${fullGraph.nodes.length} nodes, ${fullGraph.edges.length} edges`);

            // filter to manageable size for visualization
            // keep topics with count >= minCountForGraph
            const topicNodes = fullGraph.nodes
                .filter(n => n.type === 'topic' && (n.count || 0) >= DISPLAY_SETTINGS.minCountForGraph)
                .sort((a, b) => (b.count || 0) - (a.count || 0))
                .slice(0, DISPLAY_SETTINGS.maxNodesInGraph);

            const topicIds = new Set(topicNodes.map(n => n.id));

            // get edges between visible topics
            const visibleEdges = fullGraph.edges.filter(e =>
                topicIds.has(e.source) && topicIds.has(e.target)
            );

            state.graph = {
                nodes: topicNodes,
                edges: visibleEdges,
                metadata: fullGraph.metadata,
                fullGraph: fullGraph  // keep reference for panel details
            };

            console.log(`Filtered for display: ${topicNodes.length} nodes, ${visibleEdges.length} edges`);
        } else {
            throw new Error('Knowledge graph not found');
        }
    } catch (e) {
        console.log('Using fallback topic data:', e.message);
        state.graph = fallbackTopics;
    }

    // process nodes to add colors
    state.graph.nodes.forEach(node => {
        if (topicColors[node.id]) {
            node.color = topicColors[node.id];
        } else if (node.type === 'topic') {
            node.color = stringToColor(node.id);
        } else if (node.type === 'prerequisite') {
            node.color = '#64748b';
        } else {
            node.color = '#71717a';
        }
    });
};

// render topic list
const renderTopicList = (filter = '') => {
    const topics = state.graph.nodes
        .filter(n => n.type === 'topic')
        .filter(n => n.id.toLowerCase().includes(filter.toLowerCase()))
        .sort((a, b) => (b.count || 0) - (a.count || 0));

    let html = '';
    topics.forEach(topic => {
        const isActive = state.selectedTopic === topic.id ? 'active' : '';
        html += `
            <div class="topic-item ${isActive}" data-topic="${topic.id}">
                <div class="topic-dot" style="background: ${topic.color}"></div>
                <span class="topic-name">${topic.id}</span>
                <span class="topic-count">${topic.count || 0}</span>
            </div>
        `;
    });

    ui.topicList.innerHTML = html || '<div class="loading">No topics found</div>';

    // add click handlers
    document.querySelectorAll('.topic-item').forEach(item => {
        item.addEventListener('click', () => {
            selectTopic(item.dataset.topic);
        });
    });
};

// render graph
let svg, g, zoom;
const renderGraph = () => {
    const width = ui.graph.clientWidth;
    const height = ui.graph.clientHeight;

    // clear existing
    d3.select(ui.graph).selectAll('*').remove();

    svg = d3.select(ui.graph)
        .attr('width', width)
        .attr('height', height);

    // zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.2, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    g = svg.append('g');

    // prepare data
    const nodes = state.graph.nodes.map(d => ({ ...d }));
    const links = state.graph.edges.map(d => ({
        source: d.source,
        target: d.target,
        relation: d.relation,
        weight: d.weight || 1,
    }));

    // create simulation
    state.simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => getNodeRadius(d) + 10));

    // draw links
    const link = g.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('class', d => `link ${d.relation}`)
        .attr('stroke-width', d => Math.sqrt(d.weight));

    // draw nodes
    const node = g.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    node.append('circle')
        .attr('r', d => getNodeRadius(d))
        .attr('fill', d => d.color);

    node.append('text')
        .attr('dy', d => getNodeRadius(d) + 12)
        .attr('text-anchor', 'middle')
        .text(d => d.id.length > 20 ? d.id.substring(0, 18) + '...' : d.id);

    // click handler
    node.on('click', (event, d) => {
        event.stopPropagation();
        selectTopic(d.id);
    });

    // update positions
    state.simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // drag functions
    function dragstarted(event) {
        if (!event.active) state.simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) state.simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
};

const getNodeRadius = (node) => {
    if (node.type === 'topic') return Math.sqrt(node.count || 100) / 2 + 8;
    if (node.type === 'prerequisite') return 10;
    return 6;
};

// select topic
const selectTopic = (topicId) => {
    state.selectedTopic = topicId;
    renderTopicList(ui.searchBox.value);
    renderContentPanel(topicId);
    highlightNode(topicId);
};

// highlight node in graph
const highlightNode = (topicId) => {
    if (!svg) return;

    // reset all
    svg.selectAll('.node circle')
        .attr('stroke', 'var(--bg-primary)')
        .attr('stroke-width', 2);

    svg.selectAll('.link')
        .attr('stroke-opacity', 0.3);

    // highlight selected
    svg.selectAll('.node')
        .filter(d => d.id === topicId)
        .select('circle')
        .attr('stroke', '#fff')
        .attr('stroke-width', 4);

    // highlight connected edges
    svg.selectAll('.link')
        .filter(d => d.source.id === topicId || d.target.id === topicId)
        .attr('stroke-opacity', 1);
};

// render content panel
const renderContentPanel = (topicId) => {
    // try to find node in displayed graph or full graph
    let node = state.graph.nodes.find(n => n.id === topicId);
    if (!node && state.graph.fullGraph) {
        node = state.graph.fullGraph.nodes.find(n => n.id === topicId);
    }
    if (!node) return;

    ui.panelTitle.textContent = topicId;
    ui.panelSubtitle.textContent = `${node.type} • ${node.count || 0} mentions in textbooks`;
    ui.contentPanel.classList.remove('hidden');

    // use full graph for relationships if available
    const edges = state.graph.fullGraph?.edges || state.graph.edges;

    // find relationships - look for edges where this topic is involved
    const prerequisites = edges
        .filter(e => e.target === topicId && e.relation === 'prerequisite_for')
        .map(e => e.source)
        .slice(0, 10);

    const leadsTo = edges
        .filter(e => e.source === topicId && e.relation === 'leads_to')
        .map(e => e.target)
        .slice(0, 10);

    const concepts = edges
        .filter(e => e.source === topicId && e.relation === 'contains')
        .map(e => e.target)
        .slice(0, 15);

    let html = '';

    // prerequisites
    if (prerequisites.length > 0) {
        html += `
            <div class="section">
                <h3 class="section-title">Prerequisites</h3>
                ${prerequisites.map(p => `
                    <div class="prereq-link" data-topic="${p}">${p}</div>
                `).join('')}
            </div>
        `;
    }

    // leads to
    if (leadsTo.length > 0) {
        html += `
            <div class="section">
                <h3 class="section-title">Leads To</h3>
                ${leadsTo.map(l => `
                    <div class="leadsto-link" data-topic="${l}">${l}</div>
                `).join('')}
            </div>
        `;
    }

    // key concepts
    if (concepts.length > 0) {
        html += `
            <div class="section">
                <h3 class="section-title">Key Concepts</h3>
                ${concepts.map(c => `<span class="concept-tag">${c}</span>`).join('')}
            </div>
        `;
    }

    // overview section with stats
    const totalTopics = state.graph.fullGraph?.nodes.filter(n => n.type === 'topic').length || state.graph.nodes.length;
    const rank = state.graph.nodes.findIndex(n => n.id === topicId) + 1;

    html += `
        <div class="section">
            <h3 class="section-title">Overview</h3>
            <div class="narrative">
                <p><strong>${topicId}</strong> appears in <strong>${node.count || 0}</strong> textbook passages across our 7 inorganic chemistry textbooks.</p>
                ${rank > 0 ? `<p>This is the <strong>#${rank}</strong> most discussed topic out of ${totalTopics} topics extracted.</p>` : ''}
                ${prerequisites.length > 0 ? `<p>Students should first understand: ${prerequisites.slice(0, 3).join(', ')}.</p>` : ''}
                ${leadsTo.length > 0 ? `<p>Understanding this topic enables: ${leadsTo.slice(0, 3).join(', ')}.</p>` : ''}
                <p style="margin-top: 1rem;"><span class="source-tag">Extracted from 7,726 chunks</span></p>
            </div>
        </div>
    `;

    ui.panelBody.innerHTML = html;

    // add click handlers for links
    document.querySelectorAll('.prereq-link, .leadsto-link').forEach(link => {
        link.addEventListener('click', () => {
            selectTopic(link.dataset.topic);
        });
    });
};

// event listeners
const setupListeners = () => {
    ui.searchBox.addEventListener('input', (e) => {
        renderTopicList(e.target.value);
    });

    ui.closePanel.addEventListener('click', () => {
        ui.contentPanel.classList.add('hidden');
        state.selectedTopic = null;
        renderTopicList(ui.searchBox.value);
        if (svg) {
            svg.selectAll('.node circle')
                .attr('stroke', 'var(--bg-primary)')
                .attr('stroke-width', 2);
            svg.selectAll('.link')
                .attr('stroke-opacity', 0.6);
        }
    });

    ui.resetZoom.addEventListener('click', () => {
        if (svg && zoom) {
            svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
        }
    });

    ui.toggleLabels.addEventListener('click', () => {
        state.showLabels = !state.showLabels;
        ui.toggleLabels.textContent = state.showLabels ? 'Hide Labels' : 'Show Labels';
        svg.selectAll('.node text').style('opacity', state.showLabels ? 1 : 0);
    });

    // resize handler
    window.addEventListener('resize', () => {
        renderGraph();
    });
};

// init
const init = async () => {
    await loadGraph();
    renderTopicList();
    renderGraph();
    setupListeners();
};

init();
