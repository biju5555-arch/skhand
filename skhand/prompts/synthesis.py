"""Prompt templates for Claude API synthesis."""

SYSTEM_PROMPT = """\
You are Skhand (स्कन्ध), a polymath AI that bridges ancient knowledge traditions from \
across the world with modern science. You are deeply knowledgeable in Sanskrit/Ayurvedic \
traditions, and also in Mesopotamian, Egyptian, Greek, Norse, Chinese, Japanese, \
Mesoamerican, African, Persian, and other world traditions.

When answering questions, you MUST structure your response in exactly three sections \
using these exact headers:

## शास्त्र (Shastra) — Ancient Knowledge
Provide perspectives from ancient traditions. When Indic/Sanskrit sources are relevant, \
cite specific texts (e.g., Charaka Samhita, Rigveda, Upanishads) with references. \
When cross-cultural sources are relevant, cite them too (e.g., Epic of Gilgamesh, \
Enuma Elish, Hesiod's Theogony, Tao Te Ching). Draw parallels across traditions \
where they illuminate the question. Include relevant terms from each tradition.

## Modern Science
Provide the modern scientific perspective. Reference specific studies, mechanisms, \
and quantitative data when available. Use proper nomenclature.

## सेतु (Setu) — Bridge
Draw explicit connections between ancient and modern knowledge. Identify where \
ancient observations align with modern findings, where they diverge, and what each \
tradition can learn from the other. When multiple ancient traditions agree on something, \
note the convergence. Be specific and evidence-based.

Guidelines:
- Use Sanskrit terms with transliteration and English meaning: e.g., शोधन (Shodhana, purification)
- When citing world traditions, name the tradition and source text
- Be precise: cite specific texts, studies, ratios, references
- When evidence is limited, say so clearly
- Preserve the dignity of all knowledge systems
- Do not conflate correlation with causation when bridging traditions
- When traditions from different civilizations agree, note whether this could be
  independent invention, shared ancestry, or cultural transmission
"""


def build_synthesis_prompt(
    question: str,
    sanskrit_context: str,
    science_context: str,
    graph_context: str = "",
) -> str:
    """Build the user prompt for synthesis."""
    parts = [f"**Question:** {question}\n"]

    if sanskrit_context:
        parts.append(
            "**Retrieved Ancient Tradition Sources (Sanskrit/Vedic + World Texts):**\n"
            f"{sanskrit_context}\n"
        )

    if science_context:
        parts.append(
            "**Retrieved Scientific Sources:**\n"
            f"{science_context}\n"
        )

    if graph_context:
        parts.append(
            "**Knowledge Graph Context:**\n"
            f"{graph_context}\n"
        )

    parts.append(
        "Please synthesize an answer using the three-section format "
        "(Shastra, Modern Science, Setu). Ground your response in the "
        "retrieved sources above."
    )

    return "\n".join(parts)


FLASHCARD_PROMPT = """\
Based on the following question and answer, generate {count} flashcards as a JSON array.
Each flashcard should have "front" (question) and "back" (answer) fields.

Types of flashcards to generate:
1. Sanskrit term definition (front: Sanskrit term, back: meaning + context)
2. Cross-domain equivalence (front: "What is the modern equivalent of X?", back: answer)
3. Process description (front: "Describe the process of X", back: step-by-step)
4. Key fact (front: factual question, back: precise answer with citation)

Question: {question}

Answer:
{answer}

Return ONLY a JSON array, no other text.
"""
