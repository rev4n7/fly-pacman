# Fly-Pacman: The Whole Story, Explained Simply

*A debrief of everything in this project: what it is, how it works from the very basics, every step we took, every mistake we made and how we fixed it, and how to talk about it honestly.*

*Written 2026-09-17.*

---

## How to read this

- **Part 1** is the whole project in one breath.
- **Part 2** teaches the basics from zero, with an everyday comparison for every idea.
- **Part 3** introduces the "characters": the brain cells that star in the game.
- **Part 4** walks through one moment of the game, slowly.
- **Part 5** is the story of the build: what we tried, what broke, and how we fixed it.
- **Parts 6–13** are the reference: real vs. pretend, limitations, discoveries, numbers, files, how to run it, likely questions, and LinkedIn advice.
- **Part 13½** explains every gauge on the dashboard.
- **Part 14** is a word list.

---

# PART 1 — The whole project in one breath

Imagine a video game of Pac-Man. Usually **you** steer Pac-Man with the arrow keys.

In this game, **nobody steers**. The player is a **fruit fly**, and the fly steers itself using a **pretend brain inside the computer**.

That pretend brain isn't made up. Scientists took a **real male fruit fly**, mapped **every wire in its brain and nerve cord**, and put the map online. We downloaded a piece of that map, about **1,900 brain cells** and **1.15 million connections**, and built a computer brain that follows the same wiring.

Then we plugged that brain into the game:
- When the fly **sees pellets**, its "chase small things" brain cells light up and it turns toward them.
- When a **ghost rushes at it**, its "something is coming at me!" cells light up, those set off its **emergency jump button**, and the fly escapes.

**Nowhere in the code does it say "if a ghost is close, run away."** The fly only runs if the electrical buzz inside its pretend brain actually reaches the jump button. A panel beside the game shows the brain cells lighting up live, so you can watch it "think."

---

# PART 2 — The basics, from zero

## 2.1 What is a brain cell (neuron)?

> **Analogy: a person in a giant game of telephone.**

Your brain, and a fly's brain, is made of tiny cells called **neurons**. Each neuron is like a person in a huge crowd:
- It **listens** to the people connected to it.
- If it hears enough excitement, it **shouts** to the people it's connected to.
- Then it takes a tiny breath before it can shout again.

One neuron alone is simple. Hundreds of thousands passing messages is how a fly sees, hears, walks and escapes.

## 2.2 What is a "spike"?

> **Analogy: a sneeze.**

When a neuron "shouts," it sends a very quick electrical blip called a **spike** (or "firing").
- A spike is **all-or-nothing**: you don't half-sneeze.
- It's **very fast**: about a thousandth of a second.
- Information is in **how often** a neuron spikes. One spike a second is calm; a hundred spikes a second is screaming.

The panel shows this as brightness. Brighter dot = more spikes = more excited.

## 2.3 What is a synapse?

> **Analogy: a garden hose between two buckets.**

A **synapse** is the connection point where one neuron passes its message to another.

The connectome tells us **how many synapses** link two neurons. Think of that as **how many hoses** run between them:
- 1 hose: a trickle, a weak connection.
- 300 hoses: a flood, a very strong connection.

In our model, **more synapses = stronger push**. That's a simplification (real synapses differ in size), but it's the standard way scientists use this kind of data.

## 2.4 Gas pedals and brakes (excitatory and inhibitory)

> **Analogy: cheerleaders and librarians.**

Not every message says "get excited!" Neurons use different chemicals, called **neurotransmitters**:

| Chemical | What it does | Analogy |
|---|---|---|
| **Acetylcholine** | makes the next neuron **more** likely to fire | 📣 a cheerleader yelling "GO GO GO!" |
| **GABA** | makes the next neuron **less** likely to fire | 🤫 a librarian saying "shhh!" |
| **Glutamate** | in the fly brain, mostly **less** likely | 🤫 another librarian |

A neuron fires when the cheering beats the shushing. The dataset **predicts** each neuron's chemical from what its synapses look like in the microscope images. It's a very good prediction, but still a prediction.

## 2.5 What is a connectome?

> **Analogy: the complete wiring diagram of a house, or a map of every road in a city.**

A **connectome** is a full map of **which neurons connect to which, and with how many synapses**.

**How scientists made it:**
> **Analogy: slicing a loaf of bread and photographing every slice.**
1. They took a fly's brain and nerve cord and cut it into **thousands of ultra-thin slices**, far thinner than a hair.
2. They photographed every slice with an **electron microscope** (a super-powerful camera).
3. Computers plus human experts **traced each neuron from slice to slice**, like following one spaghetti noodle through a stack of photos.
4. They marked every synapse and labeled each neuron's type.

The map we used is called **MaleCNS v1.0**: the brain **and** nerve cord of a male fruit fly, about **167,000 neurons**. It was made by **Janelia Research Campus**, the **Cambridge Drosophila Connectomics Group**, and **Google**.

## 2.6 neuPrint and the token

> **Analogy: a library and a library card.**

- **neuPrint** is the online library where the connectome lives.
- **neuprint-python** is the tool that lets our code ask the library questions, like "Give me every connection between these 1,745 neurons."
- The **token** is your library card. You signed up and made one. It lives in the `.env` file. **Treat it like a password and never share that file.**

## 2.7 How our pretend neuron works (the "LIF" model)

> **Analogy: a bucket with a small hole in the bottom.**

Our brain uses the simplest realistic kind of neuron, called **Leaky Integrate-and-Fire (LIF)**. Picture every neuron as a **bucket of water**:

| Bucket | Neuron |
|---|---|
| Water poured in from the hoses | messages from other neurons ("integrate") |
| A small hole slowly draining it | charge naturally fading away ("leaky") |
| A line near the top | the **threshold** |
| When water reaches the line, the bucket **tips over** and empties | the neuron **fires a spike** and resets |
| The bucket needs a moment to stand back up | the **rest period** (refractory period) |
| Water from librarian hoses is *taken out* | inhibition |

So:
- A little water now and then drains away, and nothing happens.
- A lot of water fast fills the bucket past the line: SPIKE!

We didn't invent the bucket sizes. We copied the settings from a published fly-brain model (**Shiu et al., 2024, *Nature***):

| Setting | Value | Bucket version |
|---|---|---|
| Resting level | −52 mV | bucket's normal water level |
| Threshold | −45 mV | the tip-over line |
| Leak time | 20 ms | how fast the hole drains it |
| Hose-flow time | 5 ms | how long one splash keeps flowing |
| Rest after firing | 2.2 ms | time to stand back up |
| Travel delay | 1.8 ms | time for the message to go down the hose |
| Strength per synapse | 0.275 mV | how much water one hose adds |

*("mV" = millivolts, a tiny amount of electricity. "ms" = milliseconds, thousandths of a second.)*

## 2.8 How the brain ticks forward in time

> **Analogy: a flipbook.**

The computer can't run time smoothly, so it draws the brain like a flipbook, one tiny page at a time. Each page is **0.1 milliseconds**.
- The game shows **50 pictures per second** (one every 20 ms).
- So between two game pictures, the brain flips through **200 pages**.

On every page, every bucket gets its water added, drained and checked.

## 2.9 How the game "talks" to the brain

> **Analogy: rain on a tin roof.**

The game can't plug a camera into pretend neurons, so it does the next best thing. When something is in view, it makes the matching eye neurons receive **random little pings**, like raindrops. The more important the thing (a ghost rushing closer), the **heavier the rain**.
- Light drizzle: an occasional spike.
- Downpour: lots of spikes.

Scientists call this random-but-steady rain a **Poisson process**.

## 2.10 What is "looming"?

> **Analogy: a ball thrown at your face.**

When a ball is far away, it looks tiny and barely changes. As it gets close, it seems to **grow faster and faster**, and at the last moment it fills your view. That fast growth is **looming**, and it means *something is about to hit me*.

Flies have special neurons that detect exactly this. We compute it for each ghost:
- **How big the ghost looks:** θ = 2 × atan(ghost size ÷ (2 × distance))
- **How fast that's growing:** that growth speed goes into the looming neurons.

So a ghost **walking past sideways** doesn't grow, and the looming neurons stay quiet. A ghost **charging straight at the fly** grows fast, and they go wild.

## 2.11 Where each eye neuron looks (retinotopy and receptive fields)

> **Analogy: fans in a stadium, each with binoculars.**

Imagine a stadium around the fly. Each looming neuron is a **fan holding binoculars pointed at one patch of the field**:
- That patch is the neuron's **receptive field**.
- Fans sitting next to each other watch neighboring patches. That's **retinotopy**.

When a ghost appears in one spot, **only the fans watching that spot** start cheering. That's how the brain knows *where* the danger is. We worked out where each real neuron's binoculars point from the real data (Part 5, Chapter 4).

## 2.12 The blind spot

> **Analogy: the back of your head.**

A fly's eyes wrap almost all the way around, but there's a **narrow slice directly behind it** that no fan is watching. Ghosts sneaking up exactly from behind can't be seen, just like you can't see someone standing right behind you. The game shows it as a faint grey wedge behind the fly.

## 2.13 The Giant Fiber: the emergency button

> **Analogy: the big red fire-alarm lever.**

The fly has a special neuron, one on each side, called the **Giant Fiber**. It's one of the biggest, fastest neurons the fly has. When it fires, the fly **jumps and takes off**, which is why flies are so hard to swat. In our game, **one Giant Fiber spike = jump**.

## 2.14 Descending neurons: messengers from the brain to the body

> **Analogy: messengers running from headquarters down to the soldiers.**

The brain is in the head, but the legs and wings are in the body. **Descending neurons** carry commands from the head down. Our important ones:
- the **Giant Fiber** ("jump!"),
- **DNa02** ("turn this way"),
- **DNp02 / DNp11 / DNp04**, whose wiring suggests "danger in front / behind / below."

## 2.15 Invisible wires (electrical synapses)

> **Analogy: secret tunnels too thin for the camera.**

Most connections are **chemical synapses**, like the hoses, and the microscope can see them. Some neurons also connect through **electrical synapses**, tiny direct tunnels between cells. These are **too small to see in the images**, so they're **missing from the map**. This matters twice in our project (Part 7).

---

# PART 3 — Meet the cast (the neurons in the game)

| Character | Real name | Job | Analogy | Count in our brain |
|---|---|---|---|---|
| 👀 Looming spotters | **LC4, LPLC2, LC6** | detect "something is coming at me" | lookouts on a castle wall | 435 |
| 🟢 Small-thing spotters | **LC10a** | detect small objects (males use them to chase females); we use them to see pellets | a cat noticing a moving dot | 275 |
| 👂 Ears | **JO neurons** (Johnston's organ) | feel air vibrations near the antennae | feeling a breeze on your arm hair | 486 |
| 🚨 Emergency button | **Giant Fiber (DNp01)** | "JUMP NOW" | fire-alarm lever | 2 (left and right) |
| 🧭 Direction messengers | **DNp02, DNp11, DNp04, DNp06** | escape-related messengers | scouts yelling "danger ahead / behind / below" | 8 |
| 🦵 Jump muscle neuron | **TTMn** | powers the jumping leg | the leg's power switch | 2 |
| 🚗 Steering wheel | **DNa02** | turn left or right | a steering wheel | 2 |
| 🔗 Middlemen | 65 escape + 14 steering neurons | pass messages between spotters and buttons | relay runners | 79 |
| 🛑 Balancers (feedback) | 590 neurons | send messages back to keep things calm (and some excite) | teachers keeping a classroom from getting out of hand | 590 |

**Total: 1,887 neurons.**

---

# PART 4 — One moment of the game, in slow motion

The fly is munching pellets down a hallway. A red ghost comes around the corner ahead.

**⏱️ Every 1/50th of a second, this happens:**

**1. The game looks through the fly's eyes.**
- *Where is the ghost?* Straight ahead, 5 tiles away.
- *Can the fly see it?* We draw an invisible line from fly to ghost. If a wall blocks it, the fly can't see it.
- *Is it getting closer?* Yes. How fast is it growing in view? A little.
- *Can the fly feel its air?* Air travels along corridors, but only very close up, so not yet.
- *Pellets?* Several ahead, all visible.

**2. The game sprinkles "rain" on the right neurons.**
- Pellet-spotters (LC10a) watching straight ahead get a steady drizzle.
- Looming spotters watching straight ahead get a light drizzle.

**3. The brain flips through 200 pages.** Water pours through 1.15 million hoses:
- Spotters fire a few spikes.
- Middlemen get a little water, mostly below the line.
- The Giant Fiber bucket: a bit of water, but nowhere near the line.
- Steering neurons: left and right about equal, so go straight.

**4. The body reads the messengers.** No Giant Fiber spike, so keep walking straight.

**⏩ A second later, the ghost is 1.5 tiles away and charging.** It now grows **very fast** in view:
- Looming spotters watching the front get a **downpour** and fire rapidly.
- Their thousands of hoses flood the **Giant Fiber** bucket.
- **SPLASH, it crosses the line. SPIKE!** 🚨

**5. The body jumps.**
- **When:** immediately, because the Giant Fiber spiked.
- **Left or right?** It compares how busy the left-side escape messengers were with the right side over the last 0.3 s, and pushes away from the busier side.
- **Forward or backward?** It checks which looming spotters were firing and where they look. They look *ahead*, so jump **backward**.
- The fly **reverses** and **sprints** (9 tiles/s for 0.35 s) away from the ghost.

**6. If it lived, back to eating.** The spotters calm down, the Giant Fiber goes quiet, and the pellet-spotters take over steering again.

**Nobody told the fly "ghost = run."** The run happened because water filled the right bucket.

---

# PART 5 — The story of how we built it (and every fix along the way)

## Chapter 1 — Checking the fridge before cooking (scoping)

> **Analogy: before starting a recipe, open the fridge and check the ingredients are actually there.**

You asked for a fly whose escape and pellet-chasing come from **real** wiring. Before writing a game, I checked the real data had what we needed.

**Surprise #1: the library door was unlocked.**
- The official tool (`neuprint-python`) refuses to start without a token.
- But the neuPrint server itself was answering simple questions without one.
- So I did the early checking with plain web requests to the same server and the same dataset (`scoping/rawq.py`), and used the proper tool with your token for the real download.

**What I checked, and what I found:**

| Question | Answer |
|---|---|
| Is the Giant Fiber in the map? | ✅ Yes, called `DNp01`, one per side. |
| Do looming spotters connect to it? | ✅ Massively. **LC4 → Giant Fiber: 6,362 synapses. LPLC2: 4,862.** Its #1 and #2 inputs. |
| Which side connects to which? | ✅ **Left eye → left Giant Fiber only; right → right.** That's how the fly can tell left from right. |
| Does LC6 connect to the Giant Fiber? | ❌ Not directly. It passes through a middleman called PVLP151. |
| Giant Fiber → jump muscle neuron (TTMn)? | ⚠️ Only 20 (left) and 70 (right) visible synapses, because in real flies this link is mostly **invisible electrical tunnels** (see 2.15). |
| A real "go toward stuff" circuit? | ✅ **LC10a → AOTU middlemen → DNa02 steering.** Catch: it's the circuit **males use to chase females**, not a food circuit. |

## Chapter 2 — Your choices

I brought the problems to you, and you decided:
1. **"Giant Fiber spike = jump."** We didn't make up strengths for the invisible tunnels.
2. **Use the courtship-chase circuit for pellets**, and say so honestly.
3. **Your maze insight.** In a maze, ghosts chase you **down corridors**, so the fly must know **front from back**, not just left from right. That meant working out where each eye neuron looks.
4. **Blind spot: options C + D.** Keep the real blind spot, add hearing, and make the game easier with slower ghosts instead of changing the fly.

## Chapter 3 — Downloading the map (picking which neurons to take)

> **Analogy: picking a sports team by tryout scores, not by favorites.**

The whole fly has ~167,000 neurons. We needed the ones for seeing, hearing, escaping and steering.
- **Named stars:** looming spotters, pellet spotters, Giant Fiber, direction messengers, steering neurons. Chosen by name.
- **Middlemen, chosen by tryout rules** so I couldn't cherry-pick neurons that tell a nice story:
  - *Escape middlemen:* get ≥ 100 synapses from the spotters/ears **and** send ≥ 50 to a Giant Fiber.
  - *Steering middlemen:* get ≥ 100 from LC10a **and** send ≥ 100 to the steering neurons.
  - *Ears:* any ear neuron sending ≥ 5 synapses into the escape circuit.

**First download:** 1,155 neurons, 283,360 synapses.

## Chapter 4 — Which way is "front"? (figuring out where each eye neuron looks)

> **Analogy: you're handed a map with no compass and no labels. Which way is north?**

To know which spotters watch the front, we needed each neuron's viewing direction. The map gives 3D coordinates, but not which direction is "front" or "up."

**Step 1 — find the compass using landmarks.**
- The **smell centre** is at the front of a fly's head and the **memory centre** is at the back, so the direction from one to the other tells us which way is "back."
- There are motion neurons named for the **top** (HSN) and **bottom** (HSS) of the visual area, which tells us which way is "up."

**Step 2 — deal with the flipped wiring.**
> **Analogy: a road that crosses a bridge and ends up on the other side of the river.**

On the way from the eye into the brain, fly vision wiring **crosses over twice** (called "optic chiasms"), and each crossing flips front and back.
- The second crossing is in our data, and we **checked it**: neurons at the front of one area connect to the back of the next (a −0.97 match on the right, −0.94 on the left, where −1 would be a perfect flip).
- The first crossing happens in a part of the eye not in the dataset, so for that one we trusted textbook anatomy.
- Two flips cancel out, so **front of the lobula = front of the fly's view**.

**Step 3 — place every spotter.**
> **Analogy: working out where each fan in the stadium is aiming their binoculars.**

For each eye neuron, we found where its input synapses cluster in the visual area and how spread out they are:
- Where they cluster tells us **which direction it looks**.
- How spread out they are tells us **how wide its view is**.
- We used a reference neuron type (**Tm1**, which has one cell per column of the eye) as a grid, like graph paper.
- We converted positions to angles using approximate textbook eye coverage: from 15° past straight ahead to 160° behind, and 60° up and down. **The positions are real; the angle conversion is approximate.**

**A cool discovery here:** spotters that look at the **front** connect more to **DNp02**, spotters that look **behind** connect more to **DNp11**, spotters looking **down** connect more to **DNp04**, and LPLC2 spotters looking **up** connect more to the Giant Fiber. Both sides of the brain agree, and it matches a 2023 study (Dombrovski et al., *Nature*).

## Chapter 5 — Can flies hear? (adding ears)

You asked: *can a fly hear a noise and get scared?*
- Yes, in a way. Flies hear with their **antennae**, which wobble in air movement. They only notice things **very close**, like the air pushed by a swatter, not a shout across the room.
- The data showed ear neurons connected to the Giant Fiber, **directly and through middlemen**. Some middlemen are cheerleaders and **many are librarians**.

## Chapter 6 — The lopsided ears

> **Analogy: someone traced your left ear carefully but only sketched your right ear.**

The data had **243 left-ear neurons but only 101 right-ear neurons**, and the left ear → Giant Fiber had **679 synapses vs. 29** on the right. A real fly isn't that lopsided.
- **Why:** ear neurons start out in the antenna, which wasn't part of the imaged tissue, so they arrive "cut off" and are harder to trace and label.
- **Your choice (B): mirror the left ear onto the right**, like a mirror image of the well-traced side.
  - Each left-ear connection is copied to the same neuron type on the other side.
  - Every number is still real data, just reused.
  - The panel labels it `JO right*`.

**How the rule works:** we couldn't just use the dataset's "twin" labels, because they only paired about a third of the neurons. So the rule is: *a connection from the left ear to neuron type X on the left becomes a connection from the mirrored right ear to type X on the right. If there are several X's on the right, the connection is shared evenly between them.*

## Chapter 7 — Switching the brain on… and it had a seizure 😵

> **Analogy: a classroom where every kid cheers the others on, and there are no teachers.**

I built the pretend brain and ran my first tests:
- With nothing happening, it stayed quiet. ✅
- Then I showed it a strong looming threat for 0.3 seconds and **switched the threat off**… and **the brain kept going.** Activity **kept growing** after the threat was gone, and the Giant Fiber fired over 200 times a second forever.

**Detective work:** I checked which neurons kept it going. A group of **cheerleader middlemen** (PVLP122, DNp70, AVLP452, DNp103, …) were all cheering each other on in a loop. Once started, the cheering never stopped.

**Suspect: the spotters were cheering each other.** Looming spotters have lots of connections to each other, so I tried switching those off. It barely helped. Not guilty.

**Patch #1 (a band-aid): "tiredness."** Real neurons get tired when they fire a lot (called **adaptation**). I added a tiredness setting and found the smallest amount that stopped the seizure. It worked, but it was an **invented knob**, not real wiring.

**The real cause:** our tryout rules only picked neurons that pass messages **forward** to the Giant Fiber. We had left out most of the **librarians** that send "shhh" messages **back**. Brains need brakes.

**Real fix: add the teachers (the feedback layer).** A new, **neutral** tryout rule: *any* neuron, cheerleader or librarian, that gets **≥ 100 synapses from our circuit** and sends **≥ 100 back into it**. That added **590 neurons** (219 GABA, 45 glutamate, 311 acetylcholine, and a few others). The rule doesn't favor brakes; it takes whoever is strongly connected both ways.

**Result:** **the seizure stopped on its own, with zero tiredness.** So I **switched the invented tiredness knob off** (set it to 0). The brain grew to **1,745 downloaded neurons and 1.1 million synapses**.

## Chapter 8 — Test drives with a crash-test dummy

> **Analogy: testing a car on a track with a dummy before letting it on real roads.**

Before any game existed, I fed the brain fake scenes and checked its reactions:

| Fake scene | What the brain did |
|---|---|
| Nothing | stayed calm ✅ |
| Pellets on the left | steered left ✅ |
| Pellets on the right | steered right ✅ |
| Ghost from behind, eyes only | noticed only at ~1 tile, because of the **blind spot** ✅ realistic |
| Ghost walking past sideways | ignored it ✅ |
| Ghost hidden behind a wall | ignored it ✅ |

**Tuning the eyes:** at first the spotters were too jumpy. The fly panicked at ghosts 4–5 tiles away, and even at a ghost just walking past. I turned down how strongly "growing in view" excites the spotters. Now the fly jumps when a charging ghost is about **1.5–2 tiles** away.

## Chapter 9 — The front-or-back mystery

> **Analogy: the game of telephone. The first person hears the message perfectly, but by the end of the line it's garbled.**

I tested the escape direction by throwing ghosts at the fly from 12 directions, many times each:
- **Left vs. right: 95–100% correct.** ✅ Because each eye wires to its own-side Giant Fiber.
- **Front vs. back: 45–48% correct.** ❌ A coin flip. The simple rule "DNp11 (back) minus DNp02 (front)" almost always said "jump forward," partly because DNp11 also gets a push from the Giant Fiber itself.

**Attempt: let the messengers "vote" longer.** Maybe they needed more time to warm up, so I read them for up to 0.3 s after the first Giant Fiber spike. That only reached **65%**.

**Big question: is the front/back information in the messengers at all?** I built the smartest possible reader and tested it on directions it had never practised on:
- Reading the **eye spotters**: **100%**. The eyes know perfectly.
- Reading the **escape messengers**: **59%**.
- Reading **messengers + middlemen**: **68%**.

(I had planned to use a common toolkit called scikit-learn for this test. I wrote it with our existing tools instead, to avoid installing anything new.)

**Last check:** I scanned **every** messenger neuron in the whole fly that gets looming input, looking for a strong "front" or "back" one. None was strong. The most front-leaning, DNp05, gets 74% of its input from front-looking spotters.

**Conclusion:** the eyes know front from back, but in this wiring the message is weak by the time it reaches the messengers. Real flies probably solve this by **adjusting their leg posture before jumping**, which we don't simulate. This is a **real limitation**, not a code bug.

## Chapter 10 — The hearing surprise

> **Analogy: you'd expect a loud noise to make you jumpy, but it turns out your ears are mostly wired to people saying "calm down."**

**Problem 1: super-ears.** My first hearing formula let the fly "hear" ghosts **6–9 tiles away, through walls**, and panic-jump at nothing.

**Fix:** real near-field sound fades **extremely fast** with distance, roughly **distance × distance × distance**. I switched to that, added a minimum threshold (quiet = nothing), and made the "sound" travel **along corridors**, since air goes around corners.

**Problem 2: hearing made the fly slower to escape!** A ghost sneaking up from behind with ears **on** was caught **later** than with ears **off**.

**Detective work:** I tested the ears alone:
- Ears alone barely made the Giant Fiber fire.
- Ears **plus** a looming threat made the Giant Fiber fire **less** (from 6–7 spikes down to 0–1).

**Why:** most hearing middlemen are **librarians**. In this wiring, hearing **calms** the escape button.

**Honest caveat:** in real flies, part of the ear → Giant Fiber link is an **invisible electrical tunnel**. With it, real hearing might be more exciting than our model shows. In actual games, ears on vs. off made **no consistent difference**.

## Chapter 11 — Making the brain fast enough

> **Analogy: a postman who only visits houses that actually have mail.**

At first, every tiny step checked every connection. I rewrote it to only deliver messages from neurons that **actually spiked**, and only roll the "rain dice" for neurons that are receiving rain. **Result: one second of brain time now takes ~0.15 seconds to compute, about 6× faster than real time.**

## Chapter 12 — Building the game world

**The maze:** an original Pac-Man-style layout, 19 by 21 tiles, **181 pellets**, and a ghost house in the middle.

**The ghosts** follow classic Pac-Man personalities:
- 🔴 **Red:** heads straight for the fly.
- 🩷 **Pink:** aims 4 tiles *ahead* of the fly (tries to cut it off).
- 🩵 **Cyan:** uses Red's position to trap the fly from the other side.
- 🟠 **Orange:** chases when far, wanders off when close.
- Every 20 seconds they "scatter" to their corners for 5 seconds, then chase again.

**The fly's senses** (Part 4): line of sight for eyes, corridor distance for ears, pellets within 6 tiles.

**The fly's body:**
- **Walking** (3.5 tiles/s): at each crossroads, turn toward the side whose **DNa02 steering neuron** is more active. No U-turns while walking.
- **A little restlessness:** a tiny random drizzle into the steering neurons, so the fly wanders when nothing is in view. Real flies don't stand still either. *(Invented ingredient, labeled as such.)*
- **Jumping** (9 tiles/s for 0.35 s): triggered by any Giant Fiber spike.

## Chapter 13 — A window into the brain (the side panel)

> **Analogy: a hospital heart monitor, but for the fly's whole brain.**

- **EYES:** a circle with the fly in the middle. **Every dot is one real neuron, placed where it looks.**
  - Orange rings = looming spotters.
  - Green outer ring = pellet spotters.
  - Dots glow when firing. The dark wedge is the blind spot, and colored dots on the edge are ghosts in view.
- **EARS:** left and right hearing bars.
- **ESCAPE:** two Giant Fiber circles that **flash yellow** on each spike, plus bars for the direction messengers and the jump muscle neuron.
- **STEER:** left and right steering neurons.
- **MIDDLE LAYER:** 669 tiny squares, one per middleman or balancer. Orange = cheerleader, blue = librarian.

I also fixed small display issues after checking screenshots, like text running off the edge and a too-large blind-spot wedge.

## Chapter 14 — Two ways to read front vs. back

Because of the mystery in Chapter 9, I built **two options** you can swap with the **M** key:
- **"circuit":** read front/back from the escape messengers (DNp11 vs. DNp02). The purest option, but weak.
- **"eyes":** read front/back from **which real looming spotters fired**, weighted by where each looks. One step earlier in the brain, still simulated neurons, and not a flee rule.

In 36 two-minute test games (before the fixes in Chapter 15), "eyes" survived about **1 in 2** jumps and "circuit" about **1 in 5**.

## Chapter 15 — "Bruhhh the fly is dumb" 🕵️ (the detective story)

**Your report:** *the fly and a ghost were going the same direction, the ghost U-turned, and it killed the fly instantly.*

> **Analogy: a car crash investigation. Was it the driver's reflexes, the steering, or the road?**

**Suspect 1: "The fly is chasing ghosts."** The pellet spotters chase small things; maybe a ghost counted?
→ **Not guilty.** Ghost images don't feed the pellet spotters at all, and the fly steered slightly *away* from nearby ghosts.

**Suspect 2: "The brain reacts too slowly."**
→ **Not guilty.** I recreated your exact U-turn many times. The Giant Fiber fired **80 to 500 milliseconds before** the ghost reached the fly. The brain noticed in time.

**So the problem was the body.** I made the game **record the cause of every death**:

| Cause of death | "circuit" readout | "eyes" readout |
|---|---|---|
| Jumped **toward** the ghost | **30** | 1 |
| Jumped away, still caught | 30 | 32 |
| Brain fired but no takeoff | 3 | 0 |

**Finding A — the wrong-way jump.** The game you watched was on "circuit," which sent the fly **toward** the ghost in about **38% of jumps**. That's the "dumb" moment you saw.

**Finding B — my recharge-timer bug.** Even with "eyes," flies jumped the right way and still died, facing a ghost. I replayed one death **frame by frame**:
1. 73.46 s: Giant Fiber fires. ✅
2. 73.54 s: fly reverses and sprints away. ✅
3. A corner forces it toward a **second** ghost.
4. 73.84–74.10 s: the Giant Fiber fires **again and again**. The brain is screaming "JUMP!"
5. **But I had given jumping a 0.85-second recharge timer**, so the body **ignored the brain** and walked into the ghost. 💀

> **Analogy: a smoke alarm that goes off, but the sprinklers are "on cooldown."**

Real Giant Fibers can trigger another escape right away, so the timer was just wrong.

**Finding C — the sandwich.** About **3 out of 4** remaining deaths were by a **different ghost** from the one the fly escaped. The fly flees one ghost straight into another creeping up in its **blind spot**. Pac-Man ghosts are designed to trap you like that.

**The fixes:**
1. **Removed the recharge timer and the takeoff delay.** Brain says jump, body jumps. (Real Giant Fiber takeoffs start within milliseconds.)
2. **Made "eyes" the default readout.** Wrong-way jumps dropped to about **1%**.
3. **Slowed the ghosts from 3.0 to 2.0 tiles/s.** That's your option C: tune the game, not the fly.

**Results:**

| | Before | After |
|---|---|---|
| Wrong-way jumps (default mode) | ~38% | ~1% |
| How often caught | every ~10–20 s | every ~45 s |
| Escape jumps | — | ~11 per minute |

**Your own watch session after the fixes:** 7.8 minutes, **638 pellets** (the fly cleared the maze 3 times), **84 jumps**, **36 escapes survived**, caught **12 times** (about once every 39 s). You said: *"I love it."* 🎉

## Chapter 16 — This debrief

You asked for a full explanation so you understand your project before posting. You're reading it.

## Chapter 17 — Showing the real brain lighting up

You asked: *can we see the fly's brain glow when a threat approaches?* Great hook, and we did it **honestly**: no cartoon brain.

> **Analogy: the difference between a drawing of a city at night and a real satellite photo of its lights.**

**Step 1 — Download where everything really is.** The connectome doesn't just say who connects to whom; it records **where every synapse physically sits** in 3D. A new script (`flypac/fetch_anatomy.py`) downloaded:
- The **real 3D shapes** of the central brain and both optic lobes (lobula, lobula plate, medulla, lamina).
- **Every synapse location of all 1,745 simulated neurons: 12.7 million positions.**

**Step 2 — Flatten it into a picture.**
> **Analogy: squashing a 3D snow globe flat, looking at it from behind.**
- We look at the head **from behind**, so the fly's left is on the screen's left, matching the eye panel.
- We sort the synapse positions into little squares (pixels, each about 3 micrometres across).
- Each neuron gets a "footprint": the pixels where its synapses are.

**Step 3 — Make each neuron glow in its own footprint.** Every frame, each neuron's footprint lights up as brightly as it's firing, in its group's colour:
- orange = looming detectors
- green = pellet detectors
- blue = ears
- yellow = escape neurons like the Giant Fiber
- teal = steering
- amber / blue = middle cheerleaders / librarians

**Mistake #1 — the "everything or nothing" sample.** To save time I first asked the server for a random 8% of each neuron's synapses. The server picked **one** random number per batch instead of one per synapse, so most batches came back with **nothing** (only 136 of 1,745 neurons). Fix: take **all** synapses; the server squashes them into pixels before sending, so it only took 2 minutes.

**Mistake #2 — too bright to read.** In the first version the whole middle of the brain was white **all the time**, because hundreds of background feedback neurons overlap there and fire during normal foraging. You couldn't tell *what* was reacting.
- I compared four brightness settings side by side, at a calm moment and at a takeoff (`data/glow_options.png`).
- I also tried "glow = change from normal", the way scientists display real glowing-dye brain recordings (`data/glow_dff.png`).
- The winner was a **much gentler brightness curve** (0.9 → 0.25): calm foraging stays dark, and a ghost attack makes the brain **burst into light** (`data/glow_gain.png`).
- **Display-only choice:** the 590 feedback neurons are drawn at **45% brightness** so the escape pathway colours aren't buried. This is labelled on screen. It changes only the picture, not the simulation.

**Mistake #3 — too slow.** With the brain picture added, each frame took **30 ms**, but the game only has **20 ms** per frame (50 fps). I timed every part:
> **Analogy: a kitchen timing each cook to find who's holding up the orders.**

| Slow part | Fix | Analogy |
|---|---|---|
| Side panel recalculated 1,400 dot colours one by one | calculate all colours in one go | painting a wall with a roller instead of a toothbrush |
| Blind-spot shadow made a full-screen see-through layer every frame | only make a layer the size of the wedge | using a sticky note, not a whole poster |
| Brain loop rolled random "raindrops" 200 separate times per frame | roll them all at once, and add up spikes faster | buying groceries in one trip, not 200 |
| Line of sight recalculated constantly | remember answers (the maze never changes) | memorising your times tables |
| Glow picture redrawn every frame | redraw every other frame (still 25 times a second) | a flipbook with slightly fewer pages |

Result: **~20 ms per frame**. The brain loop was rewritten, so I **re-ran the behaviour tests**: same escape timing in the U-turn test (80–500 ms before contact) and same catch rates within random variation (about 5 catches per 3 minutes at the default settings).

**What you see now, in the middle of the window:**
- **FLY BRAIN:** the real brain silhouette with named regions (lobula, medulla, PVLP, AOTU, LAL, AMMC hearing, GNG). Neurons glow where they really are. When the Giant Fiber fires, a **yellow ring** pops out at its real location.
- **Live caption** from actual neuron activity, e.g. *"Looming detectors firing: something is coming at me"*, *"GIANT FIBER FIRED → TAKEOFF"*, *"Pellet detectors firing → steering left"*.
- **A 6-second heart-monitor trace** of looming (orange), pellet (green) and ear (blue) activity, with **yellow lines for each Giant Fiber spike**.

---

# PART 6 — What's REAL and what's PRETEND

> **Analogy: a movie "based on a true story." Some things really happened; some scenes were added to make the movie work. An honest filmmaker tells you which is which.**

| Part | Real? | In simple words |
|---|---|---|
| Which neurons exist, their names, their sides | ✅ **Real** | straight from the fly map |
| Who connects to whom, and how many synapses | ✅ **Real** | 1.1 million real synapses |
| Cheerleader vs. librarian (excite/inhibit) | ✅ **Real prediction** | the dataset predicts each neuron's chemical |
| Where each eye neuron looks | ✅ real positions, 🟡 approximate angles | converting positions to degrees uses textbook eye sizes |
| Right ear | 🟡 **Real left ear, mirrored** | disclosed |
| Bucket settings (neuron model) | 📄 **Published science** | copied from Shiu et al. 2024 |
| "More synapses = more water" | 📄 **Standard simplification** | real synapses vary in size |
| How hard ghosts and pellets "rain" on spotters | 🔧 **My tuning** | adjusted so the fly behaves sensibly |
| Ghost "sound" | 🔧 **Invented** | ghosts aren't real, so their sound isn't either |
| Turning steering signals into maze moves | 🔧 **My design** | the "motor map" |
| Jump speed and length | 🔧 **My design** | inspired by the real Giant Fiber |
| Which neurons to read for jump direction | 🔧 **My design choice** | but those neurons' activity is simulated from real wiring |
| Restless wandering drizzle | 🔧 **Invented** | so the fly explores |
| Where each neuron glows in the brain view | ✅ **Real** | 12.7M real synapse locations, flattened into a view from behind |
| Brain and optic-lobe shapes | ✅ **Real** | downloaded 3D region shapes |
| How bright the glow looks (curve, feedback neurons at 45%) | 🖌️ **Display choice** | changes the picture only, not the simulation |
| Maze, ghosts, speeds | 🎮 **Game** | |

**The most important "not in the code":** there is **no** rule like "if a ghost is close, run away." The decision to escape comes **only** from the simulated Giant Fiber firing.

---

# PART 7 — What's missing (honest limitations)

1. **Invisible tunnels.** Electrical synapses (Giant Fiber → jump muscle, ear → Giant Fiber) can't be seen in the images, so they're missing.
   > *Like a city map that shows roads but not the subway.*
2. **Hose count ≠ exact strength.** We treat every synapse as equally strong, and excite/inhibit is predicted.
   > *Like judging how loud a band is by counting its speakers, not checking their size.*
3. **A piece of the brain, not the whole brain.** 1,887 of ~167,000 neurons. The steering neuron DNa02 gets only ~5% of its real inputs in our piece.
   > *Like listening to just the drummer and guitarist from an orchestra.*
4. **No real eyeball.** The game hands "something is growing at angle X" straight to the spotters.
   > *Skipping the camera and handing the brain the summary.*
5. **The pellet circuit is a mate-chasing circuit** used for food.
6. **Front/back is weak in the messengers**, so the default reads it from the eye spotters.
7. **Right ear is mirrored** from the left.
8. **No legs, wings or physics.** Movement is simple game logic.
9. **Hearing may be too calming** because of limitation 1.

---

# PART 8 — Cool discoveries to talk about

1. **The fly ignores things that aren't coming at it.** A ghost walking past sideways causes no panic. Nobody coded that; it comes from how looming spotters work.
2. **Left/right escape comes straight from the wiring** (95–100% correct), because each eye wires only to its own-side Giant Fiber.
3. **Brains need brakes.** Leaving out the inhibitory neurons made the brain seize. Adding the real ones fixed it, with no invented knob.
4. **Spotters looking in different directions wire to different messengers** (front → DNp02, back → DNp11, down → DNp04), matching published research.
5. **The eyes know front from back perfectly, but the messengers barely do.** The information fades like a game of telephone.
6. **In this wiring, hearing calms the escape reflex** instead of triggering it.
7. **The blind spot matters.** Most deaths are ghosts sneaking up from behind while the fly flees another ghost.

---

# PART 9 — Numbers cheat sheet

| What | Number |
|---|---|
| Dataset | MaleCNS v1.0 (`male-cns:v1.0`) on neuPrint |
| Whole fly map | ~167,000 neurons |
| Neurons downloaded | 1,745 |
| Neurons in the brain (after ear mirror) | **1,887** |
| Synapses in the brain | **1,150,499** |
| Connections in the brain | 136,135 |
| Looming spotters | 435 (LC4 126, LPLC2 185, LC6 124) |
| Pellet spotters (LC10a) | 275 |
| Ear neurons | 486 (243 real left + 243 mirrored) |
| Middlemen + balancers | 669 |
| LC4 → Giant Fiber synapses | 6,362 |
| LPLC2 → Giant Fiber synapses | 4,862 |
| Brain flipbook page | 0.1 ms |
| Brain speed | ~6× faster than real time |
| Left/right escape correct | 95–100% |
| Front/back: eyes / messengers / + middlemen | 100% / 59% / 68% |
| Wrong-way jumps (circuit → eyes default) | ~38% → ~1% |
| Default game | caught ~once per 45 s, ~11 jumps per min |
| Maze | 19 × 21 tiles, 181 pellets, 4 ghosts |
| Synapse positions in brain view | 12,740,732 |
| Code | ~1,700 lines of Python in `flypac/` |

---

# PART 10 — The project files

> **Analogy: a restaurant.**

```
fly-pacman/
├── DEBRIEF.md       📖 this story
├── .env             🔑 your neuPrint token (SECRET — never share)
├── .gitignore       🚫 keeps .env and other private files out of uploads
│
├── flypac/          🍳 THE KITCHEN (the actual project)
│   ├── config.py      📋 the recipe card: which neurons, tryout rules, eye sizes
│   ├── fetch.py       🛒 grocery shopping: downloads the map with neuprint-python
│   ├── fetch_anatomy.py 📸 photographer: downloads real brain shapes + every synapse location
│   ├── brainview.py   ✨ the light show: makes neurons glow where they really are
│   ├── brain.py       🧠 the chef: bucket neurons, senses, reading the messengers, ear mirror
│   ├── test_brain.py  🧪 taste test: fake scenes to check the brain
│   ├── maze.py        🧱 the dining room layout: walls, movement, line of sight
│   ├── world.py       🎲 the service: ghosts, fly body, senses → brain → movement
│   └── game.py        🖥️ the presentation: the window and the live brain panel
│
├── data/            🥫 THE PANTRY
│   ├── neurons.csv    every neuron: name, side, chemical, role, where it looks
│   ├── edges.csv      every connection: from, to, how many synapses
│   ├── meta.json      the receipt: what was downloaded, when, with which rules
│   ├── anatomy_*      brain shapes, neuron footprints, and their receipt
│   └── *.png          screenshots and test plots
│
└── scoping/         📓 THE LAB NOTEBOOK
    ├── SCOPING.md     notes written as we went
    └── *.py           all the investigation and test scripts
```

---

# PART 11 — How to run it

Open a terminal in the project folder and run:

```bash
.venv\Scripts\python -m flypac.game
```

| Key | What it does |
|---|---|
| `M` | switch front/back readout (eyes ↔ circuit) |
| `H` | ears on/off |
| `+` / `-` | ghosts faster/slower |
| `1`–`4` | number of ghosts |
| `F` | fast-forward |
| `Space` | pause |
| `R` | restart |
| `S` | save a screenshot in `data/` |
| `Esc` | quit |

To re-download the fly map (needs your token): `.venv\Scripts\python -m flypac.fetch`

*Note: on this computer, Windows security once blocked the plotting library that `test_brain.py` uses for its charts. The game itself doesn't need it.*

---

# PART 12 — Questions people might ask you (with simple answers)

**"Is this a real fly brain?"**
> It's a computer simulation that uses the real wiring map of a real male fruit fly: about 1,900 neurons and 1.15 million connections for seeing, hearing, escaping and steering. The neurons themselves are simplified.

**"Is it AI? Did you train it?"**
> No training and no machine learning. The connections come straight from the fly map and never change. I only tuned how strongly game events excite the eye neurons, and how the output neurons turn into maze moves.

**"How does it decide to run?"**
> A ghost rushing at the fly excites its looming-detector neurons. Those flood the Giant Fiber, the fly's real escape neuron. If the Giant Fiber fires, the fly jumps. There's no "if ghost near, run" rule.

**"How does it know which way to run?"**
> Left/right comes straight from the wiring: each eye connects only to the escape neuron on its own side. Front/back turned out to be weak in the escape neurons, so by default I read it from which eye neurons fired, based on where each one looks. You can switch to the pure escape-neuron version, and the fly does worse.

**"Where did the connection strengths come from?"**
> From real synapse counts in the MaleCNS v1.0 connectome, downloaded with neuprint-python. Strength = number of synapses × a fixed amount from a published fly brain model (Shiu et al. 2024), positive or negative depending on the neuron's predicted chemical.

**"What's missing?"**
> Electrical synapses (invisible in the images), exact synapse strengths, most of the brain, the eye itself, legs and wings.

**"Why does it still die sometimes?"**
> Usually it escapes one ghost straight into another sneaking up in its blind spot. Flies really can't see directly behind them.

**"What was the hardest part?"**
> Pick your favorite chapter: the brain having a seizure until we added the real inhibitory neurons, the front-vs-back mystery, or tracking down why the fly ran into ghosts.

---

# PART 13 — Talking about it on LinkedIn

## ✅ Safe to say
- "Wired with real synapse counts from the MaleCNS v1.0 connectome (Janelia / Cambridge / Google), queried with neuPrint."
- "A spiking neural network (leaky integrate-and-fire) of ~1,900 neurons and ~1.15M synapses."
- "No scripted flee rule: escapes happen when the simulated Giant Fiber neuron fires."
- "A live panel shows which neurons fire."
- "The brain view lights up each neuron at its real position, from 12.7M synapse locations in the connectome."

## ❌ Avoid saying
- "A complete fly brain" → it's a piece of the circuit.
- "Exactly how a real fly behaves" → it's a simplified model with design choices.
- "AI learned to play" → nothing was trained.
- "Real synapse strengths" → they're synapse *counts* times one constant.

## 🙏 Give credit to
- **MaleCNS v1.0 connectome:** Janelia FlyEM, the Cambridge Drosophila Connectomics Group, Google Connectomics. Check the [Janelia male CNS page](https://www.janelia.org/project-team/flyem/male-cns-connectome) for how they want to be cited and for data terms before sharing code or data.
- **neuPrint / neuprint-python** (Janelia).
- **Shiu et al., 2024, *Nature*:** the published fly-brain model whose neuron settings we used.
- **Dombrovski et al., 2023, *Nature*:** research on how looming neurons wire to escape neurons by viewing direction.

## ✍️ Draft post (rewrite in your own voice)

> I built **Fly-Pacman**: a Pac-Man game where the player is a fruit fly that nobody controls. 🪰
>
> Its "brain" is a spiking neural network of ~1,900 neurons wired with ~1.15 million real synapses from the male fruit fly connectome (MaleCNS v1.0 by Janelia, Cambridge and Google), pulled with neuPrint.
>
> 👀 Looming-detector neurons fire as a ghost charges, and they drive the Giant Fiber, the fly's real escape neuron. There's no "if ghost near, run" rule anywhere.
> 🟢 A visual pursuit pathway steers it toward pellets.
> 🧠 You can watch the fly's real brain light up: each simulated neuron glows at its true position in the connectome as a ghost attacks.
>
> What surprised me:
> • Left/right escape falls straight out of the wiring, but front/back is surprisingly hard for the escape neurons.
> • Leaving out inhibitory neurons gave the brain a "seizure." Adding the real ones fixed it.
> • Flies have a blind spot behind them, and the ghosts exploit it.
>
> Limitations: it's a subset of the brain, synapse counts aren't exact strengths, electrical synapses aren't in the data, and some sensory/motor mappings are my own design choices.

---

# PART 13½ — How to read the dashboard

> **Analogy: a car dashboard.** The maze is the road. The panels are the gauges telling you what's happening under the hood.

The window has a top bar and three columns: **maze** (left), **fly brain** (middle), **eyes / ears / escape / steer** (right).

## The top bar
| Item | Meaning |
|---|---|
| `t 473s` | simulated seconds since the start |
| `pellets` | pellets eaten |
| `jumps` | takeoffs: times a Giant Fiber spike launched an escape |
| `survived` | jumps **not** followed by a catch within 2 seconds |
| `caught` | times a ghost got the fly |
| **FORAGING** (green) | normal walking and eating |
| **ESCAPE! (Giant Fiber fired)** (yellow) | the fly is mid-takeoff |
| **CAUGHT** (red) | a ghost got it; the round resets |

## The maze (left)
- **The fly** (brown body, red eyes, white wings) points where it's facing.
- **Faint grey wedge behind the fly** = its **blind spot**. Anything inside is invisible to the fly.
- **Yellow ring around the fly** = it's in an escape burst.
- **Pink bar in the middle** = the ghost-house door (only ghosts can pass).
- **"What you're watching"** = a plain explanation for anyone seeing a recording.

## FLY BRAIN (middle)
> **Analogy: a night-time satellite photo of a city, where lit windows show where people are awake.**

- **The dark shape is the real fly brain**, from the 3D shapes in the connectome: the big middle part is the central brain, and the two "ears" on the sides are the optic lobes (vision).
- **Seen from behind the head**, so the fly's left is on your left.
- **Every glow is a real neuron at its real location** (from its synapse positions). Brighter = firing faster. Colour = what kind of neuron (see COLOURS).
- **Labels**, and what each area does:

| Label | What happens there | Analogy |
|---|---|---|
| **lobula** | where looming and small-object detectors receive their vision input | the camera's sensor room |
| **medulla** | an earlier vision layer | the lens before the sensor |
| **PVLP** | where looming detectors deliver their message, and where the Giant Fiber listens | the alarm control room |
| **AOTU** | where pellet detectors (LC10a) deliver their message | the "target spotted" desk |
| **LAL** | steering and walking hub | the steering column |
| **AMMC (hearing)** | where ear neurons arrive | the reception for sound |
| **GNG** | bottom of the brain, near the neck, where messages head down to the body | the exit ramp to the highway |

- **Yellow ring + "Giant Fiber" tag** appears at the Giant Fiber's real position whenever it fires.
- **The caption under the brain** is written from live neuron activity:
  - *"GIANT FIBER FIRED → TAKEOFF"*: a Giant Fiber spiked.
  - *"Looming detectors firing (X Hz avg): something is coming at me"*: the average looming detector is above 1 spike per second.
  - *"Antennae feel air vibration"*: ear neurons are active.
  - *"Pellet detectors firing → steering left/right/ahead"*: pellet detectors are active, and the steering neurons say which way.
  - *"Quiet: wandering"*: nothing much is happening.

### The "last 6 s" trace
> **Analogy: a hospital heart monitor.** Newest on the right, oldest on the left.

| Line | Meaning |
|---|---|
| **orange** | average firing of all 435 looming detectors |
| **green** | average firing of all 275 pellet detectors |
| **blue** | average firing of the ear neurons |
| **yellow vertical line** | a moment when a Giant Fiber spiked |

The top of the box is 20 spikes/second. A line that goes **flat at the top** has hit the ceiling. For example, the ears max out when a ghost is right next to the fly.

**Typical story in the trace:** a wobbly green line (eating pellets), then orange rising (a ghost is coming), then yellow lines (Giant Fiber fires), then green returning (back to eating).

### COLOURS and MIDDLE LAYER
- **COLOURS** is the key for the brain picture.
- **MIDDLE LAYER** has 669 small squares, one per middleman or feedback neuron. Excitatory ones (orange when active) come first, inhibitory ones (blue when active) at the end. A square lights up as that neuron fires.
  > **Analogy: a stadium light board, one bulb per person.**

## EYES (right, top)
> **Analogy: a radar screen centred on the fly.**

- **The brown triangle in the middle is the fly**, and it always points **up** = the direction the fly is facing, **not** up on the maze. When the fly turns, the world turns around it.
- **Every dot is one real visual neuron.** Where it sits around the circle = **the direction that neuron looks**, worked out from its real position in the lobula (Part 5, Chapter 4).
  - Top of the circle = straight ahead. Left side = fly's left. Bottom = behind.
- **The rings are neuron types:** LC4 (inner), LPLC2, LC6, LC10a (outer). Within a ring, dots nudge slightly outward if they look upward and inward if they look downward.
- **The dark wedge at the bottom is the blind spot.** No neuron looks there, so there are no dots.
- **Dot brightness:** silent = a tiny dim pixel; firing = a bigger dot, brighter the faster it fires.
  - **Orange dots light up** = looming detectors seeing something coming at the fly, in that direction.
  - **Green dots light up** = pellet detectors seeing pellets in that direction.
- **Coloured dots just outside the circle** = ghosts the fly can currently see, placed at the direction they are (same colours as the ghosts). No dot = the ghost is hidden behind a wall or out of range.

**How to read it:** a pink dot appears on the right rim, then orange neuron dots on the right side brighten as the pink ghost charges, then the Giant Fibers flash below. You're watching the fly see a threat, figure out where it is, and react.

## EARS
- **JO left / JO right\*:** the average firing of the left and right ear neurons, with bars up to 40 Hz.
- The right ear is marked **\*** because it's mirrored from the left (Part 5, Chapter 6).
- The ears only react when a ghost is **very close** (about 2 tiles or less along the corridors), because near-field sound fades fast.

## ESCAPE
- **GF L / GF R circles:** the left and right Giant Fibers. They **flash yellow** when they fire, then fade.
- **Bars** (left + right added together, scale up to 150 Hz):

| Bar | Neuron | What its real wiring suggests |
|---|---|---|
| DNp02 front | DNp02 | danger in **front** |
| DNp11 back | DNp11 | danger **behind** (and above) |
| DNp04 low | DNp04 | danger **below** |
| TTMn jump | TTMn | the jump-leg muscle neuron (weak here, because its main input is the invisible electrical link) |

## STEER
- **DNa02 L / DNa02 R:** left and right steering neurons, with bars up to 80 Hz.
- **Whichever is higher is the way the fly turns at the next junction.** Right higher = turn right.
  > **Analogy: two people pulling the steering wheel. The stronger pull wins.**
- They're rarely at zero, because a tiny random drizzle keeps the fly wandering.

## SETTINGS and footer
- **SETTINGS** shows the current options and their keys (`M`, `H`, `1–4`, `+/-`, `Space`, `F`, `W`).
- **The footer** reminds viewers what's real (wiring from male-cns v1.0) and what's a design choice.

## Watch one attack, panel by panel
1. **EYES:** a ghost dot appears on the rim.
2. **EYES:** orange neuron dots on that side brighten.
3. **Trace:** the orange line rises. **Brain:** the lobula starts glowing orange.
4. **ESCAPE:** a Giant Fiber circle flashes. **Brain:** a yellow ring and "GIANT FIBER FIRED". **Trace:** a yellow line. **Top bar:** "ESCAPE!"
5. **ESCAPE bars:** DNp02 / DNp11 / DNp04 jump up. **MIDDLE LAYER:** squares light up.
6. **Maze:** the fly gets a yellow ring and sprints away.
7. **EARS** twitch only if the ghost got really close.
8. **Everything calms down**, and green (pellets) and STEER take over again.

---

# PART 14 — Word list

| Word | Simple meaning | Analogy |
|---|---|---|
| **Adaptation** | a neuron getting "tired" after firing a lot | legs tiring after running |
| **Antenna / Johnston's organ (JO)** | the fly's "ear" | arm hairs feeling a breeze |
| **Azimuth** | left-right angle | clock direction around you |
| **Blind spot** | area behind the fly it can't see | the back of your head |
| **Connectome** | full wiring map of a nervous system | every road in a city |
| **Descending neuron** | carries commands from the brain to the body | messenger from HQ |
| **Electrical synapse / gap junction** | direct tunnel between neurons, invisible in the images | secret subway |
| **Elevation** | up-down angle | looking up or down |
| **Excitatory** | makes the next neuron more likely to fire | cheerleader |
| **Feedback layer** | neurons sending signals back into the circuit | teachers in a classroom |
| **Giant Fiber (DNp01)** | the fly's emergency jump neuron | fire-alarm lever |
| **Inhibitory** | makes the next neuron less likely to fire | librarian saying "shhh" |
| **LIF (Leaky Integrate-and-Fire)** | simple neuron model | bucket with a hole |
| **Looming** | something growing fast in view | a ball flying at your face |
| **Lobula** | a visual processing area of the fly brain | a sorting room for vision |
| **MaleCNS v1.0** | the male fruit fly connectome we used | the map |
| **neuPrint** | website hosting the connectome | the library |
| **Neuron** | a brain cell | a person in a game of telephone |
| **Neurotransmitter** | chemical a neuron uses to signal | the type of message |
| **Optic chiasm** | where visual wiring crosses over | a road crossing a bridge |
| **Poisson input** | random pings at an average rate | rain on a roof |
| **Receptive field** | the patch of view one neuron watches | one fan's binoculars view |
| **Refractory period** | short rest after firing | bucket standing back up |
| **Retinotopy** | neighboring neurons watch neighboring spots | fans in stadium seats |
| **Spike** | a neuron's quick electrical blip | a sneeze |
| **Synapse** | connection point between neurons | a garden hose |
| **Threshold** | level a neuron must reach to fire | the line on the bucket |
| **Token** | your personal access key to neuPrint | a library card |
| **Tm1** | a visual neuron type, one per eye column; our reference grid | graph paper |
