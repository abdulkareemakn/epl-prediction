const CRESTS = {
    "Arsenal": "https://resources.premierleague.com/premierleague/badges/50/t3.png",
    "Aston Villa": "https://resources.premierleague.com/premierleague/badges/50/t7.png",
    "Bournemouth": "https://resources.premierleague.com/premierleague/badges/50/t91.png",
    "Brentford": "https://resources.premierleague.com/premierleague/badges/50/t94.png",
    "Brighton": "https://resources.premierleague.com/premierleague/badges/50/t36.png",
    "Chelsea": "https://resources.premierleague.com/premierleague/badges/50/t8.png",
    "Crystal Palace": "https://resources.premierleague.com/premierleague/badges/50/t31.png",
    "Everton": "https://resources.premierleague.com/premierleague/badges/50/t11.png",
    "Fulham": "https://resources.premierleague.com/premierleague/badges/50/t54.png",
    "Ipswich": "https://resources.premierleague.com/premierleague/badges/50/t40.png",
    "Leicester": "https://resources.premierleague.com/premierleague/badges/50/t13.png",
    "Liverpool": "https://resources.premierleague.com/premierleague/badges/50/t14.png",
    "Man City": "https://resources.premierleague.com/premierleague/badges/50/t43.png",
    "Man United": "https://resources.premierleague.com/premierleague/badges/50/t1.png",
    "Newcastle": "https://resources.premierleague.com/premierleague/badges/50/t4.png",
    "Nott'm Forest": "https://resources.premierleague.com/premierleague/badges/50/t17.png",
    "Southampton": "https://resources.premierleague.com/premierleague/badges/50/t20.png",
    "Tottenham": "https://resources.premierleague.com/premierleague/badges/50/t6.png",
    "West Ham": "https://resources.premierleague.com/premierleague/badges/50/t21.png",
    "Wolves": "https://resources.premierleague.com/premierleague/badges/50/t39.png",
};

function getZone(pos) {
    pos = parseInt(pos);
    if (pos <= 4) return "cl";
    if (pos === 5) return "europa";
    if (pos === 6) return "conference";
    if (pos >= 18) return "relegation";
    return null;
}

function initials(name) {
    return name.split(" ").map(w => w[0]).join("").slice(0, 3).toUpperCase();
}

function crestEl(team) {
    const url = CRESTS[team];
    if (url) {
        const img = document.createElement("img");
        img.src = url;
        img.alt = team;
        img.onerror = function() {
            const fb = fallbackCrest(team);
            this.replaceWith(fb);
        };
        return img;
    }
    return fallbackCrest(team);
}

function fallbackCrest(team) {
    const div = document.createElement("div");
    div.className = "crest-fallback";
    div.textContent = initials(team);
    return div;
}

function parseCSV(text) {
    const lines = text.trim().split("\n");
    const headers = lines[0].split(",").map(h => h.trim());
    return lines.slice(1).map(line => {
        const vals = line.split(",").map(v => v.trim());
        const obj = {};
        headers.forEach((h, i) => { obj[h] = vals[i]; });
        return obj;
    });
}

function standingsRow(row) {
    const pos = row["Pos"];
    const team = row["Team"];
    const zone = getZone(pos);

    const tr = document.createElement("tr");
    if (zone) tr.dataset.zone = zone;

    // Position
    const tdPos = document.createElement("td");
    tdPos.className = "td-pos";
    tdPos.textContent = pos;
    tr.appendChild(tdPos);

    // Crest
    const tdCrest = document.createElement("td");
    tdCrest.className = "td-crest";
    tdCrest.appendChild(crestEl(team));
    tr.appendChild(tdCrest);

    // Name
    const tdName = document.createElement("td");
    tdName.className = "td-name";
    tdName.textContent = team;
    tr.appendChild(tdName);

    // Stats
    ["P", "W", "D", "L"].forEach(col => {
        const td = document.createElement("td");
        td.className = "td-stat";
        td.textContent = row[col];
        tr.appendChild(td);
    });

    // Points
    const tdPts = document.createElement("td");
    tdPts.className = "td-pts";
    tdPts.textContent = row["Pts"];
    tr.appendChild(tdPts);

    return tr;
}

// ── Build Comparison Row ──────────────────────────────────────────────────────
function comparisonRow(row) {
    const team = row["Team"];
    const actualPos = parseInt(row["Actual Pos"]);
    const actualPts = row["Actual Pts"];
    const predPos = parseInt(row["Pred Pos"]);
    const predPts = row["Pred Pts"];
    const diff = parseInt(row["Pos Diff"]); // Pred Pos - Actual Pos

    const zone = getZone(actualPos);
    const tr = document.createElement("tr");
    if (zone) tr.dataset.zone = zone;

    // Crest
    const tdCrest = document.createElement("td");
    tdCrest.className = "td-crest";
    tdCrest.appendChild(crestEl(team));
    tr.appendChild(tdCrest);

    // Name
    const tdName = document.createElement("td");
    tdName.className = "td-name";
    tdName.textContent = team;
    tr.appendChild(tdName);

    // Actual Pos
    const tdAP = document.createElement("td");
    tdAP.style.fontWeight = "600";
    tdAP.textContent = actualPos;
    tr.appendChild(tdAP);

    // Actual Pts
    const tdAPts = document.createElement("td");
    tdAPts.className = "td-pts";
    tdAPts.textContent = actualPts;
    tr.appendChild(tdAPts);

    // Pred Pos
    const tdPP = document.createElement("td");
    tdPP.style.fontWeight = "600";
    tdPP.textContent = predPos;
    tr.appendChild(tdPP);

    // Pred Pts
    const tdPPts = document.createElement("td");
    tdPPts.className = "td-pts";
    tdPPts.textContent = predPts;
    tr.appendChild(tdPPts);

    // Delta
    // diff > 0 means model placed them LOWER (worse) than actual → red ↑ (overachieved vs model)
    // diff < 0 means model placed them HIGHER (better) than actual → green ↓ (underachieved vs model)
    // diff = 0 means exact match
    const tdDelta = document.createElement("td");
    const delta = document.createElement("span");

    if (diff === 0) {
        delta.className = "delta same";
        delta.textContent = "=";
    } else if (diff > 0) {
        // Model ranked them too low — they beat the model's expectation
        delta.className = "delta down";
        delta.textContent = `↑ ${diff}`;
    } else {
        // Model ranked them too high — they finished below the model's expectation
        delta.className = "delta up";
        delta.textContent = `↓ ${Math.abs(diff)}`;
    }

    tdDelta.appendChild(delta);
    tr.appendChild(tdDelta);

    return tr;
}

// ── Fetch & Render ────────────────────────────────────────────────────────────
async function loadAndRender() {
    try {
        const [actualText, predictedText, comparisonText] = await Promise.all([
            fetch("outputs/actual_standings.csv").then(r => r.text()),
            fetch("outputs/predicted_standings.csv").then(r => r.text()),
            fetch("outputs/standings_comparison.csv").then(r => r.text()),
        ]);

        const actualData = parseCSV(actualText);
        const predictedData = parseCSV(predictedText);
        const comparisonData = parseCSV(comparisonText);

        const actualBody = document.getElementById("actual-body");
        const predictedBody = document.getElementById("predicted-body");
        const comparisonBody = document.getElementById("comparison-body");

        actualData.forEach(row => actualBody.appendChild(standingsRow(row)));
        predictedData.forEach(row => predictedBody.appendChild(standingsRow(row)));
        comparisonData.forEach(row => comparisonBody.appendChild(comparisonRow(row)));

    } catch (err) {
        console.error("Failed to load standings data:", err);
        document.querySelector("main").insertAdjacentHTML("afterbegin", `
      <div style="background:#fef2f2;color:#b91c1c;padding:16px 24px;margin:24px 0;
                  border-radius:8px;font-size:0.85rem;border:1px solid #fecaca;">
        <strong>Could not load data.</strong> Serve the project with a local HTTP server:<br>
        <code style="font-family:monospace;margin-top:6px;display:block">python -m http.server 8000</code>
        Then open <code>http://localhost:8000</code>
      </div>
    `);
    }
}

document.addEventListener("DOMContentLoaded", loadAndRender);
