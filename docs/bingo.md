# Bingo goals

***

## Weekly Bingo Board

This is an interactive bingo board that's updated weekly.

<div id="seed-label" style="padding-bottom: 5px;"></div>
<div id="grid-wrapper">
  <div id="grid"></div>
</div>

<style>
/* Wrapper takes full width minus margins */
#grid-wrapper {
    width: 100%;
    max-width: 100vw;
    padding: 1px;
    box-sizing: border-box;
}

/* Grid scales to available width */
#grid {
    width: 60%;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 4px;
}

/* Square cells */
.grid-cell {
    aspect-ratio: 1 / 1;
    border: 1px solid #888;
    border-radius: 6px;
    cursor: pointer;
    user-select: none;

    display: flex;
    justify-content: center;
    align-items: center;

    padding: 1px;
    text-align: center;

    /* Make text auto-fit */
    font-size: min(3.2vw, 18px);
    line-height: 1.1;

    transition: background-color 0.15s, color 0.15s;
}

/* OFF state */
.grid-off {
    background-color: #f8f8f8;
    color: #333;
}

/* ON state */
.grid-on {
    background-color: #66aaff;
    color: white;
}
</style>

<script>
// ---------- Seeded RNG (Mulberry32) ----------
function mulberry32(seed) {
    return function() {
        let t = seed += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
}

// ---------- Determine Current Week of the Year ----------
function getWeekNumber(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
}

const seed = getWeekNumber(new Date());
document.getElementById("seed-label").innerText = `Seed: ${seed}`;

const rng = mulberry32(seed);

// ---------- Options ----------
const options = [
  "White Outfit","Blue Outfit","Yellow Outfit","Fuschia Outfit","Orange Outfit","Green/Blue Outfit",
  "Pink Outfit","2 Outfits","3 Outfits","3 Keys in East","3 Keys in North","3 Keys in West",
  "3 Keys in South","1 Key in each area","2 Keys in 3 areas","6 Keys","8 Keys","3 Monoliths in East",
  "3 Monoliths in North","3 Monoliths in West","3 Monoliths in South","1 Monolith in each area",
  "2 Monoliths in 3 areas","6 Monoliths","8 Monoliths","10 Monoliths","3 Modules in East",
  "5 Modules in East","7 Modules in East","3 Modules in North","5 Modules in North","7 Modules in North",
  "3 Modules in West","5 Modules in West","7 Modules in West","3 Modules in South","5 Modules in South",
  "7 Modules in South","2 Modules in each area","3 Modules in 3 areas","8 Modules","10 Modules",
  "12 Modules","South Pillar","2 Pillars","3 Pillars","12 bits in East","12 bits in North",
  "12 bits in West","12 bits in South","Diamond Shotgun","Railgun","Beat the Waterfall Arena",
  "Bullet Deflect Upgrade","Bullet Absorb Upgrade","2 Sword Upgrades","2 Dash Upgrades",
  "2 Grenade Upgrades","Beat Soccer Kid","Kill North Boss","Kill West Boss","Kill Archer",
  "Kill 3 Bosses","Kill 2 Bosses in South","No Sword upgrades","No Dash upgrades",
  "Don't pick up any Guns","Don't die","Pet the Dog in 2 areas",
  "Kill a boss using only basic attacks","Complete the tutorial without using the Pistol"
];

// ---------- Pick 25 Unique ----------
function pickRandomItems(list, count) {
    const copy = [...list];
    const result = [];
    for (let i = 0; i < count; i++) {
        const index = Math.floor(rng() * copy.length);
        result.push(copy.splice(index, 1)[0]);
    }
    return result;
}

const chosen = pickRandomItems(options, 25);

// ---------- Render Grid ----------
function renderGrid(items) {
    const grid = document.getElementById("grid");

    items.forEach(label => {
        const cell = document.createElement("div");
        cell.className = "grid-cell grid-off";
        cell.textContent = label;

        // Toggle ON/OFF
        cell.addEventListener("click", () => {
            cell.classList.toggle("grid-on");
            cell.classList.toggle("grid-off");
        });

        grid.appendChild(cell);
    });
}

renderGrid(chosen);
</script>


## BingoSync
Below are some bingo goals in the Bingosync format that you can use for playing bingo / races.

```json
[
  {"name": "White Outfit"},
  {"name": "Blue Outfit"},
  {"name": "Yellow Outfit"},
  {"name": "Fuschia Outfit"},
  {"name": "Orange Outfit"},
  {"name": "Green/Blue Outfit"},
  {"name": "Pink Outfit"},
  {"name": "2 Outfits"},
  {"name": "3 Outfits"},
  {"name": "3 Keys in East"},
  {"name": "3 Keys in North"},
  {"name": "3 Keys in West"},
  {"name": "3 Keys in South"},
  {"name": "1 Key in each area"},
  {"name": "2 Keys in 3 areas"},
  {"name": "6 Keys"},
  {"name": "8 Keys"},
  {"name": "3 Monoliths in East"},
  {"name": "3 Monoliths in North"},
  {"name": "3 Monoliths in West"},
  {"name": "3 Monoliths in South"},
  {"name": "1 Monolith in each area"},
  {"name": "2 Monoliths in 3 areas"},
  {"name": "6 Monoliths"},
  {"name": "8 Monoliths"},
  {"name": "10 Monoliths"},
  {"name": "3 Modules in East"},
  {"name": "5 Modules in East"},
  {"name": "7 Modules in East"},
  {"name": "3 Modules in North"},
  {"name": "5 Modules in North"},
  {"name": "7 Modules in North"},
  {"name": "3 Modules in West"},
  {"name": "5 Modules in West"},
  {"name": "7 Modules in West"},
  {"name": "3 Modules in South"},
  {"name": "5 Modules in South"},
  {"name": "7 Modules in South"},
  {"name": "2 Modules in each area"},
  {"name": "3 Modules in 3 areas"},
  {"name": "8 Modules"},
  {"name": "10 Modules"},
  {"name": "12 Modules"},
  {"name": "South Pillar"},
  {"name": "2 Pillars"},
  {"name": "3 Pillars"},
  {"name": "12 bits in East"},
  {"name": "12 bits in North"},
  {"name": "12 bits in West"},
  {"name": "12 bits in South"},
  {"name": "Diamond Shotgun"},
  {"name": "Railgun"},
  {"name": "Beat the Waterfall Arena"},
  {"name": "Bullet Deflect Upgrade"},
  {"name": "Bullet Absorb Upgrade"},
  {"name": "2 Sword Upgrades"},
  {"name": "2 Dash Upgrades"},
  {"name": "2 Grenade Upgrades"},
  {"name": "Beat Soccer Kid"},
  {"name": "Kill North Boss"},
  {"name": "Kill West Boss"},
  {"name": "Kill Archer"},
  {"name": "Kill 3 Bosses"},
  {"name": "Kill 2 Bosses in South"},
  {"name": "No Sword upgrades"},
  {"name": "No Dash upgrades"},
  {"name": "Don't pick up any Guns"},
  {"name": "Don't die"},
  {"name": "Pet the Dog in 2 areas"},
  {"name": "Kill a boss using only basic attacks"},
  {"name": "Complete the tutorial without using the Pistol"}
]
```


