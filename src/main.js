const state = { profiles: [], relationships: {}, stats: {} };

async function loadJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) throw new Error(`Unable to load ${path}`);
    return response.json();
}

function renderStats() {
    const labels = [
        ["followers", "Followers"], ["following", "Following"], ["mutual", "Mutual"],
        ["followers_not_followed", "Not followed back"], ["following_not_following_back", "Non-mutual following"]
    ];
    document.getElementById("stats").innerHTML = labels.map(([key, label]) =>
        `<article class="stat"><strong>${state.stats[key] ?? state.relationships[key]?.length ?? 0}</strong><span>${label}</span></article>`
    ).join("");
}

function renderFollowers() {
    const query = document.getElementById("search").value.toLowerCase();
    const filter = document.getElementById("filter").value;
    const mutual = new Set(state.relationships.mutual || []);
    const notFollowed = new Set(state.relationships.followers_not_followed || []);
    const visible = state.profiles.filter(([login]) => {
        const matchesQuery = login.toLowerCase().includes(query);
        const matchesFilter = filter === "all" || (filter === "mutual" && mutual.has(login)) ||
            (filter === "not-followed" && notFollowed.has(login));
        return matchesQuery && matchesFilter;
    });
    document.getElementById("followers").innerHTML = visible.map(([login, avatar]) =>
        `<a class="profile" href="https://github.com/${encodeURIComponent(login)}" target="_blank" rel="noopener">
          <img src="${avatar}" alt="" loading="lazy"><span>${login}</span></a>`
    ).join("") || "<p>No followers match this filter.</p>";
}

async function run() {
    try {
        [state.profiles, state.relationships, state.stats] = await Promise.all([
            loadJson("Dataset.json"), loadJson("reports/relationships.json"), loadJson("reports/community_stats.json")
        ]);
        document.getElementById("status").textContent = `Updated ${state.stats.updated_at || "not yet"}`;
        renderStats();
        renderFollowers();
    } catch (error) {
        document.getElementById("status").textContent = "The community report is unavailable.";
    }
}

document.getElementById("search").addEventListener("input", renderFollowers);
document.getElementById("filter").addEventListener("change", renderFollowers);
document.getElementById("theme-toggle").addEventListener("click", () => {
    document.body.classList.toggle("light");
});
run();
