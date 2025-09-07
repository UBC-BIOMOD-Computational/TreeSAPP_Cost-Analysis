# **Cost Analysis of Protein Production: Comparative Overview of Hydrogel-Based Cell Free Systems**

## **Introduction**

### **Why Is This Important?**

The cost of protein production directly impacts how protein research, product development, and scalability. High costs or inefficiencies can delay or inhibit innovation, particularly in fields such as synthetic biology and personalized medicine.

In recent years\[add reference\], cell-free protein synthesis methods have offered a flexible, rapid alternative that bypasses many of these bottlenecks. It enables faster prototyping of genetic constructs for synthetic biology, supports GMP-compatible workflows for therapeutic protein production, and is ideal for low-volume, field-deployable biomanufacturing applications where speed and adaptability are essential.

## **Our Models:** 

### **We chose to investigate three common use cases of protein production**

| Commercial Applications | Laboratory Applications | Prototype & Experimental Applications |
| :---- | :---- | :---- |
| Enzymes for industrial catalysis Vaccines (e.g., recombinant subunit vaccines) Diagnostics (antigens, antibodies) Research reagents | Rapid prototyping of engineered proteins High-throughput screening Feasibility testing of novel constructs | Low-volume but high-value therapeutic proteins (e.g., rare disease biologics) Biosensors and diagnostic devices Synthetic biology circuit components |

## **Overview of Findings**

We have created the following comparisons:

| Lab CFPP x Lab CBPP |  |
| :---- | :---- |
| Lab CFPP (with micropad recycling) x Lab CBPP |  |
| Industry CFPP x Industry CBPP |  |
| Industry CFPP (with micropad recycling) x Industry CBPP |  |
| CFPP Prototype x CBPP Prototype |  |
| Switching proteins CFPP Prototype x CBPP Prototype |  |

[https://www.betalifesci.com/blogs/articles/cost-analysis-and-economic-considerations-in-large-scale-protein-purification](https://www.betalifesci.com/blogs/articles/cost-analysis-and-economic-considerations-in-large-scale-protein-purification) 

## **How we evaluate comparisons**

We use the metrics of cost efficiency, production rate, and scalability because they directly reflect the practical performance and viability of a protein production system in real-world applications:

1\. Cost Efficiency (mg per $)

This metric tells us how much protein we get per unit of cost. It’s crucial for determining the economic feasibility of producing a given protein, especially at scale. A system with higher cost efficiency, like the cell-free system in this analysis, allows researchers and manufacturers to produce more material with less financial input—making it ideal for both prototyping and commercialization.

2\. Production Rate (mg per hour)

Production rate measures how quickly a system can generate protein. Time is often a limiting factor in research, diagnostics, and therapeutic applications. A higher production rate (as seen in the cell-free system, which is 4× faster than the cell-based system) means faster turnaround for experiments, product development, and urgent manufacturing scenarios—such as pandemic response or point-of-care diagnostics.

3\. Scalability (Annual Throughput)

Scalability refers to the system’s capacity to be expanded for high-volume production. It’s essential for transitioning from small-scale lab work to industrial manufacturing. The ability of the cell-free system to produce 200 kg/year—10× more than the cell-based setup—demonstrates its potential for large-scale use, particularly where traditional systems may bottleneck due to complexity, labor, or host limitations.

## **Results and Discussion**

TODO ADD HERE: Cost, time, and yield comparisons across systems.

* TODO ADD HERE: Identification of bottlenecks in traditional systems and advantages of alternative approaches.

* TODO ADD HERE:  Demonstration of how cell-free systems can reduce turnaround time and mitigate toxicity issues.

* TODO ADD HERE:   
* TODO ADD HERE:   
  **Graphs**: Include bar charts and cost breakdown comparisons across systems.

### **Discussion Points**

#### **Recycling DNA**

#### **Switching Proteins**

Cell-free: simple plasmid/DNA template switch, Cell-based: requires cell line development, and for laboratory and industrial use, it must be clinically verified with GMP certifications and a stable ell-line must be developed for the transformation. This also involves cloning, transformation, and scale-up.

**Methods for conducting Cost analysis**

The cell-based protein production model is based on a standard E. coli expression workflow,  \[CITE https://onlinelibrary.wiley.com/doi/10.1002/pro.102 \] including transformation, batch culture, induction, and purification. Cultures are grown in defined media with 1% glucose, reaching an OD600 of \~15 within 36 hours. Protein expression is induced at OD600 \~4–5 using 0.5 mM IPTG and incubated overnight at 20 °C. Cells are harvested at OD600 10–20, followed by lysis (e.g., high-pressure homogenization) and centrifugation to isolate the soluble protein. Typical yields range from 14–17 mg per 50 mL culture. This workflow serves as the basis for cost, time, and yield calculations in the technoeconomic model.

The cell-free protein production model is based on an E. coli extract-based transcription–translation system. Crude lysates are prepared by lysing harvested E. coli cell paste using CelLytic reagent (10 mL per gram of wet biomass), followed by clarification steps. Cell-free reactions are assembled with lysate, energy mix, amino acids, and DNA templates. In the micropad-based system, yields of 2–3 mg/mL can be achieved over 24–36 hours per reaction cycle. Reactions are typically performed in 50 μL volumes, with approximately 400 micropads per mL of feed. Protein is recovered from the soluble reaction mixture without the need for cell lysis or complex downstream clarification. This system forms the basis for cost and yield modeling in the cell-free technoeconomic analysis.

### **Schematic: Cell-Free vs. Cell-Based Production**

* TODO ADD HERE: Include visual diagram showing workflows for both methods:

  * DNA → Protein for cell-free

  * DNA → Transformation → Growth → Lysis → Purification for cell-based

### **Calculation Process Example:**

**Production Goal**: 100 mg purified protein

#### **Steps:**

1. **Production Cycles**:

2. **Initial Setup Costs**:

   * Equipment (e.g., thermocyclers, centrifuges)

   * Reagents (plasmids, cell extract, media)

   * Strains (commercial or engineered hosts)

3. **Per-Cycle Costs**:

   * Consumables (tubes, pipette tips, reagents)

   * Labor (time per batch, training needs)

   * Utilities (electricity, water for autoclaving, etc.)

4. **Efficiency Metrics**:

   * **Cost Efficiency**: $/mg protein

   * **Time Efficiency**: mg protein/hour

   * **Production Efficiency**: yield per batch

**Reference Data and Tools**

### **Code and Scripts**

* Python/R scripts from GitHub

**Final Tables**

* **Results Summary Table**: see models 

* **Cost Table**: Breakdown of each cost component per system.  
  .

