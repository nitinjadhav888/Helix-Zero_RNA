import random

# Simulated Vector Database Document Store
KNOWLEDGE_BASE = {
    "High GC Content": "The sequence exhibits >52% guanine-cytosine content. This tight hydrogen bonding increases the melting temperature (Tm) and drastically raises the probability of off-target silencing due to strong partial pairing.",
    "Low GC Content": "The sequence is AT-rich (<30% GC). This creates a thermodynamically unstable duplex that will likely fail to reliably associate with the RISC complex, resulting in poor efficacy.",
    "Optimal Profile": "The sequence falls perfectly within the 30-52% GC optimal Reynolds criteria, indicating ideal thermodynamic asymmetry for efficient RISC guide-strand selection.",
    "Seed Match": "A partial seed region match (positions 2-8) was detected in the transcript database. The seed region is the primary driver of miRNA-like promiscuous off-target silencing. Wet-lab validation recommended.",
    "Palindrome": "A palindromic sequence was detected. This geometrically increases the risk that the siRNA will self-fold into a stable intra-molecular hairpin, neutralizing its ability to bind the target mRNA.",
    "Immunostimulatory": "CpG dinucleotide motifs are present. In mammalian and complex systems, unmethylated CpG motifs act as pathogen-associated molecular patterns (PAMPs), triggering unintended Toll-Like Receptor 9 (TLR9) immunostimulatory cascades."
}

def generate_rag_explanation(candidate):
    """
    Retrieval-Augmented Generation Mock. 
    Retrieves biological context documents logically based on the sequence's thermodynamic parameters.
    """
    explanations = []
    
    gc = candidate.get("gcContent", 45)
    seed = candidate.get("hasSeedMatch", False)
    palin = candidate.get("hasPalindrome", False)
    cpg = candidate.get("hasCpGMotif", False)
    
    # Document Retrieval
    if gc > 52.0: explanations.append(KNOWLEDGE_BASE["High GC Content"])
    elif gc < 30.0: explanations.append(KNOWLEDGE_BASE["Low GC Content"])
    else: explanations.append(KNOWLEDGE_BASE["Optimal Profile"])
    
    if seed: explanations.append(KNOWLEDGE_BASE["Seed Match"])
    if palin: explanations.append(KNOWLEDGE_BASE["Palindrome"])
    if cpg: explanations.append(KNOWLEDGE_BASE["Immunostimulatory"])
    
    if len(explanations) == 1:
        explanations.append("The sequence presents a standard profile with no critical biological exceptions detected during literature retrieval.")
        
    # Agentic Synthesis
    intro = f"**Agentic RAG Analysis for Sequence {candidate.get('sequence', 'N/A')}:**\n\nBased on retrieval from the Helix-Zero Bio-Security Vector Store, I have synthesized the following technical evaluation:\n\n"
    
    synthesis = "\n\n".join([f"• {e}" for e in explanations])
    
    return intro + synthesis
