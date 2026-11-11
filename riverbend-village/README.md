# Riverbend Village

Visuals are an original blocky style inspired by cube-building games — not affiliated with Minecraft.

A charming single-file browser game for children ages 8–12. Help a small village solve a dry-season water shortage by exploring, listening to villagers, settling disagreements fairly, building water systems, guessing what a 7-day test will do, and improving your design.

**Level 2: Indus Valley** (`indus/index.html`) is a follow-up level. Over six seasons the monsoon weakens and a river shrinks. Kids plan ahead for three fictional cities inspired by Harappa/Mohenjo-daro, Dholavira, and Lothal, adapt with limited bricks and workers, plan careful moves, welcome newcomers fairly, and guess what the dry seasons will do. Migration is treated as a normal, dignified choice — not a failure. The game is a thinking tool, not a historical forecast.

## How to open

1. Open `index.html` in a modern browser (Chrome, Firefox, Safari, or Edge), **or**
2. From this folder, run a simple local server:

```bash
cd /workspace/riverbend-village
python3 -m http.server 8765
```

Then visit: http://localhost:8765/

Level 2 is at: http://localhost:8765/indus/

No internet connection or CDN is required — CSS and JavaScript are inline.

## How to play (about 15–25 minutes)

1. **Start** — Read the dry-season challenge, then click **Start Exploring**.
2. **Explore** — Look at the land (Dry Hill, Riverside, Low Fields, Near the Well, Downstream). Where people live shapes how they think about water. Click villagers (Maya, Arun, Rosa, Eli, Jordan) to learn their home and habit. A **Listening** meter fills as you talk, and shows how sure your forecast is. Open **Needs** anytime.
3. **Disagreements** — Neighbors may disagree about water. Hear both sides and choose a fix. Fair, win-win ideas earn the most **Trust Points**. Those points unlock leader powers in the **Leader** panel: Village Meeting, Helping Hands, and a Sharing Plan.
4. **Build** — Pick a card from the build menu, then tap a glowing **Build** plot. Use **Connect Mode** to link collectors/pumps to tanks. You start with **10 materials**.
5. **Guess, then test** — Click **Run 7 Days**, guess whether the Well, Farm, Health, and Trust will go up, stay the same, or go down, then watch the week (Slow or Skip available).
6. **Reflect** — Read your Village Report Card (including your guesses and a whole-village note), answer 3 short questions, then **Improve My Design**, **Start Again**, or **Finish for Today**.
7. Earn the **Community Inventor** badge when several metrics look healthy and fair.
8. From the intro or finish screen, open **Level 2: Indus Valley** when you are ready for the next challenge.

## Parent / Educator

Use the **Parent** button (not part of the main kid flow) for learning goals, skills, discussion prompts, and a record of the child's design. Skills include systems thinking, perspective-taking, fair conflict resolution, and hypothesis testing. Villagers are fictional characters in a learning game.

## Level 2: Indus Valley (about 15–20 minutes)

1. **Start** — You are a young council helper for three fictional cities (River City, Dry-Land City, Coastal Trade City) and the East Villages.
2. **Explore** — Click people and cities. The land shapes how they think about water. A **Listening** meter fills as you talk.
3. **Watch the climate** — Rain and river meters fall over 6 seasons. Plan ahead.
4. **Adapt** — Spend limited bricks and workers on reservoirs, wells, grain stores, hardy crops, drain repairs, water sharing, or a trade route.
5. **Settle disagreements** — Fair, win-win fixes earn Trust Points and unlock council powers (Council Meeting, Extra Bricks & Hands, Fair Welcome Plan).
6. **A careful move** — When a city cannot support everyone, plan where families go. Moving is a normal choice, not a failure. A fair welcome can turn newcomers into helpers.
7. **Guess, then see** — Before the last two dry seasons, guess whether River City's water, food, and Trust will go up, stay the same, or go down.
8. **Report** — See how many families stayed safe and fed, how fair the moves were, what the cities left behind, and how your guesses compared. Earn the **Indus Council Helper** badge.

Use **Real or imagined?** for careful, kid-level history notes (what is known, what is debated, and what this game invents). Characters and events are fictional. There is no violence.

Live play links (GitHub Pages):

- Riverbend Village: https://biju5555-arch.github.io/skhand/riverbend-village/
- Level 2: Indus Valley: https://biju5555-arch.github.io/skhand/riverbend-village/indus/

## Files

- `index.html` — complete playable village game (Level 1)
- `indus/index.html` — complete playable Indus Valley level (Level 2)
- `README.md` — this file
