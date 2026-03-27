# How Helix-Zero Actually Works (The Simple Version)
*An analogy-based explanation for non-biologists*

Imagine every living thing (a mosquito, a weed, a human, a honeybee) is a massive factory. The DNA (**Genome**) is the master blueprint that contains thousands of individual instruction manuals (**Genes**) on how to build machines to keep the factory running. 

Our goal is to build a highly targeted "molecular sniper" (an **siRNA**) that sneaks into a pest's factory, finds one specific, critical instruction manual, and glues the pages shut so the pest dies—but if that same sniper accidentally wanders into a honeybee's factory, the spell won't stick because the honeybee's manual is written in a slightly different language!

Here is exactly how our application accomplishes that.

---

## 1. What are our Inputs?
We give the system two very long text files containing strings of letters (`A`, `T`, `C`, `G`):
1. **The PEST Genome:** The entire DNA code of the insect or weed we want to eliminate.
2. **The NON-TARGET Genome:** The DNA code of the beneficial insects or mammals (like humans and bees) we want to protect.

We also upload a **"Database of Essential Genes"**—a pre-written dictionary that tells us which instruction manuals (genes) are absolutely crucial for a pest's survival.

## 2. What is our Process?
The application works like a very strict assembly line with three main steps:
1. **Find the best target:** The app scans the pest's entire blueprint and finds the genes that are rated highly in our essentiality dictionary.
2. **Design the weapon:** It slides a "magnifying glass" across that gene, 21 letters at a time, to design thousands of potential "sticky spells" (siRNAs) that exactly match combinations of those 21 letters.
3. **Run the gauntlet:** It throws every single one of those thousands of potential siRNAs into a grueling **Safety & Physics Firewall** to see which ones survive.

## 3. From where is the system fetching data?
The system isn't guessing; it is pulling real information from:
- **Your uploaded FASTA files:** The exact pest and bee DNA you supplied.
- **Local JSON Databases:** Pre-downloaded files like `essential_genes.json` that tell the app what genes are lethal. *(Note: If you upload a custom, unnamed sequence, we programmed the app to simulate this data mathematically so you can still test the UI!)*
- **The Python "AI" Brain:** The system actually makes a web request (`fetch()`) in the background to a Python server we built (`http://localhost:8000/predict`). This server uses advanced mathematical modeling to act as an "Artificial Intelligence" that scores the siRNA.

## 4. What is the system Comparing?
To ensure the siRNA is safe and effective, the system acts like a hyper-paranoid security guard comparing ID cards:
- **Toxicity Check:** It takes your 21-letter siRNA sequence and compares it against the entire Honeybee genome. If even *15 letters in a row* exactly match a sequence in the bee, the app throws it in the trash labeled `TOXIC`.
- **Allergy Check (Immune Motif):** It compares your sequence against a bad-list of known "Danger Patterns" (like the sequence `UGUGU`). If the human body naturally mistakes your siRNA for a virus because of its shape, it gets penalized.
- **Evolutionary Spread:** It compares the target gene against the family tree of other animals to see how "unique" it really is.

## 5. How are the Outputs generated in the UI?
When you click "Generate" and see numbers magically appear, here is exactly how those dials are populated under the hood:

### ⚙️ Efficiency Score (e.g. 85%)
This is how well the sticky spell will glue the manual shut. It is calculated by two things:
1. **Thermodynamic Asymmetry:** The system mathematically calculates the "energy" required to pry the 5' end open versus the 3' end open using physics formulas.
2. **Python AI Score:** It sends a batch of 100 sequences at a time to the Python server, which calculates the exact percentage score using pattern-matching logic, then beams that percentage back to the React UI.

### 🛡️ Enhanced Safety Score (e.g. 98%)
This starts at 100%. For every "security check" the siRNA fails, points are deducted:
- If the spelling looks suspiciously like a human `MicroRNA` → **Minus 40 points.**
- If there are too many `C` and `G` letters next to each other (which triggers immune shock) → **Minus points.**
If the score drops below 75%, it is immediately deleted from the candidate list so you never even see it.

### ⏳ Resistance Evolution (Durability Score)
This predicts how long it will take for the pest to randomly mutate and become immune to the pesticide (like a bacteria resisting an antibiotic).
- The system knows that `C` turning into a `U` happens naturally at a certain microscopic mutation rate (e.g. `1.37e-6`).
- It calculates exactly how many letters are available to mutate in your siRNA, multiplies it by the population of the bugs, and spits out a calendar prediction (e.g., `< 1 year` or `> 5 years`).

---
**Summary:**
You give the system the pest's DNA. It slices it into 21-letter chunks. It uses physics (thermodynamics) to grade how well they fold, AI to predict how well they kill, and a massive search engine to prove they won't harm bees. Only the perfect candidates survive the gauntlet to be displayed on your screen!
