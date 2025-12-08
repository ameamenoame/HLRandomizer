# Bingo goals

***

## Weekly Bingo Board

This is an interactive bingo board that's updated weekly. 

Tile features: Left click to toggle. Right click to mark a star. +/- to increment / decrement the tile's counter.

<p id="seed-label"></p>

<div style="margin-bottom: 12px;">
  <input id="seed-input" type="text" placeholder="Enter seed (number)"
         style="padding:6px; font-size:14px; width:160px;"/>
  <button id="seed-button" style="padding:6px 10px; font-size:14px;">Set Seed</button>
</div>

<div id="grid-wrapper">
  <div id="grid"></div>
</div>


## BingoSync
Below are some bingo goals in the Bingosync format that you can use for playing bingo / races.

```json
[
  { "name": "White Outfit" },
  { "name": "Blue Outfit" },
  { "name": "Yellow Outfit" },
  { "name": "Fuschia Outfit" },
  { "name": "Orange Outfit" },
  { "name": "Green/Blue Outfit" },
  { "name": "Ochre Outfit" },
  { "name": "Kill a main boss without healing" },
  { "name": "Kill a main boss without dashing" },
  { "name": "Kill a boss 1 second right after dying" },
  { "name": "Do 3 cough skips" },
  { "name": "Talk to every NPC" },
  { "name": "Do 2 twirl skips" },
  { "name": "Archer intro skip" },
  { "name": "Hit all laser triggers" },
  { "name": "Pink Outfit" },
  { "name": "2 Outfits" },
  { "name": "3 Outfits" },
  { "name": "3 Keys in East" },
  { "name": "3 Keys in North" },
  { "name": "3 Keys in West" },
  { "name": "3 Keys in South" },
  { "name": "1 Key in each area" },
  { "name": "2 Keys in 3 areas" },
  { "name": "6 Keys" },
  { "name": "8 Keys" },
  { "name": "3 Monoliths in East" },
  { "name": "3 Monoliths in North" },
  { "name": "3 Monoliths in West" },
  { "name": "3 Monoliths in South" },
  { "name": "1 Monolith in each area" },
  { "name": "2 Monoliths in 3 areas" },
  { "name": "6 Monoliths" },
  { "name": "8 Monoliths" },
  { "name": "10 Monoliths" },
  { "name": "3 Modules in East" },
  { "name": "5 Modules in East" },
  { "name": "7 Modules in East" },
  { "name": "3 Modules in North" },
  { "name": "5 Modules in North" },
  { "name": "7 Modules in North" },
  { "name": "3 Modules in West" },
  { "name": "5 Modules in West" },
  { "name": "7 Modules in West" },
  { "name": "3 Modules in South" },
  { "name": "5 Modules in South" },
  { "name": "7 Modules in South" },
  { "name": "2 Modules in each area" },
  { "name": "3 Modules in 3 areas" },
  { "name": "8 Modules" },
  { "name": "10 Modules" },
  { "name": "12 Modules" },
  { "name": "South Pillar" },
  { "name": "2 Pillars" },
  { "name": "3 Pillars" },
  { "name": "12 bits in East" },
  { "name": "12 bits in North" },
  { "name": "12 bits in West" },
  { "name": "12 bits in South" },
  { "name": "Diamond Shotgun" },
  { "name": "Impact Railgun" },
  { "name": "Beat the Waterfall Arena" },
  { "name": "Bullet Deflect Upgrade" },
  { "name": "Bullet Absorb Upgrade" },
  { "name": "2 Sword Upgrades" },
  { "name": "2 Dash Upgrades" },
  { "name": "2 Grenade Upgrades" },
  { "name": "Beat Soccer Kid" },
  { "name": "Kill North Boss" },
  { "name": "Kill West Boss" },
  { "name": "Kill Archer" },
  { "name": "Kill 3 Bosses" },
  { "name": "Kill 2 Bosses in South" },
  { "name": "No Sword upgrades" },
  { "name": "No Dash upgrades" },
  { "name": "Don't pick up any Guns" },
  { "name": "Don't die" },
  { "name": "Pet the Dog in 2 areas" },
  { "name": "Kill a boss using only basic attacks" },
  { "name": "Complete the tutorial without using the Pistol" }
]
```



<style>
#grid-wrapper {
    width: 50%;
    padding: 10px;
    box-sizing: border-box;
}

#grid {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
}

.grid-cell {
    aspect-ratio: 1 / 1;
    border: 1px solid #888;
    border-radius: 6px;
    cursor: pointer;
    user-select: none;

    display: flex;
    justify-content: center;
    align-items: center;

    padding: 4px;
    text-align: center;

    font-size: min(3.2vw, 18px);
    line-height: 1.1;

    transition: background-color 0.15s, color 0.15s;
}

.grid-off {
    background-color: #f8f8f8;
    color: #333;
}

.grid-on {
    background-color: #66aaff;
    color: white;
}
/* Counter appears in the top-right corner */
.grid-counter {
    position: absolute;
    top: 2px;
    right: 4px;
    font-size: 1.5rem;
    background: rgba(255, 255, 255, 0.7);
    padding: 1px 4px;
    border-radius: 3px;
    pointer-events: none;
}

/* Hover controls container */
.grid-controls {
    position: absolute;
    top: 2px;
    left: 2px;
    display: flex;
    gap: 3px;
    opacity: 0;
    transition: opacity 0.15s;
}

/* Show controls on hover */
.grid-cell:hover .grid-controls {
    opacity: 1;
}

/* Buttons for + and - */
.grid-btn {
    font-size: 1.1rem;
    padding: 1px 4px;
    background: #ffffffcc;
    border: 1px solid #aaa;
    border-radius: 3px;
    cursor: pointer;
    user-select: none;
}

.grid-btn:hover {
    background: #e6e6e6;
}
/* star icon (hidden by default) */
.grid-star {
    position: absolute;
    top: 2px;
    right: 4px;
    font-size: 18px;
    pointer-events: none; /* clicks shouldn't hit the star itself */
    opacity: 0.85;
    display: none;
}
.grid-cell.star-on .grid-star {
    display: block;
}


</style>

<script>
// ---------- Seeded RNG ----------
function mulberry32(seed) {
    return function() {
        let t = seed += 0x6D2B79F5;
        t = Math.imul(t ^ t >>> 15, t | 1);
        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
    }
}

// ---------- Week Seed ----------
function getWeekNumber(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
}

// ---------- List of Options ----------
const options = [
  "White Outfit",
  "Blue Outfit",
  "Yellow Outfit",
  "Fuschia Outfit",
  "Orange Outfit",
  "Green/Blue Outfit",
  "Pink Outfit",
  "2 Outfits",
  "3 Outfits",
  "3 Keys in East",
  "3 Keys in North",
  "3 Keys in West",
  "3 Keys in South",
  "1 Key in each area",
  "2 Keys in 3 areas",
  "6 Keys",
  "8 Keys",
  "3 Monoliths in East",
  "3 Monoliths in North",
  "3 Monoliths in West",
  "3 Monoliths in South",
  "1 Monolith in each area",
  "2 Monoliths in 3 areas",
  "6 Monoliths",
  "8 Monoliths",
  "10 Monoliths",
  "3 Modules in East",
  "5 Modules in East",
  "7 Modules in East",
  "3 Modules in North",
  "5 Modules in North",
  "7 Modules in North",
  "3 Modules in West",
  "5 Modules in West",
  "7 Modules in West",
  "3 Modules in South",
  "5 Modules in South",
  "7 Modules in South",
  "2 Modules in each area",
  "3 Modules in 3 areas",
  "8 Modules",
  "10 Modules",
  "12 Modules",
  "South Pillar",
  "2 Pillars",
  "3 Pillars",
  "12 bits in East",
  "12 bits in North",
  "12 bits in West",
  "12 bits in South",
  "Diamond Shotgun",
  "Impact Railgun",
  "Beat the Waterfall Arena",
  "Bullet Deflect Upgrade",
  "Bullet Absorb Upgrade",
  "2 Sword Upgrades",
  "2 Dash Upgrades",
  "2 Grenade Upgrades",
  "Beat Soccer Kid",
  "Kill North Boss",
  "Kill West Boss",
  "Kill Archer",
  "Kill 3 Bosses",
  "Kill 2 Bosses in South",
  "No Sword upgrades",
  "No Dash upgrades",
  "Don't pick up any Guns",
  "Don't die",
  "Pet the Dog in 2 areas",
  "Kill a boss using only basic attacks",
  "Complete the tutorial without using the Pistol",

  "Kill a main boss without healing",
  "Kill a main boss without dashing",
  "Kill a boss 1 second right after dying",

  "Do 3 cough skips" ,
  "Talk to every NPC" ,
  "Do 2 twirl skips" ,
  "Archer intro skip" ,
  "Hit all laser triggers" ,
];


// ---------- Pick N Unique Items ----------
function pickRandomItems(list, count, rng) {
    const copy = [...list];
    const result = [];
    for (let i = 0; i < count; i++) {
        const index = Math.floor(rng() * copy.length);
        result.push(copy.splice(index, 1)[0]);
    }
    return result;
}

// ---------- Render a Grid ----------
function renderGridFromSeed(seedValue) {
    const grid = document.getElementById("grid");
    grid.innerHTML = "";  // Clear old grid

    const rng = mulberry32(seedValue);
    const chosen = pickRandomItems(options, 25, rng);

    chosen.forEach(label => {
        const cell = document.createElement("div");
cell.className = "grid-cell grid-off";
cell.style.position = "relative";  // needed for overlay elements

// Main label
const text = document.createElement("div");
text.textContent = label;

// Counter (starts at 0)
let count = 0;
const counter = document.createElement("div");
counter.className = "grid-counter";
counter.textContent = "";

// Hover controls (+ and -)
const controls = document.createElement("div");
controls.className = "grid-controls";

// Buttons
const btnPlus = document.createElement("div");
btnPlus.className = "grid-btn";
btnPlus.textContent = "+";

const btnMinus = document.createElement("div");
btnMinus.className = "grid-btn";
btnMinus.textContent = "-";

// Increment
btnPlus.addEventListener("click", (event) => {
    event.stopPropagation();
    count++;
    counter.textContent = count > 0 ? count : "";
});

// Decrement (min 0)
btnMinus.addEventListener("click", (event) => {
    event.stopPropagation();
    if (count > 0) count--;
    counter.textContent = count > 0 ? count : "";
});

// Add buttons to controls
controls.appendChild(btnPlus);
controls.appendChild(btnMinus);

// Toggle ON/OFF by clicking cell body
cell.addEventListener("click", () => {
    cell.classList.toggle("grid-on");
    cell.classList.toggle("grid-off");
});

const star = document.createElement("div");
star.className = "grid-star";
star.textContent = "★";

// disable browser context menu
cell.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    cell.classList.toggle("star-on");
});


// Compose cell
cell.appendChild(text);
cell.appendChild(counter);
cell.appendChild(controls);
cell.appendChild(star);

grid.appendChild(cell);
    });
}

// ---------- Initialize with weekly seed ----------
const defaultSeed = getWeekNumber(new Date());
renderGridFromSeed(defaultSeed);
seedInput = document.getElementById("seed-input");
seedInput.value = defaultSeed;
document.getElementById("seed-label").innerText = "Current week's seed: "+ defaultSeed;


// ---------- Button Logic ----------
document.getElementById("seed-button").addEventListener("click", () => {
    const seedInput = document.getElementById("seed-input");
    let seedValue = seedInput.value.trim();

    // If empty, generate a random seed
    if (seedValue === "") {
        seedValue = Math.floor(Math.random() * 0xFFFFFFFF);
        seedInput.value = seedValue; // populate input with the chosen seed
    }

    const seed = Number(seedValue);

    if (isNaN(seed)) {
        alert("Please enter a valid numeric seed.");
        return;
    }

    renderGridFromSeed(seed);
});
</script>