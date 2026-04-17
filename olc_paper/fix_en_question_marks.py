from pathlib import Path
from docx import Document


SRC = Path(r"C:\Users\sosoy\Downloads\Ultimate_Realization_Dilemma_EN_Faithful.docx")
DST = SRC.with_name("Ultimate_Realization_Dilemma_EN_Faithful_clean.docx")


REPLACEMENTS = {
    "Whatever your ultimate realization is called?seeing one?s true nature, transcending the cycle of rebirth, entering heaven, acting through non-action...":
    "Whatever your ultimate realization is called - seeing one's true nature, transcending the cycle of rebirth, entering heaven, acting through non-action...",

    "Whatever path you use to approach that realization?Buddhist practice, Zen insight, Christian wisdom, yogic wisdom, energy cultivation, mystical verification...":
    "Whatever path you use to approach that realization - Buddhist practice, Zen insight, Christian wisdom, yogic wisdom, energy cultivation, mystical verification...",

    "Before the heart reaches freedom and completeness, there is one fundamental obstacle. If this issue is not seen clearly, the road toward ultimate realization becomes extremely difficult. This is also a repeated error among most spiritual practitioners and religious truth-seekers across history: a directional error in practice, which is really an error in how one understands one?s relationship with the Source.":
    "Before the heart reaches freedom and completeness, there is one fundamental obstacle. If this issue is not seen clearly, the road toward ultimate realization becomes extremely difficult. This is also a repeated error among most spiritual practitioners and religious truth-seekers across history: a directional error in practice, which is really an error in how one understands one's relationship with the Source.",

    "For ordinary people, ignorance is very thick?so thick that they cannot see the light of Source-wisdom, and spend their lives in fear and anxiety, using small cleverness to struggle against the world.":
    "For ordinary people, ignorance is very thick - so thick that they cannot see the light of Source-wisdom, and spend their lives in fear and anxiety, using small cleverness to struggle against the world.",

    "For sages, ignorance is somewhat thinner. They can receive some guidance from Source-wisdom and see the deeper causes of suffering, so they can respond to life?s difficulties more fundamentally.":
    "For sages, ignorance is somewhat thinner. They can receive some guidance from Source-wisdom and see the deeper causes of suffering, so they can respond to life's difficulties more fundamentally.",

    "For true awakened ones?truly awakened, because many people now claim that title?they are those who have remembered how they became lost in the dream of ignorance. They see their own nature clearly. They see that ultimately there is no ignorance, and no real problem to begin with.":
    "For true awakened ones - truly awakened, because many people now claim that title - they are those who have remembered how they became lost in the dream of ignorance. They see their own nature clearly. They see that ultimately there is no ignorance, and no real problem to begin with.",

    "All thoughts of this type lay out an infinitely long road of cultivation. How long? Exactly as long as the number of deficiencies you believe still need correction. This road can point toward the end, yes?but in time, it becomes countless cycles, countless kalpas. And how can you guarantee that in life after life you will not fall back into the dream of samsara and lose the way again? In truth, everyone in this world has walked this road many times. Yet those who truly break through are very few.":
    "All thoughts of this type lay out an infinitely long road of cultivation. How long? Exactly as long as the number of deficiencies you believe still need correction. This road can point toward the end, yes - but in time, it becomes countless cycles, countless kalpas. And how can you guarantee that in life after life you will not fall back into the dream of samsara and lose the way again? In truth, everyone in this world has walked this road many times. Yet those who truly break through are very few.",

    "True awakened ones understand this: the end is not reached by endlessly moving forward. Instead, one stops and asks: Why am I rushing? Where am I trying to go? Then a recognition appears: 'Wait. Maybe there is nowhere I actually need to go. But there is always a voice (the ego) saying, hurry, hurry, don‘t fall behind.' Looking back, the road exists?but that road was carved by your own repetitive circling. It is a loop with no end.":
    "True awakened ones understand this: the end is not reached by endlessly moving forward. Instead, one stops and asks: Why am I rushing? Where am I trying to go? Then a recognition appears: 'Wait. Maybe there is nowhere I actually need to go. But there is always a voice (the ego) saying, hurry, hurry, don't fall behind.' Looking back, the road exists - but that road was carved by your own repetitive circling. It is a loop with no end.",

    "On the eighth day of the twelfth lunar month, when the Buddha saw the morning star, a decisive recognition appeared: why does ?I? know the star is there? If we keep clinging to concepts like inner/outer, star/me, this cannot be resolved.":
    "On the eighth day of the twelfth lunar month, when the Buddha saw the morning star, a decisive recognition appeared: why does 'I' know the star is there? If we keep clinging to concepts like inner/outer, star/me, this cannot be resolved.",

    "But when language and conceptual labeling dropped away?no textual thought, no mental naming?he saw clearly: with eyes open, he saw; with eyes closed, he still saw. The star was present, but the conceptual 'I' was absent. At that point he recognized that the true mind of all beings is fundamentally the same, beyond language and beyond interpersonal division.":
    "But when language and conceptual labeling dropped away - no textual thought, no mental naming - he saw clearly: with eyes open, he saw; with eyes closed, he still saw. The star was present, but the conceptual 'I' was absent. At that point he recognized that the true mind of all beings is fundamentally the same, beyond language and beyond interpersonal division.",

    "Shakyamuni?s awakening was not gained in the middle of continuous ascetic effort. It happened when, under the Bodhi tree, he let go of all acquired knowledge and all conceptual thought from this life. In Buddhist language, this is dropping the covering of ignorance (also called the obstacle of what is known).":
    "Shakyamuni's awakening was not gained in the middle of continuous ascetic effort. It happened when, under the Bodhi tree, he let go of all acquired knowledge and all conceptual thought from this life. In Buddhist language, this is dropping the covering of ignorance (also called the obstacle of what is known).",

    "So where is the greatest dilemma of mind-cultivation and spiritual practice? It lies in what you take to be true. That 'taking to be true' comes from one?s cognitive-view system; and this system gains information by comparison. But ultimate truth is 'Originally not one thing?where can dust alight?' If there is fundamentally nothing to compare, then what problem is there? Most problems are false problems made 'real' by egoic fixation.":
    "So where is the greatest dilemma of mind-cultivation and spiritual practice? It lies in what you take to be true. That 'taking to be true' comes from one's cognitive-view system; and this system gains information by comparison. But ultimate truth is 'Originally not one thing - where can dust alight?' If there is fundamentally nothing to compare, then what problem is there? Most problems are false problems made 'real' by egoic fixation.",

    "If one has not aligned the relationship between true mind and Source, one spends life groping in darkness and feeling attacked by enemies and by the world. In that darkness, one does not see clearly that the enemy is not another person?it is one?s own misidentification.":
    "If one has not aligned the relationship between true mind and Source, one spends life groping in darkness and feeling attacked by enemies and by the world. In that darkness, one does not see clearly that the enemy is not another person - it is one's own misidentification.",

    "Yet tragically, most people live as if controlled by the remote?and they themselves granted that power. This sounds absurd, but from awakened sight, the world often appears exactly this inverted.":
    "Yet tragically, most people live as if controlled by the remote - and they themselves granted that power. This sounds absurd, but from awakened sight, the world often appears exactly this inverted.",

    "Core Claim: The text argues that the deepest obstacle in spiritual practice is not lack of effort but a mistaken relational model?assuming separation from Source and then trying to close an imagined gap.":
    "Core Claim: The text argues that the deepest obstacle in spiritual practice is not lack of effort but a mistaken relational model - assuming separation from Source and then trying to close an imagined gap.",

    "Practical Value: As a critique of recursive self-improvement frameworks, it is strong and psychologically incisive. It is especially useful for readers trapped in perpetual ?self-fixing? cycles.":
    "Practical Value: As a critique of recursive self-improvement frameworks, it is strong and psychologically incisive. It is especially useful for readers trapped in perpetual 'self-fixing' cycles.",
}


def main() -> None:
    doc = Document(str(SRC))

    for p in doc.paragraphs:
        t = p.text
        if t in REPLACEMENTS:
            p.text = REPLACEMENTS[t]
        else:
            # low-risk fallback fixes
            t2 = t.replace("one?s", "one's")
            t2 = t2.replace("don‘t", "don't")
            t2 = t2.replace("Shakyamuni?s", "Shakyamuni's")
            t2 = t2.replace(" ?I? ", " 'I' ")
            t2 = t2.replace(" ?self-fixing? ", " 'self-fixing' ")
            if t2 != t:
                p.text = t2

    doc.save(str(DST))
    print(DST)


if __name__ == "__main__":
    main()

